"""
Idea 8 agentic recommendation system: Shopper & Inventory agents for
goal-structuring + case-based planning RAG.

This module plugs into the existing stack:
- Qdrant connection via app.qdrant_client.get_qdrant_client / ensure_collection
- Embeddings via app.embeddings.embed_texts (SentenceTransformers by default)
- LLM via app.llm_client.generate (OpenAI when GENERATOR_PROVIDER=openai)

Collections (configurable via env, see app.config):
- COLL_GOALS:     structured user goals / sessions
- COLL_PRODUCTS:  product catalog
- COLL_SOLUTIONS: ranked solution bundles
- COLL_EPISODES:  episodic memory (goal–solution–outcome links)

Conceptual mapping to the Idea 8 design:
- Semantic goal matching:
    - ShopperAgent embeds structured goals into COLL_GOALS.
    - InventoryAgent retrieves prior successful episodes from COLL_EPISODES
      using the current goal vector (episodic memory).
- Inventory feasibility filter:
    - InventoryAgent only considers products with stock > 0 and matching region
      from COLL_PRODUCTS, ensuring that recommended bundles are actually
      fulfillable with current inventory.
- Success-biased, business-aware ranking:
    - InventoryAgent passes candidate products, prior successful episodes,
      and explicit multi-objective weighting instructions to the LLM so it can
      favor bundles that historically converted well, respect budget and
      delivery constraints, and align with margin / ETA objectives.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import json
import logging
import time
import uuid
from datetime import datetime

import numpy as np
from pydantic import BaseModel, Field, ValidationError
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue, Range

from app.config import (
    COLL_GOALS,
    COLL_PRODUCTS,
    COLL_SOLUTIONS,
    COLL_EPISODES,
)
from app.qdrant_client import get_qdrant_client, ensure_collection
from app.embeddings import embed_texts
from app.llm_client import generate as llm_generate

logger = logging.getLogger(__name__)


# =========================
# Pydantic models
# =========================


class StructuredGoal(BaseModel):
    goal_id: str = Field(..., description="Opaque goal identifier")
    user_id: str
    region: Optional[str] = None
    intent_summary: str
    constraints: Dict[str, Any] = Field(
        default_factory=dict,
        description="e.g. budget, time_window, style, size",
    )
    raw_query: str
    status: str = "open"  # open | in_progress | solved | failed
    created_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z",
        description="ISO-8601 creation time",
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z",
        description="ISO-8601 last update time",
    )


class SolutionCandidate(BaseModel):
    product_id: Any
    sku: Optional[str] = None
    score: float
    reason: Optional[str] = None


class SolutionBundle(BaseModel):
    solution_id: str
    goal_id: str
    user_id: str
    region: Optional[str] = None
    summary: str
    candidates: List[SolutionCandidate]
    status: str = "candidate"  # candidate | final | rejected
    created_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z",
        description="ISO-8601 creation time",
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z",
        description="ISO-8601 last update time",
    )


class EpisodeLink(BaseModel):
    episode_id: str
    user_id: str
    region: Optional[str] = None
    goal_id: str
    solution_id: str
    outcome: str  # success | partial | failure | unknown
    score: float
    notes: Optional[str] = None
    ts: float = Field(default_factory=lambda: time.time())
    created_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z",
        description="ISO-8601 creation time",
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z",
        description="ISO-8601 last update time",
    )


# =========================
# Qdrant bootstrap helpers
# =========================


def _ensure_agent_collections(client: QdrantClient, vector_size: int) -> None:
    """
    Idempotently create the four main collections used by the Shopper/Inventory loop.
    """
    ensure_collection(client, COLL_GOALS, vector_size)
    ensure_collection(client, COLL_PRODUCTS, vector_size)
    ensure_collection(client, COLL_SOLUTIONS, vector_size)
    ensure_collection(client, COLL_EPISODES, vector_size)


def _ensure_payload_indexes(client: QdrantClient) -> None:
    """
    Create a few high-value payload indexes (best-effort; safe if they already exist).
    """

    def _safe_index(coll: str, field: str, schema: rest.PayloadSchemaType) -> None:
        try:
            client.create_payload_index(
                collection_name=coll,
                field_name=field,
                field_schema=schema,
            )
        except Exception:  # noqa: BLE001
            # assume already exists or server too old; continue without hard failure
            logger.debug("Payload index on %s.%s already exists or unsupported", coll, field)

    # products
    _safe_index(COLL_PRODUCTS, "sku", rest.PayloadSchemaType.KEYWORD)
    _safe_index(COLL_PRODUCTS, "category", rest.PayloadSchemaType.KEYWORD)
    _safe_index(COLL_PRODUCTS, "stock", rest.PayloadSchemaType.INTEGER)
    _safe_index(COLL_PRODUCTS, "region", rest.PayloadSchemaType.KEYWORD)

    # goals
    _safe_index(COLL_GOALS, "status", rest.PayloadSchemaType.KEYWORD)
    _safe_index(COLL_GOALS, "user_id", rest.PayloadSchemaType.KEYWORD)
    _safe_index(COLL_GOALS, "region", rest.PayloadSchemaType.KEYWORD)
    _safe_index(COLL_GOALS, "created_at", rest.PayloadSchemaType.KEYWORD)

    # episodes
    _safe_index(COLL_EPISODES, "goal_id", rest.PayloadSchemaType.KEYWORD)
    _safe_index(COLL_EPISODES, "solution_id", rest.PayloadSchemaType.KEYWORD)
    _safe_index(COLL_EPISODES, "outcome", rest.PayloadSchemaType.KEYWORD)
    _safe_index(COLL_EPISODES, "score", rest.PayloadSchemaType.FLOAT)
    _safe_index(COLL_EPISODES, "user_id", rest.PayloadSchemaType.KEYWORD)
    _safe_index(COLL_EPISODES, "region", rest.PayloadSchemaType.KEYWORD)
    _safe_index(COLL_EPISODES, "created_at", rest.PayloadSchemaType.KEYWORD)

    # solutions
    _safe_index(COLL_SOLUTIONS, "goal_id", rest.PayloadSchemaType.KEYWORD)
    _safe_index(COLL_SOLUTIONS, "user_id", rest.PayloadSchemaType.KEYWORD)
    _safe_index(COLL_SOLUTIONS, "region", rest.PayloadSchemaType.KEYWORD)
    _safe_index(COLL_SOLUTIONS, "created_at", rest.PayloadSchemaType.KEYWORD)


def bootstrap_agent_collections(vector_size: Optional[int] = None) -> QdrantClient:
    """
    Public helper to:
    - get a Qdrant client using existing config
    - infer vector size from embedding model if not provided
    - ensure collections + payload indexes exist
    """
    client = get_qdrant_client()
    if vector_size is None:
        # derive from embedding model
        dim = embed_texts(["probe"]).shape[-1]
        vector_size = int(dim)
    _ensure_agent_collections(client, vector_size)
    _ensure_payload_indexes(client)
    return client


# =========================
# Shopper agent
# =========================


SHOPPER_INSTRUCTIONS = """
You are the Shopper agent in an e-commerce assistant.

