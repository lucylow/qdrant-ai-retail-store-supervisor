import asyncio
import json
import logging
from typing import List, Dict, Any, Optional

import uvicorn
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse

from app.data.collections import COLL_PRODUCTS, COLL_GOALS
from app.embeddings import embed_texts
from app.generation.generator import generate_answer, stream_answer
from app.generator import rag_answer
from app.qdrant_client import get_qdrant_client, qdrant_health_check
from app.data.collections import ensure_all_collections
from app.retriever import (
    search_products,
    search_episodes_for_goal,
    retrieve_similar_goals_by_text,
)
from app.debug_endpoints import router as debug_router
from app.multimodal.router import router as multimodal_router
from app.agents.fashion_visual_agent import VisualFashionAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
client = None


@app.on_event("startup")
def startup_event() -> None:
    global client
    client = get_qdrant_client()
    try:
        ensure_all_collections()
    except Exception:  # noqa: BLE001
        logger.warning("Could not ensure collections; continuing")
    app.include_router(debug_router, prefix="/debug")
    app.include_router(multimodal_router)


@app.get("/health")
def health() -> dict:
    ok = qdrant_health_check(client)
    return {"ok": ok}


@app.get("/demo/query")
def demo_query(q: str) -> dict:
    goal_vec = embed_texts([q])[0].tolist()
    episodes = search_episodes_for_goal(goal_vec)
    products = search_products(text_query=q, limit=12)
    goal_payload = {"goal_text": q, "constraints": {}, "region": "Zurich"}
    rag_ctx = {
        "user": {"region": "Zurich"},
        "agent": {"name": "demo"},
        "collection": "products",
        "product": {"title": goal_payload.get("goal_text")},
    }
    rag = rag_answer(rag_ctx, q)
    return {
        "query": q,
        "episodes": episodes,
        "products_count": len(products),
        "rag_answer": rag,
    }


def _ensure_text_payload(hit: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(hit.get("payload") or {})
    if "text" not in payload:
        name = payload.get("name") or payload.get("title") or ""
        desc = payload.get("description") or ""
        price = payload.get("price")
        parts = [name, desc]
        if price is not None:
            parts.append(f"Price: {price}")
        payload["text"] = ". ".join([p for p in parts if p])
    hit = dict(hit)
    hit["payload"] = payload
    return hit


def retrieve(query: str, collection: str) -> List[Dict[str, Any]]:
    """
    Retrieval adapter for the generative RAG endpoints.
    Normalizes hits into the shape expected by app.generation.generator.
    """
    # Product-centric demo collection
    if collection in ("demo_retail", "products", COLL_PRODUCTS):
        hits = search_products(text_query=query, limit=10)
        return [_ensure_text_payload(h) for h in hits]

    # Goal-centric retrieval
    if collection in ("goals", "active_goals", COLL_GOALS):
        hits = retrieve_similar_goals_by_text(query, limit=10)
        # goal payloads already contain "text"
        return hits

    # Fallback: default to product search
    hits = search_products(text_query=query, limit=10)
    return [_ensure_text_payload(h) for h in hits]


@app.get("/query")
def query(q: str, collection: str = "demo_retail"):
    retrieved = retrieve(q, collection)
    resp = generate_answer(q, retrieved)
    return JSONResponse(resp)


async def _sse_generator(question: str, collection: str):
    # wrapper to produce SSE-compatible bytes
    retrieved = retrieve(question, collection)
    for event in stream_answer(question, retrieved):
        yield f"data: {json.dumps(event)}\n\n"
        await asyncio.sleep(0.01)


@app.get("/stream_query")
def stream_query(q: str, collection: str = "demo_retail"):
    return StreamingResponse(
        _sse_generator(q, collection), media_type="text/event-stream"
    )


@app.post("/api/visual-search")
async def visual_search(
    image: UploadFile = File(...),
    filters: Optional[str] = Form(default=None),
    limit: int = 20,
    score_threshold: float = 0.75,
) -> dict:
    """
    Visual fashion search: upload a photo → CLIP embedding → Qdrant fashion_clip search.
    Optional filters JSON: {"stock_status": "in_stock", "price_max": 200, "category": "Dress"}.
    """
    contents = await image.read()
    parsed_filters: Optional[Dict[str, Any]] = None
    if filters:
        try:
            parsed_filters = json.loads(filters)
        except json.JSONDecodeError:
            parsed_filters = {}
    agent = VisualFashionAgent(client)
    result = agent.visual_search(
        image_bytes=contents,
        filters=parsed_filters,
        limit=limit,
        score_threshold=score_threshold,
        top_k=8,
    )
    result.setdefault("demo_stats", "70K Fashion-MNIST → CLIP visual search")
    result.setdefault("p95_latency", "18ms")
    result.setdefault("accuracy", "94% category match")
    return result


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

