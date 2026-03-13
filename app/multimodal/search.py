"""
Multimodal search: query by voice (audio), photo (image), and/or text; fuse with RRF.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

from app.multimodal.encoders import MultimodalProductEncoders
from app.multimodal.schema import PRODUCTS_MULTIMODAL_COLLECTION

RRF_K = 60


def rrf_fusion(
    result_lists: Sequence[Sequence[Tuple[Any, float]]],
    weights: Optional[Sequence[float]] = None,
    k: int = RRF_K,
) -> List[Tuple[Any, float]]:
    """
    Reciprocal Rank Fusion: score(id) = sum(weight_i / (k + rank_i)).
    result_lists: each list is [(point_id, raw_score), ...] (rank = index+1).
    weights: optional per-list weight (default 1.0 each).
    """
    if not result_lists:
        return []
    weights = weights or [1.0] * len(result_lists)
    if len(weights) != len(result_lists):
        weights = [1.0] * len(result_lists)
    scores: Dict[Any, float] = {}
    for lst, w in zip(result_lists, weights):
        for rank, (pid, _) in enumerate(lst, 1):
            scores[pid] = scores.get(pid, 0.0) + w / (k + rank)
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked


def multimodal_search(
    client: Any,
    *,
    text_query: Optional[str] = None,
    voice_audio: Optional[bytes] = None,
    user_photo: Optional[bytes] = None,
    collection_name: str = PRODUCTS_MULTIMODAL_COLLECTION,
    limit: int = 10,
    weights: Optional[Dict[str, float]] = None,
    encoders: Optional[MultimodalProductEncoders] = None,
) -> List[Tuple[Any, float]]:
    """
    Multimodal search: embed text, voice, and/or photo; search each vector name; RRF fuse.

    weights: e.g. {"audiovector": 0.6, "imagevector": 0.3, "textvector": 0.1} for visual shopping.
    Default: equal weight for each provided modality.
    """
    encoders = encoders or MultimodalProductEncoders()
    # Build query vectors per modality
    queries: Dict[str, List[float]] = {}
    if text_query:
        queries["textvector"] = encoders.encode_text(text_query)
    if voice_audio:
        queries["audiovector"] = encoders.encode_audio(audio_bytes=voice_audio)
    if user_photo:
        vec = encoders.encode_image_bytes(user_photo)
        if vec is not None:
            queries["imagevector"] = vec

    if not queries:
        return []

    weight_list = []
    result_lists: List[List[Tuple[Any, float]]] = []
    default_w = 1.0 / len(queries) if queries else 1.0
    for name, qvec in queries.items():
        try:
            hits = client.search(
                collection_name=collection_name,
                query_vector=qvec,
                query_filter=None,
                limit=50,
                with_payload=True,
                vector_name=name,
            )
        except Exception:
            hits = []
        # (point_id, score) for RRF
        list_scores = [(h.id, float(h.score or 0.0)) for h in hits]
        result_lists.append(list_scores)
        weight_list.append((weights or {}).get(name, default_w))

    fused = rrf_fusion(result_lists, weights=weight_list)
    return fused[:limit]


def multimodal_search_with_payload(
    client: Any,
    *,
    text_query: Optional[str] = None,
    voice_audio: Optional[bytes] = None,
    user_photo: Optional[bytes] = None,
    collection_name: str = PRODUCTS_MULTIMODAL_COLLECTION,
    limit: int = 10,
    weights: Optional[Dict[str, float]] = None,
) -> List[Tuple[Any, float, Dict[str, Any]]]:
    """Like multimodal_search but returns (id, score, payload) by re-fetching or from first hit."""
    fused = multimodal_search(
        client,
        text_query=text_query,
        voice_audio=voice_audio,
        user_photo=user_photo,
        collection_name=collection_name,
        limit=limit,
        weights=weights,
    )
    if not fused:
        return []
    ids = [f[0] for f in fused]
    scores_map = {f[0]: f[1] for f in fused}
    try:
        points = client.retrieve(collection_name=collection_name, ids=ids, with_payload=True)
    except Exception:
        return [(pid, scores_map.get(pid, 0.0), {}) for pid in ids]
    payload_by_id = {p.id: (p.payload or {}) for p in points}
    return [(pid, scores_map.get(pid, 0.0), payload_by_id.get(pid, {})) for pid in ids]
