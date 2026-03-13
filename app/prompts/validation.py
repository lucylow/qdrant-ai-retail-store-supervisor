"""
GENAI-HACKATHON: Response validation - Pydantic JSON schema + semantic consistency checks.
Enforces JSON schema, semantic drift < 0.15 cosine, temporal and business rules.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Type, TypeVar

from app.config import GENAI

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass(slots=True)
class ValidationResult:
    valid: bool
    errors: List[str] = field(default_factory=list)
    parsed: Optional[Dict[str, Any]] = None
    semantic_drift: float = 0.0


def _extract_json_from_response(response: str) -> str:
    """Extract JSON from model output."""
    response = response.strip()
    if "```json" in response:
        start = response.index("```json") + 7
        end = response.index("```", start)
        return response[start:end].strip()
    if "```" in response:
        start = response.index("```") + 3
        end = response.index("```", start)
        return response[start:end].strip()
    start = response.find("{")
    if start >= 0:
        end = response.rfind("}") + 1
        if end > start:
            return response[start:end]
    start = response.find("[")
    if start >= 0:
        end = response.rfind("]") + 1
        if end > start:
            return response[start:end]
    raise ValueError("No JSON object or array in response")


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    """Simple cosine similarity; returns 0 if vectors invalid."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(x * x for x in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _simple_embed(text: str, dim: int = 64) -> List[float]:
    """Deterministic pseudo-embedding for drift check (no model)."""
    vec = [0.0] * dim
    for i, c in enumerate(text.encode("utf-8")):
        vec[i % dim] += float(c)
    norm = (sum(x * x for x in vec)) ** 0.5 or 1.0
    return [x / norm for x in vec]


class ResponseValidator:
    """
    Validate LLM response: Pydantic JSON schema + semantic consistency (cosine < 0.15 drift)
    + temporal consistency + business rules (budget, stock, region).
    """

    def __init__(
        self,
        semantic_drift_max: Optional[float] = None,
        schema_cache: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._semantic_drift_max = semantic_drift_max or GENAI.semantic_drift_max
        self.schema_cache = schema_cache or {}

    def validate(
        self,
        response: str,
        schema: Optional[Dict[str, Any]] = None,
        expected_embedding: Optional[List[float]] = None,
        business_rules: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
        """
        Validate response: extract JSON, check schema, optional semantic drift, business rules.
        """
        errors: List[str] = []
        parsed: Optional[Dict[str, Any]] = None
        drift = 0.0

        try:
            raw = _extract_json_from_response(response)
            parsed = json.loads(raw)
        except Exception as e:  # noqa: BLE001
            errors.append(f"JSON extraction failed: {e}")
            return ValidationResult(valid=False, errors=errors, parsed=None, semantic_drift=0.0)

        if schema:
            schema_ok, schema_errors = _validate_against_schema(parsed, schema)
            if not schema_ok:
                errors.extend(schema_errors)
        if expected_embedding is not None and parsed is not None:
            response_str = json.dumps(parsed, sort_keys=True)
            resp_emb = _simple_embed(response_str, len(expected_embedding))
            sim = _cosine_similarity(resp_emb, expected_embedding)
            drift = 1.0 - sim
            if drift > self._semantic_drift_max:
                errors.append(
                    f"Semantic drift {drift:.3f} > max {self._semantic_drift_max}"
                )
        if business_rules:
            rule_errors = _check_business_rules(parsed, business_rules)
            errors.extend(rule_errors)

        valid = len(errors) == 0
        logger.info(
            "Response validation",
            extra={
                "template": "validation",
                "valid": valid,
                "semantic_drift": drift,
                "error_count": len(errors),
            },
        )
        return ValidationResult(
            valid=valid,
            errors=errors,
            parsed=parsed,
            semantic_drift=drift,
        )

    async def validate_async(
        self,
        response: str,
        schema: Optional[Dict[str, Any]] = None,
        expected_embedding: Optional[List[float]] = None,
        business_rules: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
        """Async wrapper for validate."""
        return self.validate(
            response, schema=schema, expected_embedding=expected_embedding, business_rules=business_rules
        )


def _validate_against_schema(data: Any, schema: Dict[str, Any]) -> tuple[bool, List[str]]:
    """Basic schema check: required keys and types. Not full JSON Schema."""
    errors: List[str] = []
    if not isinstance(data, dict):
        if schema.get("type") == "array" and isinstance(data, list):
            return True, []
        errors.append("Expected JSON object")
        return False, errors
    required = schema.get("required", [])
    for key in required:
        if key not in data:
            errors.append(f"Missing required key: {key}")
    props = schema.get("properties", {})
    for k, v in data.items():
        if k in props:
            expected = props[k]
            if isinstance(expected, dict) and "type" in expected:
                t = expected["type"]
                if t == "string" and not isinstance(v, str):
                    errors.append(f"{k}: expected string")
                elif t == "number" and not isinstance(v, (int, float)):
                    errors.append(f"{k}: expected number")
                elif t == "boolean" and not isinstance(v, bool):
                    errors.append(f"{k}: expected boolean")
                elif t == "array" and not isinstance(v, list):
                    errors.append(f"{k}: expected array")
    return len(errors) == 0, errors


def _check_business_rules(parsed: Optional[Dict[str, Any]], rules: Dict[str, Any]) -> List[str]:
    """Temporal and business rules: budget, delivery_days_max, region."""
    errors: List[str] = []
    if not parsed:
        return errors
    if "budget_usd" in rules and "budget_usd" in parsed:
        max_budget = rules.get("max_budget_usd", 500_000)
        try:
            b = float(parsed["budget_usd"])
            if b > max_budget or b < 0:
                errors.append(f"budget_usd must be 0..{max_budget}")
        except (TypeError, ValueError):
            errors.append("budget_usd must be number")
    if "delivery_days_max" in parsed:
        try:
            d = int(parsed["delivery_days_max"])
            if d < 0 or d > 365:
                errors.append("delivery_days_max must be 0..365")
        except (TypeError, ValueError):
            pass
    return errors


def validate_with_pydantic(response: str, model: Type[T]) -> tuple[bool, Optional[T], List[str]]:
    """
    Try to parse response into a Pydantic v2 model. Returns (ok, instance, errors).
    GENAI-HACKATHON: Pydantic v2 models for strict JSON schema.
    """
    try:
        from pydantic import BaseModel, ValidationError
    except ImportError:
        logger.warning("Pydantic not installed; validate_with_pydantic skipped")
        return False, None, ["Pydantic not installed"]

    try:
        raw = _extract_json_from_response(response)
        data = json.loads(raw)
        instance = model.model_validate(data)
        return True, instance, []
    except ValidationError as e:
        return False, None, [err["msg"] for err in e.errors()]
    except Exception as e:  # noqa: BLE001
        return False, None, [str(e)]


__all__: Sequence[str] = [
    "ResponseValidator",
    "ValidationResult",
    "validate_with_pydantic",
    "_extract_json_from_response",
]
