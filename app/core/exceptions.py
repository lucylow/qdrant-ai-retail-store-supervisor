"""Custom exception hierarchy for production error handling (20+ types)."""

from __future__ import annotations


class StoreSupervisorError(Exception):
    """Base exception for multi-agent store supervisor."""

    def __init__(self, message: str, *args: object, **kwargs: object) -> None:
        super().__init__(message, *args)
        self.message = message


# --- Agent layer ---


class AgentError(StoreSupervisorError):
    """Base for all agent-related failures."""


class AgentTimeoutError(AgentError):
    """Agent execution exceeded allowed timeout."""


class AgentHealthError(AgentError):
    """Agent health check failed."""


class AgentNotRegisteredError(AgentError):
    """Requested agent name not found in registry."""


# --- Retrieval / RAG ---


class RetrievalError(StoreSupervisorError):
    """Base for retrieval failures."""


class HallucinationError(RetrievalError):
    """Provenance/hallucination check failed."""


class EmbeddingError(RetrievalError):
    """Embedding generation failed."""


class RerankError(RetrievalError):
    """Reranking step failed."""


# --- Data layer ---


class DataError(StoreSupervisorError):
    """Base for data access failures."""


class QdrantConnectionError(DataError):
    """Qdrant client connection or health check failed."""


class QdrantWriteError(DataError):
    """Qdrant write (upsert/update/delete) failed."""


class QdrantQueryError(DataError):
    """Qdrant query (search/scroll) failed."""


class RepositoryError(DataError):
    """Repository CRUD or transaction failed."""


# --- Validation ---


class ValidationError(ValueError, StoreSupervisorError):
    """Input or output validation failed (Pydantic/business rule)."""


class BusinessRuleViolation(ValidationError):
    """Business rule constraint violated (e.g. budget, stock)."""


# --- Configuration / infra ---


class ConfigurationError(StoreSupervisorError):
    """Invalid or missing configuration."""


class CacheError(StoreSupervisorError):
    """Cache get/set failed (e.g. Redis)."""


# --- Generation ---


class GenerationError(StoreSupervisorError):
    """LLM or generator call failed."""


class GuardrailViolationError(StoreSupervisorError):
    """Guardrail check rejected input or output."""
