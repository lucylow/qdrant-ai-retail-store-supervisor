from __future__ import annotations

import asyncio
import logging
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Sequence

from qdrant_client.http import models as rest

from app.agents.inventory import InventoryPlan
from app.agents.pricing import PricingPlan
from app.agents.supervisor import ReasoningGraph
from app.config import COLL_EPISODES
from app.qdrant_client import get_qdrant_client


logger = logging.getLogger(__name__)


class EpisodeOutcome(str, Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILURE = "failure"
    UNKNOWN = "unknown"


@dataclass(slots=True)
class EpisodicRecord:
    goal_id: str
    outcome: EpisodeOutcome
    success_prob: float
    total_latency_ms: int
    bundle_total_price_eur: float
    pricing_margin_pct: float


class EpisodicMemoryStore:
    """
    Simple success-weighted episodic memory buffer backed by Qdrant.
    """

    async def record_episode(
        self,
        goal_id: str,
        graph: ReasoningGraph,
        bundle: InventoryPlan,
        pricing: PricingPlan,
        merchandising: object,
        outcome: EpisodeOutcome,
    ) -> None:
        # AUTONOMOUS-AGENT-HACKATHON: episodic memory for self-improving RAG.
        client = get_qdrant_client()
        record = EpisodicRecord(
            goal_id=goal_id,
            outcome=outcome,
            success_prob=graph.success_prob,
            total_latency_ms=graph.latency_ms,
            bundle_total_price_eur=bundle.total_price_eur,
            pricing_margin_pct=pricing.margin_pct,
        )
        payload = asdict(record)
        payload["outcome"] = record.outcome.value
        weight = record.success_prob
        vector = [float(weight)] * 4
        points = [
            rest.PointStruct(
                id=goal_id,
                payload=payload,
                vector=vector,
            )
        ]
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            client.upsert,
            COLL_EPISODES,
            points,
        )
        logger.info(
            "Recorded episodic memory",
            extra={
                "event": "episodic.record",
                "goal_id": goal_id,
                "outcome": outcome.value,
                "success_prob": graph.success_prob,
            },
        )


__all__: Sequence[str] = ["EpisodicMemoryStore", "EpisodeOutcome", "EpisodicRecord"]

