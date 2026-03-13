from __future__ import annotations

"""
SwissVoiceProcessor: lightweight streaming wrapper around openai-whisper.

Design:
- Optimized for 16 kHz mono PCM16 chunks from browser / WebRTC
- Maintains a rolling buffer (30s) and emits text every ~3s of audio
- Normalizes Swiss German into standard German via Whisper language="de"

Dependencies:
- pip install openai-whisper
- ffmpeg must be available on PATH
"""

import logging
import os
from collections import deque
from typing import Deque, Optional

import numpy as np

logger = logging.getLogger(__name__)

try:
    import whisper  # type: ignore[import]
except Exception:  # pragma: no cover - optional heavy dependency
    whisper = None  # type: ignore[assignment]


class SwissVoiceProcessor:
    """
    Swiss German → text processor with a simple streaming API.

    Typical usage from a WebSocket handler:

        processor = SwissVoiceProcessor()
        while True:
            chunk = await websocket.receive_bytes()
            text = processor.process_chunk(chunk)
            if text:
                ...  # handle utterance
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        sample_rate: int = 16_000,
        window_seconds: int = 30,
        emit_seconds: int = 3,
    ) -> None:
        self.sample_rate = sample_rate
        self.window_seconds = window_seconds
        self.emit_seconds = emit_seconds
        self._model_name = model_name or os.getenv("WHISPER_MODEL", "medium")
        self._model = None
        self._buffer: Deque[int] = deque(
            maxlen=self.sample_rate * self.window_seconds
        )

    def _ensure_model(self) -> None:
        if self._model is not None:
            return
        if whisper is None:
            raise RuntimeError(
                "openai-whisper is not installed. "
                "Install with `pip install openai-whisper` to enable STT."
            )
        logger.info("Loading Whisper model %s for SwissVoiceProcessor", self._model_name)
        self._model = whisper.load_model(self._model_name)

    def reset(self) -> None:
        """Clear any buffered audio."""
        self._buffer.clear()

    def _transcribe_buffer(self) -> str:
        """
        Run Whisper on the current buffer and return the transcribed text.

        The internal buffer is PCM16; Whisper expects float32 in [-1, 1].
        """
        self._ensure_model()
        if self._model is None:
            return ""

        if not self._buffer:
            return ""

        # Convert deque[int] → numpy int16 → float32
        arr_int16 = np.frombuffer(
            np.array(list(self._buffer), dtype=np.int16).tobytes(),
            dtype=np.int16,
        )
        audio = arr_int16.astype(np.float32) / 32768.0
        if audio.size == 0:
            return ""

        try:
            result = self._model.transcribe(
                audio,
                language="de",  # Normalize Swiss German into standard German
                fp16=False,
            )
        except Exception as exc:  # pragma: no cover - safety net
            logger.warning("Whisper transcription failed: %s", exc)
            return ""

        text = (result.get("text") or "").strip()
        return text

    def process_chunk(self, pcm16_chunk: bytes) -> Optional[str]:
        """
        Add a PCM16 audio chunk to the rolling buffer.

        When enough audio (emit_seconds) has accumulated, returns a
        transcribed utterance; otherwise returns None.

        pcm16_chunk: raw 16-bit little-endian mono PCM at `sample_rate`.
        """
        if not pcm16_chunk:
            return None

        try:
            samples = np.frombuffer(pcm16_chunk, dtype=np.int16)
        except ValueError:
            logger.warning("SwissVoiceProcessor received non-PCM16 chunk of size %d", len(pcm16_chunk))
            return None

        if samples.size == 0:
            return None

        self._buffer.extend(int(s) for s in samples.tolist())

        # Emit every ~emit_seconds of accumulated audio
        if len(self._buffer) < self.sample_rate * self.emit_seconds:
            return None

        text = self._transcribe_buffer()
        if text and len(text) > 3:
            # Keep a small lookahead (1s) to avoid cutting off words
            keep = self.sample_rate
            if len(self._buffer) > keep:
                # convert deque to list and keep tail
                tail = list(self._buffer)[-keep:]
                self._buffer.clear()
                self._buffer.extend(tail)
            return text

        return None

    def transcribe_once(self, pcm16_audio: bytes) -> str:
        """
        Convenience helper for non-streaming use (e.g. test endpoint).
        """
        if not pcm16_audio:
            return ""
        try:
            samples = np.frombuffer(pcm16_audio, dtype=np.int16)
        except ValueError:
            logger.warning("SwissVoiceProcessor.transcribe_once received invalid audio bytes")
            return ""
        if samples.size == 0:
            return ""
        # replace buffer temporarily
        prev = list(self._buffer)
        self._buffer.clear()
        self._buffer.extend(int(s) for s in samples.tolist())
        try:
            text = self._transcribe_buffer()
        finally:
            self._buffer.clear()
            self._buffer.extend(prev)
        return text


__all__ = ["SwissVoiceProcessor"]

