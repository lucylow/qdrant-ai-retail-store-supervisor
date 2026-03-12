from __future__ import annotations

from dataclasses import dataclass
from typing import List, Mapping, Sequence

from qdrant_client.http import models as rest

from app.config import COLLECTIONS, CONTEXT
from app.context_manager import ContextChunk, ManagedContext, build_context
from app.embeddings import as_list, embed_single
from app.qdrant_client import get_qdrant_client
from app.reranker import RerankItem, rerank


@dataclass(frozen=True)
class RetrievedDoc:
    id: str
    text: str
    score: float
    payload: Mapping[str, object]


@dataclass(frozen=True)
class RetrievalResult:
    query: str
    docs: list[RetrievedDoc]
    context: ManagedContext


def _to_retrieved(points: Sequence[rest.ScoredPoint]) -> list[RetrievedDoc]:
    docs: list[RetrievedDoc] = []
    for p in points:
        text = (p.payload or {}).get("text", "")  # type: ignore[assignment]
        docs.append(
            RetrievedDoc(
                id=str(p.id),
                text=str(text),
                score=float(p.score or 0.0),
                payload=p.payload or {},
            )
        )
    return docs


def hybrid_retrieve_products(query: str, top_k: int = 20) -> RetrievalResult:
    client = get_qdrant_client()
    emb = embed_single(query)
    search_res = client.search(
        collection_name=COLLECTIONS.products,
        query_vector=emb.vectors[0].tolist(),
        limit=top_k * 3,
        with_payload=True,
        with_vectors=False,
        params=rest.SearchParams(
            hnsw_ef=CONTEXT.max_context_documents * 16,
        ),
    )
    initial_docs = _to_retrieved(search_res)
    rerank_items = [
        RerankItem(
            id=d.id,
            text=d.text,
            meta={"payload": d.payload, "score": d.score},
        )
        for d in initial_docs
    ]
    reranked = rerank(query, rerank_items, top_k=top_k)
    top_docs: list[RetrievedDoc] = []
    for r in reranked:
        payload = r.meta.get("payload", {})  # type: ignore[assignment]
        top_docs.append(
            RetrievedDoc(
                id=r.id,
                text=next(
                    (d.text for d in initial_docs if d.id == r.id),
                    "",
                ),
                score=r.score,
                payload=payload if isinstance(payload, dict) else {},
            )
        )
    chunks = [
        ContextChunk(
            id=d.id,
            text=d.text,
            score=d.score,
            source=str(d.payload.get("source", "products")),
        )
        for d in top_docs
    ]
    ctx = build_context(query, chunks)
    return RetrievalResult(query=query, docs=top_docs, context=ctx)


__all__ = ["RetrievedDoc", "RetrievalResult", "hybrid_retrieve_products"]

from typing import List, Dict, Any
from app.qdrant_client import get_qdrant_client
from app.embeddings import embed_texts, embed_image
from app.config import TOP_K_RETRIEVE, COLL_PRODUCTS, ENABLE_MULTIMODAL
import logging

logger = logging.getLogger(__name__)


def retrieve(
    query: str,
    collection: str = COLL_PRODUCTS,
    top_k: int = TOP_K_RETRIEVE,
) -> List[Dict[str, Any]]:
    client = get_qdrant_client()
    qvec = embed_texts([query])[0].tolist()
    hits = client.search(
        collection_name=collection,
        query_vector=qvec,
        limit=top_k,
        with_payload=True,
    )
    results = [{"id": h.id, "payload": h.payload, "score": h.score} for h in hits]
    return results


def retrieve_by_image(
    image_path: str,
    collection: str = COLL_PRODUCTS,
    top_k: int = 10,
) -> List[Dict[str, Any]]:
    if not ENABLE_MULTIMODAL:
        logger.info("Multimodal retrieval disabled")
        return []
    client = get_qdrant_client()
    ivec = embed_image(image_path).tolist()
    hits = client.search(
        collection_name=collection,
        query_vector=ivec,
        vector_name="image_vector",
        limit=top_k,
        with_payload=True,
    )
    return [{"id": h.id, "payload": h.payload, "score": h.score} for h in hits]

