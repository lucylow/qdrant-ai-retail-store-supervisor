"""Load tests and benchmark assertions for async agent pool."""
from __future__ import annotations

import asyncio

import pytest

from app.performance.async_agents import AsyncAgentPool, AgentPoolConfig


@pytest.fixture
def pool() -> AsyncAgentPool:
    config = AgentPoolConfig(semaphore_limit=5, max_concurrent=4)
    pool = AsyncAgentPool(config=config)
    pool.register_agent("echo", lambda q, ctx: {"query": q, "context": ctx})
    return pool


@pytest.mark.asyncio
async def test_execute_batch(pool: AsyncAgentPool) -> None:
    inputs = [{"query": f"q{i}", "context": {}} for i in range(3)]
    results = await pool.execute_batch("echo", inputs)
    assert len(results) == 3
    assert results[0].get("ok") is True
    assert results[0].get("data", {}).get("query") == "q0"


@pytest.mark.asyncio
async def test_unknown_agent(pool: AsyncAgentPool) -> None:
    results = await pool.execute_batch("unknown", [{"query": "x", "context": {}}])
    assert len(results) == 1
    assert results[0].get("ok") is False
