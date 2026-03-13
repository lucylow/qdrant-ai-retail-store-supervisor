"""
Chunked response streaming for token-by-token generation with cache.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, AsyncIterator, Dict, List

logger = logging.getLogger(__name__)


class StreamingGenerator:
    """Token-by-token streaming with optional cache and async chunking."""

    def __init__(
        self,
        llm_stream_fn: Any = None,
        cache: Any = None,
    ) -> None:
        self._llm_stream = llm_stream_fn
        self.cache = cache

    async def generate_stream(
        self,
        prompt: str,
        context: List[str],
        max_tokens: int = 2048,
    ) -> AsyncIterator[str]:
        """Token-by-token streaming with async chunking."""
        cache_key = None
        if self.cache is not None and hasattr(self.cache, "fingerprint"):
            cache_key = self.cache.fingerprint("generate", prompt=prompt[:100])

        if cache_key and self.cache:
            try:
                cached_stream = await self.cache.get(cache_key)
                if cached_stream is not None:
                    for chunk in cached_stream if isinstance(cached_stream, list) else [cached_stream]:
                        yield chunk
                        await asyncio.sleep(0.05)
                    return
            except Exception as e:
                logger.debug("Stream cache get failed: %s", e)

        chunks: List[str] = []
        if self._llm_stream:
            async for token_chunk in self._stream_llm(prompt, context, max_tokens):
                chunks.append(token_chunk)
                yield token_chunk
            if cache_key and self.cache and chunks:
                try:
                    await self.cache.set(cache_key, chunks)
                except Exception as e:
                    logger.debug("Stream cache set failed: %s", e)
        else:
            yield f"[no LLM]: {prompt[:80]}..."

    async def _stream_llm(
        self,
        prompt: str,
        context: List[str],
        max_tokens: int,
    ) -> AsyncIterator[str]:
        """Call underlying LLM stream; override or inject via constructor."""
        if self._llm_stream is None:
            return
        if asyncio.iscoroutinefunction(self._llm_stream):
            async for chunk in await self._llm_stream(prompt, context, max_tokens):
                yield chunk
        else:
            for chunk in self._llm_stream(prompt, context, max_tokens):
                yield chunk
                await asyncio.sleep(0.02)

    async def stream_dict(self, prompt: str, context: List[str]) -> AsyncIterator[Dict[str, Any]]:
        """Yield chunks as small dicts for API responses."""
        async for token_chunk in self.generate_stream(prompt, context):
            yield {"chunk": token_chunk, "done": False}
        yield {"chunk": "", "done": True}
