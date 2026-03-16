from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import asdict, dataclass
from typing import List, Sequence

import numpy as np
from qdrant_client.http import models as rest

from app.agents.supervisor import AgentNode
from app.data.collections import COLL_REASONING_GRAPHS
from app.qdrant_client import get_qdrant_client


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class GraphEdge:
    source_idx: int
    target_idx: int
    label: str


@dataclass(slots=True)
class ReasoningGraph:
    goal_id: str
    nodes: List[AgentNode]
    edges: List[GraphEdge]
    success_prob: float
    latency_ms: int

    def to_json(self) -> str:
        return json.dumps(asdict(self), separators=(",", ":"), sort_keys=True)


class ReasoningGraphStore:
    """
    Qdrant-backed storage for agent reasoning graphs.
    """

    def __init__(self, vector_size: int = 384) -> None:
        self._vector_size = vector_size

    async def store_graph(self, graph: ReasoningGraph) -> None:
        # AUTONOMOUS-AGENT-HACKATHON: reasoning graph persistence for reuse.
        client = get_qdrant_client()
        payload = asdict(graph)
        embedding = self._embed_json(graph.to_json())
        points = [
            rest.PointStruct(
                id=graph.goal_id,
                vector=embedding.tolist(),
                payload=payload,
            )
        ]
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            client.upsert,
            COLL_REASONING_GRAPHS,
            points,
        )
        logger.info(
            "Stored reasoning graph",
            extra={
                "event": "reasoning_graphs.store",
                "goal_id": graph.goal_id,
                "success_prob": graph.success_prob,
                "latency_ms": graph.latency_ms,
            },
        )

    async def retrieve_similar_graphs(
        self,
        query_embedding: np.ndarray,
        k: int = 5,
    ) -> List[ReasoningGraph]:
        client = get_qdrant_client()
        loop = asyncio.get_running_loop()
        res = await loop.run_in_executor(
            None,
            client.search,
            COLL_REASONING_GRAPHS,
            query_embedding.tolist(),
            k,
            None,
        )
        graphs: List[ReasoningGraph] = []
        for point in res:
            payload = point.payload or {}
            try:
                graphs.append(self._from_payload(payload))
            except KeyError:
                logger.debug("Skipping malformed reasoning graph payload")
        return graphs

    def _embed_json(self, text: str) -> np.ndarray:
        # Tiny deterministic hash-based embedding to avoid external deps.
        vec = np.zeros(self._vector_size, dtype=np.float32)
        for i, ch in enumerate(text.encode("utf-8")):
            vec[i % self._vector_size] += float(ch)
        norm = float(np.linalg.norm(vec)) or 1.0
        return vec / norm

    def _from_payload(self, payload: dict) -> ReasoningGraph:
        nodes: List[AgentNode] = [
            AgentNode(
                name=n["name"],
                step=n["step"],
                input_summary=n["input_summary"],
                output_summary=n["output_summary"],
                latency_ms=int(n["latency_ms"]),
            )
            for n in payload["nodes"]
        ]
        edges: List[GraphEdge] = [
            GraphEdge(
                source_idx=int(e["source_idx"]),
                target_idx=int(e["target_idx"]),
                label=str(e["label"]),
            )
            for e in payload.get("edges", [])
        ]
        return ReasoningGraph(
            goal_id=str(payload["goal_id"]),
            nodes=nodes,
            edges=edges,
            success_prob=float(payload["success_prob"]),
            latency_ms=int(payload["latency_ms"]),
        )


__all__: Sequence[str] = ["ReasoningGraphStore", "ReasoningGraph", "GraphEdge"]