Your job:
- Take a raw user query and turn it into a structured shopping goal.
- Extract: concise intent summary, constraints (budget, timing, style, size, etc).
- Do NOT invent products or make final decisions; just structure the goal.

Return STRICT JSON with keys:
- intent_summary: string
- constraints: object (keys like budget, occasion, size, color, delivery_deadline)
"""


def _shopper_prompt(raw_query: str, user_id: str, region: Optional[str]) -> str:
    return (
        f"{SHOPPER_INSTRUCTIONS.strip()}\n\n"
        f"User id: {user_id}\n"
        f"Region: {region or 'unknown'}\n\n"
        "Raw user query:\n"
        f'\"\"\"{raw_query}\"\"\"\n\n'
        "Respond with JSON only."
    )


class ShopperAgent:
    """
    Customer-facing agent: turns a raw text request into a StructuredGoal and writes it to Qdrant.
    Uses the global LLM client (OpenAI when GENERATOR_PROVIDER=openai) via app.llm_client.generate.
    """

    def __init__(self, client: Optional[QdrantClient] = None):
        self.client = client or bootstrap_agent_collections()

    def interpret_and_store_goal(
        self,
        user_id: str,
        raw_query: str,
        region: Optional[str] = None,
    ) -> StructuredGoal:
        prompt = _shopper_prompt(raw_query, user_id, region)
        try:
            llm_output = llm_generate(prompt, max_tokens=512, temperature=0.2)
        except Exception as exc:  # noqa: BLE001
            logger.error("ShopperAgent LLM call failed: %s", exc)
            raise

        try:
            parsed = json.loads(llm_output)
        except json.JSONDecodeError as exc:
            logger.error("ShopperAgent invalid JSON: %s | output=%s", exc, llm_output)
            # fallback: minimal struct from raw query
            parsed = {
                "intent_summary": raw_query[:200],
                "constraints": {},
            }

        intent_summary = parsed.get("intent_summary") or raw_query[:200]
        constraints = parsed.get("constraints") or {}

        goal_id = str(uuid.uuid4())
        now_iso = datetime.utcnow().isoformat() + "Z"
        goal = StructuredGoal(
            goal_id=goal_id,
            user_id=user_id,
            region=region,
            intent_summary=intent_summary,
            constraints=constraints,
            raw_query=raw_query,
            created_at=now_iso,
            updated_at=now_iso,
        )

        # Embed goal (intent + constraints) using existing embedding stack
        text_for_embedding = intent_summary + " " + json.dumps(constraints, sort_keys=True)
        vec = embed_texts([text_for_embedding])[0].astype("float32").tolist()

        point = PointStruct(
            id=goal.goal_id,
            vector=vec,
            payload={
                "goal_id": goal.goal_id,
                "user_id": goal.user_id,
                "region": goal.region,
                "status": goal.status,
                "intent_summary": goal.intent_summary,
                "constraints": goal.constraints,
                "raw_query": goal.raw_query,
                "ts": time.time(),
                "created_at": goal.created_at,
                "updated_at": goal.updated_at,
            },
        )

        self.client.upsert(collection_name=COLL_GOALS, points=[point])
        logger.info("ShopperAgent stored goal %s for user %s", goal.goal_id, user_id)
        return goal


# =========================
# Inventory agent
# =========================


INVENTORY_INSTRUCTIONS = """
You are the Inventory / Planner agent for an e-commerce assistant,
implementing the Idea 8 multi-agent recommendation design.

