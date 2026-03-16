"""
Async supervisor orchestration with semaphore, cache, and circuit breakers.
"""
from __future__ import annotations

import asyncio
import logging
import time
import uuid
from typing import Any, AsyncIterator, Dict, List

from app.performance.async_agents import AsyncAgentPool, AgentPoolConfig
from app.performance.circuit_breaker import CircuitBreakerRegistry
from app.performance.metrics import get_metrics

logger = logging.getLogger(__name__)


class HighPerformanceSupervisor:
    """Full async streaming orchestration with batching + caching."""

    def __init__(
        self,
        agent_pool: AsyncAgentPool | None = None,
        cache: Any = None,
        embedder: Any = None,
    ) -> None:
        self.agent_pool = agent_pool or AsyncAgentPool(AgentPoolConfig())
        self.cache = cache
        self.embedder = embedder
        self.circuit_breakers = CircuitBreakerRegistry()
        self._metrics = get_metrics()

    async def orchestrate_streaming(self, query: str) -> AsyncIterator[Dict[str, Any]]:
        """Full async streaming orchestration with batching + caching."""
        trace_id = str(uuid.uuid4())
        start = time.monotonic()
        try:
            if self.cache is not None and hasattr(self.cache, "fingerprint"):
                cache_key = self.cache.fingerprint("orchestrate", query=query)
                cached = await self.cache.get(cache_key)
                if cached is not None:
                    self._metrics.record_cache_hit()
                    yield {"phase": "cache_hit", "trace_id": trace_id, "data": cached}
                    self._metrics.record_latency((time.monotonic() - start) * 1000, True, "supervisor")
                    return
            self._metrics.record_cache_miss()

            # Phase 1: parallel shopper + inventory (async batch)
            async def phase1() -> tuple:
                shopper_task = self.agent_pool.execute_batch("shopper", [{"query": query, "context": {}}])
                inventory_task = self.agent_pool.execute_batch("inventory", [{"query": query, "context": {}}])
                return await asyncio.gather(shopper_task, inventory_task)

            phase1_result = await phase1()
            shopper_out = phase1_result[0][0] if phase1_result and phase1_result[0] else {}
            inv_out = phase1_result[1][0] if phase1_result and len(phase1_result) > 1 and phase1_result[1] else {}
            yield {
                "phase": "phase1_complete",
                "trace_id": trace_id,
                "shopper_goal": shopper_out,
                "inventory": inv_out,
            }

            # Phase 2: pricing + merchandising (streaming-style chunks)
            pricing_task = self.agent_pool.execute_batch(
                "pricing",
                [{"query": query, "context": {"shopper": shopper_out, "inventory": inv_out}}],
            )
            merch_task = self.agent_pool.execute_batch(
                "merchandising",
                [{"query": query, "context": {"shopper": shopper_out, "inventory": inv_out}}],
            )
            pricing_result, merch_result = await asyncio.gather(pricing_task, merch_task)
            result = {
                "query": query,
                "shopper": shopper_out,
                "inventory": inv_out,
                "pricing": pricing_result[0] if pricing_result else {},
                "merchandising": merch_result[0] if merch_result else {},
            }
            yield {"phase": "complete", "trace_id": trace_id, "data": result}

            if self.cache is not None:
                cache_key = self.cache.fingerprint("orchestrate", query=query)
                await self.cache.set(cache_key, result)

            self._metrics.record_latency((time.monotonic() - start) * 1000, True, "supervisor")
        except Exception as e:
            logger.exception("Orchestrate failed: %s", e)
            self._metrics.record_latency((time.monotonic() - start) * 1000, False, "supervisor")
            yield {"phase": "error", "trace_id": trace_id, "error": str(e)}
