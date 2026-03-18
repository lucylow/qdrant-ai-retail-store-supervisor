"""
Single LLM entrypoint used across the backend.

Important separation of concerns for RAG with Qdrant:
- **Qdrant** is only used for vector search (embeddings).
- **Apertus** (`swiss-ai/Apertus-70B-2509`) is used for *generation* after retrieval.
"""

from __future__ import annotations

from typing import Iterator, Optional

from app.llm.apertus_client import get_llm_client


def generate(
    prompt: str,
    *,
    system: Optional[str] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
) -> str:
    """
    Generate text using the configured Apertus backend.

    Backend selection is controlled via env:
    - APERTUS_BACKEND=remote (OpenAI-compatible `/v1/chat/completions`)
    - APERTUS_BACKEND=hf     (HuggingFace Inference API)
    - APERTUS_BACKEND=local  (transformers pipeline)
    """
    return get_llm_client().generate(
        prompt,
        system=system,
        max_tokens=max_tokens,
        temperature=temperature,
    )


def stream_generate(
    prompt: str,
    *,
    system: Optional[str] = None,
    max_tokens: Optional[int] = None,
) -> Iterator[str]:
    return get_llm_client().stream_generate(prompt, system=system, max_tokens=max_tokens)


__all__ = ["generate", "stream_generate"]

