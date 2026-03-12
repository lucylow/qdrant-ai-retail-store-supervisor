
rom typing import Dict, List

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

from app.qdrant_client import get_qdrant_client


class RetailVectorMemory:
    """
    Lightweight wrapper around Qdrant + SentenceTransformers for retail use cases.
    """

    def __init__(self) -> None:
        # Reuse existing Qdrant configuration/health-check helper
        self.client: QdrantClient = get_qdrant_client()

        # Small, fast, widely-available embedding model
        self.embedding_model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

    def embed(self, text: str) -> List[float]:
        return self.embedding_model.encode(text).tolist()

    def store(self, collection: str, doc: Dict) -> None:
        """
        Doc is expected to contain at least:
        - id: unique identifier
        - text: content to embed
        Other keys are stored in payload as-is.
        """
        vector = self.embed(doc["text"])

        self.client.upsert(
            collection_name=collection,
            points=[
                {
                    "id": doc["id"],
                    "vector": vector,
                    "payload": doc,
                }
            ],
        )

    def search(self, collection: str, query: str, limit: int = 5):
        """
        Basic vector search. Returns Qdrant scored points.
        """
        vector = self.embed(query)

        results = self.client.search(
            collection_name=collection,
            query_vector=vector,
            limit=limit,
        )

        return results

