"""
Download and ingest Qdrant HuggingFace datasets into Qdrant collections.

Supports datasets from https://huggingface.co/Qdrant/datasets including:
  - BM25/BM42 sparse benchmarks
  - Dense embedding benchmarks
  - Retail product corpora (synthetic mapping)

Usage:
    from app.datasets.qdrant_hf_loader import load_hf_dataset, ingest_to_qdrant

    df = load_hf_dataset("Qdrant/bm42-benchmarks", split="test")
    ingest_to_qdrant(df, collection="hf_bm42_benchmark", text_field="text")
"""

from __future__ import annotations

import hashlib
import logging
import time
from typing import Any, Dict, List, Optional, Sequence

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Dataset catalog — curated Qdrant HF datasets for retail benchmarking
# ---------------------------------------------------------------------------

QDRANT_HF_DATASETS: Dict[str, Dict[str, Any]] = {
    "bm42_bench": {
        "repo_id": "Qdrant/bm42-benchmarks",
        "description": "BM42 sparse retrieval benchmark — good for evaluating hybrid sparse+dense vs pure dense on product descriptions.",
        "text_field": "text",
        "query_field": "query",
        "label_field": "label",
        "split": "test",
        "retail_mapping": "Map 'text' → product descriptions, 'query' → search intents.",
    },
    "minicoil_bench": {
        "repo_id": "Qdrant/minicoil-demo",
        "description": "MiniCOIL late-interaction demo data — useful for evaluating token-level matching on SKU descriptions.",
        "text_field": "text",
        "split": "train",
        "retail_mapping": "Treat as product catalog entries for SKU search quality evaluation.",
    },
    "sparse_vectors_demo": {
        "repo_id": "Qdrant/sparse-vectors-demo",
        "description": "Sparse vector demonstration dataset — benchmark BM25 vs learned sparse on retail queries.",
        "text_field": "text",
        "split": "train",
        "retail_mapping": "Use as synthetic product corpus for sparse retrieval quality.",
    },
}


def list_available_datasets() -> List[Dict[str, str]]:
    """Return catalog of curated Qdrant HF datasets."""
    return [
        {"key": k, "repo_id": v["repo_id"], "description": v["description"]}
        for k, v in QDRANT_HF_DATASETS.items()
    ]


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_hf_dataset(
    repo_id: str,
    split: str = "test",
    max_rows: Optional[int] = None,
    streaming: bool = False,
) -> List[Dict[str, Any]]:
    """
    Download a HuggingFace dataset and return as list of dicts.

    Requires: pip install datasets
    """
    try:
        from datasets import load_dataset as hf_load
    except ImportError:
        logger.error("Install 'datasets' package: pip install datasets")
        return []

    logger.info("Loading HF dataset %s (split=%s, streaming=%s)", repo_id, split, streaming)
    t0 = time.perf_counter()

    try:
        ds = hf_load(repo_id, split=split, streaming=streaming)
        if streaming:
            rows = []
            for i, row in enumerate(ds):
                rows.append(dict(row))
                if max_rows and i + 1 >= max_rows:
                    break
            data = rows
        else:
            if max_rows:
                ds = ds.select(range(min(max_rows, len(ds))))
            data = [dict(row) for row in ds]
    except Exception as e:
        logger.error("Failed to load dataset %s: %s", repo_id, e)
        return []

    elapsed = time.perf_counter() - t0
    logger.info("Loaded %d rows from %s in %.1fs", len(data), repo_id, elapsed)
    return data


def load_catalog_dataset(
    key: str,
    max_rows: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Load a dataset from the curated catalog by key."""
    meta = QDRANT_HF_DATASETS.get(key)
    if not meta:
        raise KeyError(f"Unknown dataset key: {key}. Available: {list(QDRANT_HF_DATASETS.keys())}")
    return load_hf_dataset(
        repo_id=meta["repo_id"],
        split=meta.get("split", "test"),
        max_rows=max_rows,
    )


# ---------------------------------------------------------------------------
# Embedding + ingestion
# ---------------------------------------------------------------------------

def _compute_id(text: str) -> str:
    """Deterministic point ID from text content."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()[:16]


def embed_rows(
    rows: List[Dict[str, Any]],
    text_field: str = "text",
    embedding_fn: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    """
    Add 'vector' key to each row by embedding text_field.

    If no embedding_fn is provided, uses the repo's default embedder.
    """
    if embedding_fn is None:
        try:
            from app.embeddings import embed_single
            embedding_fn = lambda t: embed_single(t).vectors[0].tolist()
        except ImportError:
            logger.error("No embedding function available")
            return rows

    enriched = []
    for row in rows:
        text = str(row.get(text_field, ""))
        if not text.strip():
            continue
        try:
            vec = embedding_fn(text)
            enriched.append({**row, "vector": vec, "_point_id": _compute_id(text)})
        except Exception as e:
            logger.warning("Embedding failed for row: %s", e)
    return enriched


def ingest_to_qdrant(
    rows: List[Dict[str, Any]],
    collection: str,
    text_field: str = "text",
    vector_size: int = 384,
    batch_size: int = 64,
    recreate: bool = False,
    embedding_fn: Optional[Any] = None,
) -> int:
    """
    Embed rows and upsert into a Qdrant collection.

    Returns number of points upserted.
    """
    from qdrant_client.http import models as rest

    # Embed if not already
    if rows and "vector" not in rows[0]:
        rows = embed_rows(rows, text_field=text_field, embedding_fn=embedding_fn)

    if not rows:
        logger.warning("No rows to ingest into %s", collection)
        return 0

    # Auto-detect vector size from first row
    if rows[0].get("vector"):
        vector_size = len(rows[0]["vector"])

    try:
        from app.qdrant_client import get_qdrant_client
        client = get_qdrant_client()
    except Exception as e:
        logger.error("Cannot get Qdrant client: %s", e)
        return 0

    # Create collection if needed
    if recreate:
        try:
            client.delete_collection(collection)
        except Exception:
            pass

    try:
        client.get_collection(collection)
    except Exception:
        client.create_collection(
            collection_name=collection,
            vectors_config=rest.VectorParams(size=vector_size, distance=rest.Distance.COSINE),
        )
        logger.info("Created collection %s (dim=%d)", collection, vector_size)

    # Batch upsert
    total = 0
    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        points = []
        for idx, row in enumerate(batch):
            vec = row.get("vector", [])
            payload = {k: v for k, v in row.items() if k not in ("vector", "_point_id")}
            point_id = row.get("_point_id", _compute_id(str(i + idx)))
            # Qdrant needs int or UUID ids
            int_id = int(point_id, 16) % (2**63)
            points.append(rest.PointStruct(id=int_id, vector=vec, payload=payload))
        try:
            client.upsert(collection_name=collection, points=points)
            total += len(points)
        except Exception as e:
            logger.error("Upsert batch failed: %s", e)

    logger.info("Ingested %d points into %s", total, collection)
    return total


__all__ = [
    "QDRANT_HF_DATASETS",
    "list_available_datasets",
    "load_hf_dataset",
    "load_catalog_dataset",
    "embed_rows",
    "ingest_to_qdrant",
]
