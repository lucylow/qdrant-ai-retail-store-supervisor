"""
RAG components for the learning Agentic Retail AI system.

This package intentionally stays lightweight and framework-agnostic so it can be
plugged into both the existing app flows and new RL-driven experiments.
"""

from .context_selector import ContextSelector  # noqa: F401
from .retrieval_optimizer import RetrievalOptimizer  # noqa: F401
from .agentic_rag_pipeline import AgenticRAG  # noqa: F401

