import pytest

from app.agents.inventory_agent import InventoryAgent
from app.agents.merch_agent import MerchAgent
from app.agents.image_agent import ImageAgent
from app.agents.audit_agent import AuditAgent


def test_inventory_agent_skips_without_goal():
    a = InventoryAgent()
    out = a.run({})
    assert out["status"] == "skipped" or out.get("result", {}).get("plans") is None


def test_merch_agent_requires_product():
    a = MerchAgent()
    out = a.run({})
    assert out["status"] in ("skipped", "failed")


def test_image_agent_builds_prompt():
    a = ImageAgent()
    ctx = {"product_payload": {"title": "Test product", "sku": "SKU1"}}
    out = a.run(ctx)
    assert out["status"] == "ok"
    result = out.get("result", out)
    assert "image_prompt" in result


def test_audit_agent_no_solutions():
    a = AuditAgent()
    out = a.run({})
    assert out["status"] == "skipped"

