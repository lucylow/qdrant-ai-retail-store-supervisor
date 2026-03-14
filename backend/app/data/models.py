"""Domain models for products, orders, customers (Pydantic v2)."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Product(BaseModel):
    """Product entity (catalog)."""

    id: str = Field(..., min_length=1, max_length=128)
    sku: str = Field(..., min_length=1, max_length=128)
    name: str = Field("", max_length=512)
    price_chf: float = Field(0.0, ge=0)
    stock: int = Field(0, ge=0)
    region: str | None = None
    category: str | None = None
    updated_at: datetime | None = None


class Order(BaseModel):
    """Order entity."""

    id: str = Field(..., min_length=1)
    customer_id: str = Field("", max_length=128)
    items: list[dict[str, object]] = Field(default_factory=list)
    total_chf: float = Field(0.0, ge=0)
    status: Literal["pending", "confirmed", "shipped", "delivered"] = "pending"
    created_at: datetime | None = None


class Customer(BaseModel):
    """Customer entity (pseudo-identifier for GDPR)."""

    id: str = Field(..., min_length=1, max_length=128)
    region: str | None = None
    language: Literal["de", "fr", "it", "en"] = "de"
    created_at: datetime | None = None


class GoalRecord(BaseModel):
    """Stored goal in Qdrant (goals collection)."""

    id: str = Field(..., min_length=1)
    query: str = Field("", max_length=2000)
    intent: str | None = None
    budget_chf: float | None = Field(None, ge=0)
    tenant_id: str | None = None


class EpisodeRecord(BaseModel):
    """Stored episode (episodic memory)."""

    id: str = Field(..., min_length=1)
    goal_id: str = Field("", max_length=128)
    outcome: Literal["success", "failure"] = "success"
    skus: list[str] = Field(default_factory=list)
    tenant_id: str | None = None
