"""
Pluggable LLM client centred on swiss-ai/Apertus-70B-2509.

Supports three backends:
  1. Local transformers / vLLM  (APERTUS_BACKEND=local)
  2. Remote OpenAI-compatible endpoint (APERTUS_BACKEND=remote)  — vLLM, SGLang, TGI
  3. HuggingFace Inference API     (APERTUS_BACKEND=hf)

Environment variables (see app.llm.config):
  APERTUS_MODEL          – HF model id            (default: swiss-ai/Apertus-70B-2509)
  APERTUS_BACKEND        – local | remote | hf    (default: remote)
  APERTUS_ENDPOINT       – base URL for remote    (default: http://localhost:8000/v1)
  APERTUS_MAX_TOKENS     – generation limit       (default: 1024)
  APERTUS_TEMPERATURE    – sampling temperature   (default: 0.3)
  APERTUS_TOP_P          – nucleus sampling       (default: 0.95)
  HF_TOKEN               – HuggingFace token      (reused from app.config)
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional, Sequence

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

APERTUS_MODEL: str = os.getenv("APERTUS_MODEL", "swiss-ai/Apertus-70B-2509")
APERTUS_BACKEND: str = os.getenv("APERTUS_BACKEND", "remote").lower()
APERTUS_ENDPOINT: str = os.getenv("APERTUS_ENDPOINT", "http://localhost:8000/v1")
APERTUS_MAX_TOKENS: int = int(os.getenv("APERTUS_MAX_TOKENS", "1024"))
APERTUS_TEMPERATURE: float = float(os.getenv("APERTUS_TEMPERATURE", "0.3"))
APERTUS_TOP_P: float = float(os.getenv("APERTUS_TOP_P", "0.95"))

# Tool-calling schema version
TOOL_CALL_FORMAT = "apertus_v1"

# ---------------------------------------------------------------------------
# Chat message types
# ---------------------------------------------------------------------------

@dataclass
class ChatMessage:
    role: str  # system | user | assistant | tool
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None


@dataclass
class ToolDefinition:
    """JSON-schema tool definition for Apertus function calling."""
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


@dataclass
class LLMResponse:
    content: str
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    usage: Dict[str, int] = field(default_factory=dict)
    model: str = ""
    finish_reason: str = "stop"


# ---------------------------------------------------------------------------
# System prompts per agent role (multilingual Swiss retail)
# ---------------------------------------------------------------------------

AGENT_SYSTEM_PROMPTS: Dict[str, str] = {
    "supervisor": (
        "You are the Supervisor Agent for a Swiss retail store (Coop/Migros class). "
        "You coordinate Shopper, Inventory, Pricing, and Merchandising agents. "
        "Reason step-by-step over retrieved episodes and product data. "
        "Respond in the customer's language (DE/FR/IT/EN). "
        "Use tools to search Qdrant, check stock, optimise prices, and schedule pickups. "
        "Always ground answers in retrieved facts — never hallucinate product details."
    ),
    "shopper": (
        "You are the Shopper Agent. Extract structured purchase intents from "
        "free-form, possibly multilingual user queries. Output JSON with fields: "
        "intent, budget, region, urgency_days, language, goal_text. "
        "Detect language automatically (DE/FR/IT/EN). "
        "Ask a clarifying question only when the intent is truly ambiguous."
    ),
    "inventory": (
        "You are the Inventory Agent for Swiss retail. Given a structured goal "
        "and candidate products from Qdrant, build up to 3 feasible bundles. "
        "Respect budget, stock levels, regional availability, and holiday demand "
        "multipliers (Christmas 4×, Easter 2.5×, Fondue season 1.5×). "
        "Return JSON array of bundles with skus, quantities, total_price, feasible, rationale."
    ),
    "pricing": (
        "You are the Pricing Agent. Given competitor prices and inventory bundles, "
        "optimise prices to maximise margin while staying competitive. "
        "Swiss market rules: prices in CHF, VAT 8.1% included, TWINT-friendly rounding. "
        "Return JSON with sku→price map, margin_pct, and justification."
    ),
    "merchandising": (
        "You are the Merchandising Agent. Given a bundle and pricing plan, "
        "create compelling promotional copy in the customer's language. "
        "Swiss tone: precise, trustworthy, multilingual. "
        "Return JSON with promo_text_de, promo_text_fr, promo_text_it, hero_image_prompt."
    ),
}

# ---------------------------------------------------------------------------
# ApertusClient
# ---------------------------------------------------------------------------

class ApertusClient:
    """
    Unified LLM client with Apertus-70B-2509 as default backbone.

    Usage:
        client = ApertusClient()
        resp = client.generate("What fondue kits are available?")
        # or with chat:
        resp = client.chat([ChatMessage(role="user", content="...")])
        # or with tools:
        resp = client.chat(messages, tools=[...])
    """

    def __init__(
        self,
        model: Optional[str] = None,
        backend: Optional[str] = None,
        endpoint: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
    ):
        self.model = model or APERTUS_MODEL
        self.backend = backend or APERTUS_BACKEND
        self.endpoint = endpoint or APERTUS_ENDPOINT
        self.max_tokens = max_tokens or APERTUS_MAX_TOKENS
        self.temperature = temperature if temperature is not None else APERTUS_TEMPERATURE
        self.top_p = top_p if top_p is not None else APERTUS_TOP_P

        self._local_pipeline = None
        self._tokenizer = None
        self._session = None

        logger.info(
            "ApertusClient init: model=%s backend=%s endpoint=%s",
            self.model, self.backend, self.endpoint,
        )

    # ----- public API -----

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> str:
        """Simple prompt→text generation (wraps chat internally)."""
        messages = []
        if system:
            messages.append(ChatMessage(role="system", content=system))
        messages.append(ChatMessage(role="user", content=prompt))
        resp = self.chat(messages, max_tokens=max_tokens, temperature=temperature, **kwargs)
        return resp.content

    def generate_for_agent(
        self,
        agent_name: str,
        prompt: str,
        max_tokens: Optional[int] = None,
        tools: Optional[List[ToolDefinition]] = None,
    ) -> LLMResponse:
        """Agent-specific generation with role system prompt + optional tools."""
        system = AGENT_SYSTEM_PROMPTS.get(agent_name, AGENT_SYSTEM_PROMPTS["supervisor"])
        messages = [
            ChatMessage(role="system", content=system),
            ChatMessage(role="user", content=prompt),
        ]
        return self.chat(messages, max_tokens=max_tokens, tools=tools)

    def chat(
        self,
        messages: List[ChatMessage],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        tools: Optional[List[ToolDefinition]] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Multi-turn chat completion with optional tool definitions."""
        max_tok = max_tokens or self.max_tokens
        temp = temperature if temperature is not None else self.temperature

        if self.backend == "remote":
            return self._chat_remote(messages, max_tok, temp, tools)
        elif self.backend == "hf":
            return self._chat_hf(messages, max_tok, temp)
        elif self.backend == "local":
            return self._chat_local(messages, max_tok, temp)
        else:
            raise ValueError(f"Unknown APERTUS_BACKEND: {self.backend}")

    def stream_generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> Iterator[str]:
        """Streaming generation (remote backend only, falls back to chunked)."""
        if self.backend == "remote":
            yield from self._stream_remote(prompt, system, max_tokens)
        else:
            full = self.generate(prompt, system=system, max_tokens=max_tokens)
            chunk_size = 128
            for i in range(0, len(full), chunk_size):
                yield full[i : i + chunk_size]

    # ----- remote (vLLM / SGLang / TGI via OpenAI-compat) -----

    def _get_session(self):
        if self._session is None:
            import requests
            self._session = requests.Session()
        return self._session

    def _chat_remote(
        self,
        messages: List[ChatMessage],
        max_tokens: int,
        temperature: float,
        tools: Optional[List[ToolDefinition]] = None,
    ) -> LLMResponse:
        import requests

        url = f"{self.endpoint}/chat/completions"
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [self._msg_to_dict(m) for m in messages],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": self.top_p,
        }
        if tools:
            payload["tools"] = [t.to_dict() for t in tools]
            payload["tool_choice"] = "auto"

        headers: Dict[str, str] = {"Content-Type": "application/json"}
        api_key = os.getenv("APERTUS_API_KEY") or os.getenv("OPENAI_API_KEY")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        try:
            resp = self._get_session().post(url, json=payload, headers=headers, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            choice = data["choices"][0]
            msg = choice.get("message", {})
            return LLMResponse(
                content=msg.get("content", ""),
                tool_calls=msg.get("tool_calls", []),
                usage=data.get("usage", {}),
                model=data.get("model", self.model),
                finish_reason=choice.get("finish_reason", "stop"),
            )
        except Exception as e:
            logger.error("Apertus remote call failed: %s", e)
            return LLMResponse(content="", finish_reason="error")

    def _stream_remote(
        self,
        prompt: str,
        system: Optional[str],
        max_tokens: Optional[int],
    ) -> Iterator[str]:
        import requests

        url = f"{self.endpoint}/chat/completions"
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens or self.max_tokens,
            "temperature": self.temperature,
            "stream": True,
        }
        headers: Dict[str, str] = {"Content-Type": "application/json"}
        api_key = os.getenv("APERTUS_API_KEY") or os.getenv("OPENAI_API_KEY")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        try:
            resp = self._get_session().post(
                url, json=payload, headers=headers, timeout=120, stream=True,
            )
            resp.raise_for_status()
            for line in resp.iter_lines(decode_unicode=True):
                if not line or not line.startswith("data: "):
                    continue
                chunk_str = line[len("data: "):]
                if chunk_str.strip() == "[DONE]":
                    break
                try:
                    chunk = json.loads(chunk_str)
                    delta = chunk["choices"][0].get("delta", {})
                    text = delta.get("content", "")
                    if text:
                        yield text
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue
        except Exception as e:
            logger.error("Apertus stream failed: %s", e)
            yield ""

    # ----- HuggingFace Inference API -----

    def _chat_hf(
        self,
        messages: List[ChatMessage],
        max_tokens: int,
        temperature: float,
    ) -> LLMResponse:
        import requests

        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            logger.warning("HF_TOKEN not set; HF inference unavailable")
            return LLMResponse(content="", finish_reason="error")

        url = f"https://api-inference.huggingface.co/models/{self.model}"
        # Build prompt from messages via chat template
        prompt = self._messages_to_prompt(messages)

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "top_p": self.top_p,
                "return_full_text": False,
            },
        }
        headers = {"Authorization": f"Bearer {hf_token}"}

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, list) and data:
                text = data[0].get("generated_text", "")
            elif isinstance(data, dict):
                text = data.get("generated_text", "")
            else:
                text = str(data)
            return LLMResponse(content=text, model=self.model)
        except Exception as e:
            logger.error("Apertus HF call failed: %s", e)
            return LLMResponse(content="", finish_reason="error")

    # ----- Local transformers -----

    def _chat_local(
        self,
        messages: List[ChatMessage],
        max_tokens: int,
        temperature: float,
    ) -> LLMResponse:
        if self._local_pipeline is None:
            self._init_local()
        if self._local_pipeline is None:
            return LLMResponse(content="Local pipeline unavailable", finish_reason="error")

        # Use tokenizer chat template if available
        if self._tokenizer is not None and hasattr(self._tokenizer, "apply_chat_template"):
            msg_dicts = [self._msg_to_dict(m) for m in messages]
            prompt = self._tokenizer.apply_chat_template(
                msg_dicts, tokenize=False, add_generation_prompt=True,
            )
        else:
            prompt = self._messages_to_prompt(messages)

        try:
            outputs = self._local_pipeline(
                prompt,
                max_new_tokens=max_tokens,
                temperature=temperature if temperature > 0 else None,
                top_p=self.top_p,
                do_sample=temperature > 0,
            )
            text = outputs[0].get("generated_text", "") if outputs else ""
            # Strip the prompt prefix if the pipeline returns full text
            if text.startswith(prompt):
                text = text[len(prompt):]
            return LLMResponse(content=text.strip(), model=self.model)
        except Exception as e:
            logger.error("Apertus local generation failed: %s", e)
            return LLMResponse(content="", finish_reason="error")

    def _init_local(self) -> None:
        try:
            import torch
            from transformers import AutoTokenizer, pipeline as hf_pipeline

            self._tokenizer = AutoTokenizer.from_pretrained(self.model)
            device = 0 if torch.cuda.is_available() else -1
            dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32

            self._local_pipeline = hf_pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self._tokenizer,
                device=device,
                torch_dtype=dtype,
                trust_remote_code=True,
            )
            logger.info("Apertus local pipeline loaded: %s (device=%s)", self.model, device)
        except Exception as e:
            logger.error("Failed to load Apertus locally: %s", e)
            self._local_pipeline = None

    # ----- helpers -----

    @staticmethod
    def _msg_to_dict(m: ChatMessage) -> Dict[str, Any]:
        d: Dict[str, Any] = {"role": m.role, "content": m.content}
        if m.tool_calls:
            d["tool_calls"] = m.tool_calls
        if m.tool_call_id:
            d["tool_call_id"] = m.tool_call_id
        if m.name:
            d["name"] = m.name
        return d

    @staticmethod
    def _messages_to_prompt(messages: List[ChatMessage]) -> str:
        """Fallback prompt builder when tokenizer chat template unavailable."""
        parts: List[str] = []
        for m in messages:
            if m.role == "system":
                parts.append(f"<|system|>\n{m.content}")
            elif m.role == "user":
                parts.append(f"<|user|>\n{m.content}")
            elif m.role == "assistant":
                parts.append(f"<|assistant|>\n{m.content}")
            elif m.role == "tool":
                parts.append(f"<|tool|>\n{m.content}")
        parts.append("<|assistant|>\n")
        return "\n".join(parts)


# ---------------------------------------------------------------------------
# Singleton + convenience
# ---------------------------------------------------------------------------

_client: Optional[ApertusClient] = None


def get_llm_client() -> ApertusClient:
    """Return module-level singleton ApertusClient."""
    global _client
    if _client is None:
        _client = ApertusClient()
    return _client


def generate(prompt: str, **kwargs: Any) -> str:
    """Drop-in replacement for app.llm_client.generate()."""
    return get_llm_client().generate(prompt, **kwargs)


def stream_generate(prompt: str, **kwargs: Any) -> Iterator[str]:
    return get_llm_client().stream_generate(prompt, **kwargs)


__all__ = [
    "ApertusClient",
    "ChatMessage",
    "LLMResponse",
    "ToolDefinition",
    "AGENT_SYSTEM_PROMPTS",
    "get_llm_client",
    "generate",
    "stream_generate",
]
