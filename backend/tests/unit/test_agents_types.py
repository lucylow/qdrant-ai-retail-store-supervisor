"""Unit tests for app.agents.types (Pydantic models)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.agents.types import (
    AgentContext,
    BundleSolution,
    HealthStatus,
    ProductRef,
    ShoppingGoal,
)


def test_shopping_goal_minimal() -> None:
    g = ShoppingGoal(goal="find tent")
    assert g.goal == "find tent"
    assert g.urgency == "medium"


def test_shopping_goal_stripped() -> None:
    g = ShoppingGoal(goal="  find tent  ")
    assert g.goal == "find tent"


def test_product_ref_required_sku() -> None:
    p = ProductRef(sku="SKU-1")
    assert p.quantity == 1


def test_bundle_solution_defaults() -> None:
    b = BundleSolution()
    assert b.products == []
    assert b.total_price == 0.0
    assert b.confidence == 0.0


def test_agent_context_requires_query_and_trace_id() -> None:
    with pytest.raises(ValidationError):
        AgentContext(query="", trace_id="t1")
    ctx = AgentContext(query="q", trace_id="t1")
    assert ctx.payload == {}


def test_health_status() -> None:
    h = HealthStatus(healthy=True, agent_name="shopper")
    assert h.latency_ms == 0
