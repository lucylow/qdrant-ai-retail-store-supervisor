from __future__ import annotations

import logging

from qdrant_client.http import models as rest

from app.data.collections import (
    COLL_PRODUCTS,
    ensure_all_collections,
)
from app.qdrant_client import get_qdrant_client


logger = logging.getLogger(__name__)


def main() -> None:
    # AUTONOMOUS-AGENT-HACKATHON: demo product ingestion script.
    ensure_all_collections()
    client = get_qdrant_client()
    points = [
        rest.PointStruct(
            id="SKU-BASE",
            vector=[0.1, 0.2, 0.3],
            payload={
                "sku": "SKU-BASE",
                "name": "Blue dress",
                "price_eur": 79.0,
                "category": "dress",
                "color": "blue",
            },
        )
    ]
    client.upsert(COLL_PRODUCTS, points)
    logger.info("Ingested demo retail products")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

