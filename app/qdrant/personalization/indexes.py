"""Payload indexes for personalization collections (15+ fields)."""

from __future__ import annotations

import logging
from typing import List, Tuple

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

from app.qdrant.personalization.collections import (
    COLL_CUSTOMER_JOURNEYS,
    COLL_CUSTOMER_PROFILES,
    COLL_RECOMMENDATION_HISTORY,
)

logger = logging.getLogger(__name__)

# (collection, field, schema)
PERSONALIZATION_INDEXES: List[Tuple[str, str, rest.PayloadSchemaType]] = [
    (COLL_CUSTOMER_PROFILES, "loyalty_tier", rest.PayloadSchemaType.KEYWORD),
    (COLL_CUSTOMER_PROFILES, "rf_score", rest.PayloadSchemaType.FLOAT),
    (COLL_CUSTOMER_PROFILES, "price_sensitivity", rest.PayloadSchemaType.FLOAT),
    (COLL_CUSTOMER_PROFILES, "region", rest.PayloadSchemaType.KEYWORD),
    (COLL_CUSTOMER_PROFILES, "last_active", rest.PayloadSchemaType.KEYWORD),
    (COLL_CUSTOMER_PROFILES, "channel_preference", rest.PayloadSchemaType.KEYWORD),
    (COLL_RECOMMENDATION_HISTORY, "customer_id", rest.PayloadSchemaType.KEYWORD),
    (COLL_RECOMMENDATION_HISTORY, "product_id", rest.PayloadSchemaType.KEYWORD),
    (COLL_RECOMMENDATION_HISTORY, "click_probability", rest.PayloadSchemaType.FLOAT),
    (COLL_RECOMMENDATION_HISTORY, "purchase_probability", rest.PayloadSchemaType.FLOAT),
    (COLL_RECOMMENDATION_HISTORY, "ab_variant", rest.PayloadSchemaType.KEYWORD),
    (COLL_CUSTOMER_JOURNEYS, "customer_id", rest.PayloadSchemaType.KEYWORD),
    (COLL_CUSTOMER_JOURNEYS, "journey_state", rest.PayloadSchemaType.KEYWORD),
    (COLL_CUSTOMER_JOURNEYS, "channel", rest.PayloadSchemaType.KEYWORD),
    (COLL_CUSTOMER_JOURNEYS, "next_step", rest.PayloadSchemaType.KEYWORD),
    (COLL_CUSTOMER_JOURNEYS, "conversion_probability", rest.PayloadSchemaType.FLOAT),
]


def ensure_personalization_payload_indexes(client: QdrantClient) -> None:
    """Create payload indexes for personalization collections (best-effort)."""

    def _safe_index(coll: str, field: str, schema: rest.PayloadSchemaType) -> None:
        try:
            client.create_payload_index(
                collection_name=coll,
                field_name=field,
                field_schema=schema,
            )
        except Exception:  # noqa: BLE001
            logger.debug("Payload index %s.%s already exists or unsupported", coll, field)

    for coll, field, schema in PERSONALIZATION_INDEXES:
        _safe_index(coll, field, schema)
