# scripts/ingest_demo.py
"""
Minimal ingestion script for demo data: reads demo_data/ and upserts to Qdrant.
Usage: python scripts/ingest_demo.py --collection demo_products
"""
import argparse
import os
import logging

from app.qdrant_client import get_qdrant_client, ensure_collection
from app.qdrant_utils import upsert_points
from app.embeddings import embed_texts, embed_image
from app.config import COLL_PRODUCTS

logging.basicConfig(level=logging.INFO)


def chunk_text(text: str, chunk_size: int = 256, overlap: int = 64):
    tokens = text.split()
    out = []
    i = 0
    while i < len(tokens):
        out.append(" ".join(tokens[i : i + chunk_size]))
        i += max(1, chunk_size - overlap)
    return out


def ingest_folder(data_dir: str, collection: str):
    client = get_qdrant_client()
    ensure_collection(client, collection, vector_size=384)
    ids, vecs, payloads = [], [], []
    for root, _, files in os.walk(data_dir):
        for f in files:
            path = os.path.join(root, f)
            if f.lower().endswith((".txt", ".md")):
                with open(path, encoding="utf-8") as fh:
                    text = fh.read()
                chunks = chunk_text(text)
                emb = embed_texts(chunks)
                for idx, ch in enumerate(chunks):
                    ids.append(f"{os.path.relpath(path)}::chunk::{idx}")
                    vecs.append(emb[idx].tolist())
                    payloads.append({"source": path, "text": ch})
            elif f.lower().endswith((".png", ".jpg", ".jpeg")):
                img_emb = embed_image(path)
                ids.append(f"{os.path.relpath(path)}::img")
                vecs.append(img_emb.tolist())
                payloads.append({"source": path, "type": "image"})
            if len(ids) >= 512:
                upsert_points(client, collection, vecs, payloads, ids)
                ids, vecs, payloads = [], [], []
    if ids:
        upsert_points(client, collection, vecs, payloads, ids)
    logging.info("Ingestion complete.")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data-dir", default="demo_data")
    p.add_argument("--collection", default=COLL_PRODUCTS)
    args = p.parse_args()
    ingest_folder(args.data_dir, args.collection)

