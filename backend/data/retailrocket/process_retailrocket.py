"""
RetailRocket → Qdrant: 2.7M events → Parquet + optional product collection.

Real view→add2cart→transaction funnel → inventory signals. Produces:
  events.parquet, items.parquet, inventory_signals.parquet, category_tree.parquet
Optionally: creates Qdrant "retailrocket_items" collection (batch upsert).

Usage:
  python data/retailrocket/process_retailrocket.py --data-dir data/retailrocket
  python data/retailrocket/process_retailrocket.py --data-dir data/retailrocket --qdrant-url http://localhost:6333
  python data/retailrocket/process_retailrocket.py --data-dir data/retailrocket --max-events 100000 --max-items 50000 --qdrant-url http://localhost:6333
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

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


def load_events(data_dir: Path, max_events: int | None) -> pl.DataFrame:
    """Load events.csv with optional row cap."""
    if pl is None:
        raise RuntimeError("polars is required; pip install polars")
    path = data_dir / "events.csv"
    if not path.exists():
        raise FileNotFoundError(f"events.csv not found in {data_dir}")
    df = pl.read_csv(path, try_parse_dates=True, infer_schema_length=100_000)
    if max_events is not None and len(df) > max_events:
        df = df.head(max_events)
    return df


def process_events(events: pl.DataFrame) -> pl.DataFrame:
    """Compute per-item funnel stats: views, add2cart, transactions, conversion rates, stock_status proxy."""
    funnel = (
        events.group_by("itemid")
        .agg(
            pl.col("event").filter(pl.col("event") == "view").count().alias("views"),
            pl.col("event").filter(pl.col("event") == "add2cart").count().alias("add2cart"),
            pl.col("event").filter(pl.col("event") == "transaction").count().alias("transactions"),
        )
        .with_columns(
            (pl.col("add2cart") / pl.col("views").clip(lower_bound=1)).alias("view_to_cart_rate"),
            (pl.col("transactions") / pl.col("add2cart").clip(lower_bound=1)).alias("cart_to_transaction_rate"),
        )
        .with_columns(
            pl.when(pl.col("views") > 10)
            .then(pl.lit("in_stock"))
            .otherwise(pl.lit("low_stock"))
            .alias("stock_status")
        )
    )
    return funnel


def load_category_tree(data_dir: Path) -> pl.DataFrame:
    """Load category_tree.csv if present."""
    path = data_dir / "category_tree.csv"
    if not path.exists():
        return pl.DataFrame(schema={"categoryid": pl.Int64, "parentid": pl.Int64, "catname_en": pl.Utf8})
    return pl.read_csv(path, infer_schema_length=5000)


def load_item_properties(data_dir: Path) -> pl.DataFrame:
    """Load item_properties.csv; keep categoryid per item (first occurrence)."""
    path = data_dir / "item_properties.csv"
    if not path.exists():
        return pl.DataFrame(schema={"itemid": pl.Int64, "categoryid": pl.Int64})
    # May be large; read in chunks if needed. For simplicity read all.
    df = pl.read_csv(path, infer_schema_length=50000)
    if "property" not in df.columns or "value" not in df.columns:
        return pl.DataFrame(schema={"itemid": pl.Int64, "categoryid": pl.Int64})
    cat = df.filter(pl.col("property") == "categoryid").group_by("itemid").agg(
        pl.col("value").cast(pl.Utf8).first().alias("cat_value")
    )
    cat = cat.with_columns(pl.col("cat_value").cast(pl.Int64, strict=False).alias("categoryid"))
    return cat.select("itemid", "categoryid")


def build_items_and_signals(
    data_dir: Path,
    funnel: pl.DataFrame,
    categories: pl.DataFrame,
    item_props: pl.DataFrame,
    max_items: int | None,
) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Build items.parquet (with category name) and inventory_signals.parquet."""
    items = funnel.join(item_props, on="itemid", how="left").join(
        categories, on="categoryid", how="left"
    )
    if not categories.is_empty() and "catname_en" in categories.columns:
        items = items.with_columns(pl.col("catname_en").fill_null(pl.lit("Unknown")))
    else:
        items = items.with_columns(pl.lit("Unknown").alias("catname_en"))
    if max_items is not None and len(items) > max_items:
        items = items.sort("views", descending=True).head(max_items)
    inventory_signals = items.select(
        "itemid", "views", "add2cart", "transactions",
        "view_to_cart_rate", "cart_to_transaction_rate", "stock_status"
    )
    return items, inventory_signals


