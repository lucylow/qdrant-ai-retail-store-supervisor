"""Unit tests for app.core.validators."""

from __future__ import annotations

import pytest
from pydantic import ValidationError as PydanticValidationError

from app.core.validators import BudgetConstraint, UrgencyLevel, validate_budget, validate_urgency


def test_validate_budget_positive() -> None:
    assert validate_budget(10.5) == 10.5
    assert validate_budget("99.99") == 99.99


def test_validate_budget_invalid_raises() -> None:
    with pytest.raises((ValueError, PydanticValidationError)):
        validate_budget(-1)
    with pytest.raises((ValueError, PydanticValidationError)):
        validate_budget("10.999")  # too many decimals


def test_validate_urgency() -> None:
    assert validate_urgency("low") == "low"
    assert validate_urgency("high") == "high"


def test_validate_urgency_invalid_raises() -> None:
    with pytest.raises((ValueError, PydanticValidationError)):
        validate_urgency("critical")


def test_budget_constraint_model() -> None:
    b = BudgetConstraint(value=50.0)
    assert b.value == 50.0
