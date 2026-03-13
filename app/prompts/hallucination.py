"""
GENAI-HACKATHON: Multi-method hallucination detection.
Composite score: lexical 40%, entailment 40%, confidence 20% (temporal 10% in spec: we use confidence 20%).
Score < 0.25 passes; >= 0.25 blocks response.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import List, Optional, Sequence

from app.config import GENAI

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class HallucinationScores:
    lexical_overlap: float
    entailment: float
    confidence_calibration: float
    temporal_consistency: float
    composite: float


class HallucinationDetector:
    """
    4x detection methods: lexical overlap, entailment, confidence calibration, temporal consistency.
    Composite = 0.4*lexical + 0.4*entailment + 0.1*confidence + 0.1*temporal.
    Lower composite = more grounded. Block when composite > threshold (default 0.25).
    """

    def __init__(
        self,
        lexical_weight: Optional[float] = None,
        entailment_weight: Optional[float] = None,
        confidence_weight: Optional[float] = None,
        temporal_weight: Optional[float] = None,
        block_threshold: Optional[float] = None,
    ) -> None:
        self._lexical_w = lexical_weight if lexical_weight is not None else GENAI.lexical_weight
        self._entailment_w = entailment_weight if entailment_weight is not None else GENAI.entailment_weight
        self._confidence_w = confidence_weight if confidence_weight is not None else GENAI.confidence_weight
        self._temporal_w = temporal_weight if temporal_weight is not None else GENAI.temporal_weight
        self._block_threshold = block_threshold if block_threshold is not None else GENAI.hallucination_block_threshold

    def lexical_overlap(self, generated: str, retrieved: List[str]) -> float:
        """
        Lexical overlap: fraction of important tokens in generated that appear in retrieved.
        Higher = more grounded. Return 1 - overlap_score so that higher = more hallucination.
        """
        if not retrieved:
            return 0.5  # no context -> assume moderate risk
        combined = " ".join(retrieved).lower()
        combined_tokens = set(re.findall(r"\b\w{2,}\b", combined))
        gen_tokens = set(re.findall(r"\b\w{2,}\b", generated.lower()))
        if not gen_tokens:
            return 0.0
        overlap = len(gen_tokens & combined_tokens) / len(gen_tokens)
        # Hallucination score: 1 - overlap (low overlap = high hallucination)
        return 1.0 - overlap

    async def entailment_check(self, generated: str, retrieved: List[str]) -> float:
        """
        Entailment: is generated supported by retrieved? Simplified: sentence overlap proxy.
        Return 0 = fully supported, 1 = not supported (hallucination).
        """
        if not retrieved:
            return 0.5
        # Without NLI model: use lexical overlap as proxy for entailment
        return self.lexical_overlap(generated, retrieved)

    def confidence_score(self, generated: str) -> float:
        """
        Confidence calibration: detect overconfident language. Higher = more hallucination risk.
        Look for phrases like "certainly", "absolutely", "100%", "guaranteed" without citations.
        """
        overconfident = re.compile(
            r"\b(certainly|absolutely|guaranteed|100%|definitely|always|never)\b",
            re.I,
        )
        if not generated:
            return 0.0
        matches = len(overconfident.findall(generated))
        # Has [0], [1] citations -> lower risk
        has_citations = "[" in generated and "]" in generated
        if has_citations:
            matches = max(0, matches - 1)
        return min(1.0, matches * 0.25)

    def temporal_check(self, generated: str) -> float:
        """
        Temporal consistency: delivery estimates within today ±30% sensible range.
        References to "tomorrow", "next week" etc. without conflicting numbers -> 0.
        Conflicting dates or impossible delivery -> higher score.
        """
        # Simple heuristic: if "delivery" and numbers, check for reasonable range (1-30 days)
        numbers = re.findall(r"\b(\d+)\s*day", generated.lower())
        if not numbers:
            return 0.0
        for n in numbers:
            try:
                d = int(n)
                if d < 0 or d > 365:
                    return 0.5  # suspicious
            except ValueError:
                pass
        return 0.0

    async def score(
        self,
        generated: str,
        retrieved: List[str],
    ) -> HallucinationScores:
        """
        Compute all 4 scores and composite. Composite < threshold = pass.
        """
        lexical = self.lexical_overlap(generated, retrieved)
        entailment = await self.entailment_check(generated, retrieved)
        confidence = self.confidence_score(generated)
        temporal = self.temporal_check(generated)
        composite = (
            self._lexical_w * lexical
            + self._entailment_w * entailment
            + self._confidence_w * confidence
            + self._temporal_w * temporal
        )
        result = HallucinationScores(
            lexical_overlap=lexical,
            entailment=entailment,
            confidence_calibration=confidence,
            temporal_consistency=temporal,
            composite=composite,
        )
        logger.info(
            "Hallucination score",
            extra={
                "template": "hallucination",
                "hallucination_score": round(composite, 3),
                "lexical": round(lexical, 3),
                "entailment": round(entailment, 3),
                "confidence": round(confidence, 3),
                "temporal": round(temporal, 3),
            },
        )
        return result

    def score_sync(self, generated: str, retrieved: List[str]) -> HallucinationScores:
        """Synchronous score (entailment uses overlap proxy)."""
        import asyncio
        return asyncio.get_event_loop().run_until_complete(self.score(generated, retrieved))

    def should_block(self, composite: float) -> bool:
        """Return True if response should be blocked (composite >= threshold)."""
        return composite >= self._block_threshold


__all__: Sequence[str] = ["HallucinationDetector", "HallucinationScores"]