You receive:
- A structured goal (intent + constraints).
- A list of candidate products (already filtered for stock > 0 and region).
- A few prior SUCCESSFUL episodes for similar goals (episodic memory).

Your job:
- Select a small bundle (0–5) of products that best match the goal.
- Justify the ranking and include a short solution summary.
- Use SUCCESS-BIASED, BUSINESS-AWARE RANKING with these approximate weights:
    - Past success rate / relevance from episodes: 40%
    - Margin (payload.margin if present, otherwise approximate from price): 30%
    - Delivery speed / ETA feasibility (e.g. payload.eta_days, region match): 20%
    - Price alignment with the goal's budget constraints: 10%

Notes:
- Treat prior successful episodes as very strong evidence when they closely
  match the current goal.
- Never select out-of-stock or region-incompatible products (these are
  pre-filtered, but you must not re-introduce them).
- When budget constraints are present, strongly prefer bundles whose total
  price fits the budget while still respecting the weights above.

Respond in STRICT JSON with keys:
- summary: string (1-3 sentences)
- choices: array of objects:
    - product_id: string or number
    - sku: string or null
    - score: number between 0 and 1 (your confidence for this product)
    - reason: short string

Do NOT invent products. Only pick from candidates provided.
"""


def _inventory_prompt(
    goal: StructuredGoal,
    candidate_products: List[Dict[str, Any]],
    prior_episodes: List[Dict[str, Any]],
) -> str:
    return (
        f"{INVENTORY_INSTRUCTIONS.strip()}\n\n"
        "Structured goal:\n"
        f"{goal.model_dump_json(indent=2)}\n\n"
        "Candidate products (already region/stock filtered):\n"
        f"{json.dumps(candidate_products, indent=2)}\n\n"
        "Prior successful episodes (may be empty):\n"
        f"{json.dumps(prior_episodes, indent=2)}\n\n"
        "Respond with JSON only."
    )


class InventoryAgent:
    """
    Back-office planner: polls open goals from Qdrant, retrieves products + prior episodes,
    calls the LLM to rank bundles, writes solutions + episodic memory.
    """

    def __init__(self, client: Optional[QdrantClient] = None):
        self.client = client or bootstrap_agent_collections()

    # ---- retrieval helpers ----

    def _get_open_goals(self, limit: int = 10) -> List[Any]:
        flt = Filter(
            must=[
                FieldCondition(
                    key="status",
                    match=MatchValue(value="open"),
                )
            ]
        )
        points, _, _ = self.client.scroll(
            collection_name=COLL_GOALS,
            scroll_filter=flt,
            limit=limit,
            with_payload=True,
            with_vectors=True,
        )
        return points

    def _find_prior_episodes(
        self,
        goal_vector: List[float],
        region: Optional[str],
        top_k: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve prior SUCCESSFUL episodes that are semantically close to the
        current goal. This is the episodic memory lookup that powers Idea 8's
        semantic goal matching layer.
        """
        must: List[FieldCondition] = [
            FieldCondition(
                key="outcome",
                match=MatchValue(value="success"),
            )
        ]
        if region:
            must.append(FieldCondition(key="region", match=MatchValue(value=region)))
        flt = Filter(must=must)

        hits = self.client.search(
            collection_name=COLL_EPISODES,
            query_vector=goal_vector,
            limit=top_k,
            query_filter=flt,
            with_payload=True,
        )
        return [{"id": h.id, "score": h.score, "payload": h.payload} for h in hits]

    def _find_candidate_products(
        self,
        goal_vector: List[float],
        region: Optional[str],
        top_k: int = 12,
    ) -> List[Dict[str, Any]]:
        must: List[FieldCondition] = [
            FieldCondition(
                key="stock",
                range=Range(gt=0),
            )
        ]
        if region:
            must.append(FieldCondition(key="region", match=MatchValue(value=region)))
        flt = Filter(must=must)

        hits = self.client.search(
            collection_name=COLL_PRODUCTS,
            query_vector=goal_vector,
            limit=top_k,
            query_filter=flt,
            with_payload=True,
        )
        results = [{"id": h.id, "score": h.score, "payload": h.payload} for h in hits]

        # Fallback: if vector search is empty or low-confidence, use filter-only rule-based recall.
        if not results or (results and float(results[0]["score"]) < 0.25):
            logger.info(
                "InventoryAgent: falling back to rule-based product recall (top_k=%s, region=%s)",
                top_k,
                region,
            )
            points, _, _ = self.client.scroll(
                collection_name=COLL_PRODUCTS,
                scroll_filter=flt,
                limit=top_k,
                with_payload=True,
                with_vectors=False,
            )
            fallback: List[Dict[str, Any]] = []
            for p in points:
                fallback.append(
                    {
                        "id": p.id,
                        "score": 0.0,
                        "payload": p.payload or {},
                    }
                )
            # Only override if we actually found something via fallback
            if fallback:
                return fallback

        return results

    # ---- main loop ----

    def solve_once_for_open_goals(self, max_goals: int = 5) -> List[Tuple[StructuredGoal, SolutionBundle]]:
        open_goals = self._get_open_goals(limit=max_goals)
        solved: List[Tuple[StructuredGoal, SolutionBundle]] = []

        if not open_goals:
            logger.info("InventoryAgent: no open goals.")
            return solved

        for g in open_goals:
            payload = g.payload or {}
            try:
                goal = StructuredGoal(
                    goal_id=payload.get("goal_id", g.id),
                    user_id=payload["user_id"],
                    region=payload.get("region"),
                    intent_summary=payload["intent_summary"],
                    constraints=payload.get("constraints", {}),
                    raw_query=payload.get("raw_query", ""),
                    status=payload.get("status", "open"),
                )
            except ValidationError as exc:
                logger.warning("InventoryAgent skipping goal %s: invalid payload %s", g.id, exc)
                continue

            goal_vec = g.vector
            if isinstance(goal_vec, np.ndarray):
                goal_vec = goal_vec.astype("float32").tolist()

            prior_eps = self._find_prior_episodes(goal_vec, goal.region)
            candidates = self._find_candidate_products(goal_vec, goal.region)

            if not candidates:
                logger.info("InventoryAgent: no candidates for goal %s", goal.goal_id)
                continue

            prompt = _inventory_prompt(goal=goal, candidate_products=candidates, prior_episodes=prior_eps)
            try:
                llm_output = llm_generate(prompt, max_tokens=512, temperature=0.2)
            except Exception as exc:  # noqa: BLE001
                logger.error("InventoryAgent LLM call failed for goal %s: %s", goal.goal_id, exc)
                continue

            try:
                parsed = json.loads(llm_output)
            except json.JSONDecodeError as exc:
                logger.error("InventoryAgent invalid JSON for goal %s: %s | output=%s", goal.goal_id, exc, llm_output)
                continue

            summary = parsed.get("summary", "")
            raw_choices = parsed.get("choices", []) or []

            sol_id = str(uuid.uuid4())
            bundle = SolutionBundle(
                solution_id=sol_id,
                goal_id=goal.goal_id,
                user_id=goal.user_id,
                region=goal.region,
                summary=summary,
                candidates=[
                    SolutionCandidate(
                        product_id=c.get("product_id"),
                        sku=c.get("sku"),
                        score=float(c.get("score", 0.0)),
                        reason=c.get("reason"),
                    )
                    for c in raw_choices
                ],
                status="candidate",
            )

            self._store_solution(goal, bundle, goal_vec, prior_eps)
            solved.append((goal, bundle))

        return solved

    # ---- storage helpers ----

    def _store_solution(
        self,
        goal: StructuredGoal,
        bundle: SolutionBundle,
        goal_vec: List[float],
        prior_eps: List[Dict[str, Any]],
    ) -> None:
        # 1) upsert into solutions
        sol_text = bundle.summary + " " + json.dumps(
            [c.model_dump() for c in bundle.candidates],
            sort_keys=True,
        )
        vec = embed_texts([sol_text])[0].astype("float32").tolist()

        now_iso = datetime.utcnow().isoformat() + "Z"
        sol_payload = bundle.model_dump()
        sol_payload["created_at"] = sol_payload.get("created_at", now_iso)
        sol_payload["updated_at"] = now_iso

        sol_point = PointStruct(
            id=bundle.solution_id,
            vector=vec,
            payload=sol_payload,
        )
        self.client.upsert(collection_name=COLL_SOLUTIONS, points=[sol_point])

        # 2) write episodic memory link
        outcome = "unknown"
        score = float(
            np.mean([c.score for c in bundle.candidates]) if bundle.candidates else 0.0,
        )

        episode = EpisodeLink(
            episode_id=str(uuid.uuid4()),
            user_id=goal.user_id,
            region=goal.region,
            goal_id=goal.goal_id,
            solution_id=bundle.solution_id,
            outcome=outcome,
            score=score,
            notes=f"Generated from {len(prior_eps)} prior episodes.",
        )

        ep_text = f"{goal.intent_summary} | {bundle.summary} | outcome={outcome}"
        ep_vec = embed_texts([ep_text])[0].astype("float32").tolist()

        ep_payload = episode.model_dump()
        ep_payload["created_at"] = ep_payload.get("created_at", now_iso)
        ep_payload["updated_at"] = now_iso

        ep_point = PointStruct(
            id=episode.episode_id,
            vector=ep_vec,
            payload=ep_payload,
        )
        self.client.upsert(collection_name=COLL_EPISODES, points=[ep_point])

        # 3) update goal status to in_progress (could be set to solved after user confirmation)
        self.client.set_payload(
            collection_name=COLL_GOALS,
            payload={
                "status": "in_progress",
                "updated_at": now_iso,
            },
            points=[goal.goal_id],
        )
        logger.info(
            "InventoryAgent wrote solution %s and episode %s for goal %s",
            bundle.solution_id,
            episode.episode_id,
            goal.goal_id,
        )


