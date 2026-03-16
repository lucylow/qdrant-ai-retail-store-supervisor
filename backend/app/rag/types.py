"""RAG types: RetrievalResult, Context, Provenance (production)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RetrievalResult(BaseModel):
    """Result of a retrieval call (multi-hop ready)."""

    query: str = Field(..., min_length=1)
    doc_ids: list[str] = Field(default_factory=list)
    scores: list[float] = Field(default_factory=list)
    payloads: list[dict[str, Any]] = Field(default_factory=list)

    def __len__(self) -> int:
        return len(self.doc_ids)


class Context(BaseModel):
    """Assembled context for generation (with provenance)."""

    text: str = Field(default="")
    provenance: list[dict[str, Any]] = Field(default_factory=list)
    max_tokens: int = Field(2048, ge=1, le=8192)


class Provenance(BaseModel):
    """Provenance entry for one retrieved chunk."""

    source: str = Field(..., max_length=256)
    score: float = Field(0.0, ge=0, le=1)
    doc_id: str | None = None
