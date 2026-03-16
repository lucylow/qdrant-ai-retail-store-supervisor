"""
KG embeddings: triple (head, relation, tail) text encoding for hybrid search.
GraphSAGE-style aggregation can be added via optional dependency.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np

from app.embeddings import embed_texts, as_list
from app.config import MODELS


def _triple_text(record: Dict[str, Any], head_key: str = "head", rel_key: str = "rel", tail_key: str = "tail") -> str:
    """Format a KG triple as a single string for embedding."""
    head = record.get(head_key) or record.get("product_id") or record.get("customer_id") or ""
    rel = record.get(rel_key) or record.get("relationship_type") or ""
    tail = record.get(tail_key) or record.get("product_name") or record.get("name") or ""
    if isinstance(head, dict):
        head = head.get("id") or head.get("name") or str(head)
    if isinstance(tail, dict):
        tail = tail.get("id") or tail.get("name") or str(tail)
    return f"{head} {rel} {tail}".strip()


def embed_kg_triples(
    records: List[Dict[str, Any]],
    head_key: str = "head",
    rel_key: str = "rel",
    tail_key: str = "tail",
    batch_size: int = 32,
) -> np.ndarray:
    """
    Embed KG triples as text for vector search.
    Each record is turned into "head relation tail" and embedded.
    """
    if not records:
        return np.zeros((0, 384), dtype=np.float32)  # default mpnet dimension
    texts = [_triple_text(r, head_key, rel_key, tail_key) for r in records]
    result = embed_texts(texts, batch_size=batch_size)
    return result.vectors


def embed_kg_results(records: List[Dict[str, Any]]) -> List[List[float]]:
    """
    Embed KG query results (e.g. product_id, product_name, category) for reranking.
    Uses concatenated key fields as text.
    """
    if not records:
        return []
    texts = []
    for r in records:
        parts = [
            str(r.get("product_id", r.get("customer_id", ""))),
            str(r.get("product_name", r.get("name", ""))),
            str(r.get("category", r.get("brand", ""))),
        ]
        texts.append(" ".join(p for p in parts if p))
    result = embed_texts(texts, batch_size=32)
    return as_list(result.vectors)


def embed_kg_subgraph_summary(nodes: List[Dict], relationships: List[Dict]) -> List[float]:
    """
    Create one embedding summarizing a subgraph (e.g. for hybrid retrieval).
    Concatenates node labels/ids and relationship types.
    """
    parts = []
    for n in nodes[:50]:  # cap for token limit
        labels = n.get("labels", n.get("properties", {}).get("labels", []))
        pid = n.get("properties", {}).get("id", n.get("id", ""))
        parts.append(f"{labels} {pid}")
    for r in relationships[:50]:
        rtype = r.get("type", r.get("properties", {}).get("type", ""))
        parts.append(rtype)
    text = " ".join(str(p) for p in parts)
    result = embed_texts([text], batch_size=1)
    return as_list(result.vectors)[0] if result.vectors.shape[0] else []


__all__ = ["embed_kg_triples", "embed_kg_results", "embed_kg_subgraph_summary"]
