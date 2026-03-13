"""Inventory orchestration and coordination with dynamic pricing."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, Optional, Tuple

from app.inventory.forecaster import DemandForecast, InventoryForecaster
from app.inventory.reorder_optimizer import ReorderOptimizer, ReorderRecommendation
from app.inventory.stockout_predictor import StockoutPredictor, StockoutPrediction

if TYPE_CHECKING:
    from app.dynamic_pricing.supervisor import DynamicPricingSupervisor, PriceRecommendation

logger = logging.getLogger(__name__)


@dataclass
class InventoryRecommendation:
    """Single SKU inventory recommendation with pricing impact."""
    sku: str
    current_stock: float
    safety_stock: float
    reorder_point: float
    optimal_order_qty: float
    days_to_stockout: float
    pricing_impact: Dict[str, float]
    urgency: str
    supplier_lead_days: int


def _compute_urgency(stockout_prob: StockoutPrediction, days_to_stockout: float) -> str:
    if stockout_prob.urgency_score >= 0.8 or days_to_stockout < 2:
        return "CRITICAL"
    if stockout_prob.urgency_score >= 0.5 or days_to_stockout < 5:
        return "HIGH"
    if stockout_prob.urgency_score >= 0.2 or days_to_stockout < 10:
        return "MEDIUM"
    return "LOW"


class InventorySupervisor:
    """Coordinates inventory agents and pricing supervisor for joint optimization."""

    def __init__(self, pricing_supervisor: "DynamicPricingSupervisor"):
        self.pricing_supervisor = pricing_supervisor
        self.forecaster = InventoryForecaster()
        self.reorder_optimizer = ReorderOptimizer()
        self.stockout_predictor = StockoutPredictor()

    async def optimize_jointly(
        self,
        sku: str,
        warehouse_id: str,
        current_stock: float,
        supplier_lead_days: int,
        store_id: str = "store_001",
    ) -> Tuple[InventoryRecommendation, "PriceRecommendation"]:
        """Joint inventory + pricing optimization."""
        from app.dynamic_pricing.supervisor import PriceRecommendation

        # 1. Forecast demand + safety stock
        demand_forecast = await self.forecaster.forecast_demand(
            sku, warehouse_id, horizon_days=30
        )
        safety_stock, reorder_point = self.forecaster.compute_safety_stock(
            demand_forecast, service_level=0.95
        )

        # 2. Stockout risk
        stockout_prob = self.stockout_predictor.predict_stockout(
            sku, current_stock, demand_forecast.daily_forecast
        )
        mean_demand = demand_forecast.mean
        days_to_stockout = (
            current_stock / mean_demand if mean_demand > 0 else 999.0
        )

        # 3. Competitor prices for pricing
        competitor_prices = await self.pricing_supervisor.get_competitor_prices(
            sku, store_id
        )

        # 4. EOQ
        annual_demand = mean_demand * 365
        reorder_rec = self.reorder_optimizer.recommend(
            sku, annual_demand, ordering_cost=25.0, holding_cost_pct=0.20
        )

        # 5. Pricing recommendation (inventory-aware)
        pricing_rec = await self.pricing_supervisor.compute_optimal_prices(
            sku=sku,
            store_id=store_id,
            competitor_prices=competitor_prices,
            inventory_level=current_stock,
            inventory_constraint=current_stock,
            inventory_forecast=demand_forecast.daily_forecast,
        )

        urgency = _compute_urgency(stockout_prob, days_to_stockout)
        inventory_rec = InventoryRecommendation(
            sku=sku,
            current_stock=current_stock,
            safety_stock=safety_stock,
            reorder_point=reorder_point,
            optimal_order_qty=reorder_rec.optimal_qty,
            days_to_stockout=days_to_stockout,
            pricing_impact={
                "price_adjustment_pct": (
                    pricing_rec.dynamic_price / pricing_rec.base_price - 1.0
                    if pricing_rec.base_price
                    else 0.0
                ),
                "revenue_impact": pricing_rec.expected_revenue_lift * mean_demand,
            },
            urgency=urgency,
            supplier_lead_days=supplier_lead_days,
        )
        return inventory_rec, pricing_rec
