from __future__ import annotations

"""
Tiny metrics helpers for the multi-agent store manager.

Metrics are computed directly from Qdrant using simple aggregate counts.

Definitions (current implementation):
- episode_reuse_rate:
    share of episodes that are marked as "success" out of all episodes.
    This approximates how rich your pool of reusable successful episodes is.

- conversion_rate:
    share of episodes with outcome == "success" among all episodes that have
    a non-unknown outcome (success | partial | failure).
"""

from typing import Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

from app.config import COLL_EPISODES
from app.qdrant_client import get_qdrant_client


def _build_outcome_filter(outcome: str) -> rest.Filter:
    return rest.Filter(
        must=[
            rest.FieldCondition(
                key="outcome",
                match=rest.MatchValue(value=outcome),
            )
        ]
    )


def compute_episode_reuse_rate(client: Optional[QdrantClient] = None) -> float:
    """
    Returns a float in [0, 1]. If there are no episodes, returns 0.0.
    Approximates "how often successful episodes exist to be reused" as:

        count(episodes with outcome == 'success') / count(all episodes)
    """
    client = client or get_qdrant_client()

    total = client.count(collection_name=COLL_EPISODES, count_filter=None, exact=False).count
    if not total:
        return 0.0

    success = client.count(
        collection_name=COLL_EPISODES,
        count_filter=_build_outcome_filter("success"),
        exact=False,
    ).count

    return float(success) / float(total)


def compute_conversion_rate(client: Optional[QdrantClient] = None) -> float:
    """
    Returns a float in [0, 1]. If there are no episodes with known outcomes,
    returns 0.0.

    We define conversion_rate as:

        count(episodes with outcome == 'success')
        /
        count(episodes with outcome in {'success', 'partial', 'failure'})
    """
    client = client or get_qdrant_client()

    total = client.count(collection_name=COLL_EPISODES, count_filter=None, exact=False).count
    if not total:
        return 0.0

    unknown = client.count(
        collection_name=COLL_EPISODES,
        count_filter=_build_outcome_filter("unknown"),
        exact=False,
    ).count

    denom = total - unknown
    if denom <= 0:
        return 0.0

    success = client.count(
        collection_name=COLL_EPISODES,
        count_filter=_build_outcome_filter("success"),
        exact=False,
    ).count

    return float(success) / float(denom)


__all__ = ["compute_episode_reuse_rate", "compute_conversion_rate"]

