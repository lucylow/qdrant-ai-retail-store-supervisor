from __future__ import annotations

"""
LangChain-style Context RAG pipeline for the Multi-Agent Store Manager.

Implements four RAG architectures that map onto the Qdrant blackboard:
  1. Naive RAG      — linear retrieve → generate
  2. Agentic RAG    — LLM agent decides when/how to retrieve
  3. Hybrid RAG     — query rewriting + retrieval validation
  4. GraphRAG       — knowledge-graph-augmented retrieval

Each architecture exposes Shopper and Inventory as callable *tools*
so the coordinator can dynamically dispatch.
"""

import hashlib
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

class RAGMode(str, Enum):
    NAIVE = "naive"
    AGENTIC = "agentic"
    HYBRID = "hybrid"
    GRAPH = "graph"


@dataclass
class Document:
    """Lightweight stand-in for LangChain Document."""
    page_content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    score: float = 0.0


@dataclass
class ToolResult:
    tool_name: str
    output: str
    latency_ms: float = 0.0


@dataclass
class RAGTrace:
    """Full audit trail for a single RAG invocation."""
    mode: str = ""
    query: str = ""
    rewritten_query: str = ""
    retrieved_docs: int = 0
    validated_docs: int = 0
    tools_called: List[str] = field(default_factory=list)
    steps: List[str] = field(default_factory=list)
    latency_ms: float = 0.0
    confidence: float = 0.0


@dataclass
class RAGResult:
    answer: str
    docs: List[Document]
    trace: RAGTrace


# ---------------------------------------------------------------------------
# Tool registry (mirrors LangChain Tool pattern)
# ---------------------------------------------------------------------------

@dataclass
class AgentTool:
    """Mirrors langchain.tools.Tool — name, func, description."""
    name: str
    func: Callable[..., str]
    description: str

    def run(self, *args: Any, **kwargs: Any) -> ToolResult:
        t0 = time.perf_counter()
        output = self.func(*args, **kwargs)
        return ToolResult(
            tool_name=self.name,
            output=output,
            latency_ms=(time.perf_counter() - t0) * 1000,
        )


# ---------------------------------------------------------------------------
# Built-in agent tools (Shopper + Inventory)
# ---------------------------------------------------------------------------

def _shopper_parse(user_message: str) -> str:
    """Parse free-text into a structured goal (mock LLM parse)."""
    goal = {
        "goal_text": user_message,
        "budget": None,
        "delivery_days": None,
        "region": "EU",
        "status": "open",
    }
    # Extract simple budget hints
    import re
    for cur in ("chf", "€", "\\$", "eur"):
        m = re.search(r"(\d+)\s*" + cur, user_message.lower())
        if m:
            goal["budget"] = int(m.group(1))
    return f"Parsed goal: {goal}"


def _inventory_solve(goal_text: str) -> str:
    """Solve a goal by matching products (mock)."""
    candidates = [
        {"name": "MSR Hubba Hubba NX 2", "price": 189, "stock": 4},
        {"name": "Sea to Summit Sleeping Bag", "price": 89, "stock": 12},
        {"name": "JetBoil Flash Stove", "price": 49, "stock": 8},
    ]
    return f"Inventory found {len(candidates)} candidates: {[c['name'] for c in candidates]}"


SHOPPER_TOOL = AgentTool(
    name="ShopperParseAndWrite",
    func=_shopper_parse,
    description="Parses shopper text into a structured goal and writes it to the goals collection.",
)

INVENTORY_TOOL = AgentTool(
    name="InventorySolve",
    func=_inventory_solve,
    description="Retrieve products matching a goal and propose a bundle solution.",
)

DEFAULT_TOOLS = [SHOPPER_TOOL, INVENTORY_TOOL]


# ---------------------------------------------------------------------------
# Retriever (mock — in production, wraps QdrantVectorStore.as_retriever)
# ---------------------------------------------------------------------------

