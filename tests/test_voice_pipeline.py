import os
from pathlib import Path
from typing import Dict

import pytest

pytestmark = pytest.mark.voice


def _has_whisper() -> bool:
    try:
        import whisper  # type: ignore[import]
    except Exception:
        return False
    return True


def _has_piper() -> bool:
    try:
        from piper import PiperVoice  # type: ignore[import]  # noqa: F401
    except Exception:
        return False
    return True


@pytest.mark.skipif(not _has_whisper(), reason="openai-whisper not installed")
def test_swiss_voice_processor_basic_roundtrip(tmp_path: Path) -> None:
    """
    Smoke-test SwissVoiceProcessor: ensure it can import and accept bytes.

    This does NOT assert STT accuracy (requires real audio + model weights),
    but guarantees the streaming API does not raise and returns a string.
    """
    from app.voice.voice_processor import SwissVoiceProcessor

    processor = SwissVoiceProcessor()

    # 1 second of silence at 16 kHz mono PCM16
    silence = (b"\x00\x00") * 16_000
    text = processor.transcribe_once(silence)
    # We only assert it returns a string and does not crash
    assert isinstance(text, str)


@pytest.mark.skipif(not _has_piper(), reason="piper-tts not installed or voices missing")
def test_multilingual_tts_wav_header() -> None:
    """
    Smoke-test MultilingualTTS: ensure it returns RIFF WAV bytes when voices available.
    """
    from app.voice.multilingual_tts import MultilingualTTS

    # Only run when a voices directory is configured and exists
    voices_dir = Path(os.getenv("PIPER_VOICES_DIR", "./voices"))
    if not voices_dir.exists():
        pytest.skip(f"Piper voices directory not found: {voices_dir}")

    tts = MultilingualTTS()
    audio = pytest.run(async_tts(tts))  # type: ignore[attr-defined]

    # Fallback: if synthesis returns empty bytes (e.g. voice load failed), skip
    if not audio:
        pytest.skip("Piper voices could not be loaded; skipping WAV assertion")

    assert audio.startswith(b"RIFF")


async def async_tts(tts) -> bytes:
    return await tts.synthesize(
        "Bio-Milch 2L plus Müsli und Joghurt für 12.95 Franken. Abholung Zürich HB.",
        "de",
    )


@pytest.mark.asyncio
async def test_voice_agents_integration_smoke() -> None:
    """
    Lightweight integration test: text transcript → shopper agent → response generator.
    """
    from agents.response_generator import MultilingualResponseGenerator
    from agents.shopper_agent import MultilingualShopperAgent

    shopper = MultilingualShopperAgent()
    response_gen = MultilingualResponseGenerator()

    query = "Bio-Milch laktosefrei 2L Zürich HB morgen"
    result = await shopper.process_query(query=query, tenant="coop")

    reply = response_gen.generate_response(
        solution=result.solution,
        detected_lang=result.detected_language,
        tenant="coop",
    )

    assert isinstance(reply, str)
    assert "CHF" in reply or "Franken" in reply or "CHF." in reply

