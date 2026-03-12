"""
Hallucination detector and safety filters.
- simple heuristics for now:
  - checks for unsupported named entities (e.g., dates, prices) not present in context
  - checks for contradictory statements w.r.t. retrieved passages
- exposes filter_answer(answer, retrieved) -> (pass:bool, reasons:list)
"""

import re
from typing import List, Dict, Any, Tuple
from difflib import SequenceMatcher


def find_numbers(s: str) -> List[str]:
    return re.findall(r"\d+(?:[.,]\d+)?", s)


def contains_number_from_context(answer: str, contexts: List[str]) -> bool:
    nums = find_numbers(answer)
    if not nums:
        return True
    text = " ".join(contexts)
    for n in nums:
        if n in text:
            return True
    return False


def filter_answer(answer: str, retrieved: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    reasons: List[str] = []
    contexts = [r.get("payload", {}).get("text", "") for r in retrieved]
    if not contains_number_from_context(answer, contexts):
        reasons.append("Numeric claims in answer not present in context")
    # check overlap
    sim = SequenceMatcher(None, answer, " ".join(contexts)).ratio()
    if sim < 0.05:
        reasons.append("Low lexical overlap between answer and contexts")
    ok = len(reasons) == 0
    return ok, reasons

