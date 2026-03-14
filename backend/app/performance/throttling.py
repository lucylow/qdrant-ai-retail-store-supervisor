"""
Rate limiting and adaptive concurrency for 1000 QPS target.
"""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class ThrottleConfig:
    max_qps: float = 1000.0
    burst: int = 50
    adaptive: bool = True


class Throttler:
    """Token-bucket style rate limiter; optional adaptive concurrency."""

    def __init__(self, config: ThrottleConfig | None = None) -> None:
        self.config = config or ThrottleConfig()
        self._tokens = float(self.config.burst)
        self._last_update = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_update
            self._tokens = min(
                self.config.burst,
                self._tokens + elapsed * self.config.max_qps,
            )
            self._last_update = now
            if self._tokens < 1.0:
                wait = (1.0 - self._tokens) / self.config.max_qps
                await asyncio.sleep(wait)
                self._tokens = 0.0
                self._last_update = time.monotonic()
            else:
                self._tokens -= 1.0

    @property
    def current_qps_capacity(self) -> float:
        return self.config.max_qps
