from typing import Dict, Any, Tuple, List
import re

POLICIES = {
    "max_discount_pct": 40,
    "allowed_regions": ["Zurich", "Geneva", "Bern"],
    "forbidden_terms": ["illegal", "hazardous"],
}


def validate_solution(solution: Dict[str, Any]) -> Tuple[bool, List[str]]:
    issues: List[str] = []
    if "discount_pct" in solution and solution["discount_pct"] > POLICIES["max_discount_pct"]:
        issues.append(
            f"discount {solution['discount_pct']} > max {POLICIES['max_discount_pct']}"
        )
    if "region" in solution and solution["region"] not in POLICIES["allowed_regions"]:
        issues.append(f"region {solution['region']} not allowed")
    text = (solution.get("summary") or "").lower()
    for t in POLICIES["forbidden_terms"]:
        if t in text:
            issues.append(f"forbidden term {t} found")
    return (len(issues) == 0), issues


def numeric_claims_in_context(answer: str, contexts: List[str]) -> Tuple[bool, List[str]]:
    nums = re.findall(r"\\d+(?:[.,]\\d+)?", answer)
    if not nums:
        return True, []
    joined = " ".join(contexts)
    missing = [n for n in nums if n not in joined]
    if missing:
        return False, [f"numeric claims {missing} not found in contexts"]
    return True, []

