"""
API for multimodal RAG: video/audio indexing and voice+photo+text search with RRF.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, Form, UploadFile

from app.multimodal.search import multimodal_search_with_payload
from app.qdrant_client import get_qdrant_client

router = APIRouter(prefix="/multimodal", tags=["multimodal"])


@router.post("/search")
async def multimodal_search_endpoint(
    text_query: Optional[str] = Form(None),
    voice_audio: Optional[UploadFile] = File(None),
    user_photo: Optional[UploadFile] = File(None),
    limit: int = 10,
    weight_voice: float = 0.33,
    weight_photo: float = 0.33,
    weight_text: float = 0.34,
) -> Dict[str, Any]:
    """
    Multimodal search: send text_query and/or upload voice (audio) and/or photo.
    Weights for RRF: weight_voice, weight_photo, weight_text (default equal).
    """
    client = get_qdrant_client()
    voice_bytes: Optional[bytes] = None
    photo_bytes: Optional[bytes] = None
    if voice_audio and voice_audio.filename:
        voice_bytes = await voice_audio.read()
    if user_photo and user_photo.filename:
        photo_bytes = await user_photo.read()
    weights = None
    if weight_voice or weight_photo or weight_text:
        weights = {}
        if weight_voice:
            weights["audiovector"] = weight_voice
        if weight_photo:
            weights["imagevector"] = weight_photo
        if weight_text:
            weights["textvector"] = weight_text
    try:
        results = multimodal_search_with_payload(
            client,
            text_query=text_query or None,
            voice_audio=voice_bytes,
            user_photo=photo_bytes,
            limit=limit,
            weights=weights,
        )
    except Exception as e:
        return {"error": str(e), "results": []}
    return {
        "results": [
            {"id": str(r[0]), "score": round(r[1], 4), "payload": r[2]}
            for r in results
        ],
    }
