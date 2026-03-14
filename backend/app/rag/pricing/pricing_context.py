"""Competitor and elasticity context retrieval from Qdrant for pricing RAG."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np

from app.data.collections import COLL_COMPETITOR_PRICES
from app.qdrant_client import get_qdrant_client

logger = logging.getLogger(__name__)

VECTOR_SIZE = 32


def _embed_price_context(sku: str, platform: str, price: float) -> List[float]:
    """Simple deterministic embedding for price context (no model dependency)."""
    vec = np.zeros(VECTOR_SIZE)
    vec[0] = price / 100.0
    vec[1] = hash(sku) % 1000 / 1000.0
    vec[2] = hash(platform) % 1000 / 1000.0
    for i in range(3, min(10, VECTOR_SIZE)):
        vec[i] = (price + i * 1.1) / 80.0
    return vec.tolist()


async def retrieve_pricing_context(
    sku: str,
    store_id: str,
    limit: int = 5,
) -> Dict[str, Any]:
    """Retrieve competitor pricing context from Qdrant for RAG."""
    try:
        client = get_qdrant_client()
        query_vector = _embed_price_context(sku, "query", 35.0)

        results = client.search(
            collection_name=COLL_COMPETITOR_PRICES,
            query_vector=query_vector,
            limit=limit,
            query_filter=None,
        )

        competitor_prices: List[float] = []
        for r in results:
            payload = r.payload or {}
            if "price" in payload:
                competitor_prices.append(float(payload["price"]))

        return {
            "sku": sku,
            "store_id": store_id,
            "competitor_prices": competitor_prices if competitor_prices else [35.0],
            "retrieved_at": datetime.utcnow().isoformat(),
            "sources": len(results),
        }
    except Exception as e:
        logger.warning("RAG pricing context retrieval failed: %s", e)
        return {
            "sku": sku,
            "store_id": store_id,
            "competitor_prices": [35.0],
            "retrieved_at": datetime.utcnow().isoformat(),
            "sources": 0,
            "error": str(e),
        }
