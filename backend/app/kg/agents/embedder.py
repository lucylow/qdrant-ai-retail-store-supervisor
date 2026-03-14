"""KG Embedder Agent: Graph-to-vector pipeline for hybrid KG→Qdrant search."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.kg.embeddings import embed_kg_results, embed_kg_subgraph_summary
from app.kg.neo4j_client import ProductionNeo4jClient, KGQueryResult


class KGEmbedderAgent:
    """
    Embeds KG results and subgraphs for fusion with Qdrant vectors.
    Used by HybridKGQdrantRetriever for reranking.
    """

    def __init__(self) -> None:
        pass

    def embed_kg_results(self, records: List[Dict[str, Any]]) -> List[List[float]]:
        """Embed KG query result records (product/customer context) for similarity."""
        return embed_kg_results(records)

    def embed_subgraph(self, result: KGQueryResult) -> List[float]:
        """Single vector summarizing a subgraph (nodes + relationships)."""
        return embed_kg_subgraph_summary(result.nodes, result.relationships)

    def embed_triples(self, triples: List[Dict[str, Any]]) -> List[List[float]]:
        """Embed (head, rel, tail) triples; delegates to app.kg.embeddings."""
        from app.kg.embeddings import embed_kg_triples
        import numpy as np
        vecs = embed_kg_triples(triples)
        return vecs.tolist() if vecs is not None and len(vecs) else []
