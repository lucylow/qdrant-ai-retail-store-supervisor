from __future__ import annotations

from dataclasses import dataclass
from math import atan2, cos, radians, sin, sqrt
from typing import Any, Dict, List, Sequence

import numpy as np

from app.embeddings import embed_texts
from app.qdrant_client import get_qdrant_client


@dataclass
class LiveMapCandidate:
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


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return great-circle distance between two WGS84 points in meters."""
    r = 6_371_000.0
    phi1 = radians(lat1)
    phi2 = radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return r * c


def score_live_candidates(
    intent_text: str,
    user_lat: float,
    user_lon: float,
    raw_providers: Sequence[Dict[str, Any]],
    *,
    max_radius_m: float = 1_500.0,
    max_walk_minutes: float = 20.0,
    walking_speed_m_per_min: float = 80.0,
    top_k: int = 10,
    alpha: float = 0.6,
    beta: float = 0.2,
    gamma: float = 0.2,
) -> List[LiveMapCandidate]:
    """Hybrid geo + semantic + provider utility scoring.

    - raw_providers is a list of dicts with at least:
      provider_id, name, lat, lon, rating?, utilization?, capabilities_text?
    - Uses existing sentence-transformers model and Qdrant client.
    """
    if not raw_providers:
        return []

    # 1) Embed intent once
    intent_vec = embed_texts([intent_text])[0]
    intent_norm = intent_vec / (np.linalg.norm(intent_vec) + 1e-8)

    # 2) Fetch provider vectors from Qdrant in a single batched recommend/search call
    client = get_qdrant_client()
    provider_ids = [p["provider_id"] for p in raw_providers]

    # We query widely and then filter by provider_id in Python; later we can
    # tighten this to payload filters when we introduce a dedicated collection.
    hits = client.search(
        collection_name="products",
        query_vector=intent_vec.tolist(),
        limit=min(256, max(len(provider_ids) * 4, 32)),
        with_payload=True,
        with_vectors=True,
    )

    # Map provider_id → vector & semantic score for quick lookup
    id_to_vec: Dict[str, np.ndarray] = {}
    id_to_semantic: Dict[str, float] = {}
    for h in hits:
        pid = (h.payload or {}).get("provider_id")
        if pid is None:
            continue
        vec = np.asarray(h.vector, dtype="float32")  # type: ignore[arg-type]
        vec_norm = vec / (np.linalg.norm(vec) + 1e-8)
        sim = float(np.dot(intent_norm, vec_norm))
        id_to_vec[str(pid)] = vec_norm
        id_to_semantic[str(pid)] = sim

    # 3) Compose candidates with geo + provider utility features
    candidates: List[LiveMapCandidate] = []
    for p in raw_providers:
        pid = str(p["provider_id"])
        plat = float(p["lat"])
        plon = float(p["lon"])

        dist_m = _haversine_m(user_lat, user_lon, plat, plon)
        if dist_m > max_radius_m:
            continue

        eta_min = dist_m / walking_speed_m_per_min
        if eta_min > max_walk_minutes:
            continue

        semantic = id_to_semantic.get(pid, 0.0)
        travel_score = 1.0 - min(dist_m / max_radius_m, 1.0)

        rating = float(p.get("rating", 4.5))
        utilization = float(p.get("utilization", 0.0))
        provider_score = 0.7 * (rating / 5.0) + 0.3 * (1.0 - max(min(utilization, 1.0), 0.0))

        total_score = alpha * semantic + beta * travel_score + gamma * provider_score

        candidates.append(
            LiveMapCandidate(
                provider_id=pid,
                name=str(p.get("name") or ""),
                lat=plat,
                lon=plon,
                rating=rating,
                utilization=utilization,
                distance_m=dist_m,
                eta_minutes=int(round(eta_min)),
                semantic_score=semantic,
                travel_score=travel_score,
                provider_score=provider_score,
                total_score=total_score,
                payload=dict(p),
            )
        )

    candidates.sort(key=lambda c: c.total_score, reverse=True)
    return candidates[:top_k]


__all__ = ["LiveMapCandidate", "score_live_candidates"]

