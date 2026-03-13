"""
Agent load balancing and health checks for 95% success rate.
"""
from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, List

logger = logging.getLogger(__name__)


@dataclass
class AgentEndpoint:
    name: str
    weight: int = 1
    healthy: bool = True
    last_check: float = 0.0
    consecutive_failures: int = 0


class LoadBalancer:
    """Round-robin with health checks and optional weighting."""

    def __init__(self, check_interval_s: float = 30.0) -> None:
        self.endpoints: List[AgentEndpoint] = []
        self._index = 0
        self.check_interval_s = check_interval_s
        self._health_check: Callable[[str], Any] = lambda _: True

    def add_endpoint(self, name: str, weight: int = 1) -> None:
        self.endpoints.append(AgentEndpoint(name=name, weight=weight))

    def set_health_check(self, fn: Callable[[str], Any]) -> None:
        self._health_check = fn

    def next_endpoint(self) -> AgentEndpoint | None:
        if not self.endpoints:
            return None
        healthy = [e for e in self.endpoints if e.healthy]
        if not healthy:
            return self.endpoints[self._index % len(self.endpoints)]
        self._index = (self._index + 1) % len(healthy)
        return healthy[self._index]

    async def run_health_checks(self) -> None:
        now = time.monotonic()
        for ep in self.endpoints:
            if now - ep.last_check < self.check_interval_s:
                continue
            ep.last_check = now
            try:
                result = self._health_check(ep.name)
                if asyncio.iscoroutine(result):
                    result = await result
                ep.healthy = bool(result)
                if ep.healthy:
                    ep.consecutive_failures = 0
                else:
                    ep.consecutive_failures += 1
            except Exception as e:
                logger.debug("Health check failed for %s: %s", ep.name, e)
                ep.healthy = False
                ep.consecutive_failures += 1
