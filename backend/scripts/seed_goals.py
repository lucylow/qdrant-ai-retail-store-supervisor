#!/usr/bin/env python3
"""
Create a few demo goals in the memory store so the supervisor can pick them up.
"""

import logging

from app.agents.memory import get_memory

logging.basicConfig(level=logging.INFO)
mem = get_memory()

goals = [
    {
        "id": "goal_demo_1",
        "goal_text": "Find a 2-person tent under 200 CHF deliver to Zurich",
        "status": "open",
        "region": "Zurich",
    },
    {
        "id": "goal_demo_2",
        "goal_text": "Bundle camping essentials for family weekend",
        "status": "open",
        "region": "Zurich",
    },
]

for g in goals:
    try:
        from app.embeddings import embed_texts

        vec = embed_texts([g["goal_text"]])[0].tolist()
    except Exception:  # pragma: no cover - best-effort embedding
        vec = [0.0] * 384
    mem.upsert("goals", g["id"], vec, g)
    logging.info("Seeded goal %s", g["id"])

print("Seeded goals.")

