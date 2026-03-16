"""Typed JSON serialization for production payloads."""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel


def to_json(obj: BaseModel | dict[str, Any]) -> str:
    """Serialize Pydantic model or dict to JSON string."""
    if isinstance(obj, BaseModel):
        return obj.model_dump_json()
    return json.dumps(obj, default=str)


def from_json(s: str, model: type[BaseModel]) -> BaseModel:
    """Deserialize JSON string to Pydantic model."""
    return model.model_validate_json(s)


def to_dict(obj: BaseModel) -> dict[str, Any]:
    """Export Pydantic model to dict (no JSON string)."""
    return obj.model_dump()
