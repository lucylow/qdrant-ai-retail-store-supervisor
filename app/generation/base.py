"""
GENAI-HACKATHON: Typed LLM interface with retry/backoff.
Production-grade generation base for all agents.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Optional, Sequence, Union

from app.config import GENAI, GENERATOR_MAX_TOKENS, GENERATOR_TEMPERATURE

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class GenerationResult:
    output: str
    latency_ms: int
    attempt: int
    from_cache: bool = False
    metadata: dict = field(default_factory=dict)


class GenerationError(Exception):
    """Raised when generation fails after all retries."""

    pass


class BaseLLMInterface:
    """
    Typed LLM interface with retry and exponential backoff.
    Subclass or wrap with actual provider (OpenAI, HF, local).
    """

    def __init__(
        self,
        max_retries: int = 3,
        backoff_base: float = 1.0,
        timeout_s: float = 120.0,
    ) -> None:
        self._max_retries = max_retries or GENAI.max_retries
        self._backoff_base = backoff_base
        self._timeout_s = timeout_s

    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = GENERATOR_TEMPERATURE,
        **kwargs: Any,
    ) -> str:
        """
        Synchronous generate. Override in subclass or set _generate_fn.
        """
        raise NotImplementedError("Override generate or set _generate_fn")

    async def generate_async(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = GENERATOR_TEMPERATURE,
        **kwargs: Any,
    ) -> str:
        """Async generate. Default: run sync generate in executor."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.generate(prompt, max_tokens=max_tokens, temperature=temperature, **kwargs),
        )

    def generate_with_retry(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = GENERATOR_TEMPERATURE,
    ) -> GenerationResult:
        """
        Generate with exponential backoff retry. Returns GenerationResult.
        """
        max_tokens = max_tokens or GENERATOR_MAX_TOKENS
        last_exc: Optional[Exception] = None
        for attempt in range(self._max_retries + 1):
            start = time.perf_counter()
            try:
                out = self.generate(prompt, max_tokens=max_tokens, temperature=temperature)
                latency_ms = int((time.perf_counter() - start) * 1000)
                logger.info(
                    "Generation success",
                    extra={
                        "template": "base_llm",
                        "attempt": attempt,
                        "latency_ms": latency_ms,
                        "output_len": len(out),
                    },
                )
                return GenerationResult(
                    output=out,
                    latency_ms=latency_ms,
                    attempt=attempt,
                    from_cache=False,
                    metadata={},
                )
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                logger.warning(
                    "Generation attempt failed",
                    extra={"template": "base_llm", "attempt": attempt, "error": str(exc)},
                )
                if attempt < self._max_retries:
                    delay = self._backoff_base * (2 ** attempt)
                    time.sleep(delay)
        raise GenerationError(f"All {self._max_retries + 1} attempts failed") from last_exc

    async def generate_async_with_retry(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = GENERATOR_TEMPERATURE,
    ) -> GenerationResult:
        """Async generate with retry (sequential backoff)."""
        max_tokens = max_tokens or GENERATOR_MAX_TOKENS
        last_exc: Optional[Exception] = None
        for attempt in range(self._max_retries + 1):
            start = time.perf_counter()
            try:
                out = await self.generate_async(
                    prompt, max_tokens=max_tokens, temperature=temperature
                )
                latency_ms = int((time.perf_counter() - start) * 1000)
                return GenerationResult(
                    output=out,
                    latency_ms=latency_ms,
                    attempt=attempt,
                    from_cache=False,
                    metadata={},
                )
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                if attempt < self._max_retries:
                    delay = self._backoff_base * (2 ** attempt)
                    await asyncio.sleep(delay)
        raise GenerationError("All retries exhausted") from last_exc


class WrapperLLM(BaseLLMInterface):
    """Wrap an existing callable (e.g. app.llm_client.generate) as BaseLLMInterface."""

    def __init__(
        self,
        generate_fn: Callable[..., Union[str, Awaitable[str]]],
        max_retries: int = 3,
        backoff_base: float = 1.0,
        timeout_s: float = 120.0,
    ) -> None:
        super().__init__(max_retries=max_retries, backoff_base=backoff_base, timeout_s=timeout_s)
        self._generate_fn = generate_fn

    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = GENERATOR_TEMPERATURE,
        **kwargs: Any,
    ) -> str:
        result = self._generate_fn(prompt, max_tokens=max_tokens, temperature=temperature, **kwargs)
        if asyncio.iscoroutine(result):
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(result)
        return str(result)


__all__: Sequence[str] = [
    "BaseLLMInterface",
    "WrapperLLM",
    "GenerationResult",
    "GenerationError",
]
