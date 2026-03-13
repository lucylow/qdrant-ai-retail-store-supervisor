"""
Qdrant collections and payload indexes for the four memory types.

- user_profiles: long-term user preferences & lifetime stats (embedded summary).
- goal_solution_links: episodic memory (goal → solution → outcome), semantic search.
- procedural_memory: discovered routing/bundle patterns and triggers.

Vector dim: use same as app embedding model (e.g. 768 for all-mpnet-base-v2). Cosine distance.
"""

from __future__ import annotations

import logging
from typing import Final, Sequence

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

from app.qdrant_client import ensure_collection, get_qdrant_client

logger = logging.getLogger(__name__)

COLL_USER_PROFILES: Final[str] = "user_profiles"
COLL_GOAL_SOLUTION_LINKS: Final[str] = "goal_solution_links"
COLL_PROCEDURAL_MEMORY: Final[str] = "procedural_memory"


def _memory_vector_size() -> int:
    """Infer vector size from app embedding model (e.g. 768 for all-mpnet-base-v2)."""
    from app.embeddings import embed_single
    r = embed_single("_probe_")
    return int(r.vectors.shape[-1])


def _safe_payload_index(
    client: QdrantClient,
    collection_name: str,
    field_name: str,
    field_schema: rest.PayloadSchemaType,
) -> None:
    try:
        client.create_payload_index(
            collection_name=collection_name,
            field_name=field_name,
            field_schema=field_schema,
        )
        logger.debug("Created payload index %s.%s", collection_name, field_name)
    except Exception as e:  # noqa: BLE001
        logger.debug("Payload index %s.%s already exists or unsupported: %s", collection_name, field_name, e)


def ensure_memory_collections(vector_size: int | None = None) -> None:
    """
    Idempotently create user_profiles, goal_solution_links, procedural_memory
    and their payload indexes. Run once at bootstrap.
    """
    client = get_qdrant_client()
    dim = vector_size if vector_size is not None else _memory_vector_size()

    for name in (COLL_USER_PROFILES, COLL_GOAL_SOLUTION_LINKS, COLL_PROCEDURAL_MEMORY):
        ensure_collection(client, name, vector_size=dim, distance=rest.Distance.COSINE)

    # user_profiles
    _safe_payload_index(client, COLL_USER_PROFILES, "userId", rest.PayloadSchemaType.KEYWORD)
    _safe_payload_index(client, COLL_USER_PROFILES, "last_updated", rest.PayloadSchemaType.DATETIME)

    # goal_solution_links (episodic)
    _safe_payload_index(client, COLL_GOAL_SOLUTION_LINKS, "goal_id", rest.PayloadSchemaType.KEYWORD)
    _safe_payload_index(client, COLL_GOAL_SOLUTION_LINKS, "outcome", rest.PayloadSchemaType.KEYWORD)
    _safe_payload_index(client, COLL_GOAL_SOLUTION_LINKS, "score", rest.PayloadSchemaType.FLOAT)
    _safe_payload_index(client, COLL_GOAL_SOLUTION_LINKS, "user_id", rest.PayloadSchemaType.KEYWORD)
    _safe_payload_index(client, COLL_GOAL_SOLUTION_LINKS, "created_at", rest.PayloadSchemaType.DATETIME)

    # procedural_memory
    _safe_payload_index(client, COLL_PROCEDURAL_MEMORY, "patternId", rest.PayloadSchemaType.KEYWORD)
    _safe_payload_index(client, COLL_PROCEDURAL_MEMORY, "successRate", rest.PayloadSchemaType.FLOAT)
    _safe_payload_index(client, COLL_PROCEDURAL_MEMORY, "created_at", rest.PayloadSchemaType.DATETIME)

    logger.info("Memory collections and indexes ensured (vector_size=%s)", dim)


__all__: Sequence[str] = [
    "COLL_USER_PROFILES",
    "COLL_GOAL_SOLUTION_LINKS",
    "COLL_PROCEDURAL_MEMORY",
    "ensure_memory_collections",
]
