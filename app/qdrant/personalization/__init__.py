"""Qdrant personalization: customer_profiles, recommendation_history, customer_journeys."""

from app.qdrant.personalization.collections import (
    COLL_CUSTOMER_JOURNEYS,
    COLL_CUSTOMER_PROFILES,
    COLL_RECOMMENDATION_HISTORY,
    setup_personalization_collections,
)
from app.qdrant.personalization.client import PersonalizationQdrantClient

__all__ = [
    "COLL_CUSTOMER_PROFILES",
    "COLL_RECOMMENDATION_HISTORY",
    "COLL_CUSTOMER_JOURNEYS",
    "setup_personalization_collections",
    "PersonalizationQdrantClient",
]
