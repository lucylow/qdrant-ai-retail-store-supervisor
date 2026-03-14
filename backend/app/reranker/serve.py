from __future__ import annotations

from functools import lru_cache
from typing import Dict, List

import asyncio

from fastapi import FastAPI
from pydantic import BaseModel

from app.reranker.cross_encoder import ProductionReranker


class RerankRequest(BaseModel):
    query: str
    passages: List[str]
    top_k: int = 10


class RerankResponse(BaseModel):
    indices: List[int]
    scores: List[float]


@lru_cache(maxsize=1)
def _get_reranker() -> ProductionReranker:
    return ProductionReranker()


app = FastAPI(title="Qdrant Cross‑Encoder Reranker")


@app.post("/rerank", response_model=RerankResponse)
async def rerank(req: RerankRequest) -> RerankResponse:
    reranker = _get_reranker()
    loop = asyncio.get_event_loop()
    ranked = await loop.run_in_executor(
        None, lambda: reranker.rerank(req.query, req.passages, req.top_k)
    )
    indices = [idx for idx, _ in ranked]
    scores = [score for _, score in ranked]
    return RerankResponse(indices=indices, scores=scores)


__all__ = ["app"]