def create_retailrocket_items_collection(
    items: pl.DataFrame,
    qdrant_url: str,
    embedding_model_name: str = "all-MiniLM-L6-v2",
) -> None:
    """Create Qdrant collection retailrocket_items and upsert item vectors (batch)."""
    if QdrantClient is None or qmodels is None:
        raise RuntimeError("qdrant-client is required")
    if SentenceTransformer is None:
        raise RuntimeError("sentence-transformers is required")
    print("Creating retailrocket_items collection...")
    model = SentenceTransformer(embedding_model_name)
    client = QdrantClient(url=qdrant_url)
    collection_name = "retailrocket_items"
    try:
        client.get_collection(collection_name)
        client.delete_collection(collection_name)
    except Exception:
        pass
    client.create_collection(
        collection_name=collection_name,
        vectors_config=qmodels.VectorParams(size=EMBEDDING_DIM, distance=qmodels.Distance.COSINE),
    )
    rng = np.random.default_rng(42)
    n = len(items)
    points_batch: list = []
    for i, row in enumerate(items.iter_rows(named=True)):
        try:
            itemid = int(row["itemid"])
            catname = (row.get("catname_en") or "Unknown")[:100]
            views = int(row.get("views", 0))
            add2cart = int(row.get("add2cart", 0))
            transactions = int(row.get("transactions", 0))
            view_to_cart = float(row.get("view_to_cart_rate", 0.0))
            cart_to_trans = float(row.get("cart_to_transaction_rate", 0.0))
            stock_status = str(row.get("stock_status", "low_stock"))
            categoryid = int(row["categoryid"]) if row.get("categoryid") is not None else 0
            price = float(rng.uniform(15, 450))
            popularity = min(1.0, views / 1000.0) if views else 0.0
            text = f"{catname} itemid:{itemid} views:{views} conv:{view_to_cart:.2%}"
            embedding = model.encode(text, normalize_embeddings=True).tolist()
            payload = {
                "itemid": itemid,
                "categoryid": categoryid,
                "catname": catname,
                "views": views,
                "add2cart": add2cart,
                "transactions": transactions,
                "view_to_cart_rate": round(view_to_cart, 4),
                "cart_to_transaction_rate": round(cart_to_trans, 4),
                "stock_status": stock_status,
                "price": round(price, 2),
                "popularity": round(popularity, 4),
            }
            points_batch.append(
                qmodels.PointStruct(id=str(itemid), vector=embedding, payload=payload)
            )
            if len(points_batch) >= BATCH_UPSERT_SIZE:
                client.upsert(collection_name=collection_name, points=points_batch)
                points_batch = []
                print(f"  Upserted {i + 1}/{n}")
        except Exception as e:
            continue
    if points_batch:
        client.upsert(collection_name=collection_name, points=points_batch)
    print(f"retailrocket_items ready: {n} vectors ({EMBEDDING_DIM}-dim)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="RetailRocket → Parquet + optional Qdrant retailrocket_items"
    )
    parser.add_argument("--data-dir", type=str, default="data/retailrocket", help="Directory with events.csv, etc.")
    parser.add_argument("--max-events", type=int, default=None, help="Cap number of events (demo)")
    parser.add_argument("--max-items", type=int, default=None, help="Cap number of items for Parquet/Qdrant")
    parser.add_argument("--qdrant-url", type=str, default=None, help="If set, create and fill retailrocket_items")
    args = parser.parse_args()
    data_dir = Path(args.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)

    print("Loading RetailRocket events...")
    events = load_events(data_dir, args.max_events)
    if events.is_empty():
        print("No events found. Ensure events.csv exists in --data-dir.")
        sys.exit(1)
    print(f"Events: {len(events)}")

    funnel = process_events(events)
    print(f"Funnel stats: {len(funnel)} items")

    categories = load_category_tree(data_dir)
    item_props = load_item_properties(data_dir)
    items, inventory_signals = build_items_and_signals(
        data_dir, funnel, categories, item_props, args.max_items
    )

    items.write_parquet(data_dir / "items.parquet")
    inventory_signals.write_parquet(data_dir / "inventory_signals.parquet")
    events.write_parquet(data_dir / "events.parquet")
    if not categories.is_empty():
        categories.write_parquet(data_dir / "category_tree.parquet")
    print(f"Wrote Parquet to {data_dir}")

    if args.qdrant_url and not items.is_empty():
        create_retailrocket_items_collection(items, args.qdrant_url)


if __name__ == "__main__":
    main()
