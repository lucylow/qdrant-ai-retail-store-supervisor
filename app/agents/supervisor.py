from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from app.agents.base import Agent, AgentResult, ParallelAgentExecutor
from app.agents.inventory_agent import InventoryAgent
from app.agents.merch_agent import MerchAgent
from app.agents.tool_builder import ToolBuilderAgent


@dataclass
class SupervisorTrace:
    query: str
    steps: list[dict[str, Any]]


class SupervisorAgent(Agent):
    name = "supervisor"

    def __init__(self) -> None:
        self._inventory = InventoryAgent()
        self._merch = MerchAgent()
        self._tools = ToolBuilderAgent()
        self._pool = ParallelAgentExecutor(max_workers=4)

    def run(self, query: str, context: Mapping[str, Any] | None = None) -> Mapping[str, Any]:
        """
        Very small orchestrator:
        - run inventory in parallel with an optional dynamic tool
        - then feed inventory result into merch.
        """
        trace: list[dict[str, Any]] = []
        ctx = context or {}

        inv_future = self._pool.submit(self._inventory, query, ctx)

        tool_body = ctx.get("tool_body")
        tool_future = None
        if isinstance(tool_body, str):
            tool_future = self._pool.submit(
                self._tools,
                query,
                {"tool_body": tool_body, "payload": ctx.get("tool_payload") or {}},
            )

        inventory_res = inv_future.result()
        trace.append({"agent": inventory_res.name, "ok": inventory_res.ok, "data": inventory_res.data})

        inventory_ctx = {"inventory": inventory_res.data}
        merch_res = self._pool.submit(self._merch, query, inventory_ctx).result()
        trace.append({"agent": merch_res.name, "ok": merch_res.ok, "data": merch_res.data})

        tool_data: dict[str, Any] | None = None
        if tool_future is not None:
            t_res = tool_future.result()
            trace.append({"agent": t_res.name, "ok": t_res.ok, "data": t_res.data})
            tool_data = t_res.data

        return {
            "query": query,
            "inventory": inventory_res.data,
            "merch": merch_res.data,
            "tool": tool_data,
            "trace": trace,
        }


__all__ = ["SupervisorAgent", "SupervisorTrace"]

from __future__ import annotations

import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Dict, List, Literal, Mapping, Sequence
from uuid import uuid4

from app.agents.audit import AuditAgent, AuditResult
from app.agents.inventory import InventoryAgent, InventoryPlan
from app.agents.merchandising import MerchandisingAgent, MerchandisingPlan
from app.agents.pricing import PricingAgent, PricingPlan
from app.agents.shopper import ShopperAgent, ShopperGoal
from app.data.episodic_memory import EpisodeOutcome, EpisodicMemoryStore
from app.metrics import compute_conversion_rate, compute_episode_reuse_rate
from app.rag.reasoning_graphs import GraphEdge, ReasoningGraph, ReasoningGraphStore


logger = logging.getLogger(__name__)


AgentName = Literal[
    "shopper",
    "inventory",
    "pricing",
    "merchandising",
    "audit",
]


@dataclass(slots=True)
class AgentNode:
    name: AgentName
    step: str
    input_summary: str
    output_summary: str
    latency_ms: int


@dataclass(slots=True)
class AutonomousResult:
    graph: ReasoningGraph
    success: bool
    message: str
    bundle: InventoryPlan | None = None
    pricing: PricingPlan | None = None
    merchandising: MerchandisingPlan | None = None
    audit: AuditResult | None = None
    metrics: Mapping[str, float] = field(default_factory=dict)


