"""Integration tests for production Supervisor (with mocked agents)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.agents.protocol import Agent
from app.agents.registry import AgentRegistry
from app.agents.supervisor_production import Supervisor
from app.agents.types import AgentContext, HealthStatus


class _MockAgent:
    """Minimal agent implementation for testing."""

    name = "shopper"
    version = "1.0"

    async def execute(self, context: AgentContext) -> dict[str, object]:
        return {"goal": context.query[:50]}

    def health_check(self) -> HealthStatus:
        return HealthStatus(healthy=True, agent_name=self.name)


@pytest.mark.asyncio
async def test_supervisor_orchestrate_empty_registry() -> None:
    """With no agents registered, orchestrate returns success with empty agents."""
    sup = Supervisor(registry=AgentRegistry())
    result = await sup.orchestrate("find tent under 200 CHF")
    assert result.trace_id
    assert result.success is True
    assert result.metrics.get("agents") == []


@pytest.mark.asyncio
async def test_supervisor_orchestrate_with_mock_agent() -> None:
    """With one agent registered, orchestrate runs it and records metrics."""
    reg = AgentRegistry()
    reg.register(_MockAgent())
    sup = Supervisor(registry=reg)
    result = await sup.orchestrate("find tent")
    assert result.success is True
    assert "shopper" in (result.metrics.get("agents") or [])
