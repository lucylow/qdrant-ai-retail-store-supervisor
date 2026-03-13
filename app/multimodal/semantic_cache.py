"""
Semantic cache: query vector → cached response bundle (Qdrant collection).

Production pipeline: lookup by textvector; on miss run full search and cache_result.
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any, Dict, List, Optional

from qdrant_client.http import models as qmodels

from app.multimodal.schema import TEXT_DIM, PRODUCTS_MULTIMODAL_COLLECTION

logger = logging.getLogger(__name__)

SEMANTIC_CACHE_COLLECTION = "semantic_cache"
CACHE_SCORE_THRESHOLD = 0.85
CACHE_TTL_S = 3600  # 1 hour default


def ensure_semantic_cache_collection(client: Any) -> None:
    """Create semantic_cache collection (single vector, TEXT_DIM) if missing."""
    try:
        client.get_collection(SEMANTIC_CACHE_COLLECTION)
        logger.debug("Collection %s already exists", SEMANTIC_CACHE_COLLECTION)
    except Exception:
        client.create_collection(
            collection_name=SEMANTIC_CACHE_COLLECTION,
            vectors_config=qmodels.VectorParams(size=TEXT_DIM, distance=qmodels.Distance.COSINE),
        )
        logger.info("Created collection %s", SEMANTIC_CACHE_COLLECTION)


def semantic_cache_lookup(
    client: Any,
    query_vector: List[float],
    *,
    score_threshold: float = CACHE_SCORE_THRESHOLD,
    ttl_s: int = CACHE_TTL_S,
) -> Optional[Dict[str, Any]]:
    """
    Look up cached bundle by query embedding. Returns bundle payload if hit and not expired.
    """
    try:
        ensure_semantic_cache_collection(client)
    except Exception as e:
        logger.debug("Semantic cache collection ensure failed: %s", e)
        return None

    now = time.time()
    try:
        hits = client.search(
            collection_name=SEMANTIC_CACHE_COLLECTION,
            query_vector=query_vector,
            score_threshold=score_threshold,
            limit=1,
            with_payload=True,
        )
    except Exception as e:
        logger.debug("Semantic cache search failed: %s", e)
        return None

    if not hits:
        return None

    hit = hits[0]
    payload = hit.payload or {}
    expires_at = payload.get("ttl") or 0
    if now > expires_at:
        return None

    bundle = payload.get("bundle")
    if bundle is None:
        return None

    # Optional: increment hit_count (async best-effort)
    try:
        client.set_payload(
            collection_name=SEMANTIC_CACHE_COLLECTION,
            payload={"hit_count": (payload.get("hit_count") or 0) + 1},
            points=[hit.id],
        )
    except Exception:
        pass

    return bundle


def semantic_cache_store(
    client: Any,
    query_vector: List[float],
    bundle: Dict[str, Any],
    *,
    ttl_s: int = CACHE_TTL_S,
) -> None:
    """Store a response bundle keyed by query vector for future semantic lookup."""
    try:
        ensure_semantic_cache_collection(client)
    except Exception as e:
        logger.debug("Semantic cache collection ensure failed: %s", e)
        return

    now = time.time()
    point_id = str(uuid.uuid4())
    payload = {
        "bundle": bundle,
        "ttl": now + ttl_s,
        "hit_count": 0,
    }
    try:
        client.upsert(
            collection_name=SEMANTIC_CACHE_COLLECTION,
            points=[
                qmodels.PointStruct(
                    id=point_id,
                    vector=query_vector,
                    payload=payload,
                )
            ],
        )
        logger.debug("Cached bundle for semantic lookup")
    except Exception as e:
        logger.warning("Semantic cache store failed: %s", e)
