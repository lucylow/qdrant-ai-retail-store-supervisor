"""
Live Amazon-powered multi-agent demo for judges.

"Real UCSD Amazon data -> Multimodal Qdrant agents"

Run: uvicorn agents.amazon_demo:app --port 8000
Demo: curl -X POST "http://localhost:8000/demo/amazon-search" -H "Content-Type: application/json" -d '{"query": "waterproof hiking tents under 200 CHF"}'
"""

from __future__ import annotations

import os
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as qmodels
except ImportError:
    QdrantClient = None
    qmodels = None

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

app = FastAPI(title="Amazon Store Supervisor Demo", version="1.0.0")

# Lazy init
_qdrant_client = None
_text_model = None
_supervisor = None


def get_qdrant():
    global _qdrant_client
    if _qdrant_client is None:
        url = os.getenv("QDRANT_URL", "http://localhost:6333")
        _qdrant_client = QdrantClient(url=url)
    return _qdrant_client


def get_text_model():
    global _text_model
    if _text_model is None and SentenceTransformer is not None:
        _text_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _text_model


class AmazonStoreSupervisor:
    """Multimodal product discovery over amazon_products collection."""

    def __init__(self, qdrant_client, text_model):
        self.qdrant = qdrant_client
        self.text_model = text_model
        self.collection = "amazon_products"
        self.vector_name = "text"

    def multimodal_search(
        self,
        query: str,
        category: str | None = None,
        price_max: float | None = None,
        rating_min: float | None = None,
        stock_status: str | None = "in_stock",
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Text-vector search with optional payload filters."""
        if self.text_model is None:
            return []
        text_vector = self.text_model.encode(query, normalize_embeddings=True).tolist()
        conditions = []
        if category:
            conditions.append(
                qmodels.FieldCondition(key="category", match=qmodels.MatchValue(value=category))
            )
        if price_max is not None:
            conditions.append(
                qmodels.FieldCondition(key="price", range=qmodels.Range(lt=price_max))
            )
        if rating_min is not None:
            conditions.append(
                qmodels.FieldCondition(key="avg_rating", range=qmodels.Range(gte=rating_min))
            )
        if stock_status:
            conditions.append(
                qmodels.FieldCondition(key="stock_status", match=qmodels.MatchValue(value=stock_status))
            )
        query_filter = qmodels.Filter(must=conditions) if conditions else None
        try:
            results = self.qdrant.search(
                collection_name=self.collection,
                query_vector=text_vector,
                vector_name=self.vector_name,
                query_filter=query_filter,
                limit=limit,
            )
        except Exception:
            results = []
        return [
            {
                "asin": r.payload.get("asin"),
                "title": r.payload.get("title"),
                "price": r.payload.get("price"),
                "rating": r.payload.get("avg_rating"),
                "velocity": r.payload.get("review_velocity"),
                "similarity": r.score,
            }
            for r in results
        ]

    def shopper_agent(
        self,
        query: str,
        price_max: float = 200,
        category: str = "Sports",
        rating_min: float | None = 4.0,
    ) -> Dict[str, Any]:
        """Agent A: Multimodal product discovery with defaults for demo."""
        products = self.multimodal_search(
            query=query,
            category=category,
            price_max=price_max,
            rating_min=rating_min,
            limit=20,
        )
        ratings = [p["rating"] for p in products if p.get("rating") is not None]
        return {
            "query": query,
            "matching_products": len(products),
            "avg_rating": float(sum(ratings) / len(ratings)) if ratings else 0,
            "top_products": products[:5],
        }


def get_supervisor():
    global _supervisor
    if _supervisor is None:
        client = get_qdrant()
        model = get_text_model()
        if model is None:
            raise RuntimeError("sentence-transformers required for amazon_demo")
        _supervisor = AmazonStoreSupervisor(client, model)
    return _supervisor


class SearchRequest(BaseModel):
    query: str
    price_max: float | None = 200
    category: str | None = "Sports"
    rating_min: float | None = 4.0


@app.get("/health")
def health() -> dict:
    try:
        get_qdrant().get_collections()
        return {"ok": True}
    except Exception:
        return {"ok": False}


@app.post("/shopper/search")
def shopper_search(body: SearchRequest) -> dict:
    """Shopper agent: extract filters from query + hybrid semantic search."""
    import asyncio
    from app.services.amazon_review_filter_service import AmazonFilterService, AmazonReviewFilters

    try:
        supervisor = get_supervisor()
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
    openai_key = os.getenv("OPENAI_API_KEY")
    client = None
    if openai_key:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=openai_key)
        except ImportError:
            pass
    filter_service = AmazonFilterService(client)
    try:
        semantic_query, filters = asyncio.run(filter_service.extract_filters(body.query))
    except Exception:
        semantic_query, filters = body.query, AmazonReviewFilters()
    category = filters.category or body.category
    price_max = filters.price_max if filters.price_max is not None else body.price_max
    rating_min = filters.rating_min if filters.rating_min is not None else body.rating_min
    products = supervisor.multimodal_search(
        query=semantic_query,
        category=category,
        price_max=price_max,
        rating_min=rating_min,
        limit=20,
    )
    try:
        filters_applied = filters.model_dump(exclude_unset=True)
    except AttributeError:
        filters_applied = filters.dict(exclude_none=True)
    return {
        "query": body.query,
        "semantic_query": semantic_query,
        "filters_applied": filters_applied,
        "total_matches": len(products),
        "products": products[:10],
    }


@app.post("/demo/amazon-search")
def demo_search(body: SearchRequest) -> dict:
    """Judge demo: semantic search over Amazon products with filters."""
    try:
        supervisor = get_supervisor()
        results = supervisor.shopper_agent(
            query=body.query,
            price_max=body.price_max or 200,
            category=body.category or "Sports",
            rating_min=body.rating_min,
        )
        return {
            **results,
            "demo_note": "Powered by UCSD Amazon reviews + metadata",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class FilterDemoRequest(BaseModel):
    query: str


@app.post("/demo/amazon-filtering")
def demo_amazon_filtering(body: FilterDemoRequest) -> dict:
    """60s judge demo: show extracted filters (requires filter service)."""
    import asyncio
    from app.services.amazon_review_filter_service import AmazonFilterService

    query = body.query
    openai_key = os.getenv("OPENAI_API_KEY")
    client = None
    if openai_key:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=openai_key)
        except ImportError:
            pass
    service = AmazonFilterService(client)
    try:
        semantic, filters = asyncio.run(service.extract_filters(query))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    qdrant_filter = service.build_qdrant_filter(filters)
    try:
        filters_dict = filters.model_dump(exclude_unset=True)
    except AttributeError:
        filters_dict = filters.dict(exclude_none=True)
    return {
        "user_query": query,
        "semantic_query": semantic,
        "extracted_filters": filters_dict,
        "filter_conditions": len(qdrant_filter.must) if qdrant_filter and qdrant_filter.must else 0,
        "judge_note": "Amazon reviews filtered by category + rating -> Qdrant hybrid search",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
