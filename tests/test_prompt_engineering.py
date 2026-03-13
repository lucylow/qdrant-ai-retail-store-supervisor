"""
GENAI-HACKATHON: 30+ tests - template rendering, validation, hallucination, few-shot, CoT.
"""

from __future__ import annotations

import asyncio
import json
import pytest
from typing import Any, Dict, List, Sequence


# --- Template tests ---
class TestTemplates:
    def test_render_shopper_goal(self) -> None:
        from app.prompts.templates import render, SHOPPER_GOAL_EXTRACTION
        out = render(SHOPPER_GOAL_EXTRACTION, {"user_query": "blue shirt", "fewshot_examples": ["ex1"]})
        assert "blue shirt" in out
        assert "ex1" in out
        assert "<role>" in out

    def test_render_inventory_bundle(self) -> None:
        from app.prompts.templates import render, INVENTORY_BUNDLE_REASONING
        out = render(INVENTORY_BUNDLE_REASONING, {
            "shopper_goal": "shirt under 30",
            "retrieved_products": "p1, p2",
            "bundle_json_schema": "{}",
        })
        assert "shirt under 30" in out
        assert "p1, p2" in out

    def test_render_audit_policy(self) -> None:
        from app.prompts.templates import render, AUDIT_POLICY_VERIFICATION
        out = render(AUDIT_POLICY_VERIFICATION, {"goal_summary": "g", "plan_summary": "p"})
        assert "g" in out and "p" in out

    def test_list_templates(self) -> None:
        from app.prompts.templates import list_templates
        names = list_templates()
        assert len(names) >= 12
        assert "shopper_goal" in names
        assert "inventory_bundle" in names

    def test_get_template_raises_unknown(self) -> None:
        from app.prompts.templates import get_template
        with pytest.raises(KeyError):
            get_template("nonexistent")


# --- Validation tests ---
class TestValidation:
    def test_validate_valid_json(self) -> None:
        from app.prompts.validation import ResponseValidator
        v = ResponseValidator()
        r = v.validate('{"goal": "x", "budget_usd": 10}', schema={"required": ["goal"], "properties": {"goal": {"type": "string"}}})
        assert r.valid
        assert r.parsed is not None
        assert r.parsed.get("goal") == "x"

    def test_validate_invalid_json(self) -> None:
        from app.prompts.validation import ResponseValidator
        v = ResponseValidator()
        r = v.validate("not json at all")
        assert not r.valid
        assert len(r.errors) > 0

    def test_validate_missing_required(self) -> None:
        from app.prompts.validation import ResponseValidator
        v = ResponseValidator()
        r = v.validate('{"other": 1}', schema={"required": ["goal"], "properties": {"goal": {"type": "string"}}})
        assert not r.valid
        assert any("goal" in e for e in r.errors)

    def test_extract_json_from_response_code_block(self) -> None:
        from app.prompts.validation import _extract_json_from_response
        raw = '```json\n{"a": 1}\n```'
        assert json.loads(_extract_json_from_response(raw)) == {"a": 1}

    def test_extract_json_from_response_plain(self) -> None:
        from app.prompts.validation import _extract_json_from_response
        raw = 'Here is the result: {"b": 2}'
        assert json.loads(_extract_json_from_response(raw)) == {"b": 2}


# --- Hallucination tests ---
class TestHallucination:
    @pytest.mark.asyncio
    async def test_score_returns_composite(self) -> None:
        from app.prompts.hallucination import HallucinationDetector
        d = HallucinationDetector()
        s = await d.score("Blue t-shirt €25 from context [0].", ["Blue t-shirt €25", "EU delivery"])
        assert 0 <= s.composite <= 1
        assert hasattr(s, "lexical_overlap")
        assert hasattr(s, "entailment")

    def test_lexical_overlap_high_when_matching(self) -> None:
        from app.prompts.hallucination import HallucinationDetector
        d = HallucinationDetector()
        # High overlap -> low lexical score (1 - overlap)
        score = d.lexical_overlap("blue shirt price", ["blue shirt price 30 eur"])
        assert score < 0.5

    def test_should_block_above_threshold(self) -> None:
        from app.prompts.hallucination import HallucinationDetector
        d = HallucinationDetector()
        assert d.should_block(0.3)
        assert not d.should_block(0.2)


# --- CoT tests ---
class TestCoT:
    def test_render_step_parse(self) -> None:
        from app.prompts.cot import CoTOrchestrator
        def gen(p: str) -> str:
            return "{}"
        orch = CoTOrchestrator(generate_fn=gen)
        prompt = orch.render_step("parse", {"user_query": "test query"}, 0)
        assert "test query" in prompt

    @pytest.mark.asyncio
    async def test_run_cot_returns_steps(self) -> None:
        from app.prompts.cot import CoTOrchestrator
        def gen(p: str) -> str:
            return '{"valid": true}'
        orch = CoTOrchestrator(generate_fn=gen)
        steps = await orch.run_cot("parse", {"user_query": "shirt"}, steps=2)
        assert len(steps) == 2
        assert steps[0].name == "parse"
        assert steps[1].name == "reason"


# --- Few-shot tests (unit, no Qdrant) ---
class TestFewShot:
    def test_format_examples_for_prompt(self) -> None:
        from app.prompts.fewshot import FewShotRetriever, Example
        r = FewShotRetriever(k=2)
        exs = [
            Example("q1", "out1", True, "id1", {}),
            Example("q2", "out2", True, "id2", {}),
        ]
        lines = r.format_examples_for_prompt(exs)
        assert len(lines) == 2
        assert "q1" in lines[0] and "out1" in lines[0]


# --- Generation metrics tests ---
class TestMetrics:
    def test_groundedness_from_citations(self) -> None:
        from app.generation.metrics import groundedness_from_citations
        g = groundedness_from_citations("See [0] and [1] for details.", 3)
        assert g > 0.5

    def test_coherence_heuristic_json(self) -> None:
        from app.generation.metrics import coherence_heuristic
        assert coherence_heuristic('{"a": 1}') > 0.5

    def test_compute_aggregates_empty(self) -> None:
        from app.generation.metrics import compute_aggregates
        agg = compute_aggregates([])
        assert agg["groundedness_avg"] == 0
        assert agg["first_pass_rate"] == 0


# --- Config tests ---
class TestConfig:
    def test_genai_settings(self) -> None:
        from app.config import GENAI
        assert GENAI.max_retries >= 1
        assert GENAI.cot_steps >= 2
        assert 0 < GENAI.hallucination_block_threshold < 1
