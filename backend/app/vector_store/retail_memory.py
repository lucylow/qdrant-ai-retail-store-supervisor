from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence

import logging

from app.embeddings import embed_texts
from app.qdrant_client import get_qdrant_client, ensure_collection

logger = logging.getLogger(__name__)


@dataclass
class RetailVectorSearchResult:
    id: Any
    score: float
    payload: Dict[str, Any]


class RetailVectorMemory:
    """
    Thin retail-focused layer over Qdrant + SentenceTransformers embeddings.

    This is intentionally narrow in scope: it knows how to store and search
    over product-like payloads and can be extended as needed for customers
    or arbitrary knowledge documents.
    """

    def __init__(
        self,
        collection_name: str = "retail_products",
        vector_size: Optional[int] = None,
    ) -> None:
        self._client = get_qdrant_client()
        self.collection_name = collection_name
        self._vector_size = vector_size or self._infer_vector_size()
        ensure_collection(self._client, self.collection_name, self._vector_size)

    def _infer_vector_size(self) -> int:
        """
        Infer embedding dimensionality by encoding a tiny probe string.
        """
        probe = embed_texts(["_probe_"])
        if probe.shape[0] == 0:
            raise RuntimeError("Embedding model returned empty vector for probe text")
        return int(probe.shape[1])

    def store_product(self, product: Dict[str, Any]) -> None:
        """
        Upsert a single product into the vector store.

        The product dict is expected to contain:
        - id (str or int)
        - description (str)
        Plus any additional payload fields you want to retrieve later.
        """
        description = product.get("description") or ""
        if not description:
            logger.warning("store_product called with empty description for %s", product)
        vec = embed_texts([description])[0].tolist()

        self._client.upsert(
            collection_name=self.collection_name,
            points=[
                {
                    "id": product.get("id"),
                    "vector": vec,
                    "payload": product,
                }
            ],
        )

    def store_products_batch(self, products: Sequence[Dict[str, Any]]) -> None:
        """
        Batch upsert of multiple products for faster ingestion.
        """
        if not products:
            return

        descriptions = [p.get("description") or "" for p in products]
        vectors = embed_texts(descriptions)
        points = []
        for product, vec in zip(products, vectors):
            points.append(
                {
                    "id": product.get("id"),
                    "vector": vec.tolist(),
                    "payload": product,
                }
            )

        self._client.upsert(collection_name=self.collection_name, points=points)

    def search_products(
        self,
        query: str,
        limit: int = 5,
    ) -> List[RetailVectorSearchResult]:
        """
        Semantic search over products by natural-language query.
        """
        if not query:
            return []

        qvec = embed_texts([query])[0].tolist()
        hits = self._client.search(
            collection_name=self.collection_name,
            query_vector=qvec,
            limit=limit,
            with_payload=True,
        )
        results: List[RetailVectorSearchResult] = []
        for h in hits:
            results.append(
                RetailVectorSearchResult(
                    id=h.id,
                    score=float(getattr(h, "score", 0.0)),
                    payload=dict(getattr(h, "payload", {}) or {}),
                )
            )
        return results


__all__ = ["RetailVectorMemory", "RetailVectorSearchResult"]

