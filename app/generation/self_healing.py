from __future__ import annotations

import logging
from typing import Awaitable, Callable, Sequence, TypeVar


logger = logging.getLogger(__name__)

T = TypeVar("T")


class SelfHealingGeneration:
    """
    Simple retry and context-expansion wrapper for generation calls.
    """

    def __init__(self, max_retries: int = 2) -> None:
        self.max_retries = max_retries

    async def run_with_retries(
        self,
        op: Callable[[int], Awaitable[T]],
    ) -> T:
        last_exc: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                return await op(attempt)
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                logger.warning(
                    "Generation attempt failed",
                    extra={"event": "gen.retry", "attempt": attempt},
                    exc_info=exc,
                )
        if last_exc is not None:
            raise last_exc
        raise RuntimeError("SelfHealingGeneration: unreachable state")


__all__: Sequence[str] = ["SelfHealingGeneration"]

