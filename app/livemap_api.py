from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.livemap_matching import LiveMapCandidate, score_live_candidates
from app.privacy import (
    coarse_location,
    default_intent_consent,
    pseudonymize,
)
from app.ethics.privacy import gdpr_delete_user_data  # Qdrant deletion helper
from app.qdrant_client import get_qdrant_client


router = APIRouter(prefix="/livemap", tags=["LiveMap"])


class IntentIn(BaseModel):
    user_id: str
    text: str = Field(..., description="Free-text intent, e.g. 'haircut 16:00 near Bahnhof'")
    lat: float
    lon: float
    radius_m: int = Field(1500, ge=50, le=10_000)
    max_walk_minutes: int = Field(20, ge=1, le=60)
    ttl_minutes: int = Field(15, ge=1, le=60)
    exact_share: bool = Field(
        False,
        description="If true, user has consented to share exact coordinates after booking.",
    )


class IntentOut(BaseModel):
    intent_id: str
    user_id_hash: str
    text: str
    lat: float
    lon: float
    radius_m: int
    max_walk_minutes: int
    created_at: datetime
    expires_at: datetime
    consent: Dict[str, Any]


class ProviderStub(BaseModel):
    provider_id: str
    name: str
    lat: float
    lon: float
    rating: float = 4.5
    utilization: float = 0.0
    capabilities_text: Optional[str] = None
    raw: Dict[str, Any] = Field(default_factory=dict)


class CandidateOut(BaseModel):
    provider_id: str
    name: str
    lat: float
    lon: float
    rating: float
    utilization: float
    distance_m: float
    eta_minutes: int
    semantic_score: float
    travel_score: float
    provider_score: float
    total_score: float
    payload: Dict[str, Any]


class CandidatesResponse(BaseModel):
    intent: IntentOut
    candidates: List[CandidateOut]


class BidIn(BaseModel):
    provider_id: str
    price_cents: int = Field(..., ge=0)
    eta_minutes: int = Field(15, ge=1, le=120)
    notes: Optional[str] = None


class BidOut(BaseModel):
    bid_id: str
    intent_id: str
    provider_id: str
    price_cents: int
    eta_minutes: int
    notes: Optional[str]
    created_at: datetime


class ChooseIn(BaseModel):
    bid_id: str


_INTENTS: Dict[str, IntentOut] = {}
_BIDS: Dict[str, List[Dict[str, Any]]] = {}  # intent_id -> list of bid dicts
_CHOSEN: Dict[str, str] = {}  # intent_id -> bid_id


def _cleanup_intents() -> None:
    now = datetime.utcnow()
    expired = [iid for iid, it in _INTENTS.items() if now >= it.expires_at]
    for iid in expired:
        _INTENTS.pop(iid, None)
        _BIDS.pop(iid, None)
        _CHOSEN.pop(iid, None)


def _demo_providers_near(lat: float, lon: float) -> List[Dict[str, Any]]:
    """MVP: static providers around a point.

    This keeps the API demoable without introducing a new DB dependency.
    Later this should query Postgres / PostGIS or an existing product catalog.
    """
    base = [
        {
            "provider_id": "p_barber_1",
            "name": "Bahnhof Barber",
            "lat": lat + 0.001,
            "lon": lon + 0.001,
            "rating": 4.8,
            "utilization": 0.3,
            "capabilities_text": "Quick 20 minute haircuts near train station.",
        },
        {
            "provider_id": "p_massage_1",
            "name": "Zen Massage",
            "lat": lat - 0.0015,
            "lon": lon - 0.0005,
            "rating": 4.7,
            "utilization": 0.6,
            "capabilities_text": "30 minute back and neck massage, walk-ins welcome.",
        },
        {
            "provider_id": "p_repair_1",
            "name": "Express Phone Repair",
            "lat": lat + 0.0008,
            "lon": lon - 0.0012,
            "rating": 4.4,
            "utilization": 0.2,
            "capabilities_text": "Same-day phone screen repair and battery swaps.",
        },
    ]
    return base


@router.post("/intent", response_model=IntentOut)
def create_intent(payload: IntentIn) -> IntentOut:
    """
    Create an ephemeral LiveMap intent with privacy-by-design defaults:

    - user_id is pseudonymized before storage
    - only coarse location is stored and used for matching
    - each intent has an explicit TTL (expires_at)
    - a consent block is attached to the intent record
    """
    intent_id = f"i_{uuid.uuid4().hex[:8]}"
    user_hash = pseudonymize(payload.user_id)
    ttl = timedelta(minutes=payload.ttl_minutes)
    coarse = coarse_location(payload.lat, payload.lon, precision=3)
    created = datetime.utcnow()
    expires_at = created + ttl
    consent = default_intent_consent(user_hash, ttl)

    intent = IntentOut(
        intent_id=intent_id,
        user_id_hash=user_hash,
        text=payload.text,
        lat=coarse["lat"],
        lon=coarse["lon"],
        radius_m=payload.radius_m,
        max_walk_minutes=payload.max_walk_minutes,
        created_at=created,
        expires_at=expires_at,
        consent=consent,
    )
    _cleanup_intents()
    _INTENTS[intent_id] = intent
    return intent


