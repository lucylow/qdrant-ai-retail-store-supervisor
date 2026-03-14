#!/usr/bin/env python3
"""
Run Qdrant HF dataset benchmarks.

Usage:
    python -m scripts.bench_hf --dataset bm42_bench --max-rows 500 --k 1,5,10
    # or via Makefile: make bench-hf
"""

from __future__ import annotations

import argparse
import json
import sys

from app.datasets.qdrant_hf_loader import load_catalog_dataset, ingest_to_qdrant, list_available_datasets
from app.datasets.benchmark import BenchmarkHarness


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark Qdrant retrieval with HF datasets")
    parser.add_argument("--dataset", default="bm42_bench", help="Dataset key from catalog")
    parser.add_argument("--max-rows", type=int, default=500, help="Max rows to load")
    parser.add_argument("--collection", default=None, help="Qdrant collection name (auto-generated if omitted)")
    parser.add_argument("--k", default="1,5,10", help="Comma-separated K values for Recall@K / NDCG@K")
    parser.add_argument("--strategies", default="dense,hybrid", help="Retrieval strategies to benchmark")
    parser.add_argument("--list", action="store_true", help="List available datasets and exit")
    parser.add_argument("--ingest-only", action="store_true", help="Ingest dataset without running benchmarks")
    args = parser.parse_args()

    if args.list:
        print("\nAvailable Qdrant HF Datasets:")
        for d in list_available_datasets():
            print(f"  {d['key']:20s} {d['repo_id']:40s} {d['description'][:60]}")
        return

    collection = args.collection or f"hf_{args.dataset}"
    k_values = [int(k) for k in args.k.split(",")]
    strategies = [s.strip() for s in args.strategies.split(",")]

    # 1. Load dataset
    print(f"\n Loading dataset: {args.dataset} (max {args.max_rows} rows)...")
    rows = load_catalog_dataset(args.dataset, max_rows=args.max_rows)
    if not rows:
        print("No rows loaded. Check dataset key or network.")
        sys.exit(1)
    print(f"  Loaded {len(rows)} rows")

    # 2. Ingest into Qdrant
    print(f"\n Ingesting into Qdrant collection: {collection}...")
    count = ingest_to_qdrant(rows, collection=collection, recreate=True)
    print(f"  Ingested {count} points")

    if args.ingest_only:
        print("\n Done (ingest only).")
        return

    # 3. Build evaluation queries (use rows with labels if available)
    queries = []
    for row in rows[:50]:  # Sample queries from the dataset itself
        q = row.get("query") or row.get("text", "")
        label = row.get("label") or row.get("relevant_id")
        if q and label:
            queries.append({"query": q, "relevant_ids": [str(label)]})
    
    if not queries:
        print("\n  No labeled queries found; using self-retrieval evaluation...")
        # Self-retrieval: each doc should retrieve itself
        for i, row in enumerate(rows[:50]):
            text = row.get("text", "")
            if text:
                queries.append({"query": text, "relevant_ids": [str(i)]})

    # 4. Run benchmarks
    print(f"\n Running benchmarks ({len(queries)} queries, strategies={strategies})...")
    harness = BenchmarkHarness(collection=collection, strategies=strategies)
    report = harness.run(queries, k_values=k_values)

    # 5. Report
    harness.print_report(report)


if __name__ == "__main__":
    main()
