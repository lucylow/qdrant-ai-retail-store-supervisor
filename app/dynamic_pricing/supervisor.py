"""MARL pricing orchestration: full dynamic pricing pipeline."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import List, Optional

import pandas as pd

from app.dynamic_pricing.demand_elasticity import DemandElasticityModel
from app.dynamic_pricing.margin_optimizer import MarginOptimizer
from app.rl.marl_pricing import MARLAction, PricingMARLSupervisor
from app.rag.pricing.pricing_context import retrieve_pricing_context

logger = logging.getLogger(__name__)


@dataclass
class PriceRecommendation:
    """Single SKU price recommendation from the pipeline."""
    sku: str
    base_price: float
    dynamic_price: float
    confidence: float
    elasticity: float
    competitor_prices: List[float]
    recommended_action: str  # "RAISE", "LOWER", "HOLD"
    expected_revenue_lift: float


class DynamicPricingSupervisor:
    """Full MARL-powered dynamic pricing pipeline with RAG context."""

    def __init__(self):
        self.marl_supervisor = PricingMARLSupervisor()
        self.demand_model = DemandElasticityModel()
        self.margin_optimizer = MarginOptimizer()

    async def _retrieve_pricing_context(self, sku: str, store_id: str) -> dict:
        """Retrieve competitor context via Qdrant RAG."""
        return await retrieve_pricing_context(sku=sku, store_id=store_id, limit=5)

    async def get_competitor_prices(self, sku: str, store_id: str = "store_001") -> List[float]:
        """Return competitor prices for joint inventory-pricing (RAG)."""
        ctx = await self._retrieve_pricing_context(sku, store_id)
        return ctx.get("competitor_prices") or [35.0]

    def _build_marl_state(
        self,
        sku: str,
        competitor_prices: List[float],
        elasticity: float,
    ) -> dict:
        return {
            "sku": sku,
            "competitor_prices": competitor_prices,
            "elasticity": elasticity,
        }

    def _get_action_direction(self, marl_action: MARLAction) -> str:
        if marl_action.price_multiplier > 0.02:
            return "RAISE"
        if marl_action.price_multiplier < -0.02:
            return "LOWER"
        return "HOLD"

    async def compute_optimal_prices(
        self,
        sku: str,
        store_id: str,
        competitor_prices: Optional[List[float]] = None,
        inventory_level: Optional[float] = None,
        demand_forecast: Optional[pd.Series] = None,
        inventory_constraint: Optional[float] = None,
        inventory_forecast: Optional[pd.Series] = None,
    ) -> PriceRecommendation:
        """Full MARL-powered dynamic pricing pipeline."""
        inv_level = inventory_level if inventory_level is not None else inventory_constraint
        if inv_level is None:
            inv_level = 150.0
        # 1. Retrieve competitor context via Qdrant RAG (optionally override with fresh data)
        market_context = await self._retrieve_pricing_context(sku, store_id)
        comp_prices = (
            market_context.get("competitor_prices")
            if competitor_prices is None or len(competitor_prices) == 0
            else competitor_prices
        )
        if not comp_prices:
            comp_prices = [35.0]

        # 2. Real-time elasticity
        elasticity = self.demand_model.compute_elasticity(
            sku, comp_prices, inv_level
        )

        # 3. MARL agents collaborate
        state = self._build_marl_state(sku, comp_prices, elasticity)
        marl_action = await self.marl_supervisor.act(
            state=state, sku=sku, competitor_prices=comp_prices, elasticity=elasticity
        )

        # 4. Margin optimization with business constraints
        optimal_price = self.margin_optimizer.optimize(
            base_price=marl_action.base_price,
            elasticity=elasticity,
            inventory=inv_level,
            competitor_prices=comp_prices,
        )

        return PriceRecommendation(
            sku=sku,
            base_price=marl_action.base_price,
            dynamic_price=optimal_price,
            confidence=marl_action.confidence,
            elasticity=elasticity,
            competitor_prices=comp_prices,
            recommended_action=self._get_action_direction(marl_action),
            expected_revenue_lift=marl_action.revenue_lift_pct,
        )
