from __future__ import annotations

from typing import Final, Sequence

from qdrant_client.http import models as rest

from app.config import COLLECTIONS, FASHION_CLIP_COLLECTION
from app.qdrant_client import ensure_collection, ensure_named_vectors_collection, get_qdrant_client
from app.multimodal.schema import (
    PRODUCTS_MULTIMODAL_COLLECTION,
    get_products_multimodal_vectors_config,
)
from app.multimodal.semantic_cache import ensure_semantic_cache_collection

FASHION_CLIP_DIM = 512


def get_fashion_clip_vectors_config() -> rest.VectorsConfig:
    """Named vectors for Fashion-MNIST visual search: image + text (CLIP 512d)."""
    return rest.VectorsConfig(
        named_vectors={
            "image": rest.NamedVectorParams(size=FASHION_CLIP_DIM, distance=rest.Distance.COSINE),
            "text": rest.NamedVectorParams(size=FASHION_CLIP_DIM, distance=rest.Distance.COSINE),
        }
    )


COLL_PRODUCTS: Final[str] = COLLECTIONS.products
COLL_GOALS: Final[str] = COLLECTIONS.goals
COLL_SOLUTIONS: Final[str] = COLLECTIONS.solutions
COLL_EPISODES: Final[str] = COLLECTIONS.episodes
COLL_REASONING_GRAPHS: Final[str] = "reasoning_graphs"
COLL_COMPETITOR_PRICES: Final[str] = "competitor_prices"


def ensure_all_collections() -> None:
    """
    Idempotently ensure all Qdrant collections exist with sane defaults.
    """
    client = get_qdrant_client()
    ensure_collection(client, COLL_GOALS, vector_size=384, distance=rest.Distance.COSINE)
    ensure_collection(client, COLL_PRODUCTS, vector_size=256, distance=rest.Distance.COSINE)
    ensure_collection(client, COLL_SOLUTIONS, vector_size=384, distance=rest.Distance.COSINE)
    ensure_collection(
        client, COLL_REASONING_GRAPHS, vector_size=384, distance=rest.Distance.COSINE
    )
    ensure_collection(client, COLL_EPISODES, vector_size=4, distance=rest.Distance.DOT)
    ensure_collection(
        client, COLL_COMPETITOR_PRICES, vector_size=32, distance=rest.Distance.COSINE
    )
    ensure_named_vectors_collection(
        client, PRODUCTS_MULTIMODAL_COLLECTION, get_products_multimodal_vectors_config()
    )
    ensure_named_vectors_collection(
        client, FASHION_CLIP_COLLECTION, get_fashion_clip_vectors_config()
    )
    ensure_semantic_cache_collection(client)
    try:
        from app.data.memory_collections import ensure_memory_collections
        ensure_memory_collections()
    except Exception:  # noqa: BLE001
        pass
    try:
        from app.data.shared_memory_indexes import ensure_shared_memory_indexes
        ensure_shared_memory_indexes(client)
    except Exception:  # noqa: BLE001
        pass


__all__: Sequence[str] = [
    "ensure_all_collections",
    "COLL_PRODUCTS",
    "COLL_GOALS",
    "COLL_SOLUTIONS",
    "COLL_EPISODES",
    "COLL_REASONING_GRAPHS",
    "COLL_COMPETITOR_PRICES",
    "PRODUCTS_MULTIMODAL_COLLECTION",
]

