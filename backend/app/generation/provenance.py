from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence


@dataclass(slots=True)
class TokenProvenance:
    token: str
    source_doc_id: str | None


class ProvenanceExtractor:
    """
    Dummy token-level provenance extractor.
    """

    def extract(self, text: str) -> List[TokenProvenance]:
        # AUTONOMOUS-AGENT-HACKATHON: simple per-token provenance stub.
        return [TokenProvenance(token=t, source_doc_id=None) for t in text.split()]


__all__: Sequence[str] = ["ProvenanceExtractor", "TokenProvenance"]

