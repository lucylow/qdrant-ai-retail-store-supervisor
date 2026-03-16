# app/geospatial/qdrant_stores.py
"""
Qdrant integration for semantic store search (e.g. "organic milk open now").
Use multilingual embeddings and provider_vectors collection; filter by tenant in payload.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_STORES = "provider_vectors"


def _get_client():  # lazy to avoid import at module load if qdrant not used
    from qdrant_client import QdrantClient
    return QdrantClient(url=QDRANT_URL)


def store_provider_vector(
    provider_id: str, vector: List[float], payload: Dict[str, Any]
) -> None:
    client = _get_client()
    client.upsert(
        collection_name=COLLECTION_STORES,
        points=[{"id": provider_id, "vector": vector, "payload": payload}],
    )


def semantic_search_stores(
    query_vector: List[float],
    top: int = 10,
    filter_payload: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    client = _get_client()
    res = client.search(
        collection_name=COLLECTION_STORES,
        query_vector=query_vector,
        limit=top,
        with_payload=True,
        query_filter=filter_payload,
    )
    return [{"id": r.id, "score": r.score, "payload": r.payload or {}} for r in res]
