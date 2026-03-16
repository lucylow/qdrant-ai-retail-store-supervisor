"""Business rule validators (delegate to core validators)."""

from __future__ import annotations

from app.core.validators import validate_budget as _validate_budget
from app.core.validators import validate_urgency as _validate_urgency


def validate_budget(budget: float | str) -> float:
    """Validate budget is positive and at most 2 decimals (CHF)."""
    return _validate_budget(budget)


def validate_urgency(urgency: str) -> str:
    """Validate urgency is one of low, medium, high."""
    return _validate_urgency(urgency)
