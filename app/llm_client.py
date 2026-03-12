from typing import Optional

from openai import OpenAI

from config import LLM_MODEL, client as global_openai_client  # reuse existing config


class LLMClient:
    """
    Thin wrapper around the existing OpenAI client used in the top-level prototype.
    This keeps the new app package loosely coupled while reusing configuration.
    """

    def __init__(self, client: Optional[OpenAI] = None, model: Optional[str] = None):
        self._client = client or global_openai_client
        self._model = model or LLM_MODEL

    def generate(self, prompt: str) -> str:
        resp = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return resp.choices[0].message.content


__all__ = ["LLMClient"]

"""
Pluggable minimal LLM client with sync & streaming support.
- Supports Hugging Face Inference API via hf_inference, OpenAI, or local transformers pipeline.
- Exposes: generate(prompt, **opts) -> str
           stream_generate(prompt, **opts) -> generator yielding chunks
- You can extend for model-specific options.
"""

from typing import Optional, Callable, AsyncIterator, Iterator, Dict, Any
import os
import logging
import time

from app.config import GENERATOR_PROVIDER, GENERATOR_MODEL, GENERATOR_MAX_TOKENS, GENERATOR_TEMPERATURE, GENERATOR_TOP_P

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self):
        self.provider = GENERATOR_PROVIDER.lower()
        self.model = GENERATOR_MODEL
        self._init_provider()

    def _init_provider(self):
        if self.provider == "hf":
            # Use Hugging Face Inference API if HF_API_KEY present, else fallback to local transformers
            self.hf_api_key = os.getenv("HF_API_KEY")
            if self.hf_api_key:
                import requests
                self._hf_url = f"https://api-inference.huggingface.co/models/{self.model}"
                self._session = requests.Session()
                self._session.headers.update({"Authorization": f"Bearer {self.hf_api_key}"})
            else:
                # local transformers fallback
                try:
                    from transformers import pipeline
                    device = 0 if self._has_gpu() else -1
                    self._local_gen = pipeline("text-generation", model=self.model, device=device)
                except Exception as e:
                    logger.warning("Local transformers pipeline not available: %s", e)
                    self._local_gen = None
        elif self.provider == "openai":
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
            if not self.openai_api_key:
                logger.warning("OPENAI_PROVIDER selected but OPENAI_API_KEY missing")
        else:
            logger.warning("Unknown GENERATOR_PROVIDER, falling back to local if possible")
            self._local_gen = None

    def _has_gpu(self):
        try:
            import torch
            return torch.cuda.is_available()
        except Exception:
            return False

    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = GENERATOR_TEMPERATURE,
        top_p: float = GENERATOR_TOP_P,
    ) -> str:
        max_tokens = max_tokens or GENERATOR_MAX_TOKENS
        if self.provider == "hf" and getattr(self, "_session", None):
            import requests

            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": temperature,
                    "top_p": top_p,
                },
            }
            r = self._session.post(self._hf_url, json=payload, timeout=120)
            r.raise_for_status()
            out = r.json()
            # HF returns list or dict depending on model
            if isinstance(out, list):
                return out[0].get("generated_text", "")
            if isinstance(out, dict):
                return out.get("generated_text", "") or out.get("generated_texts", [""])[0]
            return str(out)
        elif self.provider == "openai":
            try:
                import openai

                openai.api_key = os.getenv("OPENAI_API_KEY")
                resp = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                )
                return resp["choices"][0]["message"]["content"]
            except Exception as e:
                logger.exception("OpenAI call failed: %s", e)
                return ""
        else:
            # local fallback
            if getattr(self, "_local_gen", None):
                out = self._local_gen(prompt, max_length=max_tokens, do_sample=False)
                return out[0]["generated_text"]
            else:
                logger.error("No generation backend available")
                return "LLM backend not configured."

    def stream_generate(self, prompt: str, chunk_size: int = 128) -> Iterator[str]:
        """
        Simple synchronous streaming wrapper. Yields partial strings.
        For HF streaming or OpenAI streaming, implement provider-specific streaming.
        """
        # If HF session supports streaming (HF doesn't by default via simple endpoint), fallback to chunked local generation.
        full = self.generate(prompt)
        # naive chunking:
        for i in range(0, len(full), chunk_size):
            yield full[i : i + chunk_size]


# convenience singleton
_llm_client = LLMClient()


def generate(prompt: str, **opts) -> str:
    return _llm_client.generate(prompt, **opts)


def stream_generate(prompt: str, **opts):
    return _llm_client.stream_generate(prompt, **opts)

