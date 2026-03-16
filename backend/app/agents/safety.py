"""
Safety and policy validation utilities for agent outputs.
- validate_solution_against_policies: checks brand rules, price caps, region constraints
- minimal hallucination checks for LLM-produced fields
"""

from typing import Dict, Any, Tuple, List
import logging

logger = logging.getLogger(__name__)

BRAND_POLICIES = {
    "max_discount_pct": 40,
    "allowed_regions": ["Berlin", "Paris", "Zurich", "London", "Geneva", "Bern"],
    "forbidden_keywords": ["illegal", "hazardous"],
}


def validate_solution_against_policies(
    solution: Dict[str, Any],
) -> Tuple[bool, List[str]]:
    reasons: List[str] = []
    if solution.get("discount_pct") and solution["discount_pct"] > BRAND_POLICIES["max_discount_pct"]:
        reasons.append(
            f"Discount {solution['discount_pct']} exceeds max allowed {BRAND_POLICIES['max_discount_pct']}"
        )
    region = solution.get("region")
    if region and region not in BRAND_POLICIES["allowed_regions"]:
        reasons.append(f"Region {region} not allowed")
    summary = (solution.get("summary") or "").lower()
    for kw in BRAND_POLICIES["forbidden_keywords"]:
        if kw in summary:
            reasons.append(f"Contains forbidden keyword '{kw}'")
    ok = len(reasons) == 0
    return ok, reasons


def validate_generated_text_vs_context(
    text: str, contexts: List[str]
) -> Tuple[bool, List[str]]:
    """
    Simple heuristics: require that any numeric claim in text appears in at least one context.
    Return (ok, reasons)
    """
    import re

    reasons: List[str] = []
    numbers = re.findall(r"\d+(?:[.,]\d+)?", text)
    if numbers:
        context_joined = " ".join(contexts)
        missing = [n for n in numbers if n not in context_joined]
        if missing:
            reasons.append(f"Numeric claims {missing} not found in context")
    return len(reasons) == 0, reasons

