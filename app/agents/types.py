"""Pydantic models for agent inputs/outputs (Goal, Bundle, ProductRef, etc.)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ProductRef(BaseModel):
    """Reference to a product (SKU + optional price)."""

    sku: str = Field(..., min_length=1, max_length=128)
    name: str | None = None
    price_chf: float | None = Field(None, ge=0)
    quantity: int = Field(1, ge=1, le=999)


class ProvenanceEntry(BaseModel):
    """Provenance for one piece of context (RAG)."""

    source: str = Field(..., max_length=256)
    score: float = Field(0.0, ge=0, le=1)
    doc_id: str | None = None


class ShoppingGoal(BaseModel):
    """Structured shopping goal (ShopperAgent output)."""

    goal: str = Field(..., min_length=1, max_length=500)
    budget: str | None = Field(None, pattern=r"^\d+\.?\d{0,2}$")
    color: str | None = None
    delivery_days_max: int | None = Field(None, ge=1, le=365)
    region: str | None = None
    urgency: Literal["low", "medium", "high"] = "medium"

    @field_validator("goal", mode="before")
    @classmethod
    def goal_stripped(cls, v: str) -> str:
        return (v or "").strip() or "general search"


class BundleSolution(BaseModel):
    """Recommended bundle (InventoryAgent/Merchandising output)."""

    products: list[ProductRef] = Field(default_factory=list)
    total_price: float = Field(0.0, ge=0)
    delivery_days: int = Field(0, ge=0, le=365)
    confidence: float = Field(0.0, ge=0, le=1)
    provenance: list[ProvenanceEntry] = Field(default_factory=list)


class AgentContext(BaseModel):
    """Context passed to agents (query + trace_id + optional payload)."""

    query: str = Field(..., min_length=1, max_length=2000)
    trace_id: str = Field(..., min_length=1)
    tenant_id: str | None = None
    payload: dict[str, object] = Field(default_factory=dict)


class HealthStatus(BaseModel):
    """Agent health check result."""

    healthy: bool
    agent_name: str
    message: str = ""
    latency_ms: int = 0


class OrchestrationResult(BaseModel):
    """Result of supervisor orchestration."""

    success: bool
    trace_id: str
    message: str = ""
    metrics: dict[str, object] = Field(default_factory=dict)
