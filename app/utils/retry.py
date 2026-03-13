"""Exponential backoff + jitter retry decorator for async/sync."""

from __future__ import annotations

import asyncio
import random
from functools import wraps
from typing import Callable, TypeVar, ParamSpec
from typing import Literal

P = ParamSpec("P")
R = TypeVar("R")


def _jitter_full() -> float:
    """Full jitter: random [0, 1) for multiplying delay."""
    return random.random()


def _jitter_equal(delay: float) -> float:
    """Equal jitter: delay/2 + random [0, delay/2]."""
    half = delay / 2
    return half + random.uniform(0, half)


def retry_on_exception(
    max_attempts: int = 3,
    backoff_factor: float = 2.0,
    jitter: Literal["full", "equal"] = "full",
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorate async function with exponential backoff + jitter."""

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last_exc: Exception | None = None
            for attempt in range(max_attempts):
                try:
                    result = await func(*args, **kwargs)
                    return result
                except exceptions as e:
                    last_exc = e
                    if attempt == max_attempts - 1:
                        raise
                    base_delay = backoff_factor ** attempt
                    if jitter == "full":
                        delay = base_delay * _jitter_full()
                    else:
                        delay = _jitter_equal(base_delay)
                    await asyncio.sleep(delay)
            if last_exc is not None:
                raise last_exc
            raise RuntimeError("retry exhausted")

        @wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last_exc: Exception | None = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    if attempt == max_attempts - 1:
                        raise
                    base_delay = backoff_factor ** attempt
                    if jitter == "full":
                        delay = base_delay * _jitter_full()
                    else:
                        delay = _jitter_equal(base_delay)
                    import time
                    time.sleep(delay)
            if last_exc is not None:
                raise last_exc
            raise RuntimeError("retry exhausted")

        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore[return-value]
        return sync_wrapper  # type: ignore[return-value]

    return decorator
