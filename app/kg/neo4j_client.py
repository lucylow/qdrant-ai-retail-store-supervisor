"""Production Neo4j driver with connection pooling and typed results."""

from __future__ import annotations

import asyncio
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import logging

from neo4j import GraphDatabase

from app.config import NEO4J

logger = logging.getLogger(__name__)


@dataclass
class KGQueryResult:
    """Structured result from Cypher execution."""

    nodes: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    paths: List[List[Dict[str, Any]]]
    records: List[Dict[str, Any]]
    summary: Dict[str, int]


class ProductionNeo4jClient:
    """
    Production Neo4j client with connection pooling and async-friendly API.
    Uses sync driver under the hood; async methods run in executor.
    """

    def __init__(
        self,
        uri: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        max_connection_pool_size: Optional[int] = None,
    ) -> None:
        uri = uri or NEO4J.uri
        user = user or NEO4J.user
        password = password or NEO4J.password
        pool_size = max_connection_pool_size or NEO4J.max_connection_pool_size
        self.driver = GraphDatabase.driver(
            uri,
            auth=(user, password),
            max_connection_pool_size=pool_size,
        )
        self._executor: Optional[asyncio.Executor] = None

    @contextmanager
    def session(self):
        """Synchronous session context manager."""
        session = self.driver.session()
        try:
            yield session
        finally:
            session.close()

    def execute_cypher_sync(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> KGQueryResult:
        """Execute Cypher and return parsed nodes, relationships, paths, and records."""
        params = parameters or {}
        nodes: List[Dict[str, Any]] = []
        relationships: List[Dict[str, Any]] = []
        paths: List[List[Dict[str, Any]]] = []
        records: List[Dict[str, Any]] = []

        with self.session() as session:
            result = session.run(query, params)
            for record in result:
                rec_dict = dict(record)
                records.append(rec_dict)
                for key, val in rec_dict.items():
                    if hasattr(val, "nodes") and hasattr(val, "relationships"):
                        # Path object
                        path_rels = []
                        for r in val.relationships:
                            path_rels.append(
                                {
                                    "type": type(r).__name__,
                                    "start_node": r.start_node.id,
                                    "end_node": r.end_node.id,
                                    "properties": dict(r),
                                }
                            )
                        paths.append(path_rels)
                    elif hasattr(val, "labels") and hasattr(val, "id"):
                        nodes.append(
                            {"id": val.id, "labels": list(val.labels), "properties": dict(val)}
                        )
                    elif hasattr(val, "type") and hasattr(val, "start_node"):
                        relationships.append(
                            {
                                "type": val.type,
                                "start_node": val.start_node.id,
                                "end_node": val.end_node.id,
                                "properties": dict(val),
                            }
                        )
                    elif isinstance(val, dict):
                        if "id" in val and "labels" in val:
                            nodes.append(val)
                        elif "type" in val and "start_node" in val:
                            relationships.append(val)

        return KGQueryResult(
            nodes=nodes,
            relationships=relationships,
            paths=paths,
            records=records,
            summary={
                "node_count": len(nodes),
                "relationship_count": len(relationships),
                "path_count": len(paths),
                "record_count": len(records),
            },
        )

    async def execute_cypher(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> KGQueryResult:
        """Async wrapper for Cypher execution (runs in thread pool)."""
        loop = asyncio.get_event_loop()
        if self._executor is None:
            self._executor = asyncio.get_event_loop().default_executor
        return await loop.run_in_executor(
            self._executor,
            self.execute_cypher_sync,
            query,
            parameters,
        )

    def verify_connectivity(self) -> bool:
        """Verify Neo4j connectivity."""
        try:
            self.driver.verify_connectivity()
            return True
        except Exception as exc:  # noqa: BLE001
            logger.warning("Neo4j connectivity check failed: %s", exc)
            return False

    def close(self) -> None:
        """Close the driver."""
        self.driver.close()

    def __enter__(self) -> "ProductionNeo4jClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
