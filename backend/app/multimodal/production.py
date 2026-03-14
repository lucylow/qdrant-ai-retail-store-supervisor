"""
Production multimodal pipeline: Qdrant Cloud + HF Inference + Whisper + optional Replicate.

Flow: voice → Whisper → text; text+photo → HF embeddings; semantic cache lookup → multi-vector search → cache store.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from app.config import EXTERNAL_PROVIDERS
from app.multimodal.schema import PRODUCTS_MULTIMODAL_COLLECTION
from app.multimodal.search import (
    RRF_K,
    build_multimodal_filter,
    rrf_fusion,
)
from app.multimodal.semantic_cache import (
    CACHE_TTL_S,
    semantic_cache_lookup,
    semantic_cache_store,
)

logger = logging.getLogger(__name__)


def _production_embeddings(
    text: str,
    image: Optional[bytes] = None,
) -> Dict[str, List[float]]:
    """Get embeddings via HF when configured; else return empty (caller uses local encoders)."""
    if not EXTERNAL_PROVIDERS.hf_token or not text:
        return {}
    from app.providers.huggingface import embed_multimodal_hf
    out = embed_multimodal_hf(text, image)
    result: Dict[str, List[float]] = {}
    if out.get("textvector"):
        result["textvector"] = out["textvector"]
    if out.get("imagevector"):
        result["imagevector"] = out["imagevector"]
    return result


def _production_search(
    client: Any,
    queries: Dict[str, List[float]],
    *,
    stock_status: Optional[str] = "instock",
    limit: int = 5,
) -> List[Tuple[Any, float, Dict[str, Any]]]:
    """Multi-vector search with RRF; returns (id, score, payload)."""
    if not queries:
        return []
    query_filter = build_multimodal_filter(stock_status=stock_status)
    result_lists: List[List[Tuple[Any, float]]] = []
    for name, qvec in queries.items():
        try:
            hits = client.search(
                collection_name=PRODUCTS_MULTIMODAL_COLLECTION,
                query_vector=qvec,
                query_filter=query_filter,
                limit=50,
                with_payload=True,
                vector_name=name,
            )
            list_scores = [(h.id, float(h.score or 0.0)) for h in hits]
        except Exception:
            list_scores = []
        result_lists.append(list_scores)

    fused = rrf_fusion(result_lists, k=RRF_K)[:limit]
    if not fused:
        return []

    ids = [f[0] for f in fused]
    scores_map = {f[0]: f[1] for f in fused}
    try:
        points = client.retrieve(
            collection_name=PRODUCTS_MULTIMODAL_COLLECTION,
            ids=ids,
            with_payload=True,
        )
    except Exception:
        return [(pid, scores_map.get(pid, 0.0), {}) for pid in ids]
    payload_by_id = {p.id: (p.payload or {}) for p in points}
    return [(pid, scores_map.get(pid, 0.0), payload_by_id.get(pid, {})) for pid in ids]


def _inventory_bundle(
    results: List[Tuple[Any, float, Dict[str, Any]]],
    from_cache: bool = False,
    reply_text: Optional[str] = None,
    reply_audio_base64: Optional[str] = None,
) -> Dict[str, Any]:
    """Build response bundle for judge demo / frontend."""
    out: Dict[str, Any] = {
        "from_cache": from_cache,
        "results": [
            {"id": str(r[0]), "score": round(r[1], 4), "payload": r[2]}
            for r in results
        ],
        "count": len(results),
    }
    if reply_text is not None:
        out["reply_text"] = reply_text
    if reply_audio_base64 is not None:
        out["reply_audio_base64"] = reply_audio_base64
    return out


class ProductionMultiAgentStore:
    """
    Production pipeline: voice + photo + text → Whisper → HF embeddings → semantic cache
    → multi-vector search on Qdrant Cloud → optional Replicate video → cache store.
    """

    def __init__(self, client: Any):
        self.client = client

    def process_query(
        self,
        voice_audio: Optional[bytes] = None,
        user_photo: Optional[bytes] = None,
        text_query: Optional[str] = None,
        *,
        use_semantic_cache: bool = True,
        use_agent: bool = True,
        use_tts: bool = True,
        stock_status: Optional[str] = "instock",
        limit: int = 5,
        cache_ttl_s: int = CACHE_TTL_S,
    ) -> Dict[str, Any]:
        """
        Run production multimodal pipeline. Returns bundle with results, from_cache,
        and optionally reply_text + reply_audio_base64 (agent + ElevenLabs).
        """
        # 1. Voice → text (Whisper)
        voice_text = ""
        if voice_audio:
            from app.providers.whisper import transcribe_swiss_german
            voice_text = transcribe_swiss_german(voice_audio)
        combined_text = " ".join(filter(None, [voice_text, text_query or ""])).strip()
        if not combined_text and not user_photo:
            return _inventory_bundle([], from_cache=False)

        # 2. Multimodal embeddings (HF Inference)
        embeddings = _production_embeddings(combined_text or " ", user_photo)
        if not embeddings:
            # Fallback: local encoders if no HF
            from app.multimodal.encoders import MultimodalProductEncoders
            enc = MultimodalProductEncoders()
            if combined_text:
                embeddings["textvector"] = enc.encode_text(combined_text)
            if user_photo:
                iv = enc.encode_image_bytes(user_photo)
                if iv:
                    embeddings["imagevector"] = iv

        if not embeddings:
            return _inventory_bundle([], from_cache=False)

        # 3. Semantic cache lookup (by text vector)
        if use_semantic_cache and embeddings.get("textvector"):
            cache_hit = semantic_cache_lookup(self.client, embeddings["textvector"])
            if cache_hit is not None:
                cache_hit["from_cache"] = True
                return cache_hit  # may already contain reply_text / reply_audio_base64

        # 4. Multi-vector search (Qdrant Cloud)
        results = _production_search(
            self.client,
            embeddings,
            stock_status=stock_status,
            limit=limit,
        )

        # 5. Optional: video demo vectors for top product (Replicate)
        if results and EXTERNAL_PROVIDERS.replicate_api_token:
            top_payload = results[0][2]
            video_path = top_payload.get("video_demo") or top_payload.get("video_path")
            if video_path:
                try:
                    from app.providers.replicate_video import extract_video_vectors_replicate
                    _ = extract_video_vectors_replicate(video_path)
                except Exception:
                    pass

        # 5b. Agent reply (Groq/OpenAI) + optional TTS (ElevenLabs)
        reply_text: Optional[str] = None
        reply_audio_base64: Optional[str] = None
        raw_bundle = _inventory_bundle(results, from_cache=False)
        if use_agent and EXTERNAL_PROVIDERS.agent_provider != "none":
            from app.providers.groq_agent import inventory_agent_reply
            reply_text = inventory_agent_reply(raw_bundle, combined_text)
        if reply_text and use_tts and EXTERNAL_PROVIDERS.elevenlabs_api_key:
            from app.providers.elevenlabs_tts import reply_audio_base64 as tts_b64
            reply_audio_base64 = tts_b64(reply_text)
        bundle = _inventory_bundle(
            results,
            from_cache=False,
            reply_text=reply_text,
            reply_audio_base64=reply_audio_base64,
        )

        # 6. Cache result for next time (include reply so cache hits return voice too)
        if use_semantic_cache and embeddings.get("textvector"):
            semantic_cache_store(
                self.client,
                embeddings["textvector"],
                bundle,
                ttl_s=cache_ttl_s,
            )

        return bundle
