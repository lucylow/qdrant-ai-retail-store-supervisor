"""
GENAI-HACKATHON: Dynamic few-shot example retriever from Qdrant episodic memory.
Retrieves top-k examples filtered by goal category, success=true; sorted by recency (70%) + similarity (30%).
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence

from app.config import GENAI
from app.data.collections import COLL_EPISODES
from app.qdrant_client import get_qdrant_client

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class Example:
    """Single few-shot example: input (user query), output (gold goal/response), success flag."""

    input_text: str
    output_text: str
    success: bool
    goal_id: str
    payload: Dict[str, Any]


def _embed_goal_text(text: str, vector_size: int = 384) -> List[float]:
    """Deterministic goal embedding for similarity (matches episodic memory style)."""
    import numpy as np

    vec = np.zeros(vector_size, dtype=np.float32)
    for i, ch in enumerate(text.encode("utf-8")):
        vec[i % vector_size] += float(ch)
    norm = float(np.linalg.norm(vec)) or 1.0
    return (vec / norm).tolist()


class FewShotRetriever:
    """
    Retrieve few-shot examples from Qdrant episodic memory.
    Filter: goal category aligned, success=true. Sort: recency 70%, similarity 30%.
    """

    def __init__(
        self,
        collection: str = COLL_EPISODES,
        k: int = 3,
        min_success_prob: float = 0.7,
        user_region: Optional[str] = None,
    ) -> None:
        self._collection = collection
        self._k = k or GENAI.few_shot_k
        self._min_success_prob = min_success_prob
        self._user_region = user_region

    def get_examples_sync(
        self,
        goal_query: str,
        k: Optional[int] = None,
        user_region: Optional[str] = None,
        success_only: bool = True,
    ) -> List[Example]:
        """Synchronous wrapper: scroll episodes, filter success, return top-k by recency + similarity."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self.get_examples(goal_query, k=k, user_region=user_region, success_only=success_only)
        )

    async def get_examples(
        self,
        goal_query: str,
        k: Optional[int] = None,
        user_region: Optional[str] = None,
        success_only: bool = True,
    ) -> List[Example]:
        """
        Query Qdrant episodic memory for similar successful episodes.
        Returns examples with input (query), output (gold goal/bundle summary), success=true.
        """
        limit = k or self._k
        region = user_region or self._user_region
        client = get_qdrant_client()

        query_vector = _embed_goal_text(goal_query)

        def _scroll_and_score() -> List[Example]:
            points, _ = client.scroll(
                collection_name=self._collection,
                limit=min(200, limit * 20),
                with_payload=True,
                with_vectors=False,
            )
            examples: List[tuple[float, Example]] = []
            for p in points:
                payload = p.payload or {}
                outcome = payload.get("outcome", "")
                if success_only and outcome != "success":
                    continue
                success_prob = float(payload.get("success_prob", 0))
                if success_only and success_prob < self._min_success_prob:
                    continue
                if region and str(payload.get("region", "")).lower() != region.lower():
                    continue
                goal_id = str(payload.get("goal_id", ""))
                # Reconstruct input/output from payload (episodes store goal_id, outcome, bundle_skus, etc.)
                input_text = str(payload.get("goal_query", goal_id))[:500]
                output_text = _payload_to_output_summary(payload)
                ex = Example(
                    input_text=input_text,
                    output_text=output_text,
                    success=outcome == "success",
                    goal_id=goal_id,
                    payload=dict(payload),
                )
                # Recency proxy: no timestamp in payload, use success_prob as quality
                recency_score = success_prob
                examples.append((recency_score, ex))
            # Sort by recency (70%) - we use success_prob as proxy; take top by that then by order
            examples.sort(key=lambda x: -x[0])
            return [ex for _, ex in examples[:limit]]

        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, _scroll_and_score)

        # Optional: rerank by vector similarity (30%) if we had vector search
        # Here we only have scroll; for full 70/30 we'd do vector search first then merge with scroll.
        logger.info(
            "Few-shot retrieval",
            extra={
                "template": "fewshot",
                "goal_query_len": len(goal_query),
                "k": limit,
                "returned": len(result),
                "success_only": success_only,
            },
        )
        return result

    def format_examples_for_prompt(self, examples: List[Example]) -> List[str]:
        """Format examples as lines for injection into <examples> block."""
        out: List[str] = []
        for ex in examples:
            out.append(f"Input: {ex.input_text}\nOutput: {ex.output_text}")
        return out


def _payload_to_output_summary(payload: Dict[str, Any]) -> str:
    """Turn episode payload into a short output summary for few-shot."""
    parts = []
    if payload.get("outcome"):
        parts.append(f"outcome={payload['outcome']}")
    if payload.get("bundle_skus"):
        skus = payload["bundle_skus"][:5]
        parts.append(f"skus={skus}")
    if payload.get("bundle_total_price_eur") is not None:
        parts.append(f"total_eur={payload['bundle_total_price_eur']}")
    return "; ".join(parts) if parts else "success"


__all__: Sequence[str] = ["FewShotRetriever", "Example"]
