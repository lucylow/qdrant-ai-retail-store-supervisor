from __future__ import annotations

from typing import Optional

import logging
import time

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

from app.config import QDRANT


logger = logging.getLogger(__name__)


def get_qdrant_client(retries: int = 3, backoff: float = 1.0) -> QdrantClient:
    """
    Returns a QdrantClient configured for QDRANT (cloud or local).
    Retries a few times for transient network issues.
    """
    url = QDRANT.url or f"http://{QDRANT.host}:{QDRANT.port}"
    kwargs: dict[str, object] = {"url": url}
    if QDRANT.api_key:
        kwargs["api_key"] = QDRANT.api_key
    last_exc: Optional[Exception] = None
    for attempt in range(1, retries + 1):
        try:
            client = QdrantClient(**kwargs)
            client.get_collections()
            return client
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            logger.warning("Qdrant connection attempt %s failed", attempt, exc_info=exc)
            time.sleep(backoff * (2 ** (attempt - 1)))
    logger.error("All Qdrant connection attempts failed")
    if last_exc is not None:
        raise last_exc
    raise RuntimeError("Qdrant connection failed for unknown reasons")


def ensure_collection(
    client: QdrantClient,
    name: str,
    vector_size: int,
    distance: rest.Distance = rest.Distance.COSINE,
) -> None:
    """
    Idempotently create collection if missing and apply HNSW params.
    """
    existing = [c.name for c in client.get_collections().collections or []]
    if name in existing:
        logger.debug("Collection %s already exists", name)
        return
    client.recreate_collection(
        name,
        vectors_config=rest.VectorParams(size=vector_size, distance=distance),
    )
    try:
        client.update_collection(
            name,
            hnsw_config=rest.HnswConfig(
                m=QDRANT.hnsw_m,
                ef_construct=QDRANT.hnsw_ef_construct,
            ),
        )
    except Exception:  # noqa: BLE001
        logger.debug("Could not update HNSW params; continuing", exc_info=True)


def qdrant_health_check(client: Optional[QdrantClient] = None) -> bool:
    try:
        q_client = client or get_qdrant_client()
        _ = q_client.get_collections()
        return True
    except Exception as exc:  # noqa: BLE001
        logger.exception("Qdrant health check failed", exc_info=exc)
        return False


__all__ = ["get_qdrant_client", "ensure_collection", "qdrant_health_check"]

