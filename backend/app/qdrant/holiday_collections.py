"""
Holiday-aware Qdrant collections for demand forecast indexing.
"""
from __future__ import annotations

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

from app.qdrant_client import get_qdrant_client

COLLECTION_HOLIDAY_DEMAND = "holiday_demand_forecast"


def create_holiday_aware_collection(client: QdrantClient | None = None) -> None:
    """Create collection for holiday multipliers and fast filtering."""
    q = client or get_qdrant_client()
    existing = [c.name for c in q.get_collections().collections or []]
    if COLLECTION_HOLIDAY_DEMAND in existing:
        return
    q.create_collection(
        collection_name=COLLECTION_HOLIDAY_DEMAND,
        vectors_config=rest.VectorParams(size=384, distance=rest.Distance.COSINE),
        optimizers_config=rest.OptimizersConfigDiff(
            memmap_threshold=0,
            indexing_threshold=0.5,
        ),
    )
    try:
        q.create_payload_index(
            COLLECTION_HOLIDAY_DEMAND,
            "demand_multiplier",
            rest.PayloadSchemaType.FLOAT,
        )
        q.create_payload_index(
            COLLECTION_HOLIDAY_DEMAND,
            "active_periods",
            rest.PayloadSchemaType.KEYWORD,
        )
    except Exception:  # noqa: BLE001
        pass
