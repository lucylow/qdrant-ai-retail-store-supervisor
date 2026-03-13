"""ProfileBuilderAgent: real-time Customer 360 unification."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict

from app.cdp.customer_profile import CustomerProfile, CustomerSegment
from app.qdrant.personalization.client import PersonalizationQdrantClient


class ProfileBuilderAgent:
    """Build and refresh unified Customer 360 profiles from multiple sources."""

    def __init__(self) -> None:
        self.qdrant = PersonalizationQdrantClient()

    async def build_profile(
        self,
        customer_id: str,
        context: Dict[str, Any],
    ) -> CustomerProfile:
        """Real-time customer 360 unification: cache or build fresh, then update context."""
        cached_profile = await self.qdrant.get_customer_profile(customer_id)
        if (
            cached_profile
            and cached_profile.last_updated > datetime.utcnow() - timedelta(hours=1)
        ):
            profile = cached_profile
        else:
            profile = await self._build_fresh_profile(customer_id, context)
            await self.qdrant.upsert_profile(customer_id, profile)
        profile.update_context(context)
        return profile

    async def _build_fresh_profile(
        self, customer_id: str, context: Dict[str, Any]
    ) -> CustomerProfile:
        """Unify demographics + behavior + preferences from multiple sources."""
        demographic_task = self._get_demographics(customer_id)
        purchase_task = self._get_purchase_history(customer_id)
        browsing_task = self._get_browsing_history(customer_id)
        loyalty_task = self._get_loyalty_data(customer_id)
        demographics, purchases, browsing, loyalty = await asyncio.gather(
            demographic_task, purchase_task, browsing_task, loyalty_task
        )
        rf_score = self._compute_rfm(purchases)
        segments = self._compute_segments(browsing, purchases, loyalty)
        price_sensitivity = self._compute_price_sensitivity(purchases)
        return CustomerProfile(
            customer_id=customer_id,
            demographics=demographics,
            rf_score=rf_score,
            segments=segments,
            price_sensitivity=price_sensitivity,
            last_updated=datetime.utcnow(),
            confidence=0.92,
        )

    async def _get_demographics(self, customer_id: str) -> Dict[str, Any]:
        """Fetch demographics (stub: production → CDP/CRM)."""
        await asyncio.sleep(0)
        return {"region": "US", "signup_date": datetime.utcnow()}

    async def _get_purchase_history(self, customer_id: str) -> list:
        """Fetch purchase history (stub)."""
        await asyncio.sleep(0)
        return []

    async def _get_browsing_history(self, customer_id: str) -> list:
        """Fetch browsing history (stub)."""
        await asyncio.sleep(0)
        return []

    async def _get_loyalty_data(self, customer_id: str) -> Dict[str, Any]:
        """Fetch loyalty tier/points (stub)."""
        await asyncio.sleep(0)
        h = hash(customer_id) % 4
        tiers = ["BRONZE", "SILVER", "GOLD", "PLATINUM"]
        return {"tier": tiers[h], "points": (h + 1) * 500}

    def _compute_rfm(self, purchases: list) -> float:
        """RFM score 0–5 (stub)."""
        if not purchases:
            return 2.0
        return min(5.0, 2.0 + len(purchases) * 0.2)

    def _compute_segments(
        self,
        browsing: list,
        purchases: list,
        loyalty: Dict[str, Any],
    ) -> CustomerSegment:
        """Behavioral segments from browsing, purchases, loyalty."""
        tier = loyalty.get("tier", "BRONZE")
        rfm = self._compute_rfm(purchases)
        sensitivity = self._compute_price_sensitivity(purchases)
        return CustomerSegment(
            loyalty_tier=tier,
            rf_score=rfm,
            price_sensitivity=sensitivity,
            category_affinity={},
        )

    def _compute_price_sensitivity(self, purchases: list) -> float:
        """Price sensitivity 0–1 (stub)."""
        return 0.3 if len(purchases) > 5 else 0.5
