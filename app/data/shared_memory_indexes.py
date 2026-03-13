"""
Multi-agent shared memory: payload indexes for products, goals, solutions, episodes.

Mirrors Qdrant feature usage for Shopper + Inventory:
- products: stock, region, price (filtered vector search)
- goals: blackboard (status, agent_role, user_id)
- solutions: goal_id, status
- goal_solution_links: success, region, category (episodic filters)

Call ensure_shared_memory_indexes() from bootstrap after collections exist.
"""

from __future__ import annotations

import logging
from typing import Final, Sequence

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

from app.config import COLLECTIONS
from app.qdrant_client import get_qdrant_client

logger = logging.getLogger(__name__)

COLL_PRODUCTS: Final[str] = COLLECTIONS.products
COLL_GOALS: Final[str] = COLLECTIONS.goals
COLL_SOLUTIONS: Final[str] = COLLECTIONS.solutions


def _safe_payload_index(
    client: QdrantClient,
    collection_name: str,
    field_name: str,
    field_schema: rest.PayloadSchemaType,
) -> None:
    try:
        client.create_payload_index(
            collection_name=collection_name,
            field_name=field_name,
            field_schema=field_schema,
        )
        logger.debug("Created payload index %s.%s", collection_name, field_name)
    except Exception as e:  # noqa: BLE001
        logger.debug(
            "Payload index %s.%s already exists or unsupported: %s",
            collection_name,
            field_name,
            e,
        )


def ensure_shared_memory_indexes(client: QdrantClient | None = None) -> None:
    """
    Idempotently create payload indexes for multi-agent shared memory.
    Products: stock, region, price (Shopper/Inventory filtered search).
    Goals: status, user_id, agent_role (blackboard).
    Solutions: goal_id, status, created_at.
    """
    q = client or get_qdrant_client()

    # products — strict business constraints (stock, region, price)
    _safe_payload_index(q, COLL_PRODUCTS, "sku", rest.PayloadSchemaType.KEYWORD)
    _safe_payload_index(q, COLL_PRODUCTS, "stock", rest.PayloadSchemaType.INTEGER)
    _safe_payload_index(q, COLL_PRODUCTS, "region", rest.PayloadSchemaType.KEYWORD)
    _safe_payload_index(q, COLL_PRODUCTS, "price", rest.PayloadSchemaType.FLOAT)
    _safe_payload_index(q, COLL_PRODUCTS, "price_eur", rest.PayloadSchemaType.FLOAT)
    _safe_payload_index(q, COLL_PRODUCTS, "last_updated", rest.PayloadSchemaType.DATETIME)
    _safe_payload_index(q, COLL_PRODUCTS, "category", rest.PayloadSchemaType.KEYWORD)

    # goals — blackboard task board
    _safe_payload_index(q, COLL_GOALS, "goal_id", rest.PayloadSchemaType.KEYWORD)
    _safe_payload_index(q, COLL_GOALS, "user_id", rest.PayloadSchemaType.KEYWORD)
    _safe_payload_index(q, COLL_GOALS, "status", rest.PayloadSchemaType.KEYWORD)
    _safe_payload_index(q, COLL_GOALS, "created_at", rest.PayloadSchemaType.DATETIME)
    _safe_payload_index(q, COLL_GOALS, "agent_role", rest.PayloadSchemaType.KEYWORD)

    # solutions — candidate plans per goal
    _safe_payload_index(q, COLL_SOLUTIONS, "goal_id", rest.PayloadSchemaType.KEYWORD)
    _safe_payload_index(q, COLL_SOLUTIONS, "status", rest.PayloadSchemaType.KEYWORD)
    _safe_payload_index(q, COLL_SOLUTIONS, "created_at", rest.PayloadSchemaType.DATETIME)

    logger.info("Shared memory payload indexes ensured")


__all__: Sequence[str] = ["ensure_shared_memory_indexes", "COLL_PRODUCTS", "COLL_GOALS", "COLL_SOLUTIONS"]
