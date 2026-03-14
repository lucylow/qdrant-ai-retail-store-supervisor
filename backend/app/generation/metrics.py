"""
GENAI-HACKATHON: Live generation quality metrics - groundedness, coherence, first-pass success.
For dashboard and benchmark reporting.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class GenerationQualityMetrics:
    groundedness: float  # 0-1, higher = more grounded in context
    coherence: float  # 0-1, higher = more coherent
    first_pass_success: bool
    latency_ms: int
    retry_count: int
    hallucination_score: float
    validation_passed: bool


_metrics_buffer: List[Dict[str, Any]] = []


def record_generation(
    groundedness: float,
    coherence: float,
    first_pass_success: bool,
    latency_ms: int,
    retry_count: int = 0,
    hallucination_score: float = 0.0,
    validation_passed: bool = True,
    template: Optional[str] = None,
) -> None:
    """Record one generation for live metrics (in-memory buffer for dashboard)."""
    entry = {
        "groundedness": groundedness,
        "coherence": coherence,
        "first_pass_success": first_pass_success,
        "latency_ms": latency_ms,
        "retry_count": retry_count,
        "hallucination_score": hallucination_score,
        "validation_passed": validation_passed,
        "template": template or "unknown",
        "ts": time.time(),
    }
    _metrics_buffer.append(entry)
    # Keep last 1000
    while len(_metrics_buffer) > 1000:
        _metrics_buffer.pop(0)
    logger.debug(
        "GenAI metrics",
        extra={"event": "genai.metrics", "groundedness": groundedness, "hallucination_score": hallucination_score},
    )


def get_recent_metrics(n: int = 100) -> List[Dict[str, Any]]:
    """Return last n recorded metrics for dashboard."""
    return _metrics_buffer[-n:]


def compute_aggregates(metrics: Optional[List[Dict[str, Any]]] = None) -> Dict[str, float]:
    """
    Compute aggregate metrics: avg groundedness, avg hallucination, first-pass rate, avg latency.
    """
    data = metrics or _metrics_buffer
    if not data:
        return {
            "groundedness_avg": 0.0,
            "hallucination_avg": 0.0,
            "first_pass_rate": 0.0,
            "latency_avg_ms": 0.0,
        }
    n = len(data)
    groundedness_avg = sum(m.get("groundedness", 0) for m in data) / n
    hallucination_avg = sum(m.get("hallucination_score", 0) for m in data) / n
    first_pass_rate = sum(1 for m in data if m.get("first_pass_success")) / n
    latency_avg = sum(m.get("latency_ms", 0) for m in data) / n
    return {
        "groundedness_avg": groundedness_avg,
        "hallucination_avg": hallucination_avg,
        "first_pass_rate": first_pass_rate,
        "latency_avg_ms": latency_avg,
    }


def groundedness_from_citations(output: str, context_count: int) -> float:
    """
    Simple groundedness: fraction of output that is cited (has [0], [1] refs).
    If no context, return 0.5 neutral.
    """
    if context_count == 0:
        return 0.5
    import re
    citations = re.findall(r"\[\d+\]", output)
    if not output.strip():
        return 0.0
    # More citations relative to length = more grounded
    cited_ratio = min(1.0, len(citations) * 0.3)
    return 0.5 + cited_ratio * 0.5


def coherence_heuristic(output: str) -> float:
    """Simple coherence: has structure (sentences, or JSON)."""
    if not output or len(output) < 10:
        return 0.0
    if output.strip().startswith("{") or output.strip().startswith("["):
        return 0.9  # JSON
    if "." in output and len(output.split()) > 5:
        return 0.8  # Multi-sentence
    return 0.5


__all__: Sequence[str] = [
    "GenerationQualityMetrics",
    "record_generation",
    "get_recent_metrics",
    "compute_aggregates",
    "groundedness_from_citations",
    "coherence_heuristic",
]
