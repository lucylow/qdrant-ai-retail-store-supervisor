from __future__ import annotations

"""
LiveMap privacy helpers: pseudonymization, encryption, and consent logging.

This module is intentionally self-contained so it can be reused by
FastAPI routers without introducing a database dependency. For the
hackathon prototype we keep state in-memory; production deployments
should persist consent and audit logs in a durable store.
"""

import hmac
import hashlib
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Sequence

from cryptography.fernet import Fernet, InvalidToken


_PSEUDO_SECRET = os.getenv("PSEUDO_SECRET", "change_me")
_ENCRYPTION_KEY = os.getenv("LIVEMAP_ENC_KEY")


def _get_fernet() -> Optional[Fernet]:
    """Return a Fernet instance if an encryption key is configured."""
    if not _ENCRYPTION_KEY:
        return None
    try:
        return Fernet(_ENCRYPTION_KEY.encode("utf-8"))
    except Exception:
        # Misconfigured key – fail closed and treat as no encryption.
        return None


def pseudonymize(user_id: str) -> str:
    """
    HMAC-SHA256 pseudonymization for user identifiers.

    Same input + secret yields the same pseudonym, but it is not
    reversible without the secret. Use this hash in logs, Qdrant
    payloads and LiveMap intents instead of raw user IDs.
    """
    return hmac.new(
        _PSEUDO_SECRET.encode("utf-8"),
        user_id.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def encrypt_coords(lat: float, lon: float) -> Optional[bytes]:
    """
    Encrypt exact coordinates as an opaque blob.

    If no encryption key is configured, returns None so callers can
    gracefully skip storing exact coordinates rather than storing
    them in plaintext.
    """
    f = _get_fernet()
    if not f:
        return None
    payload = f"{lat:.8f},{lon:.8f}".encode("utf-8")
    return f.encrypt(payload)


def decrypt_coords(blob: bytes) -> Optional[Dict[str, float]]:
    """Decrypt an encrypted coordinate blob back into lat/lon."""
    f = _get_fernet()
    if not f:
        return None
    try:
        decoded = f.decrypt(blob).decode("utf-8")
        lat_str, lon_str = decoded.split(",", 1)
        return {"lat": float(lat_str), "lon": float(lon_str)}
    except (InvalidToken, ValueError):
        return None


def coarse_location(lat: float, lon: float, *, precision: int = 3) -> Dict[str, float]:
    """
    Return a coarse version of a coordinate pair suitable for matching
    and visualization without revealing exact position.

    For the MVP we approximate a geohash by rounding to a configurable
    number of decimal places.
    """
    factor = 10**precision
    return {
        "lat": round(lat * factor) / factor,
        "lon": round(lon * factor) / factor,
    }


@dataclass
class Consent:
    """Lightweight consent record attached to an intent."""

    user_id_hash: str
    purpose: str
    granted_at: datetime
    ttl_minutes: int
    scope: Sequence[str]
    source: str = "livemap"


_CONSENT_LOG: List[Dict[str, Any]] = []


def record_consent(consent: Consent) -> Dict[str, Any]:
    """
    Store a consent record in-memory and return a serializable dict.

    Production deployments should replace this with durable storage
    (e.g. Postgres or a consent management platform) and append-only
    audit logging.
    """
    data = asdict(consent)
    data["granted_at"] = consent.granted_at.isoformat()
    _CONSENT_LOG.append(data)
    return data


def list_consent_for_user(user_id_hash: str) -> List[Dict[str, Any]]:
    """Return all recorded consents for a pseudonymous user id."""
    return [c for c in _CONSENT_LOG if c.get("user_id_hash") == user_id_hash]


def default_intent_consent(user_id_hash: str, ttl: timedelta) -> Dict[str, Any]:
    """
    Construct a default consent payload for broadcasting an intent.

    This mirrors the JSON example from the LiveMap privacy design.
    """
    minutes = int(ttl.total_seconds() // 60) or 1
    consent = Consent(
        user_id_hash=user_id_hash,
        purpose="broadcast_intent_matching",
        granted_at=datetime.utcnow(),
        ttl_minutes=minutes,
        scope=("match", "push_to_providers"),
    )
    return record_consent(consent)


__all__ = [
    "pseudonymize",
    "encrypt_coords",
    "decrypt_coords",
    "coarse_location",
    "record_consent",
    "list_consent_for_user",
    "default_intent_consent",
]

