"""Qdrant client for personalization: profiles, recommendation history, journeys."""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

from app.cdp.customer_profile import CustomerProfile, CustomerSegment
from app.qdrant_client import get_qdrant_client
from app.qdrant.personalization.collections import (
    COLL_CUSTOMER_JOURNEYS,
    COLL_CUSTOMER_PROFILES,
    COLL_RECOMMENDATION_HISTORY,
)

logger = logging.getLogger(__name__)

VECTOR_SIZE = 64


def _embed_dummy(size: int = VECTOR_SIZE) -> List[float]:
    """Deterministic placeholder vector for scalar-keyed points."""
    return (np.zeros(size) + 0.1).tolist()


class PersonalizationQdrantClient:
    """Read/write customer profiles, recommendation history, and journey state."""

    def __init__(self, client: Optional[QdrantClient] = None) -> None:
        self._client = client or get_qdrant_client()

    def _point_id(self, prefix: str, *parts: str) -> str:
        s = "_".join(str(p) for p in parts)
        return hashlib.sha256(f"{prefix}_{s}".encode()).hexdigest()[:16]

    async def get_customer_profile(self, customer_id: str) -> Optional[CustomerProfile]:
        """Retrieve cached Customer 360 profile from Qdrant."""
        try:
            res = self._client.scroll(
                collection_name=COLL_CUSTOMER_PROFILES,
                scroll_filter=rest.Filter(
                    must=[rest.FieldCondition(key="customer_id", match=rest.MatchValue(value=customer_id))]
                ),
                limit=1,
            )
            points, _ = res
            if not points or not points[0].payload:
                return None
            p = points[0].payload
            seg = CustomerSegment(
                loyalty_tier=p.get("loyalty_tier", "BRONZE"),
                rf_score=float(p.get("rf_score", 0)),
                price_sensitivity=float(p.get("price_sensitivity", 0.5)),
                category_affinity=p.get("category_affinity") or {},
            )
            last = p.get("last_updated")
            if isinstance(last, str):
                last_updated = datetime.fromisoformat(last.replace("Z", "+00:00"))
            else:
                last_updated = datetime.utcnow()
            return CustomerProfile(
                customer_id=customer_id,
                demographics=p.get("demographics") or {},
                rf_score=float(p.get("rf_score", 0)),
                segments=seg,
                price_sensitivity=float(p.get("price_sensitivity", 0.5)),
                last_updated=last_updated,
                confidence=float(p.get("confidence", 0.8)),
            )
        except Exception as e:  # noqa: BLE001
            logger.debug("get_customer_profile: %s", e)
            return None

    async def upsert_profile(self, customer_id: str, profile: CustomerProfile) -> None:
        """Upsert Customer 360 profile to Qdrant."""
        try:
            payload = profile.to_payload()
            payload["demographics"] = profile.demographics
            payload["category_affinity"] = profile.segments.category_affinity
            payload["last_updated"] = profile.last_updated.isoformat()
            pid = self._point_id("profile", customer_id)
            self._client.upsert(
                collection_name=COLL_CUSTOMER_PROFILES,
                points=[
                    rest.PointStruct(
                        id=pid,
                        vector=_embed_dummy(),
                        payload=payload,
                    )
                ],
            )
        except Exception as e:  # noqa: BLE001
            logger.debug("upsert_profile: %s", e)

    async def store_interaction(
        self,
        customer_id: str,
        context: Dict[str, Any],
        recommendations: List[Dict[str, Any]],
        offers: List[Dict[str, Any]],
        confidence: float,
    ) -> None:
        """Store interaction for learning (recommendation_history)."""
        try:
            points = []
            for rec in recommendations[:20]:
                pid = self._point_id("rec", customer_id, rec.get("product_id", ""), str(datetime.utcnow().timestamp()))
                points.append(
                    rest.PointStruct(
                        id=pid,
                        vector=_embed_dummy(),
                        payload={
                            "customer_id": customer_id,
                            "product_id": rec.get("product_id", ""),
                            "click_probability": rec.get("scores", {}).get("relevance", 0),
                            "purchase_probability": rec.get("scores", {}).get("relevance", 0) * 0.6,
                            "ab_variant": context.get("ab_variant", "control"),
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                    )
                )
            if points:
                self._client.upsert(collection_name=COLL_RECOMMENDATION_HISTORY, points=points)
        except Exception as e:  # noqa: BLE001
            logger.debug("store_interaction: %s", e)
