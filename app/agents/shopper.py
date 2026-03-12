from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import List, Mapping, Sequence
from uuid import uuid4

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ShopperGoal:
    goal_id: str
    query: str
    intent: str
    budget_eur: float | None
    region: str | None
    urgency_days: int | None
    clarified: bool
    latency_ms: int

    def summary(self) -> str:
        parts: List[str] = [self.intent]
        if self.budget_eur is not None:
            parts.append(f"budget≤€{self.budget_eur:.0f}")
        if self.region:
            parts.append(self.region)
        if self.urgency_days is not None:
            parts.append(f"<={self.urgency_days}d")
        return " | ".join(parts)


class ShopperAgent:
    """
    Lightweight intent and goal extraction.

    In production this would host a few-shot CoT LLM prompt,
    but here we implement a deterministic parser so tests are stable.
    """

    def parse_goal(self, query: str, goal_id: str | None = None) -> ShopperGoal:
        # AUTONOMOUS-AGENT-HACKATHON: shopper goal extraction for demo query.
        started = time.perf_counter()
        goal_uuid = goal_id or str(uuid4())

        text = query.lower()
        budget: float | None = None
        urgency_days: int | None = None
        region: str | None = None

        if "€" in text:
            try:
                after = text.split("€", maxsplit=1)[1]
                digits = "".join(ch for ch in after if ch.isdigit())
                if digits:
                    budget = float(digits)
            except Exception:  # noqa: BLE001
                budget = None

        for token in ["berlin", "paris", "zurich", "london"]:
            if token in text:
                region = token.title()
                break

        if "<3 days" in text or "within 3 days" in text:
            urgency_days = 3
        elif "tomorrow" in text:
            urgency_days = 1

        intent = "purchase_bundle"
        latency_ms = int((time.perf_counter() - started) * 1000)
        logger.info(
            "Parsed shopper goal",
            extra={
                "event": "shopper.parse_goal",
                "goal_id": goal_uuid,
                "budget_eur": budget,
                "region": region,
                "urgency_days": urgency_days,
                "latency_ms": latency_ms,
            },
        )
        return ShopperGoal(
            goal_id=goal_uuid,
            query=query,
            intent=intent,
            budget_eur=budget,
            region=region,
            urgency_days=urgency_days,
            clarified=True,
            latency_ms=latency_ms,
        )


__all__: Sequence[str] = ["ShopperAgent", "ShopperGoal"]

