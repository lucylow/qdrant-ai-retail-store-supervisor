from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, List, Mapping, Sequence, Set

from qdrant_client.http import models as rest

from app.agents.shopper import ShopperGoal
from app.data.collections import COLL_PRODUCTS
from app.qdrant_client import get_qdrant_client


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class Product:
    sku: str
    name: str
    price_eur: float
    attributes: Mapping[str, str]


@dataclass(slots=True)
class InventorySearchContext:
    candidates: List[Product]
    latency_ms: int


@dataclass(slots=True)
class InventoryPlanItem:
    sku: str
    quantity: int
    unit_price_eur: float


@dataclass(slots=True)
class InventoryPlan:
    items: List[InventoryPlanItem] = field(default_factory=list)
    eta_days: int = 3
    total_price_eur: float = 0.0
    latency_ms: int = 0


def _product_from_payload(payload: Mapping) -> Product | None:
    sku = str((payload or {}).get("sku", ""))
    if not sku:
        return None
    name = str(payload.get("name", sku))
    price = float(payload.get("price_eur", 0.0))
    attributes = {
        k: str(v)
        for k, v in (payload or {}).items()
        if k not in {"sku", "name", "price_eur"}
    }
    return Product(sku=sku, name=name, price_eur=price, attributes=attributes)


