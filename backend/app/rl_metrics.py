from __future__ import annotations

"""
Lightweight logging helpers for RL-enhanced reasoning:

- Track answer quality, retrieval relevance, and user feedback over time.
- Can be extended to push metrics to Prometheus, files, or dashboards.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class InteractionMetrics:
    answer_quality: float
    retrieval_relevance: float
    user_feedback: float
    reward: float


@dataclass
class RLMetricsLogger:
    history: List[InteractionMetrics] = field(default_factory=list)

    def log(
        self,
        answer_quality: float,
        retrieval_relevance: float,
        user_feedback: float,
        reward: float,
    ) -> None:
        self.history.append(
            InteractionMetrics(
                answer_quality=answer_quality,
                retrieval_relevance=retrieval_relevance,
                user_feedback=user_feedback,
                reward=reward,
            )
        )

    def last(self) -> InteractionMetrics | None:
        return self.history[-1] if self.history else None

    def averages(self) -> dict[str, float]:
        if not self.history:
            return {
                "answer_quality": 0.0,
                "retrieval_relevance": 0.0,
                "user_feedback": 0.0,
                "reward": 0.0,
            }
        n = float(len(self.history))
        aq = sum(h.answer_quality for h in self.history) / n
        rr = sum(h.retrieval_relevance for h in self.history) / n
        uf = sum(h.user_feedback for h in self.history) / n
        rw = sum(h.reward for h in self.history) / n
        return {
            "answer_quality": aq,
            "retrieval_relevance": rr,
            "user_feedback": uf,
            "reward": rw,
        }


__all__ = ["RLMetricsLogger", "InteractionMetrics"]

