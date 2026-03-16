"""
Shopper Agent: query → semantic search → Discovery recs.

Flow: "tents" → semantic search over retailrocket_items → Discovery API
recommendations from session + semantic matches (e.g. co-carted sleeping bags).
"""

from __future__ import annotations

from typing import Any

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as qmodels
except ImportError:
    QdrantClient = None
    qmodels = None

try:
    from app.services.retailrocket_discovery import RetailRocketDiscovery
except ImportError:
    RetailRocketDiscovery = None

COLL_ITEMS = "retailrocket_items"
EMBEDDING_DIM = 384


class DiscoveryShopperAgent:
    """Semantic search + Discovery API for shopper workflow."""

    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        discovery_service: RetailRocketDiscovery | None = None,
    ):
        self.qdrant = QdrantClient(url=qdrant_url) if QdrantClient else None
        self.model = SentenceTransformer("all-MiniLM-L6-v2") if SentenceTransformer else None
        self.discovery_service = discovery_service or (
            RetailRocketDiscovery(qdrant_url=qdrant_url) if RetailRocketDiscovery else None
        )

    def _embed(self, text: str) -> list[float]:
        if self.model is None:
            return [0.0] * EMBEDDING_DIM
        return self.model.encode(text, normalize_embeddings=True).tolist()

    async def semantic_search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """Semantic search over retailrocket_items."""
        if not self.qdrant or not qmodels:
            return []
        vector = self._embed(query)
        try:
            results = self.qdrant.search(
                collection_name=COLL_ITEMS,
                query_vector=vector,
                limit=limit,
                with_payload=True,
            )
        except Exception:
            return []
        return [
            {"itemid": (r.payload or {}).get("itemid"), "score": getattr(r, "score", 0), **(r.payload or {})}
            for r in results
        ]

    async def process_query(
        self,
        query: str,
        session_items: list[int],
        limit: int = 10,
    ) -> dict[str, Any]:
        """Full workflow: semantic search + Discovery recs, then fuse."""
        semantic_results = await self.semantic_search(query, limit=5)
        semantic_ids = [r.get("itemid") for r in semantic_results if r.get("itemid") is not None]
        combined_ids = list(dict.fromkeys(session_items + semantic_ids))[:10]
        discovery_recs = []
        if self.discovery_service and combined_ids:
            discovery_recs = self.discovery_service.discover_recommendations(
                combined_ids, context="co_carted", limit=limit
            )
        unified = self._fuse_semantic_discovery(semantic_results, discovery_recs)
        return {
            "semantic_matches": len(semantic_results),
            "discovery_recs": len(discovery_recs),
            "retailrocket_lift": f"{len(discovery_recs) / max(1, len(semantic_results)):.0%}",
            "top_recommendations": unified[:limit],
        }

    def _fuse_semantic_discovery(
        self,
        semantic: list[dict[str, Any]],
        discovery: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Simple RRF-style fusion: rank by combined score."""
        scores: dict[int, float] = {}
        for i, r in enumerate(semantic):
            iid = r.get("itemid")
            if iid is not None:
                scores[iid] = scores.get(iid, 0) + 1.0 / (i + 60)
        for i, r in enumerate(discovery):
            iid = r.get("itemid")
            if iid is not None:
                scores[iid] = scores.get(iid, 0) + (r.get("score") or 0) * 0.5 + 1.0 / (i + 60)
        order = sorted(scores.items(), key=lambda x: -x[1])
        seen = set()
        out = []
        for iid, _ in order:
            if iid in seen:
                continue
            seen.add(iid)
            rec = next((d for d in discovery if d.get("itemid") == iid), None) or next(
                (s for s in semantic if s.get("itemid") == iid), None
            )
            if rec:
                out.append(rec)
        return out
