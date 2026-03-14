from typing import List, Dict, Any
import re
import logging
from difflib import SequenceMatcher

from app.generation.prompt_templates import build_prompt
from app.llm_client import generate, stream_generate
from app.config import NUM_CONTEXT_DOCS, MIN_PROVENANCE, HALLUCINATION_CONFIDENCE_THRESHOLD
from app.generation.safety import filter_answer

logger = logging.getLogger(__name__)


def _compute_overlap_score(answer: str, contexts: List[str]) -> float:
    """
    Simple heuristic: proportion of answer text that overlaps with the union of context strings.
    Use SequenceMatcher for fuzzy overlap.
    """
    total = len(answer)
    if total == 0:
        return 0.0
    match_len = 0
    for c in contexts:
        sm = SequenceMatcher(None, answer, c)
        match_len += int(sm.quick_ratio() * len(answer) * 0.1)  # heuristic weight
    return min(1.0, match_len / max(1, total))


def extract_citations(text: str) -> List[int]:
    """Extract citations like [0], [1] into int list."""
    found = re.findall(r"\[(\d+)\]", text)
    return sorted(set(int(x) for x in found))


def generate_answer(question: str, retrieved: List[Dict[str, Any]], max_contexts: int | None = None) -> Dict[str, Any]:
    """
    retrieved: list of {id, payload, text, score, reranker_score?}
    returns: {answer, provenance: [{index, id, source, score}], confidence, flag_hallucination, safety_reasons}
    """
    max_contexts = max_contexts or NUM_CONTEXT_DOCS
    contexts = [r.get("payload", {}).get("text", "") for r in retrieved[: max_contexts]]
    prompt = build_prompt(question, contexts)
    answer = generate(prompt)
    cited_idxs = extract_citations(answer)
    provenance = []
    for idx in cited_idxs:
        if 0 <= idx < len(retrieved[: max_contexts]):
            p = retrieved[idx]
            provenance.append(
                {
                    "index": idx,
                    "id": p["id"],
                    "source": p.get("payload", {}).get("source"),
                    "score": p.get("reranker_score") or p.get("score"),
                }
            )
    overlap = _compute_overlap_score(answer, contexts)
    confidence = float(overlap)
    # detect hallucination: if answer has claims but no citations or low overlap -> low confidence
    flag_hallucination = len(provenance) < MIN_PROVENANCE or confidence < HALLUCINATION_CONFIDENCE_THRESHOLD
    ok, safety_reasons = filter_answer(answer, retrieved)
    if not ok:
        flag_hallucination = True
    if flag_hallucination:
        logger.info(
            "Low provenance or safety issue detected: provenance_count=%s overlap=%.3f reasons=%s",
            len(provenance),
            confidence,
            safety_reasons,
        )
    return {
        "answer": answer,
        "provenance": provenance,
        "confidence": confidence,
        "flag_hallucination": flag_hallucination,
        "safety_reasons": safety_reasons,
    }


def stream_answer(question: str, retrieved: List[Dict[str, Any]]):
    """
    Yields chunks from stream_generate, and yields final 'meta' dict at the end with provenance & confidence.
    """
    contexts = [r.get("payload", {}).get("text", "") for r in retrieved[:NUM_CONTEXT_DOCS]]
    prompt = build_prompt(question, contexts)
    buffer = ""
    for chunk in stream_generate(prompt):
        buffer += chunk
        yield {"type": "chunk", "text": chunk}
    # after streaming complete, compute provenance & confidence
    result = generate_answer(question, retrieved, max_contexts=NUM_CONTEXT_DOCS)
    yield {"type": "meta", **result}

