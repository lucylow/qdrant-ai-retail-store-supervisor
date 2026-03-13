"""Production price forecasting collections: price_history, forecast_accuracy, competitor_strategies."""

from __future__ import annotations

import logging
from typing import Any, Dict, Final, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

from app.qdrant_client import ensure_collection, get_qdrant_client
from app.qdrant.forecasting.indexes import ensure_forecasting_payload_indexes

logger = logging.getLogger(__name__)

COLL_PRICE_HISTORY: Final[str] = "price_history"
COLL_FORECAST_ACCURACY: Final[str] = "forecast_accuracy"
COLL_COMPETITOR_STRATEGIES: Final[str] = "competitor_strategies"

FORECASTING_COLLECTIONS: Dict[str, Dict[str, Any]] = {
    COLL_PRICE_HISTORY: {
        "vector_size": 768,
        "payload_indexes": ["sku", "store_id", "date", "price", "volume"],
    },
    COLL_FORECAST_ACCURACY: {
        "vector_size": 768,
        "payload_indexes": ["sku", "agent", "mape", "timestamp"],
    },
    COLL_COMPETITOR_STRATEGIES: {
        "vector_size": 768,
        "payload_indexes": ["sku", "competitor", "strategy", "response_time"],
    },
}


async def setup_price_forecast_collections(client: Optional[QdrantClient] = None) -> None:
    """Create price forecasting collections and payload indexes (sync wrapper)."""
    c = client or get_qdrant_client()
    for name, config in FORECASTING_COLLECTIONS.items():
        ensure_collection(
            c,
            name,
            vector_size=config["vector_size"],
            distance=rest.Distance.COSINE,
        )
    ensure_forecasting_payload_indexes(c)


def setup_price_forecast_collections_sync(client: Optional[QdrantClient] = None) -> None:
    """Synchronous entrypoint for scripts."""
    import asyncio
    asyncio.run(setup_price_forecast_collections(client))
