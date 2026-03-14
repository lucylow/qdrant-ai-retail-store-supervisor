from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import logging

from qdrant_client import QdrantClient

from app.qdrant_client import get_qdrant_client


logger = logging.getLogger(__name__)


@dataclass
class CollectionStats:
    name: str
    vectors_count: int
    payload_schema_len: int


@dataclass
class QdrantHealthReport:
    alive: bool
    collections: List[CollectionStats]


def gather_qdrant_health(client: QdrantClient | None = None) -> QdrantHealthReport:
    """
    Lightweight health/usage snapshot for the sponsor dashboard.
    """
    try:
        q_client = client or get_qdrant_client()
        collections: List[CollectionStats] = []
        for coll in q_client.get_collections().collections or []:
            info = q_client.get_collection(coll.name)
            vectors = info.points_count or 0
            payload_schema_len = len(info.payload_schema or {})
            collections.append(
                CollectionStats(
                    name=coll.name,
                    vectors_count=vectors,
                    payload_schema_len=payload_schema_len,
                )
            )
        return QdrantHealthReport(alive=True, collections=collections)
    except Exception:  # noqa: BLE001
        logger.exception("Failed to gather Qdrant health")
        return QdrantHealthReport(alive=False, collections=[])


__all__ = ["CollectionStats", "QdrantHealthReport", "gather_qdrant_health"]

