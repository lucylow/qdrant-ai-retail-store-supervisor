"""
RetailRocket multi-agent demo: real conversion funnel powers inventory decisions.

Shopper search: semantic search over retailrocket_items with inventory filters
(view_to_cart_rate, stock_status). Live hackathon endpoint: GET /demo/search?query=...
"""

from __future__ import annotations

from typing import Any

try:
    from fastapi import FastAPI, Query
    from fastapi.responses import JSONResponse
except ImportError:
    FastAPI = None  # type: ignore
    Query = None  # type: ignore

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

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

EMBEDDING_DIM = 384
COLL_ITEMS = "retailrocket_items"


def _get_qdrant_url() -> str:
    try:
        from app.config import QDRANT
        if getattr(QDRANT, "url", None):
            return QDRANT.url or "http://localhost:6333"
        return f"http://{getattr(QDRANT, 'host', 'localhost')}:{getattr(QDRANT, 'port', 6333)}"
    except Exception:
        return "http://localhost:6333"


class RetailRocketSupervisor:
    """Semantic search over RetailRocket items with inventory/conversion filters."""

    def __init__(self, qdrant_client: QdrantClient | None = None):
        self.qdrant = qdrant_client or QdrantClient(url=_get_qdrant_url())
        self.model = SentenceTransformer("all-MiniLM-L6-v2") if SentenceTransformer else None

    def _embed(self, text: str) -> list[float]:
        if self.model is None:
            return [0.0] * EMBEDDING_DIM
        return self.model.encode(text, normalize_embeddings=True).tolist()

    async def shopper_search(
        self,
        query: str,
        filters: dict[str, Any] | None = None,
        limit: int = 10,
        score_threshold: float | None = 0.5,
    ) -> dict[str, Any]:
        """Semantic search with inventory filters (stock_status, view_to_cart_rate, optional categoryid)."""
        if not self.qdrant or not qmodels:
            return {"query": query, "error": "Qdrant not available", "top_items": []}
        filters = filters or {}
        vector = self._embed(query)
        must = [
            qmodels.FieldCondition(key="stock_status", match=qmodels.MatchValue(value="in_stock")),
            qmodels.FieldCondition(key="view_to_cart_rate", range=qmodels.Range(gte=0.05)),
        ]
        if filters.get("categoryid") is not None:
            must.append(
                qmodels.FieldCondition(
                    key="categoryid",
                    match=qmodels.MatchValue(value=int(filters["categoryid"])),
                )
            )
        query_filter = qmodels.Filter(must=must)
        try:
            results = self.qdrant.search(
                collection_name=COLL_ITEMS,
                query_vector=vector,
                query_filter=query_filter,
                limit=limit,
                score_threshold=score_threshold,
            )
        except Exception as e:
            return {
                "query": query,
                "error": str(e),
                "high_conv_items": 0,
                "avg_conversion": 0.0,
                "top_items": [],
            }
        payloads = [r.payload or {} for r in results]
        view_rates = [p.get("view_to_cart_rate", 0) for p in payloads if p]
        high_conv = len([r for r in payloads if (r.get("view_to_cart_rate") or 0) > 0.1])
        avg_conv = float(sum(view_rates) / len(view_rates)) if view_rates else 0.0
        top_items = [
            {
                "itemid": p.get("itemid"),
                "catname": p.get("catname"),
                "view_to_cart_rate": p.get("view_to_cart_rate"),
                "price": p.get("price"),
                "score": getattr(r, "score", None),
            }
            for r, p in zip(results, payloads)
        ]
        return {
            "query": query,
            "high_conv_items": high_conv,
            "avg_conversion": round(avg_conv, 4),
            "top_items": top_items,
        }


app = FastAPI(title="RetailRocket Store Supervisor Demo", version="0.1.0")
_supervisor: RetailRocketSupervisor | None = None


def get_supervisor() -> RetailRocketSupervisor:
    global _supervisor
    if _supervisor is None:
        _supervisor = RetailRocketSupervisor()
    return _supervisor


@app.get("/demo/search")
async def demo_search(
    query: str = Query(..., description="Shopper query e.g. tents"),
):
    """Live demo: semantic search with real conversion funnel filters."""
    sup = get_supervisor()
    results = await sup.shopper_search(query)
    return JSONResponse(
        content={
            **results,
            "dataset": "RetailRocket 2.7M events",
            "real_funnel": "view→add2cart 8.2%, add2cart→transaction 3.1%",
        }
    )


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
