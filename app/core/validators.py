"""Pydantic v2 models and business rule validators for input validation."""

from __future__ import annotations

import re
from typing import Annotated

from pydantic import BaseModel, Field, field_validator


class BudgetConstraint(BaseModel):
    """Budget in CHF with optional decimal."""

    value: Annotated[float, Field(gt=0, le=1_000_000)]

    @field_validator("value", mode="before")
    @classmethod
    def parse_decimal(cls, v: str | float) -> float:
        if isinstance(v, (int, float)):
            return float(v)
        s = str(v).strip()
        if not re.match(r"^\d+\.?\d{0,2}$", s):
            raise ValueError("Budget must be positive number, max 2 decimals")
        return float(s)


class UrgencyLevel(BaseModel):
    """Urgency: low, medium, high."""

    level: Annotated[str, Field(pattern=r"^(low|medium|high)$")]


def validate_budget(budget: float | str) -> float:
    """Validate budget is positive and at most 2 decimals (CHF)."""
    return BudgetConstraint(value=float(budget)).value


def validate_urgency(urgency: str) -> str:
    """Validate urgency is one of low, medium, high."""
    return UrgencyLevel(level=urgency).level
