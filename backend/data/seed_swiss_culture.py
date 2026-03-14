"""
Seed Qdrant with Swiss cultural metadata for episodes (e.g. Bio-Milch Zürich HB).
Run: python -m data.seed_swiss_culture (or python data/seed_swiss_culture.py)
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure app is on path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# After path fix, optional Qdrant upsert (requires running Qdrant + embeddings)
SWISS_EPISODES = [
    {
        "query_de": "Bio-Milch laktosefrei Zürich HB",
        "cultural_context": {
            "cooperative_preference": True,
            "sustainability_high": True,
            "urban_pickup": True,
            "fondue_season_boost": True,
        },
    },
    {
        "query_de": "Fondue-Käse morgen 10h Genève",
        "cultural_context": {
            "cooperative_preference": True,
            "fondue_season_boost": True,
            "pickup_window": "08:00-12:00",
        },
    },
]


def main() -> None:
    try:
        from app.qdrant_client import get_qdrant_client
        from app.embeddings import embed_texts
        from qdrant_client.http import models as rest

        client = get_qdrant_client()
        coll = "swiss_cultural_episodes"
        texts = [e["query_de"] for e in SWISS_EPISODES]
        vectors = embed_texts(texts)
        points = [
            rest.PointStruct(
                id=i,
                vector=vec.tolist() if hasattr(vec, "tolist") else list(vec),
                payload={**ep, "tenant": "coop"},
            )
            for i, (ep, vec) in enumerate(zip(SWISS_EPISODES, vectors))
        ]
        client.upsert(collection_name=coll, points=points)
        print(f"Upserted {len(points)} Swiss cultural episodes into {coll}")
    except Exception as e:
        print("Seed skipped (Qdrant or embeddings not available):", e)


if __name__ == "__main__":
    main()
