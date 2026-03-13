"""Payload indexes for inventory collections (warehouse, supplier, etc.)."""

from __future__ import annotations

import logging
from typing import List, Tuple

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

from app.qdrant.inventory.collections import (
    COLL_INVENTORY_LEVELS,
    COLL_REORDER_HISTORY,
    COLL_STOCKOUT_EVENTS,
)

logger = logging.getLogger(__name__)

# (collection, field, schema)
INVENTORY_INDEXES: List[Tuple[str, str, rest.PayloadSchemaType]] = [
    (COLL_INVENTORY_LEVELS, "warehouse_id", rest.PayloadSchemaType.KEYWORD),
    (COLL_INVENTORY_LEVELS, "sku", rest.PayloadSchemaType.KEYWORD),
    (COLL_INVENTORY_LEVELS, "stock_level", rest.PayloadSchemaType.FLOAT),
    (COLL_INVENTORY_LEVELS, "last_updated", rest.PayloadSchemaType.FLOAT),
    (COLL_REORDER_HISTORY, "sku", rest.PayloadSchemaType.KEYWORD),
    (COLL_REORDER_HISTORY, "supplier", rest.PayloadSchemaType.KEYWORD),
    (COLL_REORDER_HISTORY, "order_qty", rest.PayloadSchemaType.FLOAT),
    (COLL_REORDER_HISTORY, "arrival_date", rest.PayloadSchemaType.KEYWORD),
    (COLL_STOCKOUT_EVENTS, "sku", rest.PayloadSchemaType.KEYWORD),
    (COLL_STOCKOUT_EVENTS, "stockout_date", rest.PayloadSchemaType.KEYWORD),
    (COLL_STOCKOUT_EVENTS, "lost_sales", rest.PayloadSchemaType.FLOAT),
]


def ensure_inventory_payload_indexes(client: QdrantClient) -> None:
    """Create payload indexes for inventory collections (best-effort)."""

    def _safe_index(coll: str, field: str, schema: rest.PayloadSchemaType) -> None:
        try:
            client.create_payload_index(
                collection_name=coll,
                field_name=field,
                field_schema=schema,
            )
        except Exception:  # noqa: BLE001
            logger.debug("Payload index %s.%s already exists or unsupported", coll, field)

    for coll, field, schema in INVENTORY_INDEXES:
        _safe_index(coll, field, schema)
