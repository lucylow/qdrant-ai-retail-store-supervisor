from __future__ import annotations

from typing import Optional

import logging

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest


logger = logging.getLogger(__name__)


class QdrantQuantizer:
    """
    Helpers for enabling binary quantization and on-disk index storage.

    Designed for simple use from scripts:

        quantizer = QdrantQuantizer(client)
        quantizer.enable_binary_quantization("retail_products")
        quantizer.enable_on_disk_storage("retail_products")
    """

    def __init__(self, client: QdrantClient) -> None:
        self.client = client

    def enable_binary_quantization(self, collection_name: str) -> None:
        """Enable binary quantization for the vectors of a collection."""
        logger.info("Enabling binary quantization for %s", collection_name)
        try:
            self.client.update_collection(
                collection_name=collection_name,
                quantization_config=rest.BinaryQuantization(
                    always_ram=True,
                ),
            )
        except Exception:  # noqa: BLE001
            logger.exception(
                "Failed to enable binary quantization for %s", collection_name
            )

    def enable_on_disk_storage(
        self,
        collection_name: str,
        indexing_threshold: int = 20_000,
        memmap_threshold: int = 20_000,
    ) -> None:
        """
        Enable on-disk index (memmap) for cost‑effective scaling.
        """
        logger.info("Enabling on-disk storage for %s", collection_name)
        try:
            self.client.update_collection(
                collection_name=collection_name,
                optimizers_config=rest.OptimizersConfigDiff(
                    indexing_threshold=indexing_threshold,
                    memmap_threshold=memmap_threshold,
                ),
            )
        except Exception:  # noqa: BLE001
            logger.exception("Failed to enable on-disk storage for %s", collection_name)


__all__ = ["QdrantQuantizer"]

