from __future__ import annotations

"""
WebSocket voice chat endpoint:

Client:
  - Sends 16 kHz mono PCM16 audio chunks, base64-encoded in text frames:
      "AUDIO:<base64-bytes>"
Server:
  - SwissVoiceProcessor (Whisper) → transcript (Swiss German → standard DE)
  - Multilingual shopper/response agents → short bundle text
  - MultilingualTTS (Piper) → 16 kHz WAV bytes
  - Streams WAV bytes back via WebSocket `send_bytes`
"""

import base64
import logging
from typing import Any, Dict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from agents.response_generator import MultilingualResponseGenerator
from agents.shopper_agent import MultilingualShopperAgent
from app.voice.multilingual_tts import MultilingualTTS
from app.voice.voice_processor import SwissVoiceProcessor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["voice"])


@router.websocket("/voice/{tenant}")
async def voice_chat(websocket: WebSocket, tenant: str) -> None:
    """
    Bidirectional voice: audio in → Whisper/BGE-M3/Qdrant → Piper TTS out.

    - Input: text frames starting with "AUDIO:" followed by base64-encoded PCM16 bytes.
    - Output: binary frames containing 16 kHz mono WAV audio.
    """
    await websocket.accept()

    shopper = MultilingualShopperAgent()
    response_gen = MultilingualResponseGenerator()
    stt = SwissVoiceProcessor()
    tts = MultilingualTTS()

    try:
        while True:
            msg = await websocket.receive()
            if msg.get("type") == "websocket.disconnect":
                break

            text_data = msg.get("text")
            raw_bytes = msg.get("bytes")

            if text_data:
                # Expecting "AUDIO:<base64>"
                if text_data.startswith("AUDIO:"):
                    try:
                        audio_bytes = base64.b64decode(text_data[6:])
                    except Exception:
                        logger.warning("voice_chat: invalid base64 audio frame")
                        continue
                else:
                    # Fallback: treat as direct text query (no STT); useful for testing.
                    transcript = text_data.strip()
                    if not transcript:
                        continue
                    await _handle_transcript_and_reply(
                        websocket, shopper, response_gen, tts, transcript, tenant
                    )
                    continue
            elif raw_bytes:
                audio_bytes = raw_bytes
            else:
                continue

            transcript = stt.process_chunk(audio_bytes)
            if not transcript:
                continue

            await _handle_transcript_and_reply(
                websocket, shopper, response_gen, tts, transcript, tenant
            )
    except WebSocketDisconnect:
        logger.info("voice_chat disconnected for tenant=%s", tenant)
    except Exception as exc:  # noqa: BLE001
        logger.warning("voice_chat error for tenant=%s: %s", tenant, exc)
        try:
            await websocket.close()
        except Exception:  # pragma: no cover - best-effort close
            pass


async def _handle_transcript_and_reply(
    websocket: WebSocket,
    shopper: MultilingualShopperAgent,
    response_gen: MultilingualResponseGenerator,
    tts: MultilingualTTS,
    transcript: str,
    tenant: str,
) -> None:
    """
    Run shopper agent → generate localized text → synthesize TTS → send WAV bytes.
    """
    try:
        result = await shopper.process_query(query=transcript, tenant=tenant)
    except Exception as exc:  # noqa: BLE001
        logger.warning("voice_chat shopper error: %s", exc)
        return

    reply_text = response_gen.generate_response(
        solution=result.solution,
        detected_lang=result.detected_language,
        tenant=tenant,
    )

    audio_bytes = await tts.synthesize(reply_text, result.detected_language)
    if not audio_bytes:
        # If TTS failed, we can still send back the text as JSON for debugging.
        payload: Dict[str, Any] = {
            "transcript": transcript,
            "language": result.detected_language,
            "text": reply_text,
            "confidence": result.confidence,
        }
        await websocket.send_json(payload)
        return

    await websocket.send_bytes(audio_bytes)


__all__ = ["router"]

