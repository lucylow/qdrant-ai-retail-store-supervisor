"""
Index products with video demos into Qdrant products_multimodal (4 named vectors).

Usage:
  python scripts/index_video_products.py --catalog data/catalog.json [--qdrant-url http://localhost:6333]
  Or with a directory of (video, metadata) pairs for hackathon Day 1.

Catalog JSON format (per product):
  {
    "sku": "TENT_221",
    "title": "Lightweight 2-person tent",
    "desc": "Waterproof, 2.1kg, 2-person.",
    "image": "path/to/product.jpg",
    "video": "path/to/demo_30s.mp4",
    "price": 179,
    "region": "Zurich"
  }
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.qdrant_client import get_qdrant_client
from app.data.collections import ensure_all_collections
from app.multimodal.indexing import ensure_products_multimodal_collection, index_video_product


def load_catalog(path: str) -> list:
    with open(path) as f:
        data = json.load(f)
    return data if isinstance(data, list) else [data]


def main() -> None:
    parser = argparse.ArgumentParser(description="Index video products into Qdrant products_multimodal")
    parser.add_argument("--catalog", type=str, help="JSON file with list of product entries (sku, title, desc, image, video, ...)")
    parser.add_argument("--qdrant-url", type=str, default=None, help="Qdrant URL (default from env)")
    parser.add_argument("--every-nth-frame", type=int, default=5, help="Sample every Nth frame for video vector")
    args = parser.parse_args()

    if not args.catalog or not Path(args.catalog).exists():
        # Demo: seed 2 products without video (text + image only) so multimodal collection has data
        print("No --catalog or file not found. Ensuring collection and exiting (use --catalog for real index).")
        ensure_all_collections()
        client = get_qdrant_client()
        ensure_products_multimodal_collection(client)
        return

    ensure_all_collections()
    client = get_qdrant_client()
    ensure_products_multimodal_collection(client)
    catalog = load_catalog(args.catalog)
    for i, item in enumerate(catalog):
        sku = item.get("sku") or item.get("id") or f"product_{i}"
        video = item.get("video")
        metadata = {k: v for k, v in item.items() if k not in ("video", "sku")}
        if video and Path(video).exists():
            try:
                index_video_product(
                    client,
                    sku=sku,
                    video_file=video,
                    metadata=metadata,
                    every_nth_frame=args.every_nth_frame,
                )
                print(f"Indexed video product: {sku}")
            except Exception as e:
                print(f"Skip {sku}: {e}")
        else:
            # Text + image only (no video)
            from app.multimodal.indexing import index_product_vectors
            from app.multimodal.encoders import MultimodalProductEncoders
            from app.multimodal.schema import IMAGE_DIM, VIDEO_DIM
            enc = MultimodalProductEncoders()
            text_vec = enc.encode_text(f"{metadata.get('title', '')} {metadata.get('desc', '')}")
            image_path = metadata.get("image")
            image_vec = enc.encode_image(image_path) if image_path and Path(image_path).exists() else None
            if image_vec is None or len(image_vec) != IMAGE_DIM:
                image_vec = [0.0] * IMAGE_DIM
            vectors = {
                "textvector": text_vec,
                "imagevector": image_vec,
                "audiovector": enc.encode_audio(),
                "videovector": [0.0] * VIDEO_DIM,
            }
            index_product_vectors(client, sku, vectors, metadata)
            print(f"Indexed product (no video): {sku}")
    print(f"Done. Indexed {len(catalog)} products.")


if __name__ == "__main__":
    main()
