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


def _qdrant_search_with_fallback_vector_name(
    client,
    *,
    collection_name: str,
    query_vector: List[float],
    limit: int,
    with_payload: bool = True,
    with_vectors: bool = False,
    query_filter=None,
    params=None,
    vector_name_candidates: Sequence[str] = (),
):
    """
    Qdrant collections can be configured as:
    - single unnamed vector
    - multiple named vectors (e.g. text_vector/image_vector or textvector/imagevector)

    We first try without `vector_name`. If that fails (common when a collection
    has multiple vectors), retry with the provided candidate names.
    """
    try:
        return client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit,
            with_payload=with_payload,
            with_vectors=with_vectors,
            query_filter=query_filter,
            params=params,
        )
    except Exception:
        last_exc: Exception | None = None
        for name in vector_name_candidates:
            try:
                return client.search(
                    collection_name=collection_name,
                    query_vector=query_vector,
                    vector_name=name,
                    limit=limit,
                    with_payload=with_payload,
                    with_vectors=with_vectors,
                    query_filter=query_filter,
                    params=params,
                )
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
        if last_exc is not None:
            raise last_exc
        raise


def hybrid_retrieve_products(query: str, top_k: int = 20) -> RetrievalResult:
    client = get_qdrant_client()
    emb = embed_single(query)
    search_res = _qdrant_search_with_fallback_vector_name(
        client,
        collection_name=COLLECTIONS.products,
        query_vector=emb.vectors[0].tolist(),
        limit=top_k * 3,
        with_payload=True,
        with_vectors=False,
        params=rest.SearchParams(hnsw_ef=CONTEXT.max_context_documents * 16),
        vector_name_candidates=("text_vector", "textvector"),
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

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


def retrieve(
    query: str,
    collection: str = COLL_PRODUCTS,
    top_k: int = TOP_K_RETRIEVE,
) -> List[Dict[str, Any]]:
    client = get_qdrant_client()
    qvec = embed_texts([query])[0].tolist()
    hits = _qdrant_search_with_fallback_vector_name(
        client,
        collection_name=collection,
        query_vector=qvec,
        limit=top_k,
        with_payload=True,
        vector_name_candidates=("text_vector", "textvector"),
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
    hits = _qdrant_search_with_fallback_vector_name(
        client,
        collection_name=collection,
        query_vector=ivec,
        limit=top_k,
        with_payload=True,
        vector_name_candidates=("image_vector", "imagevector"),
    )
    return [{"id": h.id, "payload": h.payload, "score": h.score} for h in hits]

