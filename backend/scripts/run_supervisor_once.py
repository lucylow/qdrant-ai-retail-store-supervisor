#!/usr/bin/env python3
"""
Run the Supervisor pipeline once for demonstration.
"""

import logging

from app.agents.supervisor import Supervisor
from app.agents.inventory_agent import InventoryAgent
from app.agents.merch_agent import MerchAgent
from app.agents.audit_agent import AuditAgent
from app.agents.analytics_agent import AnalyticsAgent
from app.agents.message_bus import publish, list_events

logging.basicConfig(level=logging.INFO)


if __name__ == "__main__":
    pipeline = [InventoryAgent, MerchAgent, AuditAgent, AnalyticsAgent]
    sup = Supervisor(pipeline, max_workers=3, dry_run=False)

    from app.agents.memory import get_memory

    mem = get_memory()
    try:
        goal_point = mem.get_point("goals", "goal_demo_1")
        goal_payload = goal_point["payload"] if goal_point else {"goal_text": "demo"}
    except Exception:
        goal_payload = {"goal_text": "demo"}
    context = {"goal": goal_payload}
    results = sup.run_pipeline(context, parallelizable=["MerchAgent", "AnalyticsAgent"])
    for r in results:
        print(r)
        publish(r.get("agent", "unknown"), "agent_result", r)
    print("Recent events:", list_events(10))

