#!/usr/bin/env python3
"""
Seed goal_solution_links with a few high-quality episodes for case-based planning.

Run after Qdrant + memory collections are up. Example:
  python -m scripts.seed_memory_episodes

Embedding: goal_text + " | " + solution_summary + " | outcome:" + outcome
"""

from __future__ import annotations

import os
import sys

# Ensure app is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.data.memory_collections import ensure_memory_collections
from app.data.goal_solution_links import upsert_episode


SEED_EPISODES = [
    {
        "goal_text": "2-person tent under 200 CHF, ship ASAP",
        "solution_summary": "TentXYZ + groundsheet; delivered in 2 days",
        "outcome": "purchased",
        "score": 0.92,
        "revenue": 180.0,
        "user_id": "user123",
    },
    {
        "goal_text": "camping gear for Zurich, budget 150 EUR, need in 3 days",
        "solution_summary": "Sleeping bag + mat bundle, in stock Zurich",
        "outcome": "success",
        "score": 0.88,
        "revenue": 95.0,
        "user_id": "user123",
    },
    {
        "goal_text": "gift finder for dad, outdoor theme, Berlin",
        "solution_summary": "MSR stove + compact kit, gift wrap",
        "outcome": "purchased",
        "score": 0.90,
        "revenue": 120.0,
        "user_id": "user456",
    },
]


def main() -> None:
    ensure_memory_collections()
    for i, ep in enumerate(SEED_EPISODES):
        eid = upsert_episode(
            goal_id=f"seed-goal-{i+1}",
            solution_id=f"seed-sol-{i+1}",
            user_id=ep["user_id"],
            goal_text=ep["goal_text"],
            solution_summary=ep["solution_summary"],
            outcome=ep["outcome"],
            score=ep["score"],
            revenue=ep.get("revenue"),
            success=ep["outcome"] in ("purchased", "success"),
        )
        print(f"Seeded episode {eid}: {ep['goal_text'][:50]}...")


if __name__ == "__main__":
    main()
