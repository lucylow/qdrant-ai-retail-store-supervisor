"""Payload indexes for forecasting collections (sku, date, confidence, agent)."""

from __future__ import annotations

import logging
from typing import List, Tuple

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

from app.qdrant.forecasting.collections import (
    COLL_PRICE_HISTORY,
    COLL_FORECAST_ACCURACY,
    COLL_COMPETITOR_STRATEGIES,
)

logger = logging.getLogger(__name__)

# (collection, field, schema)
FORECASTING_INDEXES: List[Tuple[str, str, rest.PayloadSchemaType]] = [
    (COLL_PRICE_HISTORY, "sku", rest.PayloadSchemaType.KEYWORD),
    (COLL_PRICE_HISTORY, "store_id", rest.PayloadSchemaType.KEYWORD),
    (COLL_PRICE_HISTORY, "date", rest.PayloadSchemaType.KEYWORD),
    (COLL_PRICE_HISTORY, "price", rest.PayloadSchemaType.FLOAT),
    (COLL_PRICE_HISTORY, "volume", rest.PayloadSchemaType.FLOAT),
    (COLL_FORECAST_ACCURACY, "sku", rest.PayloadSchemaType.KEYWORD),
    (COLL_FORECAST_ACCURACY, "agent", rest.PayloadSchemaType.KEYWORD),
    (COLL_FORECAST_ACCURACY, "mape", rest.PayloadSchemaType.FLOAT),
    (COLL_FORECAST_ACCURACY, "timestamp", rest.PayloadSchemaType.FLOAT),
    (COLL_COMPETITOR_STRATEGIES, "sku", rest.PayloadSchemaType.KEYWORD),
    (COLL_COMPETITOR_STRATEGIES, "competitor", rest.PayloadSchemaType.KEYWORD),
    (COLL_COMPETITOR_STRATEGIES, "strategy", rest.PayloadSchemaType.KEYWORD),
    (COLL_COMPETITOR_STRATEGIES, "response_time", rest.PayloadSchemaType.FLOAT),
]


def ensure_forecasting_payload_indexes(client: QdrantClient) -> None:
    """Create payload indexes for forecasting collections (best-effort)."""

    def _safe_index(coll: str, field: str, schema: rest.PayloadSchemaType) -> None:
        try:
            client.create_payload_index(
                collection_name=coll,
                field_name=field,
                field_schema=schema,
            )
        except Exception:  # noqa: BLE001
            logger.debug("Payload index %s.%s already exists or unsupported", coll, field)

    for coll, field, schema in FORECASTING_INDEXES:
        _safe_index(coll, field, schema)
