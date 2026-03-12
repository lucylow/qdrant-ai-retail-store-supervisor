from __future__ import annotations

from typing import Iterable, List

import logging

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

from app.qdrant.production_client import PayloadIndexConfig


logger = logging.getLogger(__name__)


class IndexManager:
    """
    Central place to (re)create payload indexes across multiple collections.

    This is primarily used by `scripts/qdrant/create_indexes.py` and by the
    sponsor demo to ensure a consistent set of 12 filterable fields on all
    retail-related collections.
    """

    def __init__(self, client: QdrantClient) -> None:
        self.client = client

    def ensure_indexes(
        self,
        collection_name: str,
        indexes: Iterable[PayloadIndexConfig],
    ) -> None:
        for cfg in indexes:
            try:
                logger.info(
                    "Ensuring payload index %s on %s", cfg.field_name, collection_name
                )
                self.client.create_payload_index(
                    collection_name=collection_name,
                    field_name=cfg.field_name,
                    field_schema=rest.PayloadSchemaType(cfg.field_type),
                )
            except Exception:  # noqa: BLE001
                logger.info(
                    "Payload index %s already exists on %s",
                    cfg.field_name,
                    collection_name,
                )

    def sponsor_default_indexes(self) -> List[PayloadIndexConfig]:
        # Reuse the same definitions as ProductionQdrantClient to stay in sync.
        from app.qdrant.production_client import ProductionQdrantClient

        tmp = ProductionQdrantClient()
        return list(tmp.indexes.values())


__all__ = ["IndexManager"]

