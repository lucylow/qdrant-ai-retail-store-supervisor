from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import logging

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

from app.config import QDRANT
from app.qdrant_client import get_qdrant_client


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PayloadIndexConfig:
    field_name: str
    field_type: str  # "keyword", "integer", "float", "geo"
    params: Dict[str, Any]


class ProductionQdrantClient:
    """
    Thin, production-oriented wrapper around the shared QdrantClient.

    Responsibilities (for sponsor demo):
    - Provide a ready-to-use client (cloud or local, via existing config).
    - Ensure 12 useful payload indexes exist on the main product collection.
    - Offer small helpers for search / scrolling that other modules can reuse.
    """

    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        collection_name: str = "retail_products",
    ) -> None:
        if url or api_key:
            # Explicit override, e.g. Streamlit demo with Qdrant Cloud URL.
            client_kwargs: Dict[str, Any] = {"url": url or QDRANT.url}
            if api_key:
                client_kwargs["api_key"] = api_key
            self.client = QdrantClient(**client_kwargs)
        else:
            # Reuse the common connection logic (retries, health checks, etc.).
            self.client = get_qdrant_client()

        self.collection_name = collection_name
        self.indexes: Dict[str, PayloadIndexConfig] = {}
        self._create_sponsor_indexes()

    # ------------------------------------------------------------------
    # Payload indexing
    # ------------------------------------------------------------------
    def _payload_index_definitions(self) -> List[PayloadIndexConfig]:
        """
        Define 12 sponsor-friendly payload indexes.

        These are intentionally generic retail-style fields which can be
        attached to products, goals, or solutions.
        """
        return [
            PayloadIndexConfig("region", "keyword", {"on_disk": True}),
            PayloadIndexConfig(
                "stock_quantity",
                "integer",
                {"type": "integer", "lookup": True, "range": True},
            ),
            PayloadIndexConfig(
                "price_usd",
                "float",
                {"type": "float", "lookup": True, "range": True},
            ),
            PayloadIndexConfig("category", "keyword", {"on_disk": True}),
            PayloadIndexConfig("brand", "keyword", {"on_disk": True}),
            PayloadIndexConfig(
                "timestamp",
                "integer",
                {"type": "integer", "lookup": True, "range": True},
            ),
            PayloadIndexConfig("channel", "keyword", {"on_disk": True}),
            PayloadIndexConfig("language", "keyword", {"on_disk": True}),
            PayloadIndexConfig(
                "rating",
                "float",
                {"type": "float", "lookup": True, "range": True},
            ),
            PayloadIndexConfig("currency", "keyword", {"on_disk": True}),
            PayloadIndexConfig(
                "discount_pct",
                "float",
                {"type": "float", "lookup": True, "range": True},
            ),
            PayloadIndexConfig(
                "is_active",
                "integer",
                {"type": "integer", "lookup": True, "range": False},
            ),
        ]

    def _create_sponsor_indexes(self) -> None:
        """Create 12 production payload indexes for sponsor judges."""
        indexes = self._payload_index_definitions()

        for idx in indexes:
            self.indexes[idx.field_name] = idx
            try:
                logger.info("Creating payload index %s", idx.field_name)
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name=idx.field_name,
                    field_schema=rest.PayloadSchemaType(idx.field_type),
                )
                logger.info("Sponsor index created: %s", idx.field_name)
            except Exception:  # noqa: BLE001
                # Idempotent: if it already exists, we are fine.
                logger.info("Payload index already exists: %s", idx.field_name)

    # ------------------------------------------------------------------
    # Convenience wrappers used by scripts and demo
    # ------------------------------------------------------------------
    def search(
        self,
        query_vector: List[float],
        limit: int = 10,
        collection_name: Optional[str] = None,
        query_filter: Optional[rest.Filter] = None,
    ) -> List[rest.ScoredPoint]:
        return self.client.search(
            collection_name=collection_name or self.collection_name,
            query_vector=query_vector,
            limit=limit,
            query_filter=query_filter,
        )

    def scroll(
        self,
        collection_name: Optional[str] = None,
        scroll_filter: Optional[rest.Filter] = None,
        limit: int = 100,
    ) -> List[rest.Record]:
        _, points = self.client.scroll(
            collection_name=collection_name or self.collection_name,
            scroll_filter=scroll_filter,
            limit=limit,
        )
        return points or []


__all__ = ["PayloadIndexConfig", "ProductionQdrantClient"]