class InventoryAgent:
    """
    Constraint solving + inventory feasibility (logistics reasoning).

    Uses semantic search over Qdrant products (RAG) so recommendations match
    query intent; deterministic bundle optimization keeps execution grounded.
    Optional episodic_skus bias prefers SKUs from successful past episodes.
    """

    def __init__(self, use_semantic_search: bool = True) -> None:
        self._use_semantic_search = use_semantic_search

    def initial_search(
        self,
        query: str,
        episodic_skus: Sequence[str] | None = None,
        *,
        region: str | None = None,
        budget_eur: float | None = None,
        stock_gt: int | None = None,
    ) -> InventorySearchContext:
        started = time.perf_counter()
        client = get_qdrant_client()
        candidates: List[Product] = []
        prefer_skus: Set[str] = set(episodic_skus or [])

        # Filtered product search (stock, region, price) when constraints provided
        use_filtered = region is not None or budget_eur is not None or stock_gt is not None
        if use_filtered:
            try:
                from app.data.product_search import search_products_filtered
                from app.config import QDRANT

                hits = search_products_filtered(
                    query,
                    limit=32,
                    region=region,
                    price_lte=budget_eur,
                    stock_gt=stock_gt,
                    hnsw_ef=getattr(QDRANT, "hnsw_ef_search", None) or 128,
                )
                for h in hits:
                    p = _product_from_payload(h.get("payload") or {})
                    if p:
                        candidates.append(p)
                logger.info(
                    "Inventory filtered search",
                    extra={
                        "event": "inventory.filtered_search",
                        "query": query[:80],
                        "candidates": len(candidates),
                        "region": region,
                        "budget_eur": budget_eur,
                    },
                )
            except Exception as e:  # noqa: BLE001
                logger.warning("Filtered search failed, falling back to unfiltered: %s", e)
                use_filtered = False

        if not use_filtered and self._use_semantic_search:
            try:
                from app.embeddings import embed_single

                emb = embed_single(query)
                qvec = emb.vectors[0].tolist()
                dim = len(qvec)
                # Only use vector search if collection vector size matches
                coll_info = client.get_collection(COLL_PRODUCTS)
                config = getattr(coll_info, "config", None)
                if config and hasattr(config, "params"):
                    from qdrant_client.http import models as qrest

                    vparams = getattr(config.params, "vectors", None)
                    if isinstance(vparams, qrest.VectorParams):
                        coll_size = vparams.size
                    else:
                        coll_size = dim
                else:
                    coll_size = dim
                if coll_size == dim:
                    result = client.search(
                        collection_name=COLL_PRODUCTS,
                        query_vector=qvec,
                        limit=32,
                        with_payload=True,
                    )
                    for point in result:
                        p = _product_from_payload(point.payload or {})
                        if p:
                            candidates.append(p)
                    logger.info(
                        "Inventory semantic search",
                        extra={
                            "event": "inventory.semantic_search",
                            "query": query[:80],
                            "candidates": len(candidates),
                        },
                    )
            except Exception as e:  # noqa: BLE001
                logger.warning(
                    "Semantic search failed, falling back to scroll: %s",
                    e,
                    extra={"event": "inventory.semantic_fallback"},
                )

        if not candidates:
            # Fallback: scroll (no vector) when semantic search unavailable or wrong dim
            try:
                points, _ = client.scroll(
                    collection_name=COLL_PRODUCTS,
                    limit=32,
                    with_payload=True,
                    with_vectors=False,
                )
                for point in points:
                    p = _product_from_payload(point.payload or {})
                    if p:
                        candidates.append(p)
            except Exception:  # noqa: BLE001
                pass

        # Episodic bias: move SKUs that appeared in successful episodes to the front
        if prefer_skus and candidates:
            def sort_key(p: Product) -> tuple:
                return (0 if p.sku in prefer_skus else 1, -p.price_eur)

            candidates = sorted(candidates, key=sort_key)

        latency_ms = int((time.perf_counter() - started) * 1000)
        logger.info(
            "Inventory initial search",
            extra={
                "event": "inventory.initial_search",
                "query": query[:80],
                "candidates": len(candidates),
                "latency_ms": latency_ms,
            },
        )
        return InventorySearchContext(candidates=candidates, latency_ms=latency_ms)

    def optimize_bundle(
        self,
        goal: ShopperGoal,
        ctx: InventorySearchContext,
    ) -> InventoryPlan:
        # AUTONOMOUS-AGENT-HACKATHON: simple deterministic bundle selection.
        started = time.perf_counter()
        remaining = goal.budget_eur or 9999.0
        items: List[InventoryPlanItem] = []
        for product in sorted(ctx.candidates, key=lambda p: p.price_eur):
            if product.price_eur <= 0 or product.price_eur > remaining:
                continue
            items.append(
                InventoryPlanItem(
                    sku=product.sku,
                    quantity=1,
                    unit_price_eur=product.price_eur,
                )
            )
            remaining -= product.price_eur
            if remaining <= 0:
                break
        total_price = sum(i.unit_price_eur * i.quantity for i in items)
        eta_days = goal.urgency_days or 3
        latency_ms = int((time.perf_counter() - started) * 1000)
        logger.info(
            "Inventory bundle optimization",
            extra={
                "event": "inventory.optimize_bundle",
                "goal_id": goal.goal_id,
                "items": len(items),
                "total_price_eur": total_price,
                "eta_days": eta_days,
                "latency_ms": latency_ms,
            },
        )
        return InventoryPlan(
            items=items,
            eta_days=eta_days,
            total_price_eur=total_price,
            latency_ms=latency_ms,
        )

    def plan_bundles_with_memory(self, goal: ShopperGoal) -> List[dict[str, Any]]:
        """
        Memory-enhanced bundle planning: episodic precedents + procedural patterns
        + product candidates (stock/region filtered), then LLM returns up to 3 bundles.
        """
        started = time.perf_counter()
        from app.embeddings import embed_single
        from app.data.goal_solution_links import (
            format_episodic_summaries,
            search_similar as episodic_search,
        )
        from app.data.procedural_memory import search as procedural_search, format_procedural_pattern
        from app.prompts.memory_prompts import build_inventory_prompt

        goal_text = goal.query
        goal_vec = embed_single(goal_text).vectors[0].tolist()
        region = goal.region

        from app.config import QDRANT
        hnsw_ef_episodic = getattr(QDRANT, "hnsw_ef_search", None) or 192  # higher recall for episodic

        episodic_hits = episodic_search(
            goal_text,
            top_k=4,
            outcome_filter="purchased",
            min_score=0.70,
            hnsw_ef=hnsw_ef_episodic,
        )
        if not episodic_hits:
            episodic_hits = episodic_search(
                goal_text,
                top_k=4,
                outcome_filter="success",
                min_score=0.70,
                hnsw_ef=hnsw_ef_episodic,
            )
        episodic_summaries = format_episodic_summaries(episodic_hits, max_lines=5)

        procedural_hits = procedural_search(goal_vec, top_k=3, min_success_rate=0.80)
        procedural_pattern = format_procedural_pattern(procedural_hits)

        # Episodic SKUs for sort bias (from prior successful bundles when present in payload)
        episodic_skus_list: List[str] | None = None
        for h in episodic_hits[:3]:
            opt = (h.get("payload") or {}).get("optimalBundles") or []
            if opt and isinstance(opt, list):
                for b in opt:
                    if isinstance(b, str):
                        episodic_skus_list = (episodic_skus_list or []) + [s.strip() for s in b.split(",") if s.strip()][:5]
            # goal_solution_links payload may have solution_skus in procedural-style payload
            skus = (h.get("payload") or {}).get("solution_skus")
            if skus and isinstance(skus, list):
                episodic_skus_list = (episodic_skus_list or []) + [str(s) for s in skus[:5]]
        if episodic_skus_list:
            episodic_skus_list = list(dict.fromkeys(episodic_skus_list))[:15]

        ctx = self.initial_search(
            goal_text,
            episodic_skus=episodic_skus_list,
            region=region,
            budget_eur=goal.budget_eur,
            stock_gt=None,  # set to 0 when products payload has "stock" for in-stock-only
        )
        snippets: List[str] = []
        for p in ctx.candidates[:12]:
            attrs = getattr(p, "attributes", None) or {}
            stock = attrs.get("stock", "?")
            attrs_str = ", ".join(f"{k}={v}" for k, v in list(attrs.items())[:3])
            snippets.append(
                f"sku={p.sku}, name={p.name}, stock={stock}, price={p.price_eur}, attrs=[{attrs_str}]"
            )
        product_snippets = "\n".join(snippets) if snippets else "(no products)"

        goal_json = json.dumps({
            "goal_text": goal_text,
            "budget_eur": goal.budget_eur,
            "region": goal.region,
            "urgency_days": goal.urgency_days,
            "intent": goal.intent,
        }, indent=2)

        prompt = build_inventory_prompt(
            goal_json=goal_json,
            episodic_summaries=episodic_summaries,
            product_snippets=product_snippets,
            procedural_pattern=procedural_pattern,
        )

        try:
            from app.llm_client import generate as llm_generate
            raw = llm_generate(prompt, max_tokens=512, temperature=0.2)
            text = raw.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            bundles = json.loads(text)
        except Exception as e:  # noqa: BLE001
            logger.warning("Inventory LLM plan_bundles failed: %s", e)
            plan = self.optimize_bundle(goal, ctx)
            return [{
                "bundle_id": 1,
                "skus": [i.sku for i in plan.items],
                "total_price": plan.total_price_eur,
                "feasible": True,
                "score": 0.7,
                "rationale": "Fallback deterministic bundle",
            }]

        if not isinstance(bundles, list):
            bundles = [bundles] if isinstance(bundles, dict) else []
        latency_ms = int((time.perf_counter() - started) * 1000)
        logger.info(
            "Inventory plan_bundles_with_memory",
            extra={"event": "inventory.plan_bundles_memory", "goal_id": goal.goal_id, "bundles": len(bundles), "latency_ms": latency_ms},
        )
        return bundles


__all__: Sequence[str] = [
    "InventoryAgent",
    "InventoryPlan",
    "InventoryPlanItem",
    "InventorySearchContext",
    "Product",
]