class MockRetriever:
    """Simulates LangChain retriever backed by Qdrant."""

    def __init__(self, search_type: str = "mmr", k: int = 5) -> None:
        self.search_type = search_type
        self.k = k

    def get_relevant_documents(self, query: str) -> List[Document]:
        """Return mock docs with deterministic scores."""
        import random as _rng
        seed = int(hashlib.md5(query.encode()).hexdigest(), 16) % (2**32)
        r = _rng.Random(seed)
        n = min(self.k, r.randint(2, self.k))
        return [
            Document(
                page_content=f"Product doc #{i+1} for '{query[:40]}'",
                metadata={"source": f"products/doc_{i}", "collection": "products"},
                score=round(r.uniform(0.6, 0.98), 3),
            )
            for i in range(n)
        ]


# ---------------------------------------------------------------------------
# LangChain Context RAG — four modes
# ---------------------------------------------------------------------------

class LangChainContextRAG:
    """
    Unified RAG pipeline supporting Naive, Agentic, Hybrid, and Graph modes.

    In production:
      - Replace MockRetriever with QdrantVectorStore.as_retriever()
      - Replace _generate() with LLM chain call
      - Replace agent loop with LangGraph state machine
    """

    def __init__(
        self,
        retriever: Optional[MockRetriever] = None,
        tools: Optional[List[AgentTool]] = None,
        default_mode: RAGMode = RAGMode.AGENTIC,
    ) -> None:
        self.retriever = retriever or MockRetriever()
        self.tools = {t.name: t for t in (tools or DEFAULT_TOOLS)}
        self.default_mode = default_mode

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def query(
        self, question: str, mode: Optional[RAGMode] = None
    ) -> RAGResult:
        m = mode or self.default_mode
        dispatch = {
            RAGMode.NAIVE: self._naive_rag,
            RAGMode.AGENTIC: self._agentic_rag,
            RAGMode.HYBRID: self._hybrid_rag,
            RAGMode.GRAPH: self._graph_rag,
        }
        return dispatch[m](question)

    # ------------------------------------------------------------------
    # 1) Naive RAG
    # ------------------------------------------------------------------

    def _naive_rag(self, question: str) -> RAGResult:
        t0 = time.perf_counter()
        trace = RAGTrace(mode="naive", query=question)

        docs = self.retriever.get_relevant_documents(question)
        trace.retrieved_docs = len(docs)
        trace.steps.append(f"retrieve: {len(docs)} docs")

        context = self._docs_to_context(docs)
        answer = self._generate(context, question)
        trace.steps.append("generate")

        trace.latency_ms = (time.perf_counter() - t0) * 1000
        trace.confidence = self._avg_score(docs)
        return RAGResult(answer=answer, docs=docs, trace=trace)

    # ------------------------------------------------------------------
    # 2) Agentic RAG
    # ------------------------------------------------------------------

    def _agentic_rag(self, question: str) -> RAGResult:
        t0 = time.perf_counter()
        trace = RAGTrace(mode="agentic", query=question)

        # Step 1 — Shopper parses goal
        shopper = self.tools.get("ShopperParseAndWrite")
        if shopper:
            res = shopper.run(question)
            trace.tools_called.append(res.tool_name)
            trace.steps.append(f"tool:{res.tool_name} ({res.latency_ms:.0f}ms)")

        # Step 2 — Retrieve context
        docs = self.retriever.get_relevant_documents(question)
        trace.retrieved_docs = len(docs)
        trace.steps.append(f"retrieve: {len(docs)} docs (MMR)")

        # Step 3 — Inventory solves
        inventory = self.tools.get("InventorySolve")
        if inventory:
            res = inventory.run(question)
            trace.tools_called.append(res.tool_name)
            trace.steps.append(f"tool:{res.tool_name} ({res.latency_ms:.0f}ms)")

        # Step 4 — Confidence check → possibly re-retrieve
        avg = self._avg_score(docs)
        if avg < 0.7 and len(docs) > 0:
            trace.steps.append("low_confidence → re-retrieve with expanded query")
            expanded = question + " product recommendation alternative"
            extra = self.retriever.get_relevant_documents(expanded)
            docs = self._deduplicate(docs + extra)
            trace.retrieved_docs = len(docs)

        # Step 5 — Generate
        context = self._docs_to_context(docs)
        answer = self._generate(context, question)
        trace.steps.append("generate")

        trace.latency_ms = (time.perf_counter() - t0) * 1000
        trace.confidence = self._avg_score(docs)
        return RAGResult(answer=answer, docs=docs, trace=trace)

    # ------------------------------------------------------------------
    # 3) Hybrid RAG
    # ------------------------------------------------------------------

    def _hybrid_rag(self, question: str) -> RAGResult:
        t0 = time.perf_counter()
        trace = RAGTrace(mode="hybrid", query=question)

        # Query rewriting
        rewritten = self._rewrite_query(question)
        trace.rewritten_query = rewritten
        trace.steps.append(f"rewrite: '{question[:40]}' → '{rewritten[:40]}'")

        # Retrieve
        docs = self.retriever.get_relevant_documents(rewritten)
        trace.retrieved_docs = len(docs)
        trace.steps.append(f"retrieve: {len(docs)} docs")

        # Validate relevance
        validated = [d for d in docs if d.score > 0.65]
        trace.validated_docs = len(validated)
        trace.steps.append(f"validate: kept {len(validated)}/{len(docs)}")

        context = self._docs_to_context(validated or docs[:2])
        answer = self._generate(context, question)
        trace.steps.append("generate")

        trace.latency_ms = (time.perf_counter() - t0) * 1000
        trace.confidence = self._avg_score(validated or docs)
        return RAGResult(answer=answer, docs=validated or docs, trace=trace)

    # ------------------------------------------------------------------
    # 4) GraphRAG
    # ------------------------------------------------------------------

    def _graph_rag(self, question: str) -> RAGResult:
        t0 = time.perf_counter()
        trace = RAGTrace(mode="graph", query=question)

        # Vector retrieval
        docs = self.retriever.get_relevant_documents(question)
        trace.retrieved_docs = len(docs)
        trace.steps.append(f"vector_retrieve: {len(docs)} docs")

        # Simulate knowledge graph traversal
        graph_entities = self._extract_entities(question)
        trace.steps.append(f"graph_entities: {graph_entities}")

        graph_docs = [
            Document(
                page_content=f"Graph relation: {e} → related products",
                metadata={"source": "knowledge_graph", "entity": e},
                score=0.88,
            )
            for e in graph_entities
        ]
        all_docs = self._deduplicate(docs + graph_docs)
        trace.steps.append(f"graph_merge: {len(all_docs)} total docs")

        context = self._docs_to_context(all_docs)
        answer = self._generate(context, question)
        trace.steps.append("generate")

        trace.latency_ms = (time.perf_counter() - t0) * 1000
        trace.confidence = self._avg_score(all_docs)
        return RAGResult(answer=answer, docs=all_docs, trace=trace)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _docs_to_context(docs: List[Document], max_chars: int = 4000) -> str:
        pieces, total = [], 0
        for d in docs:
            if total + len(d.page_content) > max_chars:
                break
            pieces.append(d.page_content)
            total += len(d.page_content)
        return "\n".join(pieces)

    @staticmethod
    def _generate(context: str, question: str) -> str:
        """In production, call LLM chain. Mock for now."""
        if not context.strip():
            return "I need more information to answer that."
        return (
            f"Based on {len(context.split())} words of context for your query:\n\n"
            f"{context[:800]}"
        )

    @staticmethod
    def _rewrite_query(query: str) -> str:
        return query + " retail product recommendation high quality"

    @staticmethod
    def _extract_entities(query: str) -> List[str]:
        tokens = query.lower().split()
        stopwords = {"a", "an", "the", "for", "in", "under", "i", "need", "want"}
        return [t for t in tokens if t not in stopwords and len(t) > 2][:5]

    @staticmethod
    def _avg_score(docs: List[Document]) -> float:
        scores = [d.score for d in docs if d.score > 0]
        return sum(scores) / len(scores) if scores else 0.0

    @staticmethod
    def _deduplicate(docs: List[Document]) -> List[Document]:
        seen: set[str] = set()
        out: List[Document] = []
        for d in docs:
            key = d.page_content[:80]
            if key not in seen:
                seen.add(key)
                out.append(d)
        return out
