from __future__ import annotations

from typing import Final, Sequence

from qdrant_client.http import models as rest

from app.config import COLLECTIONS
from app.qdrant_client import ensure_collection, get_qdrant_client


COLL_PRODUCTS: Final[str] = COLLECTIONS.products
COLL_GOALS: Final[str] = COLLECTIONS.goals
COLL_SOLUTIONS: Final[str] = COLLECTIONS.solutions
COLL_EPISODES: Final[str] = COLLECTIONS.episodes
COLL_REASONING_GRAPHS: Final[str] = "reasoning_graphs"


def ensure_all_collections() -> None:
    """
    Idempotently ensure all Qdrant collections exist with sane defaults.
    """
    client = get_qdrant_client()
    ensure_collection(client, COLL_GOALS, vector_size=64, distance=rest.Distance.COSINE)
    ensure_collection(client, COLL_PRODUCTS, vector_size=256, distance=rest.Distance.COSINE)
    ensure_collection(
        client, COLL_REASONING_GRAPHS, vector_size=384, distance=rest.Distance.COSINE
    )
    ensure_collection(client, COLL_EPISODES, vector_size=4, distance=rest.Distance.DOT)


__all__: Sequence[str] = [
    "ensure_all_collections",
    "COLL_PRODUCTS",
    "COLL_GOALS",
    "COLL_SOLUTIONS",
    "COLL_EPISODES",
    "COLL_REASONING_GRAPHS",
]

