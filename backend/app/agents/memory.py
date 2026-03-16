"""
Memory abstraction used by agents. Default implementation uses Qdrant if available,
and falls back to an in-memory dict for dev/test.

This module exposes:
- MemoryStore interface
- QdrantMemory (if Qdrant available)
- InMemoryMemory (fallback)
- get_memory() helper to instantiate per env
"""

from typing import Any, Dict, List, Optional
import logging
import os

logger = logging.getLogger(__name__)


class MemoryStore:
    def upsert(self, collection: str, id: str, vector: List[float], payload: Dict[str, Any]):
        raise NotImplementedError

    def search(self, collection: str, query_vector: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def get_point(self, collection: str, id: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError


class InMemoryMemory(MemoryStore):
    """In-memory fallback store."""

    def __init__(self):
        # structure: {collection: {id: {"vector": vec, "payload": payload}}}
        self._store: Dict[str, Dict[str, Dict[str, Any]]] = {}

    def upsert(self, collection: str, id: str, vector: List[float], payload: Dict[str, Any]):
        col = self._store.setdefault(collection, {})
        col[id] = {"vector": vector, "payload": payload}
        logger.debug("InMemoryMemory upsert: %s/%s", collection, id)

    def search(self, collection: str, query_vector: List[float], top_k: int = 10):
        import math

        col = self._store.get(collection, {})
        results = []
        for pid, rec in col.items():
            v = rec["vector"]
            if not v or not query_vector:
                score = 0.0
            else:
                dot = sum(a * b for a, b in zip(v, query_vector))
                norm1 = math.sqrt(sum(a * a for a in v))
                norm2 = math.sqrt(sum(a * a for a in query_vector))
                score = dot / (norm1 * norm2 + 1e-8)
            results.append({"id": pid, "payload": rec["payload"], "score": score})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def get_point(self, collection: str, id: str):
        return self._store.get(collection, {}).get(id)


_memory_singleton: Optional[MemoryStore] = None


def get_memory() -> MemoryStore:
    """Lazy singleton factory for MemoryStore."""
    global _memory_singleton
    if _memory_singleton is None:
        if os.getenv("QDRANT_URL") or os.getenv("QDRANT_HOST"):
            try:
                from app.agents.qdrant_memory import QdrantMemory  # type: ignore

                _memory_singleton = QdrantMemory()
            except Exception as e:  # pragma: no cover - best-effort
                logger.warning(
                    "QdrantMemory not available, falling back to InMemoryMemory: %s", e
                )
                _memory_singleton = InMemoryMemory()
        else:
            _memory_singleton = InMemoryMemory()
    return _memory_singleton

