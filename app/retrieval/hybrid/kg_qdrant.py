"""Hybrid KG + Qdrant retrieval: structural KG reasoning → vector search → reranking fusion."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from app.config import COLLECTIONS
from app.embeddings import embed_single, as_list
from app.kg.neo4j_client import ProductionNeo4jClient
from app.kg.agents.reasoner import KGReasonerAgent
from app.kg.agents.embedder import KGEmbedderAgent
from app.qdrant_client import get_qdrant_client
from app.reranker import RerankItem, rerank


@dataclass
class HybridRetrievalResult:
    """Single result from hybrid KG + Qdrant pipeline."""

    id: str
    text: str
    score: float
    source: str  # "kg" | "qdrant" | "hybrid"
    payload: Dict[str, Any]
    kg_path_length: Optional[int] = None


class HybridKGQdrantRetriever:
    """
    KG structural retrieval + Qdrant vector search + cross-encoder reranking.
    """

    def __init__(
        self,
        neo4j_client: Optional[ProductionNeo4jClient] = None,
        qdrant_client: Optional[Any] = None,
        collection_name: Optional[str] = None,
    ) -> None:
        from app.kg.neo4j_client import ProductionNeo4jClient as DefaultNeo4j
        self.neo4j = neo4j_client or DefaultNeo4j()
        self.qdrant = qdrant_client or get_qdrant_client()
        self.collection_name = collection_name or COLLECTIONS.products
        self.reasoner = KGReasonerAgent(self.neo4j)
        self.kg_embedder = KGEmbedderAgent()

    async def _kg_structural_search(
        self,
        query: str,
        customer_context: Dict[str, Any],
        top_k: int,
    ) -> List[Dict[str, Any]]:
        """Run KG reasoning: similar customers → product recs from graph."""
        customer_id = customer_context.get("customer_id")
        if not customer_id:
            return []
        recs = await self.reasoner.product_recommendation_paths(
            customer_id, max_results=top_k
        )
        return recs

    def _embed_query(self, query: str) -> List[float]:
        """Embed query for Qdrant search."""
        result = embed_single(query)
        return as_list(result.vectors)[0] if result.vectors.shape[0] else []

    def _build_customer_filter(self, customer_context: Dict[str, Any]) -> Optional[Any]:
        """Build Qdrant filter from customer context (e.g. region, segment)."""
        from qdrant_client.http import models as rest
        conditions = []
        if customer_context.get("region"):
            conditions.append(
                rest.FieldCondition(key="region", match=rest.MatchValue(value=customer_context["region"]))
            )
        if not conditions:
            return None
        return rest.Filter(must=conditions)

    async def retrieve_hybrid(
        self,
        query: str,
        customer_context: Optional[Dict[str, Any]] = None,
        top_k: int = 20,
    ) -> List[HybridRetrievalResult]:
        """
        KG reasoning → Qdrant vectors → reranking fusion.
        """
        customer_context = customer_context or {}
        kg_results = await self._kg_structural_search(query, customer_context, top_k)

        # Qdrant semantic search
        query_vector = self._embed_query(query)
        q_filter = self._build_customer_filter(customer_context)
        qdrant_results = self.qdrant.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=q_filter,
            limit=top_k * 2,
            with_payload=True,
            with_vectors=False,
        )

        # Build rerank items: KG results as text, then Qdrant hits
        rerank_items: List[RerankItem] = []
        seen_ids: set = set()
        for r in kg_results:
            pid = str(r.get("product_id", ""))
            if pid and pid not in seen_ids:
                seen_ids.add(pid)
                text = f"{r.get('product_name', '')} {r.get('category', '')}".strip() or pid
                rerank_items.append(
                    RerankItem(
                        id=pid,
                        text=text,
                        meta={"payload": r, "source": "kg", "path_length": r.get("path_length")},
                    )
                )
        for p in (qdrant_results or []):
            pid = str(p.id) if hasattr(p, "id") else str(p.get("id", ""))
            if pid not in seen_ids:
                seen_ids.add(pid)
                payload = getattr(p, "payload", None) or p.get("payload", {}) if isinstance(p, dict) else {}
                text = (payload.get("text") or payload.get("product_name") or "").strip() or pid
                rerank_items.append(
                    RerankItem(id=pid, text=text, meta={"payload": payload, "source": "qdrant"})
                )

        if not rerank_items:
            return []

        reranked = rerank(query, rerank_items, top_k=top_k)
        out: List[HybridRetrievalResult] = []
        for r in reranked:
            meta = r.meta or {}
            payload = meta.get("payload", {})
            source = meta.get("source", "hybrid")
            path_len = meta.get("path_length")
            text = next((x.text for x in rerank_items if x.id == r.id), "")
            out.append(
                HybridRetrievalResult(
                    id=r.id,
                    text=text,
                    score=r.score,
                    source=source,
                    payload=payload,
                    kg_path_length=path_len,
                )
            )
        return out