class SupervisorAgent:
    """
    Core orchestrator for the autonomous retail agents.

    Coordinates all 6 specialized agents in parallel / serial phases and
    persists a reasoning graph for reuse.
    """

    def __init__(
        self,
        shopper: ShopperAgent | None = None,
        inventory: InventoryAgent | None = None,
        pricing: PricingAgent | None = None,
        merchandising: MerchandisingAgent | None = None,
        audit: AuditAgent | None = None,
        graph_store: ReasoningGraphStore | None = None,
        episodic_store: EpisodicMemoryStore | None = None,
        max_workers: int = 4,
    ) -> None:
        self.shopper = shopper or ShopperAgent()
        self.inventory = inventory or InventoryAgent()
        self.pricing = pricing or PricingAgent()
        self.merchandising = merchandising or MerchandisingAgent()
        self.audit = audit or AuditAgent()
        self.graph_store = graph_store or ReasoningGraphStore()
        self.episodic_store = episodic_store or EpisodicMemoryStore()
        self._pool = ThreadPoolExecutor(max_workers=max_workers)

    async def orchestrate(self, user_query: str) -> AutonomousResult:
        """
        Full end-to-end orchestration of the autonomous store pipeline.

        # AUTONOMOUS-AGENT-HACKATHON: main judge demo entrypoint.
        """
        start_ts = time.perf_counter()
        goal_id = str(uuid4())

        nodes: List[AgentNode] = []
        edges: List[GraphEdge] = []

        # 1. PARALLEL PHASE 1: Parse + Inventory search + competitor scan
        phase1_start = time.perf_counter()
        loop = asyncio.get_running_loop()

        shopper_future = loop.run_in_executor(
            self._pool, self.shopper.parse_goal, user_query, goal_id
        )
        inventory_future = loop.run_in_executor(
            self._pool, self.inventory.initial_search, user_query
        )
        pricing_future = loop.run_in_executor(
            self._pool, self.pricing.fetch_competitor_context, user_query
        )

        shopper_goal, inventory_ctx, competitor_ctx = await asyncio.gather(
            shopper_future, inventory_future, pricing_future
        )
        phase1_latency = int((time.perf_counter() - phase1_start) * 1000)
        logger.info(
            "Supervisor phase1 completed in %sms",
            phase1_latency,
            extra={
                "event": "supervisor.phase1",
                "latency_ms": phase1_latency,
                "goal_id": goal_id,
            },
        )

        nodes.append(
            AgentNode(
                name="shopper",
                step="parse_goal",
                input_summary=user_query[:120],
                output_summary=shopper_goal.summary(),
                latency_ms=shopper_goal.latency_ms,
            )
        )
        nodes.append(
            AgentNode(
                name="inventory",
                step="initial_search",
                input_summary=user_query[:120],
                output_summary=str(len(inventory_ctx.candidates)),
                latency_ms=inventory_ctx.latency_ms,
            )
        )
        nodes.append(
            AgentNode(
                name="pricing",
                step="fetch_competitor_context",
                input_summary=user_query[:120],
                output_summary=str(len(competitor_ctx.competitors)),
                latency_ms=competitor_ctx.latency_ms,
            )
        )

        # 2. PARALLEL PHASE 2: Bundle + Price + Audit
        phase2_start = time.perf_counter()
        bundle_future = loop.run_in_executor(
            self._pool,
            self.inventory.optimize_bundle,
            shopper_goal,
            inventory_ctx,
        )
        pricing_future2 = loop.run_in_executor(
            self._pool,
            self.pricing.optimize_pricing,
            shopper_goal,
            competitor_ctx,
        )

        bundle, pricing_plan = await asyncio.gather(bundle_future, pricing_future2)
        audit_result = await self.audit.evaluate_plan(
            goal=shopper_goal,
            inventory_plan=bundle,
            pricing_plan=pricing_plan,
        )

        phase2_latency = int((time.perf_counter() - phase2_start) * 1000)
        logger.info(
            "Supervisor phase2 completed in %sms",
            phase2_latency,
            extra={
                "event": "supervisor.phase2",
                "latency_ms": phase2_latency,
                "goal_id": goal_id,
                "hallucination_score": audit_result.hallucination_score,
            },
        )

        nodes.append(
            AgentNode(
                name="inventory",
                step="optimize_bundle",
                input_summary=str(len(inventory_ctx.candidates)),
                output_summary=str(len(bundle.items)),
                latency_ms=bundle.latency_ms,
            )
        )
        nodes.append(
            AgentNode(
                name="pricing",
                step="optimize_pricing",
                input_summary=str(len(competitor_ctx.competitors)),
                output_summary=str(len(pricing_plan.prices)),
                latency_ms=pricing_plan.latency_ms,
            )
        )
        nodes.append(
            AgentNode(
                name="audit",
                step="evaluate_plan",
                input_summary="bundle+pricing",
                output_summary=str(audit_result.hallucination_score),
                latency_ms=audit_result.latency_ms,
            )
        )

        # 3. SERIAL: Merchandising + Final validation
        merch_start = time.perf_counter()
        merchandising_plan = await self.merchandising.build_merchandising_plan(
            shopper_goal, bundle, pricing_plan
        )
        merch_latency = int((time.perf_counter() - merch_start) * 1000)
        nodes.append(
            AgentNode(
                name="merchandising",
                step="build_merchandising_plan",
                input_summary="bundle+pricing",
                output_summary=merchandising_plan.primary_promo_text[:80],
                latency_ms=merch_latency,
            )
        )

        if audit_result.hallucination_score > 0.2:
            outcome = EpisodeOutcome.FAILURE
            success = False
            message = "Plan blocked by safety guardrails (hallucination_score > 0.2)."
        else:
            outcome = EpisodeOutcome.SUCCESS
            success = True
            message = "Plan approved and ready for deployment."

        total_latency = int((time.perf_counter() - start_ts) * 1000)

        # 4. Store reasoning graph + episodic outcome to Qdrant
        graph = ReasoningGraph(
            goal_id=goal_id,
            nodes=nodes,
            edges=edges,
            success_prob=audit_result.success_prob,
            latency_ms=total_latency,
        )
        # AUTONOMOUS-AGENT-HACKATHON: reasoning graph persistence for live viz.
        await self.graph_store.store_graph(graph)
        await self.episodic_store.record_episode(
            goal_id=goal_id,
            graph=graph,
            bundle=bundle,
            pricing=pricing_plan,
            merchandising=merchandising_plan,
            outcome=outcome,
        )

        metrics: Dict[str, float] = {
            "episode_reuse_rate": compute_episode_reuse_rate(),
            "conversion_rate": compute_conversion_rate(),
        }

        logger.info(
            "Supervisor orchestrate finished",
            extra={
                "event": "supervisor.orchestrate",
                "goal_id": goal_id,
                "success": success,
                "latency_ms": total_latency,
                "hallucination_score": audit_result.hallucination_score,
                "episode_reuse_rate": metrics["episode_reuse_rate"],
                "conversion_rate": metrics["conversion_rate"],
            },
        )

        return AutonomousResult(
            graph=graph,
            success=success,
            message=message,
            bundle=bundle,
            pricing=pricing_plan,
            merchandising=merchandising_plan,
            audit=audit_result,
            metrics=metrics,
        )


