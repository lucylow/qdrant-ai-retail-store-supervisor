"""
Seed Qdrant with Swiss holiday episodes for semantic matching.
Run: python -m data.seed_holidays (or python data/seed_holidays.py)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

HOLIDAY_EPISODES = [
    {
        "query": "Bio-Milch Christmas",
        "demand_multiplier": 4.0,
        "category": "dairy",
        "stockout_risk": 0.25,
        "date": "2025-12-24",
    },
    {
        "query": "Fondue cheese November",
        "demand_multiplier": 1.5,
        "category": "cheese",
        "stockout_risk": 0.5,
        "date": "2025-11-15",
    },
]


def main() -> None:
    try:
        from app.qdrant_client import get_qdrant_client
        from app.embeddings import embed_texts
        from qdrant_client.http import models as rest

        client = get_qdrant_client()
        coll = "holiday_episodes"
        texts = [e["query"] for e in HOLIDAY_EPISODES]
        vectors = embed_texts(texts)
        points = [
            rest.PointStruct(
                id=i,
                vector=vec.tolist() if hasattr(vec, "tolist") else list(vec),
                payload=ep,
            )
            for i, (ep, vec) in enumerate(zip(HOLIDAY_EPISODES, vectors))
        ]
        client.upsert(collection_name=coll, points=points)
        print(f"Upserted {len(points)} holiday episodes into {coll}")
    except Exception as e:
        print("Seed skipped (Qdrant or embeddings not available):", e)


if __name__ == "__main__":
    main()
