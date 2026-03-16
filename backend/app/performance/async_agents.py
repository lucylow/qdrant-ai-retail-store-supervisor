"""
AsyncIO agent pool with semaphore for 1000 QPS production scale.
Limits concurrent agent executions and supports batch execution.
"""
from __future__ import annotations

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, Callable, Dict, List

logger = logging.getLogger(__name__)


@dataclass
class AgentPoolConfig:
    max_concurrent: int = 50
    semaphore_limit: int = 20
    queue_timeout: float = 5.0


class AsyncAgentPool:
    """Async agent pool with semaphore protection and optional thread pool for sync agents."""

    def __init__(
        self,
        config: AgentPoolConfig | None = None,
        agent_registry: Dict[str, Callable[..., Any]] | None = None,
    ) -> None:
        self.config = config or AgentPoolConfig()
        self.semaphore = asyncio.Semaphore(self.config.semaphore_limit)
        self.pool = ThreadPoolExecutor(max_workers=self.config.max_concurrent)
        self.running_tasks: Dict[str, asyncio.Task[Any]] = {}
        self._registry = agent_registry or {}

    def register_agent(self, name: str, fn: Callable[..., Any]) -> None:
        self._registry[name] = fn

    async def _execute_single(
        self,
        agent_name: str,
        input_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        fn = self._registry.get(agent_name)
        if fn is None:
            return {"ok": False, "error": f"Unknown agent: {agent_name}", "data": {}}
        loop = asyncio.get_event_loop()
        try:
            query = input_data.get("query", "")
            context = input_data.get("context") or {}
            result = await loop.run_in_executor(
                self.pool,
                lambda: fn(query, context) if callable(fn) else {},
            )
            if isinstance(result, dict) and "data" not in result:
                return {"ok": True, "data": result}
            return {"ok": True, "data": result.get("data", result)}
        except Exception as e:
            logger.exception("Agent %s failed: %s", agent_name, e)
            return {"ok": False, "error": str(e), "data": {}}

    async def execute_batch(
        self,
        agent_name: str,
        inputs: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Execute batch of agent calls with semaphore protection."""
        if not inputs:
            return []
        async with self.semaphore:
            tasks = [
                asyncio.create_task(self._execute_single(agent_name, inp))
                for inp in inputs
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            out: List[Dict[str, Any]] = []
            for r in results:
                if isinstance(r, Exception):
                    out.append({"ok": False, "error": str(r), "data": {}})
                else:
                    out.append(r)
            return out

    async def execute_single(
        self,
        agent_name: str,
        query: str,
        context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """Execute a single agent call with semaphore."""
        return (await self.execute_batch(agent_name, [{"query": query, "context": context or {}}]))[0]

    def shutdown(self) -> None:
        self.pool.shutdown(wait=True)
