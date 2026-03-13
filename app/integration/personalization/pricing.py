"""Personalized dynamic pricing: integrate with dynamic_pricing + customer profile."""

from __future__ import annotations

from typing import Any, Dict, Optional

from app.cdp.customer_profile import CustomerProfile


async def personalized_dynamic_price(
    customer_id: str,
    product_id: str,
    base_price: float,
    profile: Optional[CustomerProfile] = None,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Return personalized price (and discount) using profile's price_sensitivity
    and loyalty tier; integrates with existing dynamic pricing where available.
    """
    if profile is None:
        sensitivity = 0.5
        tier = "BRONZE"
    else:
        sensitivity = profile.price_sensitivity
        tier = profile.segments.loyalty_tier
    tier_discount = {"BRONZE": 0, "SILVER": 0.02, "GOLD": 0.05, "PLATINUM": 0.08}.get(
        tier, 0
    )
    if sensitivity > 0.6:
        tier_discount = min(0.15, tier_discount + 0.03)
    final_price = base_price * (1 - tier_discount)
    return {
        "customer_id": customer_id,
        "product_id": product_id,
        "base_price": base_price,
        "personalized_price": round(final_price, 2),
        "discount_pct": tier_discount,
        "loyalty_tier": tier,
    }
