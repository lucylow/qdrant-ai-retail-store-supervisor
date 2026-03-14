#!/usr/bin/env python3
"""
GENAI-HACKATHON: Mine and rank examples for few-shot improvement.
Scans episodic memory (or demo data), filters success=true, ranks by recency + similarity.
Usage: python scripts/fewshot_mining.py [--goal-count 100] [--output demo_data/fewshot_examples.json]
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Sequence

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from app.data.collections import COLL_EPISODES
    from app.qdrant_client import get_qdrant_client
    HAS_APP = True
except ImportError:
    HAS_APP = False


def mine_episodic_goals(goal_count: int = 100) -> List[Dict[str, Any]]:
    """
    Scroll episodic collection, keep success outcomes, return up to goal_count.
    """
    if not HAS_APP:
        return _mock_goals(goal_count)
    client = get_qdrant_client()
    points, _ = client.scroll(
        collection_name=COLL_EPISODES,
        limit=min(goal_count * 3, 500),
        with_payload=True,
        with_vectors=False,
    )
    results: List[Dict[str, Any]] = []
    for p in points:
        payload = p.payload or {}
        if payload.get("outcome") != "success":
            continue
        results.append({
            "goal_id": payload.get("goal_id"),
            "outcome": payload.get("outcome"),
            "success_prob": payload.get("success_prob"),
            "bundle_skus": payload.get("bundle_skus", []),
            "bundle_total_price_eur": payload.get("bundle_total_price_eur"),
        })
        if len(results) >= goal_count:
            break
    return results


def _mock_goals(n: int) -> List[Dict[str, Any]]:
    """Return mock goals when Qdrant not available."""
    return [
        {
            "goal_id": f"goal_{i}",
            "outcome": "success",
            "success_prob": 0.9,
            "bundle_skus": ["SKU1", "SKU2"],
            "bundle_total_price_eur": 45.0,
        }
        for i in range(min(n, 20))
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Mine few-shot examples from episodic memory")
    parser.add_argument("--goal-count", type=int, default=100)
    parser.add_argument("--output", default=None, help="JSON file to write mined examples")
    args = parser.parse_args()

    goals = mine_episodic_goals(args.goal_count)
    logger.info("Mined %d goal examples", len(goals))

    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(goals, f, indent=2)
        logger.info("Wrote %s", path)


if __name__ == "__main__":
    main()
