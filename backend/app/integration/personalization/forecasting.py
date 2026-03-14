"""Customer-specific demand forecasting for personalization."""

from __future__ import annotations

from typing import Any, Dict, List

from app.cdp.customer_profile import CustomerProfile


async def personalization_forecast_demand(
    profile: CustomerProfile,
    product_ids: List[str],
    horizon_days: int = 7,
) -> Dict[str, Any]:
    """
    Customer-specific demand forecast (e.g. for recommended products);
    integrates with existing forecasting where available.
    """
    aff = profile.segments.category_affinity or {}
    rf = profile.rf_score
    forecasts = {}
    for pid in product_ids:
        a = aff.get(pid, 0.1) + aff.get(f"product_{pid}", 0.05)
        base = 10.0 * (1 + rf / 5.0)
        forecasts[pid] = max(0.1, base * (0.5 + a))
    return {
        "customer_id": profile.customer_id,
        "horizon_days": horizon_days,
        "demand_forecast": forecasts,
    }
