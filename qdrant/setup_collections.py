"""
Four Qdrant collections for OTTO multi-agent blackboard architecture.

Blackboard pattern: goals ←→ solutions ←→ episodes; products for retrieval.

Usage:
  python qdrant/setup_collections.py [--url http://localhost:6333]
"""

from __future__ import annotations

import argparse
import sys

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as qmodels
except ImportError:
    print("qdrant-client required: pip install qdrant-client", file=sys.stderr)
    sys.exit(1)

VECTOR_SIZE = 384
COLLECTIONS = {
    "products": {
        "size": VECTOR_SIZE,
        "distance": qmodels.Distance.COSINE,
        "payload_schema": ["aid", "price", "stock_status", "category", "conv_rate", "popularity"],
    },
    "goals": {
        "size": VECTOR_SIZE,
        "distance": qmodels.Distance.COSINE,
        "payload_schema": ["session", "query", "filters", "status", "user_id", "text"],
    },
    "solutions": {
        "size": VECTOR_SIZE,
        "distance": qmodels.Distance.COSINE,
        "payload_schema": ["goal_id", "products", "total_price", "confidence", "items", "text", "status"],
    },
    "episodes": {
        "size": VECTOR_SIZE,
        "distance": qmodels.Distance.COSINE,
        "payload_schema": ["goal_id", "solution_id", "success", "revenue", "outcome", "goal_text", "solution_text", "items"],
    },
}


def setup(url: str = "http://localhost:6333", recreate: bool = False) -> None:
    client = QdrantClient(url=url)
    for name, config in COLLECTIONS.items():
        try:
            client.get_collection(name)
            if recreate:
                client.delete_collection(name)
                client.create_collection(
                    collection_name=name,
                    vectors_config=qmodels.VectorParams(size=config["size"], distance=config["distance"]),
                )
                print(f"Recreated {name}")
            else:
                print(f"Collection {name} already exists")
        except Exception:
            client.create_collection(
                collection_name=name,
                vectors_config=qmodels.VectorParams(size=config["size"], distance=config["distance"]),
            )
            print(f"Created {name}")
    print("All four collections (products, goals, solutions, episodes) are ready.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:6333", help="Qdrant HTTP URL")
    parser.add_argument("--recreate", action="store_true", help="Delete and recreate collections")
    args = parser.parse_args()
    setup(url=args.url, recreate=args.recreate)


if __name__ == "__main__":
    main()
