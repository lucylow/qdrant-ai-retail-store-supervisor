"""
Multilingual support for Apertus-70B-2509 (1811 languages).

Handles:
  - Language detection (Apertus prompt or langdetect fallback)
  - Cross-lingual query normalisation
  - Response localisation (DE/FR/IT/EN)
  - Swiss-specific linguistic patterns ("morgen 10h", "Bio-Milch")
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Swiss retail supported languages
SUPPORTED_LANGUAGES = {"de", "fr", "it", "en"}

# Language-specific system prompt suffixes
LANGUAGE_INSTRUCTIONS: Dict[str, str] = {
    "de": "Antworte auf Deutsch. Verwende Schweizer Konventionen (CHF, 24h-Format, formelle Anrede).",
    "fr": "Réponds en français. Utilise les conventions suisses (CHF, format 24h, vouvoiement).",
    "it": "Rispondi in italiano. Usa le convenzioni svizzere (CHF, formato 24h, forma di cortesia).",
    "en": "Respond in English. Use Swiss conventions (CHF, 24h format, formal tone).",
}

# Canonical field translations for Qdrant payloads
FIELD_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "de": {"name": "name_de", "description": "beschreibung", "category": "kategorie"},
    "fr": {"name": "name_fr", "description": "description", "category": "catégorie"},
    "it": {"name": "name_it", "description": "descrizione", "category": "categoria"},
    "en": {"name": "name", "description": "description", "category": "category"},
}


def detect_language(text: str) -> str:
    """
    Detect language of input text. Returns ISO 639-1 code.
    Falls back to 'de' (most common Swiss retail language).
    """
    try:
        from langdetect import detect
        lang = detect(text)
        # Map variants to base
        lang_map = {"de": "de", "fr": "fr", "it": "it", "en": "en", "rm": "de"}
        return lang_map.get(lang, lang if lang in SUPPORTED_LANGUAGES else "de")
    except Exception:
        # Simple heuristic fallback
        text_lower = text.lower()
        if any(w in text_lower for w in ["pour", "avec", "livraison", "recherche"]):
            return "fr"
        if any(w in text_lower for w in ["per", "con", "consegna", "cerca"]):
            return "it"
        if any(w in text_lower for w in ["für", "mit", "morgen", "suche", "bio"]):
            return "de"
        return "en"


def get_language_instruction(lang: str) -> str:
    """Return language-specific system prompt suffix."""
    return LANGUAGE_INSTRUCTIONS.get(lang, LANGUAGE_INSTRUCTIONS["en"])


def localise_payload_field(payload: Dict[str, Any], field: str, lang: str) -> str:
    """
    Extract a localised field from a Qdrant payload.

    Tries lang-specific field first (e.g., name_de), then falls back to base field.
    """
    translations = FIELD_TRANSLATIONS.get(lang, FIELD_TRANSLATIONS["en"])
    localised_key = translations.get(field, field)

    # Try localised field first
    if localised_key in payload:
        return str(payload[localised_key])
    # Try base field
    if field in payload:
        return str(payload[field])
    # Try lang-suffixed variant
    suffixed = f"{field}_{lang}"
    if suffixed in payload:
        return str(payload[suffixed])
    return ""


def build_multilingual_system_prompt(
    agent_name: str,
    detected_lang: str,
    base_prompt: Optional[str] = None,
) -> str:
    """
    Build a complete system prompt with language instruction appended.

    Uses Apertus agent prompt as base, adds language-specific suffix.
    """
    from app.llm.apertus_client import AGENT_SYSTEM_PROMPTS

    base = base_prompt or AGENT_SYSTEM_PROMPTS.get(agent_name, AGENT_SYSTEM_PROMPTS["supervisor"])
    lang_instruction = get_language_instruction(detected_lang)
    return f"{base}\n\n{lang_instruction}"


# ---------------------------------------------------------------------------
# Cross-lingual query normalisation
# ---------------------------------------------------------------------------

# Common Swiss retail terms across languages → canonical English
SWISS_TERM_MAP: Dict[str, str] = {
    # German
    "bio-milch": "organic milk",
    "raclette-käse": "raclette cheese",
    "fondue-set": "fondue set",
    "schokolade": "chocolate",
    "brot": "bread",
    "fleisch": "meat",
    "morgen": "tomorrow",
    # French
    "lait bio": "organic milk",
    "fromage": "cheese",
    "chocolat": "chocolate",
    "pain": "bread",
    "viande": "meat",
    "demain": "tomorrow",
    # Italian
    "latte biologico": "organic milk",
    "formaggio": "cheese",
    "cioccolato": "chocolate",
    "pane": "bread",
    "carne": "meat",
    "domani": "tomorrow",
}


def normalise_query(query: str, source_lang: Optional[str] = None) -> str:
    """
    Normalise a multilingual query into canonical terms for Qdrant search.

    This does lightweight keyword-level normalisation; the LLM handles
    complex cross-lingual understanding.
    """
    if source_lang is None:
        source_lang = detect_language(query)

    normalised = query.lower()
    for term, canonical in SWISS_TERM_MAP.items():
        if term in normalised:
            normalised = normalised.replace(term, canonical)

    return normalised


__all__ = [
    "detect_language",
    "get_language_instruction",
    "localise_payload_field",
    "build_multilingual_system_prompt",
    "normalise_query",
    "SUPPORTED_LANGUAGES",
]
