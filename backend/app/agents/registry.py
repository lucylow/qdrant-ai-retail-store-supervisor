"""Agent discovery and health checks for production orchestration."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from app.agents.types import HealthStatus
from app.core.exceptions import AgentNotRegisteredError
from app.core.logger import get_logger

if TYPE_CHECKING:
    from app.agents.protocol import Agent

logger = get_logger(__name__)


class AgentRegistry:
    """Register and resolve agents by name with health checks."""

    def __init__(self) -> None:
        self._agents: dict[str, Agent] = {}

    def register(self, agent: Agent) -> None:
        """Register an agent under its name."""
        self._agents[agent.name] = agent
        logger.info("agent_registered", agent=agent.name, version=getattr(agent, "version", ""))

    def get(self, name: str) -> Agent:
        """Return agent by name; raises AgentNotRegisteredError if missing."""
        if name not in self._agents:
            raise AgentNotRegisteredError(f"Agent not registered: {name}")
        return self._agents[name]

    def names(self) -> list[str]:
        """Return all registered agent names."""
        return list(self._agents.keys())

    def health_check(self, name: str | None = None) -> list[HealthStatus]:
        """Run health check for one agent or all."""
        if name is not None:
            agents = [self.get(name)]
        else:
            agents = list(self._agents.values())
        results: list[HealthStatus] = []
        for a in agents:
            start_ms = time.perf_counter() * 1000
            try:
                status = a.health_check()
                latency_ms = int((time.perf_counter() * 1000) - start_ms)
                results.append(
                    HealthStatus(
                        healthy=status.healthy,
                        agent_name=a.name,
                        message=status.message,
                        latency_ms=latency_ms,
                    )
                )
            except Exception as e:  # noqa: BLE001
                results.append(
                    HealthStatus(
                        healthy=False,
                        agent_name=a.name,
                        message=str(e),
                        latency_ms=int((time.perf_counter() * 1000) - start_ms),
                    )
                )
        return results
