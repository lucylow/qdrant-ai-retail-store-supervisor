"""
GENAI-HACKATHON: Generation orchestrator - few-shot goal extraction, CoT clarification,
bundle reasoning with validation, audit with strict JSON schema, hallucination detection.
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from app.agents.shopper import ShopperGoal
from app.config import GENAI
from app.prompts.templates import (
    AUDIT_POLICY_VERIFICATION,
    INVENTORY_BUNDLE_REASONING,
    SHOPPER_GOAL_EXTRACTION,
    render,
)
from app.prompts.fewshot import FewShotRetriever
from app.prompts.cot import CoTOrchestrator, CoTResult, Step
from app.prompts.validation import ResponseValidator
from app.prompts.hallucination import HallucinationDetector, HallucinationScores
from app.generation.metrics import (
    record_generation,
    groundedness_from_citations,
    coherence_heuristic,
)

logger = logging.getLogger(__name__)

# Goal schema for validation
GOAL_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "goal": {"type": "string"},
        "budget_usd": {"type": "number"},
        "color": {"type": "string"},
        "delivery_days_max": {"type": "integer"},
        "region": {"type": "string"},
        "urgency": {"type": "string"},
    },
    "required": ["goal"],
}

BUNDLE_JSON_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "bundle_id": {"type": "integer"},
            "skus": {"type": "array", "items": {"type": "string"}},
            "total_price": {"type": "number"},
            "feasible": {"type": "boolean"},
            "score": {"type": "number"},
            "rationale": {"type": "string"},
        },
    },
}

AUDIT_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "compliance_ok": {"type": "boolean"},
        "policy_violations": {"type": "array", "items": {"type": "string"}},
        "explanation": {"type": "string"},
        "success_prob": {"type": "number"},
    },
    "required": ["compliance_ok", "explanation", "success_prob"],
}


@dataclass
class GenAIGoalResult:
    goal: ShopperGoal
    raw_goal_json: Dict[str, Any]
    few_shot_examples_used: int
    cot_steps: List[Step]
    validation_passed: bool


@dataclass
class GenAIBundleResult:
    bundles: List[Dict[str, Any]]
    raw_output: str
    validation_passed: bool
    hallucination_score: float
    cot_steps: List[Step]


@dataclass
class GenAIAuditResult:
    compliance_ok: bool
    explanation: str
    success_prob: float
    policy_violations: List[str]
    validation_passed: bool
    hallucination_score: float


@dataclass
class GenAIOrchestratorResult:
    goal_result: Optional[GenAIGoalResult] = None
    bundle_result: Optional[GenAIBundleResult] = None
    audit_result: Optional[GenAIAuditResult] = None
    reasoning_trace: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)


def _default_generate(prompt: str) -> str:
    try:
        from app.llm_client import generate as llm_generate
        return llm_generate(prompt, max_tokens=512, temperature=0.2)
    except Exception as e:  # noqa: BLE001
        logger.warning("LLM generate fallback failed: %s", e)
        return "{}"


class GenAIOrchestrator:
    """
    GENAI-HACKATHON: Orchestrator that applies few-shot, CoT, validation, hallucination detection
    across shopper goal extraction, inventory bundle reasoning, and audit.
    """

    def __init__(
        self,
        generate_fn: Optional[Any] = None,
        use_few_shot: bool = True,
        use_cot: bool = True,
        use_validation: bool = True,
        use_hallucination_check: bool = True,
    ) -> None:
        self._generate = generate_fn or _default_generate
        self._use_few_shot = use_few_shot
        self._use_cot = use_cot
        self._use_validation = use_validation
        self._use_hallucination_check = use_hallucination_check
        self._few_shot = FewShotRetriever(k=GENAI.few_shot_k)
        self._validator = ResponseValidator()
        self._hallucination = HallucinationDetector()
        self._cot = CoTOrchestrator(generate_fn=self._generate)

    async def extract_goal_with_genai(self, user_query: str, goal_id: str) -> GenAIGoalResult:
        """Few-shot goal extraction → optional CoT clarification → validation."""
        from app.agents.shopper import ShopperAgent, VALID_REGIONS

        examples: List[str] = []
        if self._use_few_shot:
            ex_list = await self._few_shot.get_examples(user_query, k=3, success_only=True)
            examples = self._few_shot.format_examples_for_prompt(ex_list)

        context = {
            "user_query": user_query,
            "fewshot_examples": examples or ["Input: (none)\nOutput: goal=shopping; region=global"],
        }
        prompt = render(SHOPPER_GOAL_EXTRACTION, context)
        raw = self._generate(prompt)
        if asyncio.iscoroutine(raw):
            raw = await raw
        raw = str(raw).strip()
        try:
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            goal_json = json.loads(raw)
        except Exception:  # noqa: BLE001
            goal_json = {"goal": user_query, "region": None, "budget_usd": None}

        val_result = self._validator.validate(raw, schema=GOAL_JSON_SCHEMA) if self._use_validation else None
        validation_passed = val_result.valid if val_result else True

        # Build ShopperGoal from goal_json
        budget_eur = goal_json.get("budget_usd")
        if budget_eur is not None:
            budget_eur = float(budget_eur)
        region = goal_json.get("region") or None
        if region and region not in VALID_REGIONS:
            region = None
        urgency_days = goal_json.get("delivery_days_max")
        goal = ShopperGoal(
            goal_id=goal_id,
            query=goal_json.get("goal", user_query),
            intent="purchase_bundle",
            budget_eur=budget_eur,
            region=region,
            urgency_days=int(urgency_days) if urgency_days is not None else None,
            clarified=True,
            latency_ms=0,
        )
        cot_steps: List[Step] = []
        if self._use_cot:
            cot_context = {"user_query": user_query, "context": raw}
            cot_steps = await self._cot.run_cot("parse", cot_context, steps=2)
        return GenAIGoalResult(
            goal=goal,
            raw_goal_json=goal_json,
            few_shot_examples_used=len(examples),
            cot_steps=cot_steps,
            validation_passed=validation_passed,
        )

    async def bundle_reasoning_with_genai(
        self,
        shopper_goal: ShopperGoal,
        retrieved_products: str,
        context_chunks: List[str],
    ) -> GenAIBundleResult:
        """Bundle reasoning with CoT steps → validation → hallucination check."""
        context = {
            "shopper_goal": shopper_goal.summary(),
            "retrieved_products": retrieved_products,
            "bundle_json_schema": json.dumps(BUNDLE_JSON_SCHEMA),
        }
        prompt = render(INVENTORY_BUNDLE_REASONING, context)
        raw = self._generate(prompt)
        if asyncio.iscoroutine(raw):
            raw = await raw
        raw = str(raw).strip()
        try:
            raw_json = raw
            if "```" in raw_json:
                start = raw_json.find("[")
                end = raw_json.rfind("]") + 1
                if start >= 0 and end > start:
                    raw_json = raw_json[start:end]
            parsed = json.loads(raw_json)
            bundles = parsed if isinstance(parsed, list) else []
        except Exception:  # noqa: BLE001
            bundles = []

        val_result = self._validator.validate(raw, schema=BUNDLE_JSON_SCHEMA) if self._use_validation else None
        validation_passed = val_result.valid if val_result else True
        score_result = await self._hallucination.score(raw, context_chunks) if self._use_hallucination_check else None
        hallucination_score = score_result.composite if score_result else 0.0

        record_generation(
            groundedness=groundedness_from_citations(raw, len(context_chunks)),
            coherence=coherence_heuristic(raw),
            first_pass_success=validation_passed and (hallucination_score < GENAI.hallucination_block_threshold),
            latency_ms=0,
            retry_count=0,
            hallucination_score=hallucination_score,
            validation_passed=validation_passed,
            template="inventory_bundle",
        )
        return GenAIBundleResult(
            bundles=bundles,
            raw_output=raw,
            validation_passed=validation_passed,
            hallucination_score=hallucination_score,
            cot_steps=[],
        )

    async def audit_with_genai(
        self,
        goal_summary: str,
        plan_summary: str,
        context_chunks: List[str],
    ) -> GenAIAuditResult:
        """Policy verification with strict JSON schema + hallucination check."""
        context = {"goal_summary": goal_summary, "plan_summary": plan_summary}
        prompt = render(AUDIT_POLICY_VERIFICATION, context)
        raw = self._generate(prompt)
        if asyncio.iscoroutine(raw):
            raw = await raw
        raw = str(raw).strip()
        try:
            if "```" in raw:
                start = raw.find("{")
                end = raw.rfind("}") + 1
                if start >= 0 and end > start:
                    raw = raw[start:end]
            audit_json = json.loads(raw)
        except Exception:  # noqa: BLE001
            audit_json = {"compliance_ok": False, "explanation": "Parse failed", "success_prob": 0.0, "policy_violations": []}

        val_result = self._validator.validate(raw, schema=AUDIT_JSON_SCHEMA) if self._use_validation else None
        validation_passed = val_result.valid if val_result else True
        score_result = await self._hallucination.score(raw, context_chunks) if self._use_hallucination_check else None
        hallucination_score = score_result.composite if score_result else 0.0

        return GenAIAuditResult(
            compliance_ok=bool(audit_json.get("compliance_ok", False)),
            explanation=str(audit_json.get("explanation", "")),
            success_prob=float(audit_json.get("success_prob", 0)),
            policy_violations=list(audit_json.get("policy_violations") or []),
            validation_passed=validation_passed,
            hallucination_score=hallucination_score,
        )


__all__: Sequence[str] = [
    "GenAIOrchestrator",
    "GenAIOrchestratorResult",
    "GenAIGoalResult",
    "GenAIBundleResult",
    "GenAIAuditResult",
]
