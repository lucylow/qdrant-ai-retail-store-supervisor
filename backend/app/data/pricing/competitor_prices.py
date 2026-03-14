"""Qdrant competitor price indexing for RAG retrieval."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import List

import numpy as np
from qdrant_client.http import models as rest

from app.data.collections import COLL_COMPETITOR_PRICES
from app.qdrant_client import ensure_collection, get_qdrant_client

logger = logging.getLogger(__name__)

VECTOR_SIZE = 32


def _embed_price_context(sku: str, platform: str, price: float) -> List[float]:
    """Deterministic embedding for price context."""
    vec = np.zeros(VECTOR_SIZE)
    vec[0] = price / 100.0
    vec[1] = hash(sku) % 1000 / 1000.0
    vec[2] = hash(platform) % 1000 / 1000.0
    for i in range(3, min(10, VECTOR_SIZE)):
        vec[i] = (price + i * 1.1) / 80.0
    return vec.tolist()


def ensure_competitor_prices_collection() -> None:
    """Create competitor_prices collection if missing."""
    client = get_qdrant_client()
    ensure_collection(
        client, COLL_COMPETITOR_PRICES, vector_size=VECTOR_SIZE, distance=rest.Distance.COSINE
    )


def upsert_competitor_price(
    sku: str,
    platform: str,
    price: float,
    store_id: str = "global",
) -> None:
    """Index a single competitor price in Qdrant."""
    try:
        client = get_qdrant_client()
        point_id = f"{sku}_{platform}_{datetime.utcnow().isoformat()}".replace(" ", "_")
        vector = _embed_price_context(sku, platform, price)
        client.upsert(
            collection_name=COLL_COMPETITOR_PRICES,
            points=[
                rest.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "sku": sku,
                        "platform": platform,
                        "price": price,
                        "timestamp": datetime.utcnow().timestamp(),
                        "store_id": store_id,
                    },
                )
            ],
        )
    except Exception as e:
        logger.warning("Failed to upsert competitor price: %s", e)
