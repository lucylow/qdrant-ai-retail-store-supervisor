from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from langdetect import detect
from qdrant_client.http import models as rest
from sentence_transformers import SentenceTransformer

from app.qdrant_client import ensure_collection, get_qdrant_client

logger = logging.getLogger(__name__)


_EMBEDDER: SentenceTransformer = SentenceTransformer("BAAI/bge-m3")
_VECTOR_DIM: int = _EMBEDDER.get_sentence_embedding_dimension()


@dataclass
class MultilingualQueryResult:
    detected_language: str
    query_original: str
    episodes: List[Dict[str, Any]]
    structured_goal: Dict[str, Any]
    solution: Dict[str, Any]
    confidence: float


class MultilingualShopperAgent:
    """
    Multilingual shopper agent for Swiss retail (DE/FR/IT/EN).

    - Detects language (incl. Swiss German → de)
    - Uses BGE-M3 embeddings for cross-lingual semantic search
    - Searches tenant-specific Qdrant episode collections
    - Returns a simple structured goal + bundle-style solution
    """

    def __init__(self) -> None:
        self._client = get_qdrant_client()

    def _detect_swiss_language(self, text: str) -> str:
        try:
            lang = detect(text)
        except Exception:  # noqa: BLE001
            return "de"
        if lang == "gsw":
            return "de"
        if lang not in ("de", "fr", "it", "en"):
            return "de"
        return lang

    def _embed(self, text: str) -> List[float]:
        vec = _EMBEDDER.encode([text], convert_to_numpy=True, show_progress_bar=False)[0]
        return vec.astype("float32").tolist()

    def _ensure_tenant_collection(self, tenant: str) -> str:
        """
        Ensure a tenant-specific multilingual episodes collection exists.
        """
        collection = f"{tenant}_episodes_multilingual"
        try:
            ensure_collection(
                self._client,
                name=collection,
                vector_size=_VECTOR_DIM,
                distance=rest.Distance.COSINE,
            )
        except Exception:  # noqa: BLE001
            logger.warning("Could not ensure collection %s", collection, exc_info=True)
        return collection

    def _search_episodes(self, query_vec: List[float], tenant: str) -> List[Dict[str, Any]]:
        collection = self._ensure_tenant_collection(tenant)
        try:
            hits = self._client.search(
                collection_name=collection,
                query_vector=query_vec,
                limit=5,
                with_payload=True,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Qdrant search failed for %s: %s", collection, exc)
            return []
        return [
            {
                "id": str(h.id),
                "score": float(h.score or 0.0),
                "payload": h.payload or {},
            }
            for h in hits
        ]

    def _parse_goal(self, query: str, lang: str, region_hint: Optional[str]) -> Dict[str, Any]:
        """
        Very lightweight structured goal for demo purposes.
        """
        region = region_hint or None
        text_l = query.lower()
        if any(city in text_l for city in ("zürich", "zurich", "zh")):
            region = "ZH"
        elif any(city in text_l for city in ("genf", "geneva", "ge")):
            region = "GE"
        elif any(city in text_l for city in ("basel", "bs")):
            region = "BS"

        return {
            "text": query,
            "lang": lang,
            "region": region,
            "budget_chf": None,
            "urgency": "normal",
        }

    def _build_solution(self, episodes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build a simple bundle-style solution from top episode payload (if any).
        Falls back to a generic placeholder bundle.
        """
        if not episodes:
            return {
                "products": [],
                "total_chf": 0.0,
                "pickup_location": "online",
            }

        top = episodes[0]
        payload = top.get("payload") or {}
        products = payload.get("products") or payload.get("bundle_products") or []
        price = payload.get("price") or payload.get("total_chf") or payload.get("price_chf") or 0.0
        location = payload.get("pickup_location") or payload.get("location") or "online"

        try:
            price_f = float(price)
        except Exception:  # noqa: BLE001
            price_f = 0.0

        if isinstance(products, str):
            products_list: List[str] = [products]
        else:
            products_list = list(products) if products else []

        return {
            "products": products_list,
            "total_chf": price_f,
            "pickup_location": str(location),
        }

    async def process_query(self, query: str, tenant: str = "coop", region: Optional[str] = None) -> MultilingualQueryResult:
        lang = self._detect_swiss_language(query)
        query_vec = self._embed(query)
        episodes = self._search_episodes(query_vec, tenant)
        structured_goal = self._parse_goal(query, lang, region)
        solution = self._build_solution(episodes)
        confidence = float(episodes[0]["score"]) if episodes else 0.0

        return MultilingualQueryResult(
            detected_language=lang,
            query_original=query,
            episodes=episodes,
            structured_goal=structured_goal,
            solution=solution,
            confidence=confidence,
        )


__all__ = ["MultilingualShopperAgent", "MultilingualQueryResult"]

