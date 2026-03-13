from __future__ import annotations

"""
VoiceShopperAgent: thin voice-optimized wrapper over MultilingualShopperAgent.

Goals:
- Short, confirmation-friendly responses for hands-free grocery shopping
- Reuse existing BGE-M3 + Qdrant multilingual shopper and templates
"""

from dataclasses import dataclass, field
from typing import Any, Dict

from agents.response_generator import MultilingualResponseGenerator
from agents.shopper_agent import MultilingualShopperAgent, MultilingualQueryResult


@dataclass
class VoiceSessionState:
    step: str = "greeting"
    last_result: MultilingualQueryResult | None = None


class VoiceShopperAgent:
    """
    Conversational, voice-first layer around the core shopper agent.

    This keeps minimal in-memory state keyed by `session_id` so the caller
    (e.g. WebSocket connection) can offer short confirmations like:
      - "Ich habe 3 Produkte für 12.95 CHF. Abholung Zürich HB. Fortfahren?"
    """

    def __init__(self) -> None:
        self._shopper = MultilingualShopperAgent()
        self._response_gen = MultilingualResponseGenerator()
        self._sessions: Dict[str, VoiceSessionState] = {}

    def _get_state(self, session_id: str) -> VoiceSessionState:
        if session_id not in self._sessions:
            self._sessions[session_id] = VoiceSessionState()
        return self._sessions[session_id]

    async def handle_voice_query(
        self,
        transcript: str,
        tenant: str,
        session_id: str,
    ) -> Dict[str, Any]:
        """
        Process a single utterance and return a short voice-friendly reply payload.
        """
        state = self._get_state(session_id)

        # First turn: greeting
        if state.step == "greeting":
            state.step = "query"
            return {
                "text": "Willkommen bei Coop leShop.ch! Was möchten Sie heute einkaufen?",
                "language": "de",
                "next_step": state.step,
            }

        # Main query turn: run full shopper pipeline
        result = await self._shopper.process_query(query=transcript, tenant=tenant)
        state.last_result = result
        state.step = "confirmation"

        text = self._response_gen.generate_response(
            solution=result.solution,
            detected_lang=result.detected_language,
            tenant=tenant,
        )

        products = result.solution.get("products") or []
        if isinstance(products, str):
            count = 1
        else:
            count = len(products)

        reply = {
            "text": text,
            "language": result.detected_language,
            "bundle": result.solution,
            "product_count": count,
            "confidence": result.confidence,
            "next_step": state.step,
        }
        return reply


__all__ = ["VoiceShopperAgent"]

