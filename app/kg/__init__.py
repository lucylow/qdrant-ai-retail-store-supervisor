"""Knowledge Graph core: Neo4j + retail ontology + hybrid retrieval."""

from app.kg.neo4j_client import ProductionNeo4jClient, KGQueryResult

__all__ = [
    "ProductionNeo4jClient",
    "KGQueryResult",
]
