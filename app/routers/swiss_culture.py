"""
Swiss cultural intelligence API: profiles, seasonal boosts, culturally adapted bundles.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Request

from app.models.swiss_culture import SWISS_RETAILERS
from app.services.swiss_calendar import SwissCulturalCalendar
from agents.cultural_agent import SwissCulturalAgent

router = APIRouter(prefix="/culture", tags=["swiss-culture"])


@router.get("/{tenant}")
async def get_cultural_profile(tenant: str) -> Dict[str, Any]:
    """Swiss retailer cultural profile + seasonal boosts."""
    culture = SWISS_RETAILERS.get(tenant)
    if not culture:
        return {"error": "unknown_tenant", "tenant": tenant}

    today = datetime.now().date()
    seasonal_boost = SwissCulturalCalendar.get_seasonal_boost(today, tenant)
    pickup_prefs = culture.pickup_preferences or {}
    preferred_pickup = (
        max(pickup_prefs.items(), key=lambda x: x[1])
        if pickup_prefs
        else ("ZH", 0.0)
    )

    return {
        "retailer": culture.name,
        "languages": [l.value for l in culture.primary_languages],
        "seasonal_boost": seasonal_boost,
        "preferred_pickup": {"canton": preferred_pickup[0], "weight": preferred_pickup[1]},
        "cooperative_culture": culture.cooperative_culture,
        "sustainability_focus": culture.sustainability_focus,
    }


@router.post("/adapt")
async def culturally_adapt_bundle(request: Request, bundle: Dict[str, Any]) -> Dict[str, Any]:
    """Adapt product bundle to Swiss cultural preferences."""
    tenant = request.headers.get("X-Tenant", "coop")
    canton = bundle.get("pickup_canton", "ZH")
    products = bundle.get("products", [])

    agent = SwissCulturalAgent()
    adapted = await agent.adapt_recommendation(products, tenant, canton)
    return {"culturally_optimized": adapted[:3]}
