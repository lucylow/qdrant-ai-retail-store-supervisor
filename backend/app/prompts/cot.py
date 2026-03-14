"""
GENAI-HACKATHON: Chain-of-Thought orchestrator with step validation.
Multi-step reasoning: parse → reason → verify → synthesize with intermediate JSON.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence

from app.config import GENAI
from app.prompts.templates import (
    COT_STEP_PARSE,
    COT_STEP_REASON,
    COT_STEP_SYNTHESIZE,
    COT_STEP_VERIFY,
    render,
)

logger = logging.getLogger(__name__)

# Step names for 4 mandatory steps
COT_STEP_NAMES: Sequence[str] = ("parse", "reason", "verify", "synthesize")
COT_TEMPLATES: Dict[str, str] = {
    "parse": COT_STEP_PARSE,
    "reason": COT_STEP_REASON,
    "verify": COT_STEP_VERIFY,
    "synthesize": COT_STEP_SYNTHESIZE,
}


@dataclass(slots=True)
class Step:
    step: int
    name: str
    output: str
    valid: bool
    parsed: Optional[Dict[str, Any]] = None


@dataclass(slots=True)
class CoTResult:
    steps: List[Step] = field(default_factory=list)
    final_output: str = ""
    success: bool = False


class CoTOrchestrator:
    """
    Run 4-step chain-of-thought: parse → reason → verify → synthesize.
    Each step is rendered, generated, validated; context is progressively updated.
    """

    def __init__(
        self,
        generate_fn: Callable[[str], Any],
        validate_step_fn: Optional[Callable[[str, int], bool]] = None,
        steps: int = 4,
    ) -> None:
        self._generate = generate_fn
        self._validate_step = validate_step_fn or _default_validate_step
        self._steps_count = steps or GENAI.cot_steps

    def render_step(
        self,
        template_name: str,
        context: Dict[str, Any],
        step_index: int,
    ) -> str:
        """Render the prompt for step step_index (0..3)."""
        step_name = COT_STEP_NAMES[step_index] if step_index < len(COT_STEP_NAMES) else "synthesize"
        tpl_name = COT_TEMPLATES.get(step_name, COT_STEP_SYNTHESIZE)
        ctx = dict(context)
        if step_index >= 1:
            ctx["step1_output"] = context.get("step1_output", "{}")
        if step_index >= 2:
            ctx["step2_output"] = context.get("step2_output", "{}")
        if step_index >= 3:
            ctx["all_steps"] = context.get("all_steps", "[]")
        return render(tpl_name, ctx)

    async def run_cot(
        self,
        template_base: str,
        context: Dict[str, Any],
        steps: Optional[int] = None,
    ) -> List[Step]:
        """
        Execute CoT pipeline. template_base and context used to build step prompts.
        Returns list of Step with output and valid flag.
        """
        n = steps or self._steps_count
        results: List[Step] = []
        ctx = dict(context)

        for i in range(n):
            step_name = COT_STEP_NAMES[i] if i < len(COT_STEP_NAMES) else "synthesize"
            step_prompt = self.render_step(template_base, ctx, i)

            # Generate (support both sync and async)
            gen = self._generate(step_prompt)
            if hasattr(gen, "__await__"):
                step_output = await gen
            else:
                step_output = str(gen)

            step_valid = self._validate_step(step_output, i)
            parsed: Optional[Dict[str, Any]] = None
            try:
                parsed = json.loads(_extract_json(step_output))
            except Exception:  # noqa: BLE001
                pass
            results.append(
                Step(step=i, name=step_name, output=step_output, valid=step_valid, parsed=parsed)
            )
            # Progressive context building
            ctx[f"step{i + 1}_output"] = step_output
            if parsed:
                ctx[f"step{i + 1}_parsed"] = parsed
            if i == 2:
                ctx["all_steps"] = str([s.output for s in results])

            logger.info(
                "CoT step",
                extra={
                    "template": template_base,
                    "cot_step": i,
                    "valid": step_valid,
                    "output_len": len(step_output),
                },
            )

        return results

    def run_cot_sync(
        self,
        template_base: str,
        context: Dict[str, Any],
        steps: Optional[int] = None,
    ) -> CoTResult:
        """Synchronous run: execute CoT and return CoTResult with final_output from last step."""
        import asyncio

        step_list = asyncio.get_event_loop().run_until_complete(
            self.run_cot(template_base, context, steps)
        )
        final = step_list[-1].output if step_list else ""
        success = all(s.valid for s in step_list)
        return CoTResult(steps=step_list, final_output=final, success=success)


def _default_validate_step(step_output: str, step_index: int) -> bool:
    """Default: consider step valid if we can extract some JSON."""
    try:
        _extract_json(step_output)
        return True
    except Exception:  # noqa: BLE001
        return False


def _extract_json(text: str) -> str:
    """Extract JSON block from model output (handles markdown code blocks)."""
    text = text.strip()
    if "```json" in text:
        start = text.index("```json") + 7
        end = text.index("```", start)
        return text[start:end].strip()
    if "```" in text:
        start = text.index("```") + 3
        end = text.index("```", start)
        return text[start:end].strip()
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        return text[start:end]
    raise ValueError("No JSON found in output")


__all__: Sequence[str] = ["CoTOrchestrator", "CoTResult", "Step", "COT_STEP_NAMES"]
