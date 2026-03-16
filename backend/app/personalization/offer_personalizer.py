"""OfferPersonalizerAgent: dynamic pricing and loyalty-tier optimization."""

from __future__ import annotations

from typing import Any, Dict, List

from app.cdp.customer_profile import CustomerProfile


class OfferPersonalizerAgent:
    """Personalize offers and discounts by loyalty tier and price sensitivity."""

    async def personalize(
        self,
        recommendations: List[Dict[str, Any]],
        profile: CustomerProfile,
    ) -> List[Dict[str, Any]]:
        """
        Attach personalized offers (discount, free shipping, etc.) to recommendations
        based on loyalty tier and price sensitivity.
        """
        offers = []
        for rec in recommendations[:12]:
            product_id = rec.get("product_id", "")
            discount = self._discount_for_tier(profile.segments.loyalty_tier)
            if profile.price_sensitivity > 0.6:
                discount = min(1.0, discount + 0.05)
            offers.append({
                "product_id": product_id,
                "discount_pct": discount,
                "free_shipping": profile.segments.loyalty_tier in ("GOLD", "PLATINUM"),
                "message": f"{discount:.0%} off for {profile.segments.loyalty_tier} members",
            })
        return offers

    def _discount_for_tier(self, tier: str) -> float:
        """Base discount by loyalty tier."""
        return {"BRONZE": 0.0, "SILVER": 0.05, "GOLD": 0.10, "PLATINUM": 0.15}.get(
            tier, 0.0
        )
