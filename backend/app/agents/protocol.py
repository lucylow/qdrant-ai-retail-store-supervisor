"""Typed Agent protocol and decorators (production)."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Protocol, runtime_checkable

from app.agents.types import AgentContext, HealthStatus
from app.core.logger import get_logger
from app.core.metrics import ProductionMetrics

logger = get_logger(__name__)
_metrics = ProductionMetrics()


@runtime_checkable
class Agent(Protocol):
    """Production agent protocol: execute with context, health_check."""

    name: str
    version: str

    @abstractmethod
    async def execute(self, context: AgentContext) -> dict[str, Any]:
        """Execute one agent step; returns result dict."""
        ...

    @abstractmethod
    def health_check(self) -> HealthStatus:
        """Return current health status."""
        ...


def record_agent_success(agent_name: str, duration_seconds: float) -> None:
    """Record successful agent execution for metrics."""
    _metrics.record_agent_call(agent_name, "success")
    _metrics.record_agent_latency(agent_name, duration_seconds)


def record_agent_failure(agent_name: str, duration_seconds: float) -> None:
    """Record failed agent execution for metrics."""
    _metrics.record_agent_call(agent_name, "failure")
    _metrics.record_agent_latency(agent_name, duration_seconds)
