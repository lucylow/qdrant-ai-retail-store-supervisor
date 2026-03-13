from __future__ import annotations

"""
Multilingual NLP pipeline for Swiss retail queries.

Phase 1: introduce a production-grade embedding + language detection layer
backed by BGE-M3 and langdetect, without yet wiring full intent parsing
or hybrid retrieval. This module is designed to be extended in later phases.
"""

from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Dict, Optional, Union

from langdetect import detect
from sentence_transformers import SentenceTransformer


InputType = Union[str, bytes]


@lru_cache(maxsize=1)
def _load_bge_m3() -> SentenceTransformer:
    """
    Centralized BGE-M3 loader so the rest of the app can share
    a single multilingual embedding model instance.
    """
    # BAAI/bge-m3: strong multilingual model (DE/FR/IT/EN + many more)
    return SentenceTransformer("BAAI/bge-m3")


@dataclass
class NLPResult:
    language: str
    original_text: str
    embedding: list[float]
    structured_goal: Dict[str, Any]
    confidence: float
    timestamp_ms: float


class SwissRetailNLP:
    """
    Core NLP facade used by higher-level agents and HTTP endpoints.

    Current responsibilities (Phase 1):
    - Handle text or raw audio bytes (audio currently treated as unsupported).
    - Detect language for DE/FR/IT/EN/other via langdetect.
    - Produce a BGE-M3 embedding for the raw user text.
    - Return a minimal structured_goal stub that can be enriched later.
    """

    def __init__(self) -> None:
        self._embedder = _load_bge_m3()

    async def process(self, input_data: InputType, tenant: str) -> Dict[str, Any]:
        """
        Run the minimal production NLP pipeline.

        Later phases will extend this to:
        - Transcribe Swiss German voice via Whisper.
        - Run spaCy NER + regex patterns + LLM-based intent parsing.
        - Feed into hybrid retrieval + multi-agent orchestration.
        """
        # Phase 1: only support text directly. Audio bytes will be rejected
        # explicitly so that future phases can plug in Whisper cleanly.
        if isinstance(input_data, bytes):
            raise ValueError("Audio input not yet supported in Phase 1 NLP pipeline")

        text = input_data.strip()

        # Language detection (fast heuristic; works well for DE/FR/IT/EN).
        try:
            lang = detect(text) if text else "unknown"
        except Exception:  # noqa: BLE001
            lang = "unknown"

        # Multilingual embedding via BGE-M3.
        emb = self._embedder.encode([text], convert_to_numpy=True, show_progress_bar=False)
        embedding_list = emb[0].astype("float32").tolist()

        # Minimal structured goal stub – to be replaced by SwissIntentParser.
        structured_goal: Dict[str, Any] = {
            "raw_query": text,
            "tenant": tenant,
            "language": lang,
        }

        result = NLPResult(
            language=lang,
            original_text=text,
            embedding=embedding_list,
            structured_goal=structured_goal,
            confidence=0.75 if text else 0.0,
            # Latency accounting will be filled in once we add real timing.
            timestamp_ms=0.0,
        )

        return {
            "language": result.language,
            "original_text": result.original_text,
            "structured_goal": result.structured_goal,
            "embedding": result.embedding,
            "confidence": result.confidence,
            "timestamp_ms": result.timestamp_ms,
        }


__all__ = ["SwissRetailNLP", "NLPResult"]

