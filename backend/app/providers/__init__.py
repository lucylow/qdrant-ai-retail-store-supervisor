"""
External provider integrations for production: HF, Whisper, Replicate, Groq (agent), ElevenLabs (TTS).

Use when HF_TOKEN / OPENAI_API_KEY / GROQ_API_KEY / ELEVENLABS_API_KEY are set.
"""

from app.providers.huggingface import embed_multimodal_hf
from app.providers.whisper import transcribe_swiss_german
from app.providers.groq_agent import inventory_agent_reply
from app.providers.elevenlabs_tts import text_to_speech_german, reply_audio_base64

__all__ = [
    "embed_multimodal_hf",
    "transcribe_swiss_german",
    "inventory_agent_reply",
    "text_to_speech_german",
    "reply_audio_base64",
]
