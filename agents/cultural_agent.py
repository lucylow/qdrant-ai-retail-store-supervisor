"""
Swiss retail behavior adaptation: bio/Swiss-made for Coop, low-price for Denner.
"""
from __future__ import annotations

from typing import Any, Dict, List

from app.models.swiss_culture import SWISS_RETAILERS
from app.services.swiss_logistics import SwissLogistics


class SwissCulturalAgent:
    """Adapt recommendations to tenant culture and canton."""

    async def adapt_recommendation(
        self,
        products: List[Dict[str, Any]],
        tenant: str,
        canton: str,
    ) -> List[Dict[str, Any]]:
        """Prioritize bio/Swiss-made for Coop, low-price for Denner."""
        culture = SWISS_RETAILERS.get(tenant)
        if not culture:
            culture = SWISS_RETAILERS["coop"]

        scoring = {
            "sustainability": culture.sustainability_focus * 0.3,
            "swiss_made": 0.25 if culture.cooperative_culture else 0.1,
            "price_competitive": 0.4 if culture.price_sensitive else 0.15,
            "alpine_feasibility": 1.0 - SwissLogistics.ALPINE_PENALTIES.get(canton, 0),
        }

        for product in products:
            meta = product.get("cultural_metadata") or {}
            sust = meta.get("sustainability_score", 0) or culture.sustainability_focus
            swiss = 1.0 if meta.get("swiss_made") else 0.0
            price = float(product.get("price") or 1.0)
            price_score = (1.0 / price) * scoring["price_competitive"] if price > 0 else 0
            alpine = scoring["alpine_feasibility"]

            product["cultural_score"] = (
                sust * scoring["sustainability"]
                + swiss * scoring["swiss_made"]
                + price_score
                + alpine
            )

        return sorted(products, key=lambda x: x.get("cultural_score", 0), reverse=True)
