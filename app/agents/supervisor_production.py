"""Production supervisor: parallel orchestration with timeout and retry."""

from __future__ import annotations

import asyncio
import time
from uuid import UUID, uuid4

from app.agents.protocol import record_agent_failure, record_agent_success
from app.agents.registry import AgentRegistry
from app.agents.types import AgentContext, OrchestrationResult
from app.core.exceptions import AgentError
from app.core.logger import get_logger
from app.core.metrics import ProductionMetrics
from app.utils.retry import retry_on_exception

logger = get_logger(__name__)
ORCHESTRATION_TIMEOUT_S = 30.0


class Supervisor:
    """Production orchestrator: parallel phases + timeout + metrics."""

    def __init__(self, registry: AgentRegistry | None = None) -> None:
        self.registry = registry or AgentRegistry()
        self.metrics = ProductionMetrics()

    @retry_on_exception(max_attempts=3, exceptions=(AgentError, asyncio.TimeoutError))
    async def orchestrate(self, query: str) -> OrchestrationResult:
        """
        Full agent orchestration with parallel execution and timeout.

        Phase 1: parallel shopper + inventory (if registered).
        Phase 2: sequential pricing + merchandising (if registered).
        """
        trace_id = str(uuid4())
        ctx = AgentContext(query=query.strip(), trace_id=trace_id)
        start = time.perf_counter()
        try:
            async with asyncio.timeout(ORCHESTRATION_TIMEOUT_S):
                phase1_names = [n for n in ["shopper", "inventory"] if n in self.registry.names()]
                phase1_results = await self._execute_parallel(ctx, phase1_names)
                phase2_names = [n for n in ["pricing", "merchandising"] if n in self.registry.names()]
                phase2_results = await self._execute_parallel(ctx, phase2_names)
                combined = {**phase1_results, **phase2_results}
            duration = time.perf_counter() - start
            metrics_snapshot = self.metrics.record_orchestration(
                trace_id=UUID(trace_id),
                success=True,
                duration_seconds=duration,
            )
            return OrchestrationResult(
                success=True,
                trace_id=trace_id,
                message="Orchestration completed",
                metrics={**metrics_snapshot, "agents": list(combined.keys())},
            )
        except asyncio.TimeoutError:
            duration = time.perf_counter() - start
            self.metrics.record_orchestration(
                trace_id=UUID(trace_id), success=False, duration_seconds=duration
            )
            logger.warning("orchestration_timeout", trace_id=trace_id, timeout_s=ORCHESTRATION_TIMEOUT_S)
            return OrchestrationResult(
                success=False,
                trace_id=trace_id,
                message=f"Orchestration timed out after {ORCHESTRATION_TIMEOUT_S}s",
                metrics={"duration_seconds": duration},
            )
        except AgentError as e:
            duration = time.perf_counter() - start
            self.metrics.record_orchestration(
                trace_id=UUID(trace_id), success=False, duration_seconds=duration
            )
            logger.error("orchestration_failed", trace_id=trace_id, error=str(e))
            return OrchestrationResult(
                success=False,
                trace_id=trace_id,
                message=str(e),
                metrics={"duration_seconds": duration},
            )

    async def _execute_parallel(
        self,
        ctx: AgentContext,
        names: list[str],
    ) -> dict[str, object]:
        """Run agents in parallel; return name -> result."""
        if not names:
            return {}
        tasks = [self._run_one(name, ctx) for name in names]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        out: dict[str, object] = {}
        for name, res in zip(names, results, strict=True):
            if isinstance(res, Exception):
                logger.warning("agent_failed", agent=name, error=str(res))
                out[name] = {"error": str(res)}
            else:
                out[name] = res
        return out

    async def _run_one(self, name: str, ctx: AgentContext) -> dict[str, object]:
        """Run one agent and record metrics."""
        agent = self.registry.get(name)
        start = time.perf_counter()
        try:
            result = await agent.execute(ctx)
            record_agent_success(name, time.perf_counter() - start)
            return result
        except Exception as e:
            record_agent_failure(name, time.perf_counter() - start)
            raise AgentError(f"Agent {name} failed: {e}") from e