def record_solution_feedback(
    client: QdrantClient,
    goal_id: str,
    solution_id: str,
    outcome: str,
    purchased: bool,
) -> None:
    """
    Outcome feedback loop:
    - Update EpisodeLink.outcome from "unknown" → "success" | "partial" | "failure".
    - Optionally bump the episode score up/down based on outcome & purchase flag.
    - Update goal / solution status to reflect final outcome.
    """
    outcome = outcome.lower()
    if outcome not in {"success", "partial", "failure"}:
        raise ValueError(f"Invalid outcome '{outcome}' (expected success|partial|failure)")

    now_iso = datetime.utcnow().isoformat() + "Z"

    # 1) find matching episodes for this (goal_id, solution_id)
    flt = Filter(
        must=[
            FieldCondition(key="goal_id", match=MatchValue(value=goal_id)),
            FieldCondition(key="solution_id", match=MatchValue(value=solution_id)),
        ]
    )
    episodes, _, _ = client.scroll(
        collection_name=COLL_EPISODES,
        scroll_filter=flt,
        limit=100,
        with_payload=True,
        with_vectors=False,
    )

    if not episodes:
        logger.warning(
            "record_solution_feedback: no episodes found for goal_id=%s, solution_id=%s",
            goal_id,
            solution_id,
        )
    else:
        ids = [e.id for e in episodes]
        # simple score bumping logic
        for e in episodes:
            payload = e.payload or {}
            base_score = float(payload.get("score", 0.0))
            if outcome == "success":
                delta = 0.1 if purchased else 0.05
            elif outcome == "partial":
                delta = 0.02 if purchased else -0.02
            else:  # failure
                delta = -0.1
            new_score = max(0.0, min(1.0, base_score + delta))
            payload["score"] = new_score
            payload["outcome"] = outcome
            payload["updated_at"] = now_iso

        client.set_payload(
            collection_name=COLL_EPISODES,
            payload={"outcome": outcome, "updated_at": now_iso},
            points=ids,
        )

    # 2) update solution status
    sol_status = "final" if outcome in {"success", "partial"} else "rejected"
    client.set_payload(
        collection_name=COLL_SOLUTIONS,
        payload={"status": sol_status, "updated_at": now_iso},
        points=[solution_id],
    )

    # 3) update goal status + updated_at
    goal_status = "solved" if outcome in {"success", "partial"} else "failed"
    client.set_payload(
        collection_name=COLL_GOALS,
        payload={"status": goal_status, "updated_at": now_iso},
        points=[goal_id],
    )

    logger.info(
        "Recorded feedback outcome=%s purchased=%s for goal_id=%s solution_id=%s",
        outcome,
        purchased,
        goal_id,
        solution_id,
    )


