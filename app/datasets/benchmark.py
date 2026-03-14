"""
Benchmarking harness for Qdrant retrieval quality.

Compares BM25-only, Dense-only, and Hybrid (sparse+dense) retrieval
using Qdrant HF datasets as evaluation corpora.

Usage:
    from app.datasets.benchmark import BenchmarkHarness

    harness = BenchmarkHarness(collection="hf_bm42_benchmark")
    results = harness.run(queries_with_labels, k_values=[1, 5, 10])
    harness.print_report(results)
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    query: str
    retrieved_ids: List[str]
    relevant_ids: List[str]
    scores: List[float]
    latency_ms: float


@dataclass
class BenchmarkMetrics:
    strategy: str  # "dense" | "sparse" | "hybrid"
    recall_at_k: Dict[int, float] = field(default_factory=dict)
    ndcg_at_k: Dict[int, float] = field(default_factory=dict)
    mrr: float = 0.0
    avg_latency_ms: float = 0.0
    num_queries: int = 0


@dataclass
class BenchmarkReport:
    collection: str
    strategies: List[BenchmarkMetrics]
    timestamp: float = 0.0


def _recall_at_k(retrieved: List[str], relevant: List[str], k: int) -> float:
    if not relevant:
        return 0.0
    top_k = set(retrieved[:k])
    return len(top_k & set(relevant)) / len(relevant)


def _dcg(scores: List[float], k: int) -> float:
    import math
    dcg = 0.0
    for i, s in enumerate(scores[:k]):
        dcg += s / math.log2(i + 2)
    return dcg


def _ndcg_at_k(retrieved: List[str], relevant: List[str], k: int) -> float:
    # Binary relevance
    rel_set = set(relevant)
    gains = [1.0 if rid in rel_set else 0.0 for rid in retrieved[:k]]
    ideal = sorted(gains, reverse=True)
    dcg = _dcg(gains, k)
    idcg = _dcg(ideal, k)
    return dcg / idcg if idcg > 0 else 0.0


def _mrr(retrieved: List[str], relevant: List[str]) -> float:
    rel_set = set(relevant)
    for i, rid in enumerate(retrieved):
        if rid in rel_set:
            return 1.0 / (i + 1)
    return 0.0


class BenchmarkHarness:
    """
    Run retrieval benchmarks against a Qdrant collection.

    Supports three strategies:
      - dense: standard vector search
      - sparse: BM25/BM42 keyword search (requires sparse vectors)
      - hybrid: combined sparse+dense with RRF fusion
    """

    def __init__(
        self,
        collection: str = "hf_bm42_benchmark",
        strategies: Optional[List[str]] = None,
    ):
        self.collection = collection
        self.strategies = strategies or ["dense", "sparse", "hybrid"]

    def run(
        self,
        queries: List[Dict[str, Any]],
        k_values: List[int] = [1, 5, 10],
        embedding_fn: Optional[Any] = None,
    ) -> BenchmarkReport:
        """
        Run benchmarks.

        Each query dict should have:
          - "query": str
          - "relevant_ids": List[str]  (ground truth)
        """
        report = BenchmarkReport(
            collection=self.collection,
            strategies=[],
            timestamp=time.time(),
        )

        for strategy in self.strategies:
            metrics = self._benchmark_strategy(strategy, queries, k_values, embedding_fn)
            report.strategies.append(metrics)

        return report

    def _benchmark_strategy(
        self,
        strategy: str,
        queries: List[Dict[str, Any]],
        k_values: List[int],
        embedding_fn: Optional[Any],
    ) -> BenchmarkMetrics:
        results: List[RetrievalResult] = []

        for q in queries:
            query_text = q["query"]
            relevant = q.get("relevant_ids", [])
            t0 = time.perf_counter()

            try:
                retrieved_ids, scores = self._search(strategy, query_text, max(k_values), embedding_fn)
            except Exception as e:
                logger.warning("Search failed for strategy=%s query=%s: %s", strategy, query_text[:50], e)
                retrieved_ids, scores = [], []

            latency = (time.perf_counter() - t0) * 1000
            results.append(RetrievalResult(
                query=query_text,
                retrieved_ids=retrieved_ids,
                relevant_ids=relevant,
                scores=scores,
                latency_ms=latency,
            ))

        # Aggregate metrics
        metrics = BenchmarkMetrics(strategy=strategy, num_queries=len(results))

        for k in k_values:
            recalls = [_recall_at_k(r.retrieved_ids, r.relevant_ids, k) for r in results]
            ndcgs = [_ndcg_at_k(r.retrieved_ids, r.relevant_ids, k) for r in results]
            metrics.recall_at_k[k] = sum(recalls) / len(recalls) if recalls else 0.0
            metrics.ndcg_at_k[k] = sum(ndcgs) / len(ndcgs) if ndcgs else 0.0

        mrrs = [_mrr(r.retrieved_ids, r.relevant_ids) for r in results]
        metrics.mrr = sum(mrrs) / len(mrrs) if mrrs else 0.0
        metrics.avg_latency_ms = sum(r.latency_ms for r in results) / len(results) if results else 0.0

        return metrics

    def _search(
        self,
        strategy: str,
        query: str,
        limit: int,
        embedding_fn: Optional[Any],
    ) -> Tuple[List[str], List[float]]:
        """Execute search against Qdrant collection using specified strategy."""
        try:
            from app.qdrant_client import get_qdrant_client
            client = get_qdrant_client()
        except Exception:
            return [], []

        if strategy == "dense":
            return self._dense_search(client, query, limit, embedding_fn)
        elif strategy == "sparse":
            return self._sparse_search(client, query, limit)
        elif strategy == "hybrid":
            return self._hybrid_search(client, query, limit, embedding_fn)
        return [], []

    def _dense_search(self, client: Any, query: str, limit: int, embedding_fn: Optional[Any]) -> Tuple[List[str], List[float]]:
        if embedding_fn is None:
            try:
                from app.embeddings import embed_single
                embedding_fn = lambda t: embed_single(t).vectors[0].tolist()
            except ImportError:
                return [], []

        vec = embedding_fn(query)
        results = client.search(
            collection_name=self.collection,
            query_vector=vec,
            limit=limit,
            with_payload=True,
        )
        ids = [str(r.id) for r in results]
        scores = [r.score for r in results]
        return ids, scores

    def _sparse_search(self, client: Any, query: str, limit: int) -> Tuple[List[str], List[float]]:
        """BM25/BM42 sparse search — requires sparse vectors in collection."""
        try:
            from qdrant_client.http import models as rest
            results = client.query_points(
                collection_name=self.collection,
                query=rest.Query(nearest=rest.NearestQuery(
                    using="sparse",
                    query=query,
                )),
                limit=limit,
            )
            ids = [str(r.id) for r in results.points]
            scores = [r.score for r in results.points]
            return ids, scores
        except Exception as e:
            logger.warning("Sparse search not available: %s", e)
            return [], []

    def _hybrid_search(self, client: Any, query: str, limit: int, embedding_fn: Optional[Any]) -> Tuple[List[str], List[float]]:
        """Hybrid: dense + sparse with RRF fusion."""
        dense_ids, dense_scores = self._dense_search(client, query, limit * 2, embedding_fn)
        sparse_ids, sparse_scores = self._sparse_search(client, query, limit * 2)

        # Reciprocal Rank Fusion
        rrf_k = 60
        fused: Dict[str, float] = {}
        for rank, doc_id in enumerate(dense_ids):
            fused[doc_id] = fused.get(doc_id, 0.0) + 1.0 / (rrf_k + rank + 1)
        for rank, doc_id in enumerate(sparse_ids):
            fused[doc_id] = fused.get(doc_id, 0.0) + 1.0 / (rrf_k + rank + 1)

        sorted_items = sorted(fused.items(), key=lambda x: x[1], reverse=True)[:limit]
        return [item[0] for item in sorted_items], [item[1] for item in sorted_items]

    @staticmethod
    def print_report(report: BenchmarkReport) -> None:
        """Pretty-print benchmark results."""
        print(f"\n{'=' * 60}")
        print(f"  Benchmark Report: {report.collection}")
        print(f"{'=' * 60}")
        for m in report.strategies:
            print(f"\n  Strategy: {m.strategy.upper()}")
            print(f"  Queries: {m.num_queries} | Avg Latency: {m.avg_latency_ms:.1f}ms | MRR: {m.mrr:.4f}")
            for k, v in sorted(m.recall_at_k.items()):
                ndcg = m.ndcg_at_k.get(k, 0.0)
                print(f"    Recall@{k}: {v:.4f}  |  NDCG@{k}: {ndcg:.4f}")
        print(f"\n{'=' * 60}\n")


__all__ = ["BenchmarkHarness", "BenchmarkMetrics", "BenchmarkReport"]
