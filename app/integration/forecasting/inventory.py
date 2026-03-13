"""Price forecast → reorder optimization: expected price path informs EOQ and timing."""

from __future__ import annotations

import logging
from typing import Optional

from app.forecasting.price.supervisor import PriceForecast
from app.inventory.reorder_optimizer import ReorderOptimizer, ReorderRecommendation

logger = logging.getLogger(__name__)


def apply_forecast_to_inventory(
    forecast: PriceForecast,
    sku: str,
    current_stock: float = 100.0,
    annual_demand_scale: float = 365.0,
) -> ReorderRecommendation:
    """Use price forecast to adjust reorder (e.g. higher expected price → earlier reorder)."""
    optimizer = ReorderOptimizer()
    expected_price = float(forecast.point_forecast.mean())
    # Scale demand by forecast trend (simplified)
    demand = current_stock * 12 * (expected_price / 35.0) if expected_price else current_stock * 12
    eoq = optimizer.compute_eoq(
        annual_demand=demand,
        avg_unit_cost=expected_price * 0.85,
    )
    supplier = optimizer.select_supplier(sku, eoq)
    from datetime import datetime, timedelta
    lead = supplier.get("lead_time_days", 7)
    return ReorderRecommendation(
        optimal_qty=eoq,
        supplier=supplier.get("id", "sup_a"),
        lead_time_days=lead,
        total_cost=eoq * supplier.get("unit_price", expected_price * 0.9),
        arrival_date=datetime.utcnow() + timedelta(days=lead),
    )
