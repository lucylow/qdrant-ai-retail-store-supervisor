"""Typed Qdrant client wrapper with connection pooling and health checks."""

from __future__ import annotations

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

from app.core.exceptions import QdrantConnectionError
from app.core.logger import get_logger
from app.qdrant_client import (
    ensure_collection as _ensure_collection,
    get_qdrant_client as _get_qdrant_client,
    qdrant_health_check as _qdrant_health_check,
)

logger = get_logger(__name__)


def get_client(retries: int = 3, backoff: float = 1.0) -> QdrantClient:
    """Return a connected Qdrant client; raises QdrantConnectionError on failure."""
    try:
        return _get_qdrant_client(retries=retries, backoff=backoff)
    except Exception as e:
        logger.error("qdrant_connection_failed", error=str(e))
        raise QdrantConnectionError(f"Qdrant connection failed: {e}") from e


def ensure_collection(
    client: QdrantClient,
    name: str,
    vector_size: int,
    distance: rest.Distance = rest.Distance.COSINE,
) -> None:
    """Idempotently create collection if missing (delegate to app.qdrant_client)."""
    _ensure_collection(client, name, vector_size, distance)


def health_check(client: QdrantClient | None = None) -> bool:
    """Return True if Qdrant is reachable."""
    return _qdrant_health_check(client)
