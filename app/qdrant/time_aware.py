"""
Qdrant collections for Swiss pickup windows and punctuality-aware episodes.
"""
from __future__ import annotations

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

from app.qdrant_client import get_qdrant_client

COLLECTION_SWISS_PICKUP = "swiss_pickup_episodes"


def create_time_aware_collection(client: QdrantClient | None = None) -> None:
    """Index 'morgen 10h' queries with pickup availability metadata."""
    q = client or get_qdrant_client()
    existing = [c.name for c in q.get_collections().collections or []]
    if COLLECTION_SWISS_PICKUP in existing:
        return
    q.create_collection(
        collection_name=COLLECTION_SWISS_PICKUP,
        vectors_config=rest.VectorParams(size=1024, distance=rest.Distance.COSINE),
    )
    try:
        q.create_payload_index(
            COLLECTION_SWISS_PICKUP,
            "pickup_window_start",
            rest.PayloadSchemaType.DATETIME,
        )
        q.create_payload_index(
            COLLECTION_SWISS_PICKUP,
            "pickup_window_end",
            rest.PayloadSchemaType.DATETIME,
        )
    except Exception:  # noqa: BLE001
        pass
