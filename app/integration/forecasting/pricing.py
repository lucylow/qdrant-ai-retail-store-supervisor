"""Price forecast → dynamic pricing: feed forecast into MARL and margin optimizer."""

from __future__ import annotations

import logging
from typing import Optional

from app.forecasting.price.supervisor import PriceForecast
from app.dynamic_pricing.supervisor import DynamicPricingSupervisor, PriceRecommendation

logger = logging.getLogger(__name__)


async def apply_forecast_to_pricing(
    forecast: PriceForecast,
    store_id: str = "store_001",
    inventory_level: Optional[float] = None,
) -> PriceRecommendation:
    """Use price forecast to inform dynamic pricing (e.g. expected path as prior)."""
    pricing = DynamicPricingSupervisor()
    # Use forecast horizon mean as demand/price context for MARL
    expected_price = float(forecast.point_forecast.mean())
    comp_prices = [expected_price * 0.98, expected_price * 1.02, expected_price]
    rec = await pricing.compute_optimal_prices(
        sku=forecast.sku,
        store_id=store_id,
        competitor_prices=comp_prices,
        inventory_level=inventory_level,
    )
    return rec
