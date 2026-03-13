"""Production inventory collections: inventory_levels, reorder_history, stockout_events."""

from __future__ import annotations

import logging
from typing import Any, Dict, Final, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

from app.qdrant_client import ensure_collection, get_qdrant_client
from app.qdrant.inventory.indexes import ensure_inventory_payload_indexes

logger = logging.getLogger(__name__)

COLL_INVENTORY_LEVELS: Final[str] = "inventory_levels"
COLL_REORDER_HISTORY: Final[str] = "reorder_history"
COLL_STOCKOUT_EVENTS: Final[str] = "stockout_events"

INVENTORY_COLLECTIONS: Dict[str, Dict[str, Any]] = {
    COLL_INVENTORY_LEVELS: {
        "vector_size": 64,
        "payload_indexes": ["warehouse_id", "sku", "stock_level", "last_updated"],
    },
    COLL_REORDER_HISTORY: {
        "vector_size": 64,
        "payload_indexes": ["sku", "supplier", "order_qty", "arrival_date"],
    },
    COLL_STOCKOUT_EVENTS: {
        "vector_size": 64,
        "payload_indexes": ["sku", "stockout_date", "lost_sales"],
    },
}


def setup_inventory_collections(client: Optional[QdrantClient] = None) -> None:
    """Create inventory collections and payload indexes (sync)."""
    c = client or get_qdrant_client()
    for name, config in INVENTORY_COLLECTIONS.items():
        ensure_collection(
            c,
            name,
            vector_size=config["vector_size"],
            distance=rest.Distance.COSINE,
        )
    ensure_inventory_payload_indexes(c)
