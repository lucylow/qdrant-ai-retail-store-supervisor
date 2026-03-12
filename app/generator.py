from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import logging

from app.config import MODELS
from app.context_manager import ManagedContext


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GenerationProvenance:
    context_fingerprint: str
    source_docs: list[str]


@dataclass(frozen=True)
class GenerationResult:
    text: str
    confidence: float
    provenance: GenerationProvenance


def generate_answer(
    query: str,
    context: ManagedContext,
    llm_call: callable[[str], str] | None = None,
) -> GenerationResult:
    """
    Tiny abstraction around an LLM call.
    For hackathon we keep this pluggable via `llm_call`.
    """
    prompt = (
        "You are a retail assistant. Use ONLY the provided context.\n\n"
        f"Query:\n{query}\n\nContext:\n{context.text}\n\nAnswer:"
    )
    if llm_call is None:
        # CURSOR: plug in your preferred LLM here (OpenAI, local, etc.).
        logger.warning("No llm_call provided; returning echo answer")
        answer = f"(demo) Unable to call LLM. Context length={len(context.text.split())}."
    else:
        answer = llm_call(prompt)
    prov = GenerationProvenance(
        context_fingerprint=context.fingerprint,
        source_docs=[c.id for c in context.chunks],
    )
    # CURSOR: add real confidence from scoring/head if desired.
    return GenerationResult(text=answer, confidence=0.6, provenance=prov)


__all__ = ["GenerationResult", "GenerationProvenance", "generate_answer"]

from typing import Dict, Any
import logging
import re

from app.context_manager import build_context_for_query
from app.llm_client import generate

logger = logging.getLogger(__name__)


def generate_from_prompt(prompt: str) -> Dict[str, Any]:
    """
    Simple wrapper for the LLM call. Returns a structured dict.
    """
    try:
        ans = generate(prompt)
        return {"answer": ans}
    except Exception as e:
        logger.exception("generate_from_prompt failed: %s", e)
        return {"answer": "ERROR: generation unavailable"}


def rag_answer(
    context_input: Dict[str, Any],
    question: str,
    token_budget: int | None = None,
) -> Dict[str, Any]:
    """
    End-to-end RAG helper:
    - build context (profile, retrieval, compression, assembly)
    - call LLM
    - return answer + provenance metadata
    """
    ctx = build_context_for_query(context_input, question, token_budget=token_budget)
    prompt = ctx["prompt"]
    metadata = ctx["metadata"]
    llm_out = generate_from_prompt(prompt)

    answer_text = llm_out.get("answer") or ""
    cited: list[int] = []
    if answer_text:
        try:
            cited = sorted(
                set(int(x) for x in re.findall(r"\\[(\\d+)\\]", answer_text))
            )
        except Exception:
            cited = []

    provenance = []
    for c in cited:
        mapping = metadata.get("doc_index_map", {}).get(c)
        if mapping:
            provenance.append(mapping)

    return {
        "answer": answer_text,
        "provenance": provenance,
        "metadata": metadata,
    }


__all__ = ["generate_from_prompt", "rag_answer"]

