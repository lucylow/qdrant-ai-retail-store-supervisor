"""
Adaptive failure handling: circuit breaker and load shedding for 95% agent success rate.
"""
from __future__ import annotations

import asyncio
import logging
import time
from enum import Enum
from typing import Any, Callable, Dict, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitOpenError(Exception):
    """Raised when the circuit is open and the call is rejected."""

    pass


class CircuitBreaker:
    """Circuit breaker: opens after failure threshold, allows probe after recovery_timeout."""

    def __init__(
        self,
        name: str = "default",
        failure_threshold: float = 0.5,
        recovery_timeout: int = 60,
        min_calls: int = 5,
    ) -> None:
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.min_calls = min_calls
        self.failure_count = 0
        self.success_count = 0
        self.last_failure: float | None = None
        self.state = CircuitState.CLOSED

    def _on_success(self) -> None:
        self.success_count += 1
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0

    def _on_failure(self) -> None:
        self.failure_count += 1
        self.last_failure = time.time()
        total = self.failure_count + self.success_count
        if total >= self.min_calls and (self.failure_count / total) >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning("Circuit %s opened after %s failures", self.name, self.failure_count)

    async def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        if self.state == CircuitState.OPEN:
            if self.last_failure and (time.time() - self.last_failure) > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitOpenError(f"Circuit breaker '{self.name}' open")
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise


class CircuitBreakerRegistry:
    """Registry of circuit breakers per agent or service."""

    def __init__(self) -> None:
        self._breakers: Dict[str, CircuitBreaker] = {}

    def get(self, name: str, **kwargs: Any) -> CircuitBreaker:
        if name not in self._breakers:
            self._breakers[name] = CircuitBreaker(name=name, **kwargs)
        return self._breakers[name]

    async def call(
        self,
        name: str,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        return await self.get(name).call(func, *args, **kwargs)
