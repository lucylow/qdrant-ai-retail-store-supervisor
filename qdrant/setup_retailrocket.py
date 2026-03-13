"""
Qdrant collections for RetailRocket multi-agent blackboard.

- retailrocket_items: 384-dim product vectors (from process_retailrocket.py)
- visitor_sessions: 384-dim session context (417K sessions)
- goals: 384-dim (Shopper Agent)
- solutions: 384-dim (Inventory Agent)

Usage:
  python qdrant/setup_retailrocket.py [--url http://localhost:6333] [--recreate]
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
    "retailrocket_items": {
        "vectors_config": lambda: qmodels.VectorParams(size=VECTOR_SIZE, distance=qmodels.Distance.COSINE),
    },
    "visitor_sessions": {
        "vectors_config": lambda: qmodels.VectorParams(size=VECTOR_SIZE, distance=qmodels.Distance.COSINE),
    },
    "goals": {
        "vectors_config": lambda: qmodels.VectorParams(size=VECTOR_SIZE, distance=qmodels.Distance.COSINE),
    },
    "solutions": {
        "vectors_config": lambda: qmodels.VectorParams(size=VECTOR_SIZE, distance=qmodels.Distance.COSINE),
    },
}


def setup(url: str = "http://localhost:6333", recreate: bool = False) -> None:
    client = QdrantClient(url=url)
    for name, config in COLLECTIONS.items():
        vec_config = config["vectors_config"]()
        try:
            client.get_collection(name)
            if recreate:
                client.delete_collection(name)
                client.create_collection(collection_name=name, vectors_config=vec_config)
                print(f"Recreated {name}")
            else:
                print(f"Collection {name} already exists")
        except Exception:
            client.create_collection(collection_name=name, vectors_config=vec_config)
            print(f"Created {name}")
    print("RetailRocket collections (retailrocket_items, visitor_sessions, goals, solutions) are ready.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:6333", help="Qdrant HTTP URL")
    parser.add_argument("--recreate", action="store_true", help="Delete and recreate collections")
    args = parser.parse_args()
    setup(url=args.url, recreate=args.recreate)


if __name__ == "__main__":
    main()
