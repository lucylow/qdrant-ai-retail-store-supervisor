from __future__ import annotations

import asyncio

from app.agents.supervisor import SupervisorAgent
from app.generation.multimodal import MultimodalProductGenerator
from app.promo.autonomous import AutonomousPromoPlanner, Opportunity
from app.promo.segmentation import Customer
from app.rag.self_improving import SelfImprovingRAG


def test_supervisor_orchestrate_runs() -> None:
    supervisor = SupervisorAgent()
    result = asyncio.run(supervisor.orchestrate("Blue dress €80 Berlin <3 days"))
    assert result.graph.goal_id
    assert result.audit is not None


def test_self_improving_cycle() -> None:
    rag = SelfImprovingRAG()
    rag.daily_improvement_cycle()


def test_multimodal_generator() -> None:
    gen = MultimodalProductGenerator()
    url = gen.generate_bundle_mockup([])
    assert "mock://image" in url


def test_autonomous_promo_planner() -> None:
    planner = AutonomousPromoPlanner()
    customers = [
        Customer(
            customer_id="c1",
            monetary=250.0,
            frequency=5,
            recency_days=10,
            features={},
        )
    ]
    opp = Opportunity(
        sku="SKU-BASE",
        store="Berlin-Store",
        customers=customers,
        event="Spring launch",
    )
    campaign = asyncio.run(planner.plan_campaign(opp))
    assert campaign.selected_variant in campaign.variants

