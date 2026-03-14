"""Unit tests for app.core.exceptions."""

from __future__ import annotations

import pytest

from app.core.exceptions import (
    AgentError,
    AgentNotRegisteredError,
    AgentTimeoutError,
    BusinessRuleViolation,
    DataError,
    HallucinationError,
    QdrantConnectionError,
    RepositoryError,
    RetrievalError,
    StoreSupervisorError,
    ValidationError,
)


def test_agent_error_is_store_supervisor_error() -> None:
    assert issubclass(AgentError, StoreSupervisorError)


def test_agent_timeout_is_agent_error() -> None:
    assert issubclass(AgentTimeoutError, AgentError)


def test_retrieval_error_is_base() -> None:
    assert issubclass(RetrievalError, StoreSupervisorError)


def test_hallucination_is_retrieval_error() -> None:
    assert issubclass(HallucinationError, RetrievalError)


def test_qdrant_connection_is_data_error() -> None:
    assert issubclass(QdrantConnectionError, DataError)


def test_validation_error_is_value_error() -> None:
    assert issubclass(ValidationError, ValueError)


def test_business_rule_violation_is_validation_error() -> None:
    assert issubclass(BusinessRuleViolation, ValidationError)


def test_agent_not_registered_message() -> None:
    e = AgentNotRegisteredError("Agent not registered: foo")
    assert e.message == "Agent not registered: foo"
    assert "foo" in str(e)


def test_repository_error_chain() -> None:
    cause = ValueError("inner")
    e = RepositoryError("Product get failed: inner")
    assert "Product" in str(e)
