"""
Swiss cultural metadata in Qdrant product payloads.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from app.models.swiss_culture import SWISS_RETAILERS
from app.services.swiss_calendar import SwissCulturalCalendar
from app.services.swiss_pricing import SwissPricingCulture


def create_swiss_product_payload(product: Dict[str, Any], tenant: str) -> Dict[str, Any]:
    """Enhanced payloads with Swiss cultural data for vector search."""
    culture = SWISS_RETAILERS.get(tenant)
    if not culture:
        culture = SWISS_RETAILERS["coop"]

    name = (product.get("name") or product.get("title") or "").lower()
    price = product.get("price", 0.0)
    pickup_zones = product.get("pickup_zones", [])

    return {
        **product,
        "cultural_metadata": {
            "retailer_cooperative": culture.cooperative_culture,
            "sustainability_score": culture.sustainability_focus,
            "swiss_made": product.get("origin") == "CH",
            "bio_organic": "bio" in name,
            "cantons_available": pickup_zones,
            "seasonal_priority": SwissCulturalCalendar.is_fondue_season(
                datetime.now().date()
            ),
        },
        "pricing_culture": {
            "swiss_rounded": SwissPricingCulture.round_to_swiss_price(
                float(price), tenant
            ),
            "price_sensitive": culture.price_sensitive,
        },
    }