@router.get("/intent/{intent_id}/candidates", response_model=CandidatesResponse)
def get_candidates(intent_id: str, top_k: int = 10) -> CandidatesResponse:
    _cleanup_intents()
    intent = _INTENTS.get(intent_id)
    if not intent:
        raise HTTPException(status_code=404, detail="intent not found or expired")

    # Step 1: geo pre-filter (here: static demo providers)
    raw_providers = _demo_providers_near(intent.lat, intent.lon)

    # Step 2: hybrid scoring using Qdrant + embeddings
    scored: List[LiveMapCandidate] = score_live_candidates(
        intent_text=intent.text,
        user_lat=float(intent.lat),
        user_lon=float(intent.lon),
        raw_providers=raw_providers,
        max_radius_m=float(intent.radius_m),
        max_walk_minutes=float(intent.max_walk_minutes),
        top_k=top_k,
    )

    out_candidates: List[CandidateOut] = []
    for c in scored:
        out_candidates.append(
            CandidateOut(
                provider_id=c.provider_id,
                name=c.name,
                lat=c.lat,
                lon=c.lon,
                rating=c.rating,
                utilization=c.utilization,
                distance_m=c.distance_m,
                eta_minutes=c.eta_minutes,
                semantic_score=c.semantic_score,
                travel_score=c.travel_score,
                provider_score=c.provider_score,
                total_score=c.total_score,
                payload=c.payload,
            )
        )

    return CandidatesResponse(intent=intent, candidates=out_candidates)


@router.get("/intent/{intent_id}", response_model=IntentOut)
def get_intent(intent_id: str) -> IntentOut:
    _cleanup_intents()
    intent = _INTENTS.get(intent_id)
    if not intent:
        raise HTTPException(status_code=404, detail="intent not found or expired")
    return intent


@router.post("/intent/{intent_id}/bid", response_model=BidOut)
def submit_bid(intent_id: str, payload: BidIn) -> BidOut:
    """Provider submits a bid for an intent. Broadcast to user via WebSocket in production."""
    _cleanup_intents()
    intent = _INTENTS.get(intent_id)
    if not intent:
        raise HTTPException(status_code=404, detail="intent not found or expired")
    bid_id = f"b_{uuid.uuid4().hex[:8]}"
    created = datetime.utcnow()
    bid = {
        "bid_id": bid_id,
        "intent_id": intent_id,
        "provider_id": payload.provider_id,
        "price_cents": payload.price_cents,
        "eta_minutes": payload.eta_minutes,
        "notes": payload.notes,
        "created_at": created,
    }
    _BIDS.setdefault(intent_id, []).append(bid)
    return BidOut(
        bid_id=bid_id,
        intent_id=intent_id,
        provider_id=payload.provider_id,
        price_cents=payload.price_cents,
        eta_minutes=payload.eta_minutes,
        notes=payload.notes,
        created_at=created,
    )


@router.post("/intent/{intent_id}/choose")
def choose_bid(intent_id: str, payload: ChooseIn) -> Dict[str, Any]:
    """User selects a bid; booking is confirmed. Exact location can be shared after this."""
    _cleanup_intents()
    intent = _INTENTS.get(intent_id)
    if not intent:
        raise HTTPException(status_code=404, detail="intent not found or expired")
    bids = _BIDS.get(intent_id, [])
    if not any(b["bid_id"] == payload.bid_id for b in bids):
        raise HTTPException(status_code=404, detail="bid not found")
    _CHOSEN[intent_id] = payload.bid_id
    return {"ok": True, "intent_id": intent_id, "bid_id": payload.bid_id}


@router.get("/intent/{intent_id}/bids")
def get_bids(intent_id: str) -> Dict[str, Any]:
    """List bids for an intent (e.g. for user's offers panel)."""
    _cleanup_intents()
    intent = _INTENTS.get(intent_id)
    if not intent:
        raise HTTPException(status_code=404, detail="intent not found or expired")
    bids = _BIDS.get(intent_id, [])
    chosen = _CHOSEN.get(intent_id)
    return {"intent_id": intent_id, "bids": bids, "chosen_bid_id": chosen}


@router.post("/user/{user_id_hash}/delete")
def delete_user_data(user_id_hash: str) -> Dict[str, Any]:
    """
    GDPR-style deletion for LiveMap:

    - remove any in-memory intents for this pseudonymous user
    - attempt to delete any Qdrant points keyed by the same hash
    """
    # Purge in-memory intents
    to_delete = [iid for iid, it in _INTENTS.items() if it.user_id_hash == user_id_hash]
    for iid in to_delete:
        _INTENTS.pop(iid, None)

    # Best-effort Qdrant deletion; if there is no dedicated LiveMap collection
    # yet this will simply return an empty summary or errors list.
    client = get_qdrant_client()
    qdrant_summary = gdpr_delete_user_data(client, user_id_hash)

    return {
        "status": "ok",
        "deleted_intents": len(to_delete),
        "qdrant": qdrant_summary,
    }


__all__ = ["router"]

