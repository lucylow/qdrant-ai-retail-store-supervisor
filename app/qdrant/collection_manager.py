from __future__ import annotations

from typing import Dict

import logging

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

from app.qdrant.quantization import QdrantQuantizer


logger = logging.getLogger(__name__)


class CollectionManager:
    """
    Responsible for creating the four sponsor collections and applying
    quantization / optimizer configs.
    """

    DEFAULT_COLLECTIONS: Dict[str, Dict[str, int]] = {
        "retail_goals": {"size": 768},
        "retail_products": {"size": 768},
        "retail_solutions": {"size": 768},
        "reasoning_graphs": {"size": 1024},
    }

    def __init__(self, client: QdrantClient) -> None:
        self.client = client
        self.quantizer = QdrantQuantizer(client)

    def ensure_collections(self) -> None:
        for name, cfg in self.DEFAULT_COLLECTIONS.items():
            self._ensure_collection(name, cfg["size"])

    def _ensure_collection(self, name: str, size: int) -> None:
        existing = [c.name for c in self.client.get_collections().collections or []]
        if name in existing:
            logger.info("Collection %s already exists", name)
        else:
            logger.info("Creating sponsor collection %s", name)
            self.client.recreate_collection(
                name,
                vectors_config=rest.VectorParams(size=size, distance=rest.Distance.COSINE),
            )
        # Apply quantization + on-disk storage
        self.quantizer.enable_binary_quantization(name)
        self.quantizer.enable_on_disk_storage(name)


__all__ = ["CollectionManager"]

