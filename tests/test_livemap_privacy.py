from datetime import timedelta

from app.livemap_api import IntentIn, create_intent, delete_user_data, _INTENTS  # type: ignore[attr-defined]
from app.privacy import coarse_location, pseudonymize, default_intent_consent


def test_pseudonymize_is_deterministic_and_not_plain() -> None:
    uid = "user-123"
    h1 = pseudonymize(uid)
    h2 = pseudonymize(uid)
    assert h1 == h2
    assert h1 != uid


def test_coarse_location_rounds_coordinates() -> None:
    lat, lon = 47.378177, 8.540192
    coarse = coarse_location(lat, lon, precision=3)
    assert abs(coarse["lat"] - lat) < 0.0015
    assert abs(coarse["lon"] - lon) < 0.0015


def test_create_intent_uses_pseudonymous_id_and_ttl() -> None:
    payload = IntentIn(
        user_id="user-abc",
        text="haircut near Bahnhof",
        lat=47.378177,
        lon=8.540192,
        radius_m=1500,
        max_walk_minutes=20,
        ttl_minutes=10,
    )
    intent = create_intent(payload)

    assert intent.user_id_hash != payload.user_id
    assert intent.expires_at > intent.created_at
    assert (intent.expires_at - intent.created_at) <= timedelta(minutes=10)
    assert intent.intent_id in _INTENTS


def test_delete_user_data_is_idempotent() -> None:
    # Create two intents for the same user hash
    payload1 = IntentIn(
        user_id="deleteme",
        text="coffee",
        lat=47.0,
        lon=8.0,
        radius_m=1000,
        max_walk_minutes=10,
        ttl_minutes=15,
    )
    payload2 = IntentIn(
        user_id="deleteme",
        text="another coffee",
        lat=47.0,
        lon=8.0,
        radius_m=1000,
        max_walk_minutes=10,
        ttl_minutes=15,
    )
    i1 = create_intent(payload1)
    i2 = create_intent(payload2)

    assert i1.intent_id in _INTENTS
    assert i2.intent_id in _INTENTS

    user_hash = i1.user_id_hash
    resp1 = delete_user_data(user_hash)
    assert resp1["status"] == "ok"
    assert resp1["deleted_intents"] == 2

    # Second call should be safe and delete zero additional intents
    resp2 = delete_user_data(user_hash)
    assert resp2["status"] == "ok"
    assert resp2["deleted_intents"] == 0

