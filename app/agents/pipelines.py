from typing import Dict, Any, List, Optional

from app.agents.base import Context, AgentResult
from app.agents.supervisor import Supervisor
from app.agents.inventory_agent import InventoryAgent
from app.agents.merch_agent import MerchAgent
from app.agents.analytics_agent import AnalyticsAgent
from app.agents.audit_agent import AuditAgent
from app.agents.image_agent import ImageAgent


def build_retail_supervisor(max_workers: int = 4) -> Supervisor:
    """
    Construct a Supervisor wired with the core retail agents.
    Execution order (sequential with some parallel groups):
      - InventoryAgent, MerchAgent, ImageAgent (parallel-capable)
      - AuditAgent
      - AnalyticsAgent
    """
    agents = [
        InventoryAgent,
        MerchAgent,
        ImageAgent,
        AuditAgent,
        AnalyticsAgent,
    ]
    return Supervisor(agents=agents, max_workers=max_workers)


def run_retail_pipeline(
    goal: Dict[str, Any],
    user: Optional[Dict[str, Any]] = None,
    extra_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Convenience helper to run the default retail pipeline end-to-end.
    Returns a dict with both the final shared context and per-agent results.
    """
    context: Context = Context()
    context["goal"] = goal
    context["user"] = user or {}
    if extra_context:
        context.update(extra_context)

    supervisor = build_retail_supervisor()
    # Run inventory/merch/image in parallel, then audit + analytics sequentially.
    results: List[AgentResult] = supervisor.run_pipeline(
        context,
        parallel_bucket=["InventoryAgent", "MerchAgent", "ImageAgent"],
    )
    return {"context": context, "results": results}