__all__: Sequence[str] = ["SupervisorAgent", "AutonomousResult", "AgentNode"]

from typing import List, Dict, Any, Callable, Optional
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.agents.base import Agent, AgentResult, Context
from app.agents.message_bus import publish
from app.agents.observability import incr_metric, time_metric

logger = logging.getLogger(__name__)


class Supervisor:
    def __init__(
        self,
        agents: List[Callable[..., Agent]],
        max_workers: int = 4,
        dry_run: bool = False,
    ):
        self.agent_classes = agents
        self.max_workers = max_workers
        self.dry_run = dry_run

    def run_pipeline(
        self,
        context: Context,
        parallel_bucket: Optional[List[str]] = None,
    ) -> List[AgentResult]:
        results: List[AgentResult] = []
        instances = [
            cls() if isinstance(cls, type) else cls for cls in self.agent_classes
        ]
        i = 0
        while i < len(instances):
            inst = instances[i]
            name = getattr(inst, "name", inst.__class__.__name__)
            if parallel_bucket and name in parallel_bucket:
                chunk = []
                j = i
                while (
                    j < len(instances)
                    and getattr(
                        instances[j],
                        "name",
                        instances[j].__class__.__name__,
                    )
                    in parallel_bucket
                ):
                    chunk.append(instances[j])
                    j += 1
                with ThreadPoolExecutor(
                    max_workers=min(self.max_workers, len(chunk))
                ) as ex:
                    futures = {ex.submit(self._run_agent, ag, context): ag for ag in chunk}
                    for fut in as_completed(futures):
                        res = fut.result()
                        results.append(res)
                        self._merge_context(context, res)
                i = j
            else:
                res = self._run_agent(inst, context)
                results.append(res)
                self._merge_context(context, res)
                i += 1
        return results

    def _run_agent(
        self,
        agent: Agent,
        context: Context,
        retry: int = 2,
        backoff: float = 0.5,
    ) -> AgentResult:
        name = getattr(agent, "name", agent.__class__.__name__)
        attempt = 0
        t0 = time.time()
        while attempt <= retry:
            try:
                result = agent.run(context)
                duration = time.time() - t0
                result.setdefault("agent", name)
                result.setdefault("duration_s", duration)
                result.setdefault("status", result.get("status", "ok"))
                publish(name, "agent_result", result)
                incr_metric("agents.runs", 1)
                time_metric(f"agent.{name}.duration_s", duration)
                return result
            except Exception as e:  # noqa: BLE001
                logger.exception("Agent %s threw: %s", name, e)
                attempt += 1
                if attempt > retry:
                    break
                time.sleep(backoff * (2 ** (attempt - 1)))
        duration = time.time() - t0
        return {
            "agent": name,
            "status": "failed",
            "error": f"exhausted retries for {name}",
            "duration_s": duration,
        }

    def _merge_context(self, context: Context, res: AgentResult) -> None:
        r = res.get("result")
        if isinstance(r, dict):
            for k, v in r.items():
                if k not in context:
                    context[k] = v
        prov = r.get("provenance") if isinstance(r, dict) else None
        if prov:
            context.setdefault("provenance", []).extend(
                prov if isinstance(prov, list) else [prov]
            )

