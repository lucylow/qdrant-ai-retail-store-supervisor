"""
OpenAI Whisper API: audio → text (Swiss German normalization for cache keys).

$0.006/min; 25 min/month free. Use for voice queries in production pipeline.
"""

from __future__ import annotations

import io
import logging
from typing import Union

from app.config import EXTERNAL_PROVIDERS

logger = logging.getLogger(__name__)


def transcribe_swiss_german(
    audio_file: Union[str, bytes, io.BytesIO],
    *,
    language: str = "de",
    prompt: str = "Swiss German shopping query",
) -> str:
    """
    Transcribe audio to text using OpenAI Whisper. Use for voice → normalized text.

    audio_file: path (str), or bytes, or BytesIO.
    """
    if not EXTERNAL_PROVIDERS.openai_api_key:
        logger.warning("OPENAI_API_KEY not set; Whisper transcription skipped")
        return ""

    try:
        from openai import OpenAI
    except ImportError:
        logger.warning("openai package not installed; pip install openai")
        return ""

    client = OpenAI(api_key=EXTERNAL_PROVIDERS.openai_api_key)

    if isinstance(audio_file, str):
        with open(audio_file, "rb") as f:
            file_obj = f
            resp = client.audio.transcriptions.create(
                model="whisper-1",
                file=file_obj,
                language=language,
                response_format="json",
                prompt=prompt,
            )
    elif isinstance(audio_file, bytes):
        resp = client.audio.transcriptions.create(
            model="whisper-1",
            file=("audio.mp3", audio_file, "audio/mpeg"),
            language=language,
            response_format="json",
            prompt=prompt,
        )
    elif isinstance(audio_file, io.BytesIO):
        resp = client.audio.transcriptions.create(
            model="whisper-1",
            file=("audio.mp3", audio_file.read(), "audio/mpeg"),
            language=language,
            response_format="json",
            prompt=prompt,
        )
    else:
        logger.warning("transcribe_swiss_german: unsupported audio_file type")
        return ""

    if hasattr(resp, "text"):
        return resp.text or ""
    return str(resp) if resp else ""
