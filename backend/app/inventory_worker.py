from __future__ import annotations

import logging
import time
from typing import Optional

from qdrant_client import QdrantClient

from app.shopping_agents import InventoryAgent, bootstrap_agent_collections

logger = logging.getLogger(__name__)


def run_inventory_worker(
    client: Optional[QdrantClient] = None,
    poll_interval_seconds: float = 2.0,
    max_goals_per_tick: int = 5,
) -> None:
    """
    Simple background worker loop that:
    - polls Qdrant for open goals
    - lets InventoryAgent create solutions + episodes
    - sleeps for a short interval between polls

    Intended to be run as a separate process alongside the web/API layer.
    """
    logging.basicConfig(level=logging.INFO)
    client = client or bootstrap_agent_collections()
    inventory = InventoryAgent(client)

    logger.info(
        "Starting inventory worker (poll_interval=%.1fs, max_goals_per_tick=%d)",
        poll_interval_seconds,
        max_goals_per_tick,
    )

    while True:
        try:
            solved = inventory.solve_once_for_open_goals(max_goals=max_goals_per_tick)
            logger.info("Inventory worker tick: solved %d goals", len(solved))
        except Exception as exc:  # noqa: BLE001
            logger.exception("Inventory worker tick failed: %s", exc)

        time.sleep(poll_interval_seconds)


if __name__ == "__main__":
    run_inventory_worker()

