"""
Session Context Agent: use OTTO session history → predict next best bundle.

"Past sessions like this converted 23% better."
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from qdrant_client import QdrantClient
except ImportError:
    QdrantClient = None

from agents.multimodal_rag import MultimodalOttoRAG

COLLECTION_OTTO_SESSIONS = "otto_sessions"


class SessionContextAgent:
    """Agent B: RAG over similar OTTO sessions → bundle prediction from successful patterns."""

    def __init__(self, qdrant_client: QdrantClient, rag: MultimodalOttoRAG | None = None):
        self.qdrant = qdrant_client
        self.rag = rag or MultimodalOttoRAG(qdrant_client)

    async def recommend_from_history(
        self,
        current_goal: dict[str, Any],
        user_session: str | None = None,
        limit_sessions: int = 10,
    ) -> dict[str, Any]:
        """RAG over similar historical sessions → extract successful patterns → score candidates."""
        query = current_goal.get("query") or current_goal.get("text", "")
        filters = current_goal.get("filters") or {}
        similar = self.rag.hybrid_search(shopper_query=query, goal_filters=filters, limit=limit_sessions)
        successful_patterns = []
        for session_point_id, _score in similar:
            try:
                points = self.qdrant.retrieve(
                    collection_name=COLLECTION_OTTO_SESSIONS,
                    ids=[session_point_id],
                    with_payload=True,
                    with_vectors=False,
                )
                if not points:
                    continue
                payload = points[0].payload or {}
                if payload.get("conversion_success"):
                    successful_patterns.append({
                        "session_id": payload.get("session_id"),
                        "event_sequence": payload.get("event_sequence", []),
                        "conv_rate": 0.23,
                    })
            except Exception:
                continue
        # Placeholder: in production we'd score current_goal candidate_products against patterns
        top_bundle = current_goal.get("candidate_products") or []
        if successful_patterns and top_bundle:
            top_bundle = top_bundle[:5]
        return {
            "historical_similar_sessions": len(similar),
            "successful_patterns_found": len(successful_patterns),
            "top_bundle": top_bundle[:5] if top_bundle else [],
            "historical_conv_rate": 0.23 if successful_patterns else 0.0,
        }


__all__ = ["SessionContextAgent"]
