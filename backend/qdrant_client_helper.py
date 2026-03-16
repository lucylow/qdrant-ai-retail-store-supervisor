from qdrant_client import QdrantClient

from app.qdrant_client import get_qdrant_client as _get_qdrant_client


def get_qdrant_client() -> QdrantClient:
    """
    Backwards-compatible helper that now delegates to the centralized app.qdrant_client.

    This ensures all agents (Shopper, Inventory, Promotions, Supervisor) use the same
    cloud-ready, retrying Qdrant client configuration, including QDRANT_URL/QDRANT_API_KEY.
    """

    return _get_qdrant_client()


__all__ = ["get_qdrant_client"]
