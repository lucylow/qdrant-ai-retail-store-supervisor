"""CRUD patterns and transactions (typed repositories)."""

from __future__ import annotations

from qdrant_client import QdrantClient

from app.core.exceptions import RepositoryError
from app.core.logger import get_logger

logger = get_logger(__name__)


class ProductRepository:
    """Product CRUD (read-only for production spec)."""

    def __init__(self, client: QdrantClient, collection: str) -> None:
        self._client = client
        self._collection = collection

    def get(self, product_id: str) -> dict[str, object] | None:
        """Fetch one product by id; returns payload or None."""
        try:
            points = self._client.retrieve(
                collection_name=self._collection,
                ids=[product_id],
                with_payload=True,
                with_vectors=False,
            )
            if not points:
                return None
            return points[0].payload or {}
        except Exception as e:
            logger.warning("product_get_failed", product_id=product_id, error=str(e))
            raise RepositoryError(f"Product get failed: {e}") from e


class GoalRepository:
    """Goal collection repository (write goals for RAG)."""

    def __init__(self, client: QdrantClient, collection: str) -> None:
        self._client = client
        self._collection = collection

    def list_ids(self, limit: int = 100) -> list[str]:
        """List goal ids (scroll)."""
        try:
            result, _ = self._client.scroll(
                collection_name=self._collection,
                limit=limit,
                with_payload=False,
                with_vectors=False,
            )
            return [str(p.id) for p in (result or [])]
        except Exception as e:
            logger.warning("goal_list_failed", error=str(e))
            raise RepositoryError(f"Goal list failed: {e}") from e
