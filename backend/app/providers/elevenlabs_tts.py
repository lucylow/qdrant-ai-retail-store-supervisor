"""
ElevenLabs TTS: German voice response for live demo.

~$0.20/demo; $100 credit free tier. Use for judge demo voice-out.
"""

from __future__ import annotations

import base64
import logging
from typing import Optional

import requests

from app.config import EXTERNAL_PROVIDERS

logger = logging.getLogger(__name__)

ELEVENLABS_API = "https://api.elevenlabs.io/v1"
# Default: German-friendly voice (Rachel); override with ELEVENLABS_VOICE_ID
DEFAULT_VOICE_ID = "EXAVITQu4vr4xnSDxMaL"


def text_to_speech_german(
    text: str,
    *,
    voice_id: Optional[str] = None,
) -> Optional[bytes]:
    """
    Convert text to German voice audio via ElevenLabs.

    Returns raw audio bytes (mp3) or None if API key missing or error.
    """
    key = EXTERNAL_PROVIDERS.elevenlabs_api_key
    if not key or not text.strip():
        return None
    vid = voice_id or EXTERNAL_PROVIDERS.elevenlabs_voice_id or DEFAULT_VOICE_ID
    url = f"{ELEVENLABS_API}/text-to-speech/{vid}"
    headers = {
        "xi-api-key": key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.content
    except Exception as e:
        logger.warning("ElevenLabs TTS failed: %s", e)
        return None


def reply_audio_base64(text: str, *, voice_id: Optional[str] = None) -> Optional[str]:
    """Return base64-encoded MP3 for JSON response, or None."""
    raw = text_to_speech_german(text, voice_id=voice_id)
    if raw is None:
        return None
    return base64.b64encode(raw).decode("ascii")
