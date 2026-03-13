"""
Privacy-first memory: anonymized user IDs and GDPR-compliant deletion.

- Episodic memory uses hashed_user_id in payloads (no plain user_id in Qdrant).
- No cross-session inference without explicit consent (application policy).
- GDPR-compliant deletion: delete all points for a user by hashed_user_id.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any, Dict, List, Optional, Sequence, Tuple

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from qdrant_client.models import Filter, FieldCondition, MatchValue

from app.config import COLLECTIONS
from app.data.memory_collections import COLL_USER_PROFILES, COLL_GOAL_SOLUTION_LINKS

logger = logging.getLogger(__name__)

# Collections that store user identity (payload key may be user_id or userId)
_USER_COLLECTIONS: List[Tuple[str, str]] = [
    (COLLECTIONS.goals, "user_id"),
    (COLLECTIONS.solutions, "user_id"),
    (COLLECTIONS.episodes, "user_id"),
    (COLL_USER_PROFILES, "userId"),
    (COLL_GOAL_SOLUTION_LINKS, "userId"),
]


def hash_user_id(user_id: str, *, salt: Optional[str] = None) -> str:
    """
    One-way hash for privacy-first memory. Same user_id always yields same hash.
    Use a fixed app-level salt (e.g. from env) to avoid rainbow tables; optional.
    """
    data = f"{salt or ''}{user_id}".encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def gdpr_delete_user_data(
    client: QdrantClient,
    user_id_hash: str,
    *,
    collection_keys: Optional[Sequence[Tuple[str, str]]] = None,
) -> Dict[str, Any]:
    """
    GDPR-compliant deletion: delete all points whose user identifier equals user_id_hash.
    Use the hashed user id (from hash_user_id) so that only the data for that user is removed.

    Returns a summary with keys: deleted_collections, errors.
    """
    collections = collection_keys or _USER_COLLECTIONS
    deleted: List[str] = []
    errors: List[Dict[str, Any]] = []

    for collection_name, payload_key in collections:
        try:
            client.delete(
                collection_name=collection_name,
                points_selector=rest.FilterSelector(
                    filter=Filter(
                        must=[FieldCondition(key=payload_key, match=MatchValue(value=user_id_hash))]
                    )
                ),
            )
            deleted.append(collection_name)
            logger.info("GDPR delete: removed points for user_id_hash from %s", collection_name)
        except Exception as e:
            errors.append({"collection": collection_name, "error": str(e)})
            logger.warning("GDPR delete failed for %s: %s", collection_name, e)

    return {"deleted_collections": deleted, "errors": errors}
