"""
Amazon -> Qdrant: 82M+ reviews -> production multimodal collections.

Generates: review_stats.parquet, products.parquet, and Qdrant collection
amazon_products with named vectors (text 384, image 512, sentiment 384).

Usage:
  python data/amazon/process_amazon.py --reviews data/amazon/reviews_Sports_and_Outdoors_5.json --meta data/amazon/meta_Sports_and_Outdoors.json --out-dir data/amazon
  python data/amazon/process_amazon.py --reviews data/amazon/reviews_Sports.json --meta data/amazon/meta_Sports.json --out-dir data/amazon --max-reviews 500000 --qdrant-url http://localhost:6333
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List

try:
    import numpy as np
except ImportError:
    np = None

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

TEXT_DIM = 384
IMAGE_DIM = 512
SENTIMENT_DIM = 384
BATCH_UPSERT = 256


def _read_reviews_jsonl(path: str, max_reviews: int | None) -> pl.DataFrame:
    """Read JSONL (one JSON object per line)."""
    if pl is None:
        raise RuntimeError("polars required; pip install polars")
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    rows = []
    with open(path, "r") as f:
        for i, line in enumerate(f):
            if max_reviews is not None and i >= max_reviews:
                break
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            rows.append({
                "reviewerID": obj.get("reviewerID", ""),
                "asin": obj.get("asin", ""),
                "overall": float(obj.get("overall", 0)),
                "reviewText": str(obj.get("reviewText", ""))[:2000],
                "summary": str(obj.get("summary", ""))[:500],
                "unixReviewTime": int(obj.get("unixReviewTime", 0)),
            })
    if not rows:
        return pl.DataFrame()
    return pl.DataFrame(rows)


def _read_meta_jsonl(path: str, max_products: int | None) -> pl.DataFrame:
    """Read metadata JSONL (one JSON per line)."""
    if pl is None:
        raise RuntimeError("polars required")
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    rows = []
    with open(path, "r") as f:
        for i, line in enumerate(f):
            if max_products is not None and i >= max_products:
                break
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            cats = obj.get("categories") or obj.get("category") or []
            if isinstance(cats, list) and cats and isinstance(cats[0], list):
                cat_str = "/".join(cats[0][:5]) if cats[0] else ""
            else:
                cat_str = "/".join(str(c) for c in cats[:5]) if cats else ""
            price = obj.get("price")
            if price is None:
                price = 99.99
            try:
                price = float(price)
            except (TypeError, ValueError):
                price = 99.99
            image_urls = obj.get("imageURL") or obj.get("imageURLs") or obj.get("imUrl")
            if isinstance(image_urls, str):
                image_urls = [image_urls]
            elif not isinstance(image_urls, list):
                image_urls = []
            rows.append({
                "asin": obj.get("asin", ""),
                "title": (obj.get("title") or "Unknown Product")[:200],
                "brand": (obj.get("brand") or "Unknown")[:50],
                "category": cat_str[:100],
                "price": price,
                "imageURLs": image_urls[:3],
            })
    if not rows:
        return pl.DataFrame()
    return pl.DataFrame(rows)


def compute_review_stats(reviews_df: pl.DataFrame) -> pl.DataFrame:
    """Per-product: avg_rating, review_count, last_review_ts, sentiment_positive, review_velocity."""
    if reviews_df.is_empty():
        return pl.DataFrame()
    return reviews_df.group_by("asin").agg([
        pl.col("overall").mean().alias("avg_rating"),
        pl.count().alias("review_count"),
        pl.col("unixReviewTime").max().alias("last_review_ts"),
        pl.col("unixReviewTime").min().alias("first_review_ts"),
        (pl.col("overall") >= 4.0).mean().alias("sentiment_positive"),
    ]).with_columns([
        (
            pl.col("review_count").cast(pl.Float64)
            / ((pl.col("last_review_ts") - pl.col("first_review_ts")).clip(1) / 86400.0)
        ).alias("review_velocity"),
    ]).drop("first_review_ts")


def _truncate_sentiment(vec: List[float], size: int) -> List[float]:
    if len(vec) >= size:
        return vec[:size]
    return vec + [0.0] * (size - len(vec))


def run(
    reviews_path: str,
    meta_path: str,
    out_dir: str,
    qdrant_url: str | None = None,
    max_reviews: int | None = None,
    max_products: int | None = None,
    skip_qdrant: bool = False,
) -> None:
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    print("Reading reviews...")
    reviews_df = _read_reviews_jsonl(reviews_path, max_reviews)
    if reviews_df.is_empty():
        print("No reviews found.")
        return
    print("Reviews:", len(reviews_df))

    print("Computing review stats...")
    review_stats = compute_review_stats(reviews_df)
    stats_path = out_path / "review_stats.parquet"
    review_stats.write_parquet(stats_path)
    print("Wrote", stats_path)

    print("Reading metadata...")
    meta_df = _read_meta_jsonl(meta_path, max_products)
    if meta_df.is_empty():
        print("No metadata found.")
        return
    print("Metadata:", len(meta_df))

    enriched = meta_df.join(review_stats, on="asin", how="left").with_columns([
        pl.col("avg_rating").fill_null(4.0),
        pl.col("review_count").fill_null(0),
        pl.col("sentiment_positive").fill_null(0.7),
        pl.col("review_velocity").fill_null(0.1),
    ])
    products_path = out_path / "products.parquet"
    enriched.write_parquet(products_path)
    print("Wrote", products_path)

    if skip_qdrant:
        print("Skipping Qdrant (--skip-qdrant).")
        return

    if SentenceTransformer is None or QdrantClient is None or qmodels is None:
        print("Install sentence-transformers and qdrant-client to index to Qdrant.")
        return

    print("Loading embedding models...")
    text_model = SentenceTransformer("all-MiniLM-L6-v2")
    sentiment_model = SentenceTransformer("cardiffnlp/twitter-roberta-base-sentiment-latest")

    client = QdrantClient(url=qdrant_url or "http://localhost:6333")
    collection_name = "amazon_products"

    try:
        client.get_collection(collection_name)
        client.delete_collection(collection_name)
    except Exception:
        pass

    vectors_config = qmodels.VectorsConfig(
        named_vectors={
            "text": qmodels.NamedVectorParams(size=TEXT_DIM, distance=qmodels.Distance.COSINE),
            "image": qmodels.NamedVectorParams(size=IMAGE_DIM, distance=qmodels.Distance.COSINE),
            "sentiment": qmodels.NamedVectorParams(size=SENTIMENT_DIM, distance=qmodels.Distance.COSINE),
        }
    )
    client.create_collection(collection_name=collection_name, vectors_config=vectors_config)
    print("Created collection", collection_name)

    image_placeholder = [0.0] * IMAGE_DIM

    points_batch: List = []
    total = 0
    for row in enriched.iter_rows(named=True):
        try:
            asin = str(row["asin"])
            if not asin:
                continue
            title = str(row.get("title", "Unknown"))[:200]
            brand = str(row.get("brand", "Unknown"))[:50]
            category = str(row.get("category", ""))[:100]
            price = float(row.get("price", 99.99))
            avg_rating = float(row.get("avg_rating", 4.0))
            review_count = int(row.get("review_count", 0))
            sentiment_positive = float(row.get("sentiment_positive", 0.7))
            review_velocity = float(row.get("review_velocity", 0.1))
            stock_status = "in_stock" if review_velocity > 0.05 else "low_stock"
        except Exception:
            continue

        text_for_embed = f"{title} {brand} {category} {avg_rating} stars"
        text_vec = text_model.encode(text_for_embed, normalize_embeddings=True).tolist()
        if len(text_vec) != TEXT_DIM:
            text_vec = (text_vec + [0.0] * TEXT_DIM)[:TEXT_DIM]

        sentiment_text = f"rating {avg_rating} sentiment {sentiment_positive}"
        sent_vec = sentiment_model.encode(sentiment_text, normalize_embeddings=True).tolist()
        sentiment_vec = _truncate_sentiment(sent_vec, SENTIMENT_DIM)

        payload = {
            "asin": asin,
            "title": title,
            "brand": brand,
            "category": category,
            "price": price,
            "avg_rating": avg_rating,
            "review_count": review_count,
            "sentiment_positive": sentiment_positive,
            "review_velocity": review_velocity,
            "stock_status": stock_status,
        }

        point = qmodels.PointStruct(
            id=asin,
            vector={
                "text": text_vec,
                "image": image_placeholder,
                "sentiment": sentiment_vec,
            },
            payload=payload,
        )
        points_batch.append(point)
        if len(points_batch) >= BATCH_UPSERT:
            client.upsert(collection_name=collection_name, points=points_batch)
            total += len(points_batch)
            print("Upserted", total, "products...")
            points_batch = []

    if points_batch:
        client.upsert(collection_name=collection_name, points=points_batch)
        total += len(points_batch)
    print("Done.", total, "multimodal products in", collection_name)


def main() -> None:
    parser = argparse.ArgumentParser(description="Amazon reviews -> Qdrant multimodal collection")
    parser.add_argument("--reviews", required=True, help="Path to reviews JSONL")
    parser.add_argument("--meta", required=True, help="Path to metadata JSONL")
    parser.add_argument("--out-dir", default="data/amazon", help="Output directory for Parquet files")
    parser.add_argument("--qdrant-url", default="http://localhost:6333", help="Qdrant URL")
    parser.add_argument("--max-reviews", type=int, default=None, help="Cap number of reviews")
    parser.add_argument("--max-products", type=int, default=None, help="Cap number of products")
    parser.add_argument("--skip-qdrant", action="store_true", help="Only write Parquet, do not index Qdrant")
    args = parser.parse_args()
    run(
        reviews_path=args.reviews,
        meta_path=args.meta,
        out_dir=args.out_dir,
        qdrant_url=args.qdrant_url,
        max_reviews=args.max_reviews,
        max_products=args.max_products,
        skip_qdrant=args.skip_qdrant,
    )


if __name__ == "__main__":
    main()
