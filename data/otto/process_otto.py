"""
OTTO → Qdrant: process 14M sessions into Parquet and optional product collection.

Generates: sessions.parquet, product_stats.parquet, conversion_rates.parquet.
Optionally: creates Qdrant "products" collection (batch upsert, optional cap for demo).

Usage:
  python data/otto/process_otto.py --input data/otto/train.jsonl --out-dir data/otto
  python data/otto/process_otto.py --input data/otto/train.jsonl --out-dir data/otto --max-sessions 100000 --max-products 50000 --qdrant-url http://localhost:6333
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

# Optional heavy deps (so script can run for --help without installing all)
try:
    import polars as pl
except ImportError:
    pl = None

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

EMBEDDING_DIM = 384
BATCH_UPSERT_SIZE = 256


def _read_otto_events_stream(input_path: str, max_sessions: int | None) -> pl.DataFrame:
    """Read train.jsonl and explode to one row per event. Optionally cap sessions."""
    if pl is None:
        raise RuntimeError("polars is required; pip install polars")
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Input not found: {input_path}")

    rows: list[dict] = []
    seen_sessions: set[str] = set()
    with open(path, "r") as f:
        for line in f:
            if max_sessions is not None and len(seen_sessions) >= max_sessions:
                break
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            session = obj.get("session") or obj.get("id")
            events = obj.get("events", [])
            if not events:
                continue
            seen_sessions.add(str(session))
            for ev in events:
                rows.append({
                    "session": str(session),
                    "aid": int(ev.get("aid", 0)),
                    "ts": int(ev.get("ts", 0)),
                    "type": str(ev.get("type", "clicks")).lower().replace("clicks", "click"),
                })
    if not rows:
        return pl.DataFrame()
    return pl.DataFrame(rows)


def process_events(input_path: str, out_dir: str, max_sessions: int | None) -> tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame]:
    """Convert OTTO events to session stats, product stats, and conversion rates."""
    if pl is None:
        raise RuntimeError("polars is required")
    print("Processing OTTO events...")
    df = _read_otto_events_stream(input_path, max_sessions)
    if df.is_empty():
        print("No events read. Check input path and format.")
        return pl.DataFrame(), pl.DataFrame(), pl.DataFrame()

    # Event type normalization
    df = df.with_columns(
        pl.col("type").replace({"clicks": "click", "carts": "cart", "orders": "order"})
    )

    # Session stats
    session_stats = df.group_by("session").agg([
        pl.col("aid").n_unique().alias("unique_products"),
        pl.col("aid").alias("aids"),
        pl.col("type").alias("event_types"),
        pl.col("ts").alias("ts_list"),
        pl.len().alias("total_events"),
    ])

    # Product stats (for stock/conv simulation)
    product_stats = df.group_by("aid").agg([
        pl.len().alias("total_events"),
        (pl.col("type") == "order").sum().alias("orders"),
        (pl.col("type") == "cart").sum().alias("carts"),
        (pl.col("type") == "click").sum().alias("clicks"),
    ])
    total_events = product_stats["total_events"].sum()
    product_stats = product_stats.with_columns(
        (pl.col("orders") / pl.col("total_events").clip(lower_bound=1)).alias("conv_rate")
    )

    # Conversion rates (global)
    orders_count = df.filter(pl.col("type") == "order").height
    carts_count = df.filter(pl.col("type") == "cart").height
    clicks_count = df.filter(pl.col("type") == "click").height
    conversion_rates = pl.DataFrame({
        "metric": ["click_to_cart", "cart_to_order", "click_to_order"],
        "rate": [
            carts_count / max(clicks_count, 1),
            orders_count / max(carts_count, 1),
            orders_count / max(clicks_count, 1),
        ],
        "count_orders": [orders_count] * 3,
        "count_carts": [carts_count] * 3,
        "count_clicks": [clicks_count] * 3,
    })

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    session_stats.write_parquet(out / "sessions.parquet")
    product_stats.write_parquet(out / "product_stats.parquet")
    conversion_rates.write_parquet(out / "conversion_rates.parquet")
    print(f"Wrote sessions={session_stats.height}, products={product_stats.height}, conversion_rates to {out_dir}")
    return session_stats, product_stats, conversion_rates


def create_product_collection(
    product_stats: pl.DataFrame,
    qdrant_url: str,
    max_products: int | None,
    embedding_model: str = "all-MiniLM-L6-v2",
) -> None:
    """Create Qdrant 'products' collection and upsert product vectors (batch)."""
    if QdrantClient is None or qmodels is None:
        raise RuntimeError("qdrant-client is required")
    if SentenceTransformer is None:
        raise RuntimeError("sentence-transformers is required")

    df = product_stats
    if max_products is not None and df.height > max_products:
        df = df.sort("total_events", descending=True).head(max_products)
    print(f"Creating product collection (n={df.height})...")
    model = SentenceTransformer(embedding_model)
    client = QdrantClient(url=qdrant_url)

    collection_name = "products"
    try:
        client.get_collection(collection_name)
        client.delete_collection(collection_name)
    except Exception:
        pass
    client.create_collection(
        collection_name=collection_name,
        vectors_config=qmodels.VectorParams(size=EMBEDDING_DIM, distance=qmodels.Distance.COSINE),
    )

    aids = df["aid"].to_list()
    total_events = df["total_events"].to_list()
    orders = df["orders"].to_list()
    carts = df["carts"].to_list()
    conv_rates = df["conv_rate"].to_list()

    categories = ["tents", "jackets", "shoes", "backpacks", "accessories"]
    rng = np.random.default_rng(42)
    points_batch: list = []
    for i, (aid, te, ords, crts, conv) in enumerate(zip(aids, total_events, orders, carts, conv_rates)):
        price = float(rng.uniform(10, 500))
        stock_status = "in_stock" if rng.random() > 0.1 else "low_stock"
        category = str(rng.choice(categories))
        popularity = min(1.0, (te or 0) / 1000.0)
        text = f"aid:{aid} {category} CHF{price:.0f} popularity:{popularity:.2f}"
        embedding = model.encode(text, normalize_embeddings=True).tolist()
        payload = {
            "aid": int(aid),
            "price": round(price, 2),
            "stock_status": stock_status,
            "category": category,
            "conv_rate": round(float(conv), 4),
            "popularity": round(popularity, 4),
        }
        points_batch.append(
            qmodels.PointStruct(id=int(aid), vector=embedding, payload=payload)
        )
        if len(points_batch) >= BATCH_UPSERT_SIZE:
            client.upsert(collection_name=collection_name, points=points_batch)
            points_batch = []
            print(f"  Upserted {i + 1}/{len(aids)}")
    if points_batch:
        client.upsert(collection_name=collection_name, points=points_batch)
    print(f"Products collection ready: {len(aids)} vectors (384-dim)")


def main() -> None:
    parser = argparse.ArgumentParser(description="OTTO → Parquet + optional Qdrant products")
    parser.add_argument("--input", default="data/otto/train.jsonl", help="Path to train.jsonl")
    parser.add_argument("--out-dir", default="data/otto", help="Output directory for Parquet files")
    parser.add_argument("--max-sessions", type=int, default=None, help="Cap number of sessions (demo)")
    parser.add_argument("--max-products", type=int, default=None, help="Cap products for Qdrant (demo)")
    parser.add_argument("--qdrant-url", type=str, default=None, help="If set, create and fill products collection")
    args = parser.parse_args()

    session_stats, product_stats, conversion_rates = process_events(
        args.input, args.out_dir, args.max_sessions
    )
    if session_stats.is_empty():
        sys.exit(1)

    if args.qdrant_url and not product_stats.is_empty():
        create_product_collection(
            product_stats,
            args.qdrant_url,
            args.max_products,
        )


if __name__ == "__main__":
    main()
