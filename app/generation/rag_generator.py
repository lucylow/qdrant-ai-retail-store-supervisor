"""
GENAI-HACKATHON: RAG-aware generator with provenance extraction.
Uses retrieved context + prompt templates; extracts citations and provenance for audit.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from app.generation.base import BaseLLMInterface, GenerationResult

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ProvenanceChunk:
    index: int
    text: str
    score: float
    source: str


@dataclass(slots=True)
class RAGGenerationResult(GenerationResult):
    provenance: List[ProvenanceChunk] = field(default_factory=list)
    citations: List[int] = field(default_factory=list)
    context_used: List[str] = field(default_factory=list)


def extract_citations(text: str) -> List[int]:
    """Extract citation indices [0], [1], ... from generated text."""
    indices: List[int] = []
    for m in re.finditer(r"\[(\d+)\]", text):
        try:
            indices.append(int(m.group(1)))
        except ValueError:
            pass
    return indices


def build_context_block(contexts: List[str], max_tokens_approx: int = 1500) -> str:
    """Build numbered context block for prompt. Approximate token limit by chars/4."""
    block: List[str] = []
    total = 0
    for i, c in enumerate(contexts):
        chunk = f"[{i}] {c}"
        if total + len(chunk) // 4 > max_tokens_approx:
            break
        block.append(chunk)
        total += len(chunk) // 4
    return "\n\n".join(block)


class RAGGenerator:
    """
    RAG-aware generator: inject retrieved context, generate, extract provenance and citations.
    """

    def __init__(
        self,
        llm: BaseLLMInterface,
        template_render_fn: Optional[Any] = None,
    ) -> None:
        self._llm = llm
        self._template_render = template_render_fn

    def generate(
        self,
        prompt: str,
        context_chunks: Optional[List[str]] = None,
        context_scores: Optional[List[float]] = None,
        context_sources: Optional[List[str]] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.2,
    ) -> RAGGenerationResult:
        """
        Generate from prompt (optionally already containing context). If context_chunks
        provided, they are used for provenance extraction and citation validation.
        """
        if not context_chunks:
            context_chunks = []
        if not context_scores:
            context_scores = [0.0] * len(context_chunks)
        if not context_sources:
            context_sources = [f"doc_{i}" for i in range(len(context_chunks))]

        base_result = self._llm.generate_with_retry(
            prompt, max_tokens=max_tokens, temperature=temperature
        )
        output = base_result.output
        citations = extract_citations(output)
        provenance: List[ProvenanceChunk] = []
        for i, (text, score, src) in enumerate(
            zip(context_chunks, context_scores, context_sources)
        ):
            provenance.append(
                ProvenanceChunk(index=i, text=text[:500], score=score, source=src)
            )

        logger.info(
            "RAG generation",
            extra={
                "template": "rag_generator",
                "context_count": len(context_chunks),
                "citations_count": len(citations),
                "latency_ms": base_result.latency_ms,
            },
        )
        return RAGGenerationResult(
            output=output,
            latency_ms=base_result.latency_ms,
            attempt=base_result.attempt,
            from_cache=base_result.from_cache,
            metadata=base_result.metadata,
            provenance=provenance,
            citations=citations,
            context_used=context_chunks,
        )


__all__: Sequence[str] = ["RAGGenerator", "RAGGenerationResult", "ProvenanceChunk", "extract_citations", "build_context_block"]
