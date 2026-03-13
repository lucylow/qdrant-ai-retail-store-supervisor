"""
LLM agent for inventory/shopper reply: Groq (Mixtral, ~42ms) or OpenAI GPT-4o mini.

Turns search results into a short German reply for voice/text response.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.config import EXTERNAL_PROVIDERS

logger = logging.getLogger(__name__)

AGENT_SYSTEM = """Du bist ein freundlicher Verkäufer in einem Schweizer Einzelhandelsgeschäft.
Antworte kurz auf Deutsch (Hochdeutsch oder Schweizerdeutsch). Nenne Preise in Franken.
Halte die Antwort auf 1-2 Sätze; bestätige Lieferung oder Abholung wenn relevant."""


def _payloads_from_bundle(bundle: Dict[str, Any]) -> List[Dict[str, Any]]:
    results = bundle.get("results") or []
    return [r.get("payload") or {} for r in results]


def _build_products_summary(payloads: List[Dict[str, Any]], max_items: int = 5) -> str:
    lines = []
    for i, p in enumerate(payloads[:max_items]):
        name = p.get("name") or p.get("title") or "Produkt"
        price = p.get("price") or p.get("price_chf")
        stock = p.get("stock_status") or p.get("in_stock")
        line = f"- {name}"
        if price is not None:
            line += f", {price} CHF"
        if stock is not None:
            line += f", Lager: {stock}"
        lines.append(line)
    return "\n".join(lines) if lines else "Keine Produkte gefunden."


def inventory_agent_reply(
    bundle: Dict[str, Any],
    query_text: str,
    *,
    provider: Optional[str] = None,
) -> str:
    """
    Use Groq or OpenAI to generate a short German reply from search results.

    bundle: output of production pipeline (results + payloads).
    query_text: original user query (voice transcript or text).
    provider: override "groq" | "openai" | "none"; default from config.
    Returns empty string if no agent configured or on error.
    """
    prov = (provider or EXTERNAL_PROVIDERS.agent_provider or "none").lower()
    if prov == "none":
        return ""

    payloads = _payloads_from_bundle(bundle)
    products_summary = _build_products_summary(payloads)
    user_msg = f"Kundenanfrage: {query_text or 'Allgemeine Anfrage'}\n\nGefundene Produkte:\n{products_summary}\n\nAntworte kurz auf Deutsch."

    if prov == "groq" and EXTERNAL_PROVIDERS.groq_api_key:
        try:
            from groq import Groq
            client = Groq(api_key=EXTERNAL_PROVIDERS.groq_api_key)
            resp = client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[
                    {"role": "system", "content": AGENT_SYSTEM},
                    {"role": "user", "content": user_msg},
                ],
                max_tokens=150,
                temperature=0.3,
            )
            if resp.choices:
                return (resp.choices[0].message.content or "").strip()
        except Exception as e:
            logger.warning("Groq agent failed: %s", e)
        return ""

    if prov == "openai" and EXTERNAL_PROVIDERS.openai_api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=EXTERNAL_PROVIDERS.openai_api_key)
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": AGENT_SYSTEM},
                    {"role": "user", "content": user_msg},
                ],
                max_tokens=150,
                temperature=0.3,
            )
            if resp.choices:
                return (resp.choices[0].message.content or "").strip()
        except Exception as e:
            logger.warning("OpenAI agent failed: %s", e)
        return ""

    return ""
