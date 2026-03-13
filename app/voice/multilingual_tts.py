from __future__ import annotations

"""
MultilingualTTS: Piper-based DE/FR/IT/EN text-to-speech for Swiss retail.

Design:
- Uses on-device Piper models (ONNX) for low-latency synthesis
- Wraps Piper's streaming API and returns WAV bytes for WebSocket playback
- Fallbacks gracefully when Piper or voice models are missing
"""

import asyncio
import io
import logging
import os
from pathlib import Path
from typing import Dict, Optional

import numpy as np

logger = logging.getLogger(__name__)

try:
    from piper import PiperVoice  # type: ignore[import]
except Exception:  # pragma: no cover - optional heavy dependency
    PiperVoice = None  # type: ignore[assignment]


VOICES_DIR = Path(os.getenv("PIPER_VOICES_DIR", "./voices"))


class MultilingualTTS:
    """
    Lightweight wrapper over Piper voices for DE/FR/IT/EN.

    Returns 16 kHz mono WAV bytes suitable for WebSocket `send_bytes`.
    """

    def __init__(self) -> None:
        self.sample_rate = 16_000
        self._voices: Dict[str, Optional["PiperVoice"]] = {}
        self._load_voices()

    def _load_voice(self, lang: str, filename: str) -> Optional["PiperVoice"]:
        if PiperVoice is None:
            logger.warning("piper-tts not installed; MultilingualTTS will be disabled")
            return None
        model_path = VOICES_DIR / filename
        if not model_path.exists():
            logger.warning("Piper voice model not found for %s: %s", lang, model_path)
            return None
        try:
            logger.info("Loading Piper voice for %s from %s", lang, model_path)
            return PiperVoice.load(model_path)
        except Exception as exc:  # pragma: no cover - safety net
            logger.warning("Failed to load Piper voice for %s: %s", lang, exc)
            return None

    def _load_voices(self) -> None:
        # Reasonable defaults; callers can override via env + mounted ./voices dir
        self._voices = {
            "de": self._load_voice("de", "de_DE-karl-medium.onnx"),
            "fr": self._load_voice("fr", "fr_FR-nettie-medium.onnx"),
            "it": self._load_voice("it", "it_IT-riccardo-medium.onnx"),
            "en": self._load_voice("en", "en_US-lessac-medium.onnx"),
        }

    def _get_voice(self, language: str) -> Optional["PiperVoice"]:
        # Normalize language codes: de-CH → de, fr-CH → fr, etc.
        lang = (language or "de").split("-")[0].lower()
        voice = self._voices.get(lang) or self._voices.get("de")
        if voice is None:
            logger.warning("No Piper voice available for language=%s", language)
        return voice

    def _synthesize_wav_sync(self, text: str, language: str) -> bytes:
        """
        Blocking synthesis: text → PCM16 → WAV bytes.
        """
        if not text.strip():
            return b""

        voice = self._get_voice(language)
        if voice is None:
            return b""

        # Piper streaming yields int16 samples; we accumulate then wrap as WAV.
        audio_samples: list[int] = []
        try:
            for chunk in voice.synthesize_stream(text):
                # `chunk` is expected to be an iterable[float] or int16; normalize to int
                if isinstance(chunk, np.ndarray):
                    audio_samples.extend(int(x) for x in chunk.astype(np.int16).tolist())
                else:
                    audio_samples.extend(int(x) for x in chunk)
        except Exception as exc:  # pragma: no cover - safety net
            logger.warning("Piper synthesis failed: %s", exc)
            return b""

        if not audio_samples:
            return b""

        pcm = np.array(audio_samples, dtype=np.int16)

        # Build a simple WAV header in-memory
        import wave

        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes(pcm.tobytes())
        return buf.getvalue()

    async def synthesize(self, text: str, language: str) -> bytes:
        """
        Async-friendly wrapper: delegates to threadpool to avoid blocking event loop.
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, self._synthesize_wav_sync, text, language
        )


__all__ = ["MultilingualTTS"]

