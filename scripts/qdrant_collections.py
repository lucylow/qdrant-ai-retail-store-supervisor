"""
Create the Qdrant collections used by the multi-agent store supervisor app.
Run: python scripts/qdrant_collections.py
"""
import logging

from qdrant_client.http import models as rest

from app.qdrant_client import get_qdrant_client
from app.config import (
    COLL_GOALS,
    COLL_SOLUTIONS,
    COLL_EPISODES,
    COLL_PRODUCTS,
    COLL_MESSAGES,
    DEFAULT_VECTOR_SIZE,
    PRODUCT_IMAGE_VECTOR_SIZE,
    HNSW_M,
    HNSW_EF_CONSTRUCT,
)

logger = logging.getLogger(__name__)


def create_collections() -> None:
    client = get_qdrant_client()
    existing = [c["name"] for c in client.get_collections().get("collections", [])]

    def ensure(name: str, vectors_config) -> None:
        if name in existing:
            logger.info("Collection %s exists, skipping create.", name)
            return
        client.recreate_collection(name, vectors_config=vectors_config)
        try:
            client.update_collection(
                collection_name=name,
                hnsw_config=rest.HnswConfig(m=HNSW_M, ef_construct=HNSW_EF_CONSTRUCT),
            )
        except Exception:  # noqa: BLE001
            logger.info(
                "Could not update collection %s HNSW params (SDK or server version).",
                name,
            )

    ensure(
        COLL_GOALS,
        rest.VectorParams(size=DEFAULT_VECTOR_SIZE, distance=rest.Distance.COSINE),
    )
    ensure(
        COLL_SOLUTIONS,
        rest.VectorParams(size=DEFAULT_VECTOR_SIZE, distance=rest.Distance.COSINE),
    )
    ensure(
        COLL_EPISODES,
        rest.VectorParams(size=DEFAULT_VECTOR_SIZE, distance=rest.Distance.COSINE),
    )

    try:
        vectors_cfg = rest.VectorsConfig(
            params={
                "text_vector": rest.VectorParams(
                    size=DEFAULT_VECTOR_SIZE, distance=rest.Distance.COSINE
                ),
                "image_vector": rest.VectorParams(
                    size=PRODUCT_IMAGE_VECTOR_SIZE, distance=rest.Distance.COSINE
                ),
            }
        )
        ensure(COLL_PRODUCTS, vectors_cfg)
    except Exception:  # noqa: BLE001
        ensure(
            COLL_PRODUCTS,
            rest.VectorParams(size=DEFAULT_VECTOR_SIZE, distance=rest.Distance.COSINE),
        )

    ensure(
        COLL_MESSAGES,
        rest.VectorParams(size=DEFAULT_VECTOR_SIZE, distance=rest.Distance.COSINE),
    )
    logger.info("Collections ensured.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    create_collections()