# =========================
# Minimal demo / manual test
# =========================


def _seed_demo_products(client: QdrantClient) -> None:
    """
    Seed a simple camping-oriented catalog into the products collection for quick local testing.
    Safe to call repeatedly; uses fixed IDs.

    Products are designed to exercise the Idea 8 objectives:
    - margin: gross margin per item (higher is better for business)
    - eta_days: typical delivery time in days (lower is better)
    - success_rate: historical conversion rate for this SKU in similar goals
    """
    products = [
        {
            "id": "CAMP_TENT_2P_BUDGET",
            "sku": "TENT-2P-BASIC",
            "name": "Basic 2-Person Tent",
            "category": "camping_tent",
            "stock": 25,
            "region": "EU",
            "price": 129.0,
            "margin": 32.0,
            "eta_days": 2,
            "success_rate": 0.62,
            "description": "Lightweight 2-person dome tent, weather resistant, suitable for weekend trips.",
        },
        {
            "id": "CAMP_TENT_2P_PREMIUM",
            "sku": "TENT-2P-PREMIUM",
            "name": "Premium 2-Person Tent",
            "category": "camping_tent",
            "stock": 8,
            "region": "EU",
            "price": 219.0,
            "margin": 68.0,
            "eta_days": 1,
            "success_rate": 0.78,
            "description": "Premium 4-season 2-person tent with reinforced poles and superior waterproofing.",
        },
        {
            "id": "CAMP_SLEEPINGBAG_STD",
            "sku": "SBAG-STD-3C",
            "name": "Standard Sleeping Bag (3°C)",
            "category": "sleeping_bag",
            "stock": 40,
            "region": "EU",
            "price": 59.0,
            "margin": 18.0,
            "eta_days": 2,
            "success_rate": 0.71,
            "description": "Synthetic-fill sleeping bag rated to 3°C, ideal for spring and summer camping.",
        },
        {
            "id": "CAMP_SLEEPINGBAG_PREM",
            "sku": "SBAG-PREM-0C",
            "name": "Premium Sleeping Bag (0°C)",
            "category": "sleeping_bag",
            "stock": 15,
            "region": "EU",
            "price": 99.0,
            "margin": 34.0,
            "eta_days": 1,
            "success_rate": 0.81,
            "description": "Down-filled mummy sleeping bag rated to 0°C, compact and lightweight.",
        },
        {
            "id": "CAMP_BUNDLE_BUDGET_2P",
            "sku": "BUNDLE-2P-BUDGET",
            "name": "Budget 2-Person Camping Kit",
            "category": "bundle",
            "stock": 10,
            "region": "EU",
            "price": 239.0,
            "margin": 74.0,
            "eta_days": 2,
            "success_rate": 0.68,
            "description": "Bundle: Basic 2-person tent + 2 standard sleeping bags, ideal for trips under 400 EUR.",
        },
        {
            "id": "CAMP_BUNDLE_PREM_2P",
            "sku": "BUNDLE-2P-PREMIUM",
            "name": "Premium 2-Person Camping Kit",
            "category": "bundle",
            "stock": 6,
            "region": "EU",
            "price": 349.0,
            "margin": 112.0,
            "eta_days": 1,
            "success_rate": 0.92,
            "description": "Bundle: Premium 2-person tent + 2 premium sleeping bags, optimized for comfort and fast delivery.",
        },
        {
            "id": "CAMP_TENT_3P_SLOW",
            "sku": "TENT-3P-SLOW",
            "name": "3-Person Tent (Slow Delivery)",
            "category": "camping_tent",
            "stock": 20,
            "region": "EU",
            "price": 189.0,
            "margin": 46.0,
            "eta_days": 5,
            "success_rate": 0.35,
            "description": "Spacious 3-person tent with good margin but slower standard delivery (5 days).",
        },
    ]

    texts = [p["name"] + " " + p["description"] for p in products]
    vecs = embed_texts(texts).astype("float32")

    points = []
    for p, v in zip(products, vecs):
        payload = {
            "sku": p["sku"],
            "name": p["name"],
            "category": p["category"],
            "stock": p["stock"],
            "region": p["region"],
            "price": p["price"],
            "margin": p.get("margin"),
            "eta_days": p.get("eta_days"),
            "success_rate": p.get("success_rate"),
            "description": p["description"],
            "ts": time.time(),
        }
        points.append(
            PointStruct(
                id=p["id"],
                vector=v.tolist(),
                payload=payload,
            )
        )

    client.upsert(collection_name=COLL_PRODUCTS, points=points)
    logger.info("Seeded %d demo products into %s", len(products), COLL_PRODUCTS)


