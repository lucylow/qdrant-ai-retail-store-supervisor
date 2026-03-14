"""Prometheus metrics and tracing for production observability."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from prometheus_client import Counter, Histogram

# Agent execution
AGENT_CALLS = Counter(
    "store_supervisor_agent_calls_total",
    "Total agent invocations",
    ["agent", "status"],
)
AGENT_LATENCY = Histogram(
    "store_supervisor_agent_duration_seconds",
    "Agent execution duration",
    ["agent"],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0),
)

# Retrieval
RETRIEVAL_CALLS = Counter(
    "store_supervisor_retrieval_calls_total",
    "Retrieval calls",
    ["collection", "status"],
)
RETRIEVAL_LATENCY = Histogram(
    "store_supervisor_retrieval_duration_seconds",
    "Retrieval duration",
    ["collection"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0),
)

# Orchestration
ORCHESTRATION_TOTAL = Counter(
    "store_supervisor_orchestrations_total",
    "Orchestration runs",
    ["status"],
)
ORCHESTRATION_LATENCY = Histogram(
    "store_supervisor_orchestration_duration_seconds",
    "Full orchestration duration",
    buckets=(0.5, 1.0, 2.0, 5.0, 10.0, 30.0),
)


class ProductionMetrics:
    """Record and expose production metrics (Prometheus-ready)."""

    def record_agent_call(self, agent: str, status: str = "success") -> None:
        """Record one agent invocation."""
        AGENT_CALLS.labels(agent=agent, status=status).inc()

    def record_agent_latency(self, agent: str, duration_seconds: float) -> None:
        """Record agent execution duration."""
        AGENT_LATENCY.labels(agent=agent).observe(duration_seconds)

    def record_retrieval(
        self,
        collection: str,
        status: str,
        duration_seconds: float,
    ) -> None:
        """Record retrieval call and duration."""
        RETRIEVAL_CALLS.labels(collection=collection, status=status).inc()
        RETRIEVAL_LATENCY.labels(collection=collection).observe(duration_seconds)

    def record_orchestration(
        self,
        trace_id: UUID,
        success: bool,
        duration_seconds: float,
    ) -> dict[str, Any]:
        """Record orchestration run and return metrics snapshot."""
        status = "success" if success else "failure"
        ORCHESTRATION_TOTAL.labels(status=status).inc()
        ORCHESTRATION_LATENCY.observe(duration_seconds)
        return {
            "trace_id": str(trace_id),
            "success": success,
            "duration_seconds": round(duration_seconds, 3),
        }
