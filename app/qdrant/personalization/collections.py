"""Personalization collections: customer_profiles, recommendation_history, customer_journeys."""

from __future__ import annotations

import logging
from typing import Any, Dict, Final, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

from app.qdrant_client import ensure_collection, get_qdrant_client
from app.qdrant.personalization.indexes import ensure_personalization_payload_indexes

logger = logging.getLogger(__name__)

COLL_CUSTOMER_PROFILES: Final[str] = "customer_profiles"
COLL_RECOMMENDATION_HISTORY: Final[str] = "recommendation_history"
COLL_CUSTOMER_JOURNEYS: Final[str] = "customer_journeys"

PERSONALIZATION_COLLECTIONS: Dict[str, Dict[str, Any]] = {
    COLL_CUSTOMER_PROFILES: {
        "vector_size": 64,
        "payload_indexes": [
            "loyalty_tier",
            "rf_score",
            "price_sensitivity",
            "region",
            "last_active",
            "channel_preference",
        ],
    },
    COLL_RECOMMENDATION_HISTORY: {
        "vector_size": 64,
        "payload_indexes": [
            "customer_id",
            "product_id",
            "click_probability",
            "purchase_probability",
            "ab_variant",
        ],
    },
    COLL_CUSTOMER_JOURNEYS: {
        "vector_size": 64,
        "payload_indexes": [
            "customer_id",
            "journey_state",
            "channel",
            "next_step",
            "conversion_probability",
        ],
    },
}


def setup_personalization_collections(client: Optional[QdrantClient] = None) -> None:
    """Create personalization collections and 15+ payload indexes (sync)."""
    c = client or get_qdrant_client()
    for name, config in PERSONALIZATION_COLLECTIONS.items():
        ensure_collection(
            c,
            name,
            vector_size=config["vector_size"],
            distance=rest.Distance.COSINE,
        )
    ensure_personalization_payload_indexes(c)
    logger.info("Personalization collections and indexes ready")