def demo_single_flow() -> None:
    """
    Minimal end-to-end demo:
    - Shopper interprets a raw query and writes a goal.
    - Inventory polls open goals, creates a solution bundle, and writes episodic memory.

    Usage:
        export GENERATOR_PROVIDER=openai
        export OPENAI_API_KEY=...
        python -m app.shopping_agents
    """
    client = bootstrap_agent_collections()
    _seed_demo_products(client)

    shopper = ShopperAgent(client)
    inventory = InventoryAgent(client)

    user_id = "user_123"
    region = "EU"
    raw_query = "I need a blue shirt for a birthday party, budget around 40, delivered in a week."

    goal = shopper.interpret_and_store_goal(user_id=user_id, raw_query=raw_query, region=region)
    goal_written_at = time.time()
    print("Structured goal:", goal.model_dump())

    solved = inventory.solve_once_for_open_goals(max_goals=5)
    first_solution_time = time.time() if solved else None
    time_to_first_solution = (
        (first_solution_time - goal_written_at) if first_solution_time is not None else None
    )

    # Simple feasibility metric: did we produce at least one candidate for this goal?
    feasibility_rate = 1.0 if solved and solved[0][1].candidates else 0.0

    logger.info(
        "Metrics: time_to_first_solution=%.3fs, feasibility_rate=%.2f",
        time_to_first_solution or -1.0,
        feasibility_rate,
    )
    for g, bundle in solved:
        print("\n--- SOLUTION ---")
        print("Goal:", g.intent_summary)
        print("Solution summary:", bundle.summary)
        print("Candidates:")
        for c in bundle.candidates:
            print(" ", c.model_dump())


if __name__ == "__main__":
    demo_single_flow()

