#!/usr/bin/env python3
"""
Complete Multimodal Dataset Integration Pipeline.

Integrates OTTO sessions → goals, Amazon metadata → products (text+image),
MS COCO → visual catalog, InternVid → video demos into unified Qdrant
products_multimodal collection with 4 named vectors and payload indexes.

Phases:
  1. setup     - Create collection + payload indexes (stock_status, price_band, category, language)
  2. otto      - OTTO sessions → goals collection (episodic memory)
  3. amazon    - Amazon metadata → products_multimodal (text + image vectors)
  4. coco      - MS COCO images → products_multimodal (imagevector)
  5. internvid - InternVid keyframes → products_multimodal (videovector)
  6. search    - Run unified multimodal_search demo

Usage:
  python -m scripts.multimodal_pipeline setup
  python -m scripts.multimodal_pipeline otto --input data/otto/train.jsonl --max-sessions 8000
  python -m scripts.multimodal_pipeline amazon --meta data/amazon/meta_*.json --max-products 5000
  python -m scripts.multimodal_pipeline coco --annotations data/coco/instances_train2017.json --image-dir data/coco/train2017 --max-images 2000
  python -m scripts.multimodal_pipeline internvid --max-videos 1000
  python -m scripts.multimodal_pipeline search --query "Zelt unter 200 Franken"
  python -m scripts.multimodal_pipeline all  # run setup + otto + amazon (coco/internvid need data paths)
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def phase_setup(qdrant_url: str | None) -> None:
    """Phase 1: Create products_multimodal collection and payload indexes."""
    from app.qdrant_client import get_qdrant_client
    from app.data.collections import ensure_all_collections
    from app.multimodal.indexing import (
        ensure_products_multimodal_collection,
        ensure_multimodal_payload_indexes,
        PRODUCTS_MULTIMODAL_COLLECTION,
    )
    if qdrant_url:
        import os
        os.environ["QDRANT_URL"] = qdrant_url
    ensure_all_collections()
    client = get_qdrant_client()
    ensure_products_multimodal_collection(client)
    ensure_multimodal_payload_indexes(client, PRODUCTS_MULTIMODAL_COLLECTION)
    logger.info("Phase 1 done: collection %s + payload indexes", PRODUCTS_MULTIMODAL_COLLECTION)


def phase_otto(input_path: str, out_dir: str, max_sessions: int | None, qdrant_url: str | None) -> None:
    """Phase 2: OTTO sessions → goals collection (session goal vectors for episodic memory)."""
    try:
        import polars as pl
    except ImportError:
        logger.error("polars required: pip install polars")
        return
    try:
        from sentence_transformers import SentenceTransformer
        from qdrant_client import QdrantClient
        from qdrant_client.http import models as qmodels
    except ImportError as e:
        logger.error("sentence-transformers and qdrant-client required: %s", e)
        return

    if qdrant_url:
        import os
        os.environ["QDRANT_URL"] = qdrant_url
    from app.config import COLLECTIONS
    from app.qdrant_client import get_qdrant_client

    path = Path(input_path)
    if not path.exists():
        logger.warning("OTTO input not found: %s (skip phase otto)", input_path)
        return

    logger.info("Reading OTTO sessions from %s (max_sessions=%s)", input_path, max_sessions)
    rows = []
    seen = set()
    with open(path) as f:
        for line in f:
            if max_sessions is not None and len(seen) >= max_sessions:
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
            seen.add(str(session))
            aids = [int(e.get("aid", 0)) for e in events]
            types = [str(e.get("type", "clicks")).lower().replace("clicks", "click") for e in events]
            mode_type = max(set(types), key=types.count) if types else "click"
            rows.append({
                "session": str(session),
                "aids": aids[:20],
                "actions": types,
                "intent": mode_type,
                "has_order": 1 if "order" in types else 0,
            })
    if not rows:
        logger.warning("No OTTO sessions read")
        return

    df = pl.DataFrame(rows)
    model = SentenceTransformer("all-MiniLM-L6-v2")
    client = get_qdrant_client()
    goals_coll = COLLECTIONS.goals
    try:
        client.get_collection(goals_coll)
    except Exception:
        client.create_collection(
            collection_name=goals_coll,
            vectors_config=qmodels.VectorParams(size=384, distance=qmodels.Distance.COSINE),
        )
    batch = []
    for i, row in enumerate(df.iter_rows(named=True)):
        goal_text = f"shopping session: products {row['aids'][:5]} actions {row['intent']}"
        goal_vec = model.encode(goal_text).tolist()
        batch.append(
            qmodels.PointStruct(
                id=f"otto_goal_{row['session']}_{i}",
                vector=goal_vec,
                payload={
                    "session_id": row["session"],
                    "products": row["aids"][:20],
                    "intent": row["intent"],
                    "status": "solved" if row["has_order"] else "open",
                    "conversion": float(row["has_order"]),
                },
            )
        )
        if len(batch) >= 1000:
            client.upsert(collection_name=goals_coll, points=batch)
            batch = []
            logger.info("OTTO goals: %s sessions", i + 1)
    if batch:
        client.upsert(collection_name=goals_coll, points=batch)
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    df.write_parquet(Path(out_dir) / "otto_goals.parquet")
    logger.info("Phase 2 done: %s OTTO sessions → goals collection %s", len(rows), goals_coll)


def phase_amazon(meta_path: str, max_products: int | None, qdrant_url: str | None) -> None:
    """Phase 3: Amazon metadata → products_multimodal (text + image vectors)."""
    from app.qdrant_client import get_qdrant_client
    from app.multimodal.indexing import (
        ensure_products_multimodal_collection,
        ensure_multimodal_payload_indexes,
        index_product_vectors,
        PRODUCTS_MULTIMODAL_COLLECTION,
    )
    from app.multimodal.encoders import MultimodalProductEncoders
    from app.multimodal.schema import IMAGE_DIM, VIDEO_DIM

    if qdrant_url:
        import os
        os.environ["QDRANT_URL"] = qdrant_url
    client = get_qdrant_client()
    ensure_products_multimodal_collection(client)
    ensure_multimodal_payload_indexes(client, PRODUCTS_MULTIMODAL_COLLECTION)

    paths = list(Path(meta_path).parent.glob(Path(meta_path).name)) if "*" in meta_path else [Path(meta_path)]
    if not paths or not paths[0].exists():
        logger.warning("Amazon meta not found: %s (skip phase amazon)", meta_path)
        return

    enc = MultimodalProductEncoders()
    batch_count = 0
    for p in paths:
        with open(p) as f:
            for i, line in enumerate(f):
                if max_products is not None and batch_count >= max_products:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    meta = json.loads(line)
                except json.JSONDecodeError:
                    continue
                asin = meta.get("asin")
                if not asin:
                    continue
                title = (meta.get("title") or "")[:200]
                main_cat = (meta.get("main_cat") or meta.get("categories") or "")
                if isinstance(main_cat, list):
                    main_cat = "/".join(str(x) for x in main_cat[:3])
                text = f"{title} {main_cat}"
                text_vec = enc.encode_text(text)
                image_vec = None
                img_url = (meta.get("imageURL") or meta.get("imageURLs") or [])
                if isinstance(img_url, str):
                    img_url = [img_url]
                if img_url:
                    try:
                        import requests
                        from PIL import Image
                        r = requests.get(img_url[0], timeout=5)
                        r.raise_for_status()
                        img = Image.open(r.raw).convert("RGB")
                        import tempfile
                        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tf:
                            img.save(tf.name)
                        try:
                            image_vec = enc.encode_image(tf.name)
                        finally:
                            Path(tf.name).unlink(missing_ok=True)
                    except Exception as e:
                        logger.debug("Amazon image %s: %s", asin, e)
                if image_vec is None or len(image_vec) != IMAGE_DIM:
                    image_vec = [0.0] * IMAGE_DIM
                price = meta.get("price")
                try:
                    price = float(price) if price is not None else 0.0
                except (TypeError, ValueError):
                    price = 0.0
                price_band = "low" if price < 20 else "high" if price >= 100 else "medium"
                vectors = {
                    "textvector": text_vec,
                    "imagevector": image_vec,
                    "audiovector": enc.encode_audio(),
                    "videovector": [0.0] * VIDEO_DIM,
                }
                payload = {
                    "asin": asin,
                    "title": title,
                    "category": str(main_cat)[:100],
                    "price": price,
                    "stock_status": "instock",
                    "price_band": price_band,
                    "language": "en",
                }
                index_product_vectors(client, f"amazon_{asin}", vectors, payload)
                batch_count += 1
                if batch_count % 500 == 0:
                    logger.info("Amazon: %s products", batch_count)
    logger.info("Phase 3 done: %s Amazon products → %s", batch_count, PRODUCTS_MULTIMODAL_COLLECTION)


def phase_coco(annotations_path: str, image_dir: str, max_images: int | None, qdrant_url: str | None) -> None:
    """Phase 4: MS COCO images → products_multimodal (imagevector)."""
    from app.qdrant_client import get_qdrant_client
    from app.multimodal.indexing import (
        ensure_products_multimodal_collection,
        ensure_multimodal_payload_indexes,
        index_product_vectors,
        PRODUCTS_MULTIMODAL_COLLECTION,
    )
    from app.multimodal.encoders import MultimodalProductEncoders
    from app.multimodal.schema import TEXT_DIM, IMAGE_DIM, AUDIO_DIM, VIDEO_DIM

    if qdrant_url:
        import os
        os.environ["QDRANT_URL"] = qdrant_url
    path_ann = Path(annotations_path)
    path_img = Path(image_dir)
    if not path_ann.exists() or not path_img.is_dir():
        logger.warning("COCO paths not found: %s / %s (skip phase coco)", annotations_path, image_dir)
        return

    with open(path_ann) as f:
        coco = json.load(f)
    images = coco.get("images", [])[: max_images if max_images else len(coco.get("images", []))]
    cat_map = {c["id"]: c.get("name", "gear") for c in coco.get("categories", [])}

    client = get_qdrant_client()
    ensure_products_multimodal_collection(client)
    ensure_multimodal_payload_indexes(client, PRODUCTS_MULTIMODAL_COLLECTION)
    enc = MultimodalProductEncoders()
    import numpy as np
    count = 0
    for img_info in images:
        fn = img_info.get("file_name")
        if not fn:
            continue
        img_path = path_img / fn
        if not img_path.exists():
            continue
        cat_id = img_info.get("category_id", 1)
        category = cat_map.get(cat_id, "gear")
        image_vec = enc.encode_image(str(img_path))
        if image_vec is None:
            continue
        if len(image_vec) != IMAGE_DIM:
            continue
        text_vec = enc.encode_text(f"{category} product")
        price = 150.0 + float(np.random.normal(0, 30))
        price_band = "medium"
        point_id = f"coco_{img_info['id']}"
        vectors = {
            "textvector": text_vec,
            "imagevector": image_vec,
            "audiovector": enc.encode_audio(),
            "videovector": [0.0] * VIDEO_DIM,
        }
        payload = {
            "coco_id": img_info["id"],
            "category": category,
            "stock_status": "instock",
            "price": round(price, 2),
            "price_band": price_band,
            "language": "en",
        }
        index_product_vectors(client, point_id, vectors, payload)
        count += 1
        if count % 500 == 0:
            logger.info("COCO: %s images", count)
    logger.info("Phase 4 done: %s COCO images → %s", count, PRODUCTS_MULTIMODAL_COLLECTION)


def phase_internvid(max_videos: int | None, qdrant_url: str | None) -> None:
    """Phase 5: InternVid (or local videos) → products_multimodal videovector."""
    from app.qdrant_client import get_qdrant_client
    from app.multimodal.indexing import (
        ensure_products_multimodal_collection,
        ensure_multimodal_payload_indexes,
        index_video_product,
        PRODUCTS_MULTIMODAL_COLLECTION,
    )

    if qdrant_url:
        import os
        os.environ["QDRANT_URL"] = qdrant_url
    client = get_qdrant_client()
    ensure_products_multimodal_collection(client)
    ensure_multimodal_payload_indexes(client, PRODUCTS_MULTIMODAL_COLLECTION)

    try:
        from datasets import load_dataset
    except ImportError:
        logger.warning("datasets not installed; use catalog + index_video_products.py for video indexing")
        return
    try:
        ds = load_dataset("internvid/InternVid-2M-v1.0", split=f"train[:{max_videos or 1000}]")
    except Exception as e:
        logger.warning("InternVid dataset not available: %s. Use index_video_products.py with local videos.", e)
        return
    count = 0
    for i, sample in enumerate(ds):
        video_path = sample.get("video_local_path") or sample.get("video_path")
        if not video_path or not Path(video_path).exists():
            continue
        try:
            index_video_product(
                client,
                sku=f"internvid_{i}",
                video_file=str(video_path),
                metadata={
                    "caption": (sample.get("queries") or ["product demo"])[0],
                    "category": "gear",
                    "stock_status": "instock",
                    "language": "en",
                },
                every_nth_frame=5,
            )
            count += 1
        except Exception as e:
            logger.debug("InternVid %s: %s", i, e)
    logger.info("Phase 5 done: %s InternVid videos → %s", count, PRODUCTS_MULTIMODAL_COLLECTION)


def phase_search(query: str, language: str, limit: int, qdrant_url: str | None) -> None:
    """Phase 6: Unified multimodal search demo."""
    if qdrant_url:
        import os
        os.environ["QDRANT_URL"] = qdrant_url
    from app.qdrant_client import get_qdrant_client
    from app.multimodal.search import multimodal_search_with_payload, build_multimodal_filter
    from app.multimodal.schema import PRODUCTS_MULTIMODAL_COLLECTION

    client = get_qdrant_client()
    results = multimodal_search_with_payload(
        client,
        text_query=query,
        collection_name=PRODUCTS_MULTIMODAL_COLLECTION,
        limit=limit,
        stock_status="instock",
        language=language or None,
    )
    print(f"Query: {query!r} (language={language})")
    print(f"Found {len(results)} multimodal matches")
    for pid, score, payload in results[:10]:
        print(f"  {pid} score={score:.3f} {payload.get('title', payload.get('category', ''))}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Multimodal dataset integration pipeline")
    parser.add_argument("phase", choices=["setup", "otto", "amazon", "coco", "internvid", "search", "all"])
    parser.add_argument("--qdrant-url", type=str, default=None, help="Qdrant URL")
    parser.add_argument("--input", type=str, default="data/otto/train.jsonl", help="OTTO train.jsonl")
    parser.add_argument("--out-dir", type=str, default="data/otto", help="OTTO output dir")
    parser.add_argument("--max-sessions", type=int, default=None, help="Cap OTTO sessions")
    parser.add_argument("--meta", type=str, default="data/amazon/meta_*.json", help="Amazon metadata path/glob")
    parser.add_argument("--max-products", type=int, default=5000, help="Cap Amazon products")
    parser.add_argument("--annotations", type=str, default="data/coco/instances_train2017.json")
    parser.add_argument("--image-dir", type=str, default="data/coco/train2017")
    parser.add_argument("--max-images", type=int, default=2000)
    parser.add_argument("--max-videos", type=int, default=1000)
    parser.add_argument("--query", type=str, default="Zelt unter 200 Franken")
    parser.add_argument("--language", type=str, default="de")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    if args.phase == "setup":
        phase_setup(args.qdrant_url)
    elif args.phase == "otto":
        phase_otto(args.input, args.out_dir, args.max_sessions, args.qdrant_url)
    elif args.phase == "amazon":
        phase_amazon(args.meta, args.max_products, args.qdrant_url)
    elif args.phase == "coco":
        phase_coco(args.annotations, args.image_dir, args.max_images, args.qdrant_url)
    elif args.phase == "internvid":
        phase_internvid(args.max_videos, args.qdrant_url)
    elif args.phase == "search":
        phase_search(args.query, args.language, args.limit, args.qdrant_url)
    elif args.phase == "all":
        phase_setup(args.qdrant_url)
        phase_otto(args.input, args.out_dir, args.max_sessions, args.qdrant_url)
        phase_amazon(args.meta, args.max_products, args.qdrant_url)
        phase_search(args.query, args.language, args.limit, args.qdrant_url)
    return None


if __name__ == "__main__":
    main()
