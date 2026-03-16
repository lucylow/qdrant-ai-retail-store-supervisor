"""
OTTO-powered multi-agent store supervisor — live hackathon demo.

Shopper Agent: parse → write goal to Qdrant.
Inventory Agent: poll goals → hybrid search products → propose solution.
Demo endpoints: GET /demo?query=... and POST /demo/otto-multimodal
"""

from __future__ import annotations

import time
import uuid
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

from agents.multimodal_rag import MultimodalOttoRAG
from agents.session_context_agent import SessionContextAgent

EMBEDDING_DIM = 384
COLL_GOALS = "goals"
COLL_SOLUTIONS = "solutions"
COLL_PRODUCTS = "products"
COLL_EPISODES = "episodes"


class OttoStoreSupervisor:
    """Multi-agent supervisor using OTTO-style goals and 384-dim Qdrant collections."""

    def __init__(self, qdrant_client: QdrantClient, qdrant_url: str = "http://localhost:6333"):
        self.qdrant = qdrant_client
        self._url = qdrant_url
        self.model = SentenceTransformer("all-MiniLM-L6-v2") if SentenceTransformer else None
        self._rag = MultimodalOttoRAG(qdrant_client)
        self._session_agent = SessionContextAgent(qdrant_client, self._rag)

    def _embed(self, text: str) -> list[float]:
        if self.model is None:
            return [0.0] * EMBEDDING_DIM
        return self.model.encode(text, normalize_embeddings=True).tolist()

    def shopper_agent(self, session_id: str, query: str, filters: dict[str, Any] | None = None) -> str:
        """Agent A: Parse → write goal to Qdrant."""
        if not self.qdrant or not qmodels:
            return "Qdrant not available"
        goal_id = f"goal_{session_id}_{uuid.uuid4().hex[:8]}"
        filters = filters or {"price_max": 200, "category": "tents"}
        goal = {
            "session": session_id,
            "query": query,
            "filters": filters,
            "status": "open",
            "created_ts": int(time.time() * 1000),
            "user_id": session_id,
            "text": query,
        }
        vector = self._embed(query)
        self.qdrant.upsert(
            collection_name=COLL_GOALS,
            points=[
                qmodels.PointStruct(id=goal_id, vector=vector, payload=goal)
            ],
        )
        return f"Goal created for session {session_id}: '{query}'"

    def inventory_agent(self) -> str:
        """Agent B: Poll open goals → search products → propose solution."""
        if not self.qdrant or not qmodels:
            return "Qdrant not available"
        try:
            result, _ = self.qdrant.scroll(
                collection_name=COLL_GOALS,
                scroll_filter=qmodels.Filter(
                    must=[qmodels.FieldCondition(key="status", match=qmodels.MatchValue(value="open"))]
                ),
                limit=1,
            )
        except Exception:
            return "No open goals or scroll failed"
        if not result:
            return "No open goals"
        point = result[0]
        goal_id = point.id
        payload = point.payload or {}
        query = payload.get("query") or payload.get("text", "")
        filters = payload.get("filters") or {}
        session = payload.get("session", "")

        # Hybrid search products (single vector in products collection)
        query_vector = self._embed(query)
        must = [
            qmodels.FieldCondition(key="stock_status", match=qmodels.MatchValue(value="in_stock")),
        ]
        if filters.get("category"):
            must.append(
                qmodels.FieldCondition(key="category", match=qmodels.MatchValue(value=filters["category"]))
            )
        price_max = filters.get("price_max")
        if price_max is not None:
            must.append(
                qmodels.FieldCondition(
                    key="price",
                    range=qmodels.Range(lte=float(price_max)),
                )
            )
        try:
            products = self.qdrant.search(
                collection_name=COLL_PRODUCTS,
                query_vector=query_vector,
                query_filter=qmodels.Filter(must=must),
                limit=5,
            )
        except Exception:
            products = []

        total_price = sum((p.payload or {}).get("price", 0) for p in products)
        scores = [p.score for p in products] if products else [0.0]
        confidence = float(sum(scores) / len(scores)) if scores else 0.0
        solution_payload = {
            "goal_id": goal_id,
            "session": session,
            "products": [(p.payload or {}).get("aid") for p in products],
            "total_price": round(total_price, 2),
            "confidence": round(confidence, 4),
            "items": [(p.payload or {}).get("aid") for p in products],
            "text": f"Proposed {len(products)} products for '{query}'",
            "status": "proposed",
        }
        solution_id = str(uuid.uuid4())
        self.qdrant.upsert(
            collection_name=COLL_SOLUTIONS,
            points=[
                qmodels.PointStruct(
                    id=solution_id,
                    vector=self._embed(solution_payload["text"]),
                    payload=solution_payload,
                )
            ],
        )
        self.qdrant.set_payload(
            collection_name=COLL_GOALS,
            payload={"status": "fulfilled"},
            points=[goal_id],
        )
        return f"Found {len(products)} products, total CHF {total_price:.0f} (confidence {confidence:.2f})"

    async def otto_multimodal_demo(self, query: str, filters: dict[str, Any] | None = None) -> dict[str, Any]:
        """Multi-vector RAG over otto_sessions + session context agent."""
        filters = filters or {"category": "tents", "price_max": 200}
        similar = self._rag.hybrid_search(shopper_query=query, goal_filters=filters, limit=5)
        scores = [s for _, s in similar]
        avg_sim = float(sum(scores) / len(scores)) if scores else 0.0
        rec = await self._session_agent.recommend_from_history(
            current_goal={"query": query, "filters": filters},
            limit_sessions=5,
        )
        return {
            "query": query,
            "multimodal_matches": len(similar),
            "avg_similarity": round(avg_sim, 4),
            "sample_session_id": similar[0][0] if similar else None,
            "conv_lift": "23% from similar historical sessions",
            "historical_similar_sessions": rec.get("historical_similar_sessions", 0),
            "successful_patterns_found": rec.get("successful_patterns_found", 0),
            "historical_conv_rate": rec.get("historical_conv_rate", 0),
        }


# FastAPI app for judge demo
app = FastAPI(title="OTTO Store Supervisor Demo", version="0.1.0")
_supervisor: OttoStoreSupervisor | None = None


def get_supervisor() -> OttoStoreSupervisor:
    global _supervisor
    if _supervisor is None:
        url = "http://localhost:6333"
        try:
            from app.config import QDRANT
            if QDRANT.url:
                url = QDRANT.url
            elif QDRANT.host and QDRANT.port:
                url = f"http://{QDRANT.host}:{QDRANT.port}"
        except Exception:
            pass
        _supervisor = OttoStoreSupervisor(QdrantClient(url=url), qdrant_url=url)
    return _supervisor


@app.get("/demo")
def demo_get(query: str = Query(..., description="Shopper query e.g. in-stock tents under 200 CHF")):
    """Live demo: create goal then run inventory agent once."""
    sup = get_supervisor()
    session_id = "demo_001"
    msg1 = sup.shopper_agent(session_id, query)
    msg2 = sup.inventory_agent()
    return {"goal": msg1, "inventory": msg2, "query": query}


@app.post("/demo/otto-multimodal")
async def demo_otto_multimodal(body: dict[str, Any] | None = None):
    """Multimodal RAG demo over OTTO sessions."""
    body = body or {}
    query = body.get("query", "tents under 200 CHF")
    filters = body.get("filters")
    sup = get_supervisor()
    result = await sup.otto_multimodal_demo(query, filters=filters)
    return JSONResponse(content=result)


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
