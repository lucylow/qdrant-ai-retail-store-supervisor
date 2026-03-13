"""
GENAI-HACKATHON: Self-healing generation - automatic prompt repair + example refresh.
Retry logic: validate structure -> hallucination check -> repair prompt / add context.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List, Optional, Sequence, TypeVar

from app.config import GENAI

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


@dataclass
class SelfHealingResult:
    output: str
    context: List[str]
    schema: Optional[Dict[str, Any]]
    validated: bool
    hallucination_score: float
    attempt: int


class GenerationFailed(Exception):
    """Raised when all self-healing retries are exhausted."""

    pass


class SelfHealingGenerator:
    """
    GENAI-HACKATHON: Automatic prompt repair + example refresh.
    Validate structure -> hallucination check -> repair prompt or add more context; retry.
    """

    def __init__(
        self,
        generate_fn: Callable[[str], Any],
        validator: Any,
        detector: Any,
        max_retries: Optional[int] = None,
    ) -> None:
        self._generate_fn = generate_fn
        self._validator = validator
        self._detector = detector
        self._max_retries = max_retries or GENAI.max_retries

    def _repair_prompt(self, prompt: str, errors: List[str]) -> str:
        """Append validation errors so model can self-correct."""
        err_block = "\n".join(f"- {e}" for e in errors[:5])
        return prompt + f"\n\n<validation_errors>\n{err_block}\n</validation_errors>\nOutput valid JSON only."

    def _add_more_context(self, prompt: str, context: List[str]) -> str:
        """Inject more context into prompt to reduce hallucination."""
        ctx_block = "\n".join(f"[{i}] {c[:300]}" for i, c in enumerate(context[:5]))
        if "<context>" in prompt:
            return prompt.replace("</context>", f"\n{ctx_block}\n</context>")
        return prompt + f"\n\n<additional_context>\n{ctx_block}\n</additional_context>"

    async def generate_safe(
        self,
        prompt: str,
        context: Optional[List[str]] = None,
        schema: Optional[Dict[str, Any]] = None,
        max_retries: Optional[int] = None,
    ) -> SelfHealingResult:
        """
        Generate with validation and hallucination check. On failure: repair prompt or add context and retry.
        """
        context = context or []
        max_retries = max_retries or self._max_retries
        current_prompt = prompt

        for attempt in range(max_retries):
            # Generate
            gen = self._generate_fn(current_prompt)
            if asyncio.iscoroutine(gen):
                output = await gen
            else:
                output = str(gen)

            # Validate structure
            val_result = self._validator.validate(output, schema=schema)
            if not val_result.valid:
                current_prompt = self._repair_prompt(current_prompt, val_result.errors)
                logger.info(
                    "Self-healing: prompt repair",
                    extra={"template": "self_healing", "attempt": attempt, "errors": val_result.errors[:3]},
                )
                continue

            # Hallucination check
            score_result = await self._detector.score(output, context)
            if self._detector.should_block(score_result.composite):
                current_prompt = self._add_more_context(current_prompt, context)
                logger.info(
                    "Self-healing: added context",
                    extra={
                        "template": "self_healing",
                        "hallucination_score": score_result.composite,
                        "attempt": attempt,
                    },
                )
                continue

            return SelfHealingResult(
                output=output,
                context=context,
                schema=schema,
                validated=True,
                hallucination_score=score_result.composite,
                attempt=attempt,
            )

        raise GenerationFailed("All retries exhausted: validation or hallucination check failed.")


__all__: Sequence[str] = ["SelfHealingGeneration", "SelfHealingGenerator", "SelfHealingResult", "GenerationFailed"]

