"""
Inject Swiss cultural context into request state (tenant, languages, seasonal boost).
"""
from __future__ import annotations

from datetime import datetime
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.models.swiss_culture import SWISS_RETAILERS
from app.services.swiss_calendar import SwissCulturalCalendar
from app.services.swiss_logistics import SwissLogistics


class SwissCultureMiddleware(BaseHTTPMiddleware):
    """Adds request.state.swiss_culture for downstream handlers."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Response]
    ) -> Response:
        tenant = request.headers.get("X-Tenant", "coop")
        culture = SWISS_RETAILERS.get(tenant, SWISS_RETAILERS["coop"])

        today = datetime.now().date()
        seasonal_boost = SwissCulturalCalendar.get_seasonal_boost(today, tenant)
        delivery_penalty = SwissLogistics.delivery_penalty_for_tenant(
            tenant, canton="ZH", category="general"
        )

        request.state.swiss_culture = {
            "retailer": culture,
            "preferred_languages": [l.value for l in culture.primary_languages],
            "seasonal_boost": seasonal_boost,
            "delivery_penalty": delivery_penalty,
        }

        return await call_next(request)
