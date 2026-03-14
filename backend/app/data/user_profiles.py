"""
Long-term user profile memory: user_profiles collection in Qdrant.

Stores stable preferences & lifetime stats; embedded summary for similar-user retrieval.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

from app.data.memory_collections import COLL_USER_PROFILES
from app.embeddings import embed_single
from app.qdrant_client import get_qdrant_client

logger = logging.getLogger(__name__)


def get_by_user_id(user_id: str) -> dict[str, Any] | None:
    """Fetch user profile by userId (exact match). Returns payload or None."""
    client = get_qdrant_client()
    from qdrant_client.http import models as rest
    from qdrant_client.models import Filter, FieldCondition, MatchValue
    flt = Filter(must=[FieldCondition(key="userId", match=MatchValue(value=user_id))])
    points, _ = client.scroll(
        collection_name=COLL_USER_PROFILES,
        scroll_filter=flt,
        limit=1,
        with_payload=True,
        with_vectors=False,
    )
    if not points:
        return None
    return points[0].payload or None


def search_similar(vector: list[float], limit: int = 5) -> list[dict]:
    """Search by embedding (e.g. for similar users). Returns list of {payload, score}."""
    client = get_qdrant_client()
    hits = client.search(
        collection_name=COLL_USER_PROFILES,
        query_vector=vector,
        limit=limit,
        with_payload=True,
    )
    return [{"payload": h.payload or {}, "score": h.score} for h in hits]


def upsert(
    user_id: str,
    preferences: Mapping[str, Any] | None = None,
    lifetime_value: float | None = None,
    summary: str | None = None,
) -> None:
    """
    Upsert a user profile. Embeds summary (or builds one from preferences) for vector search.
    Payload shape: userId, preferences, lifetimeValue, last_updated, summary.
    """
    client = get_qdrant_client()
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    prefs = dict(preferences or {})
    if summary is None:
        parts = [f"preferences: {prefs}"]
        if lifetime_value is not None:
            parts.append(f"lifetime_value: {lifetime_value}")
        summary = " | ".join(parts)[:500]
    vec = embed_single(summary).vectors[0].tolist()
    payload = {
        "userId": user_id,
        "preferences": prefs,
        "lifetimeValue": lifetime_value,
        "last_updated": now,
        "summary": summary,
    }
    # Use userId as point id for idempotent upsert
    point_id = hash(user_id) % (2**63)
    from qdrant_client.http import models as rest
    client.upsert(
        collection_name=COLL_USER_PROFILES,
        points=[rest.PointStruct(id=point_id, vector=vec, payload=payload)],
    )
    logger.debug("Upserted user profile for %s", user_id)


__all__: Sequence[str] = ["get_by_user_id", "search_similar", "upsert"]
