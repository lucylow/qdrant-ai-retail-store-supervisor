from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from typing import List, Mapping, Sequence, Tuple
from uuid import uuid4

logger = logging.getLogger(__name__)

# Layer 1 Guardrail: valid intents (LLM extracts intent; schema validates)
VALID_INTENTS: Sequence[str] = (
    "purchase_bundle",
    "find_product",
    "compare_prices",
    "gift_finder",
    "replenish",
)
# Allowed regions for constraint validation
VALID_REGIONS: Sequence[str] = ("Berlin", "Paris", "Zurich", "London", "Geneva", "Bern")
# Max sensible budget (eur) to catch extraction errors
MAX_BUDGET_EUR: float = 500_000.0
# Max urgency days
MAX_URGENCY_DAYS: int = 365


@dataclass(slots=True)
class ShopperGoal:
    goal_id: str
    query: str
    intent: str
    budget_eur: float | None
    region: str | None
    urgency_days: int | None
    clarified: bool
    latency_ms: int

    def summary(self) -> str:
        parts: List[str] = [self.intent]
        if self.budget_eur is not None:
            parts.append(f"budget≤€{self.budget_eur:.0f}")
        if self.region:
            parts.append(self.region)
        if self.urgency_days is not None:
            parts.append(f"<={self.urgency_days}d")
        return " | ".join(parts)


def _validate_goal_schema(
    intent: str,
    budget_eur: float | None,
    region: str | None,
    urgency_days: int | None,
) -> Tuple[bool, List[str]]:
    """
    Layer 1 Guardrail: schema validation. Intent only, no business logic.
    Ensures extracted fields are within allowed ranges and enums.
    """
    reasons: List[str] = []
    if intent not in VALID_INTENTS:
        reasons.append(f"intent '{intent}' not in {list(VALID_INTENTS)}")
    if budget_eur is not None:
        if budget_eur <= 0:
            reasons.append("budget must be > 0")
        elif budget_eur > MAX_BUDGET_EUR:
            reasons.append(f"budget exceeds max {MAX_BUDGET_EUR}")
    if region is not None and region not in VALID_REGIONS:
        reasons.append(f"region '{region}' not in allowed list")
    if urgency_days is not None and (urgency_days < 1 or urgency_days > MAX_URGENCY_DAYS):
        reasons.append(f"urgency_days must be 1..{MAX_URGENCY_DAYS}")
    return len(reasons) == 0, reasons


class ShopperAgent:
    """
    Goal extraction + user intent (language understanding).

    Research-backed: single LLMs fail complex retail workflows; specialized
    agents excel (BytePlus 30% stockout reduction). This agent does semantic
    understanding only; deterministic schema validation prevents bad inputs.
    LLM role: intent extraction. Deterministic layer: schema validation.
    """

    def parse_goal(self, query: str, goal_id: str | None = None) -> ShopperGoal:
        # AUTONOMOUS-AGENT-HACKATHON: shopper goal extraction for demo query.
        started = time.perf_counter()
        goal_uuid = goal_id or str(uuid4())

        text = query.lower()
        budget: float | None = None
        urgency_days: int | None = None
        region: str | None = None

        if "€" in text:
            try:
                after = text.split("€", maxsplit=1)[1]
                digits = "".join(ch for ch in after if ch.isdigit())
                if digits:
                    budget = float(digits)
            except Exception:  # noqa: BLE001
                budget = None

        for token in ["berlin", "paris", "zurich", "london", "geneva", "bern"]:
            if token in text:
                region = token.title()
                break

        if "<3 days" in text or "within 3 days" in text:
            urgency_days = 3
        elif "tomorrow" in text:
            urgency_days = 1

        # Intent taxonomy: map keywords to valid intents (deterministic fallback)
        intent = "purchase_bundle"
        if "compare" in text or "cheaper" in text:
            intent = "compare_prices"
        elif "find" in text or "looking for" in text:
            intent = "find_product"
        elif "gift" in text:
            intent = "gift_finder"
        elif "replenish" in text or "restock" in text:
            intent = "replenish"

        # Layer 1: schema validation (budget>0, valid categories/regions)
        valid, validation_reasons = _validate_goal_schema(
            intent, budget, region, urgency_days
        )
        if not valid:
            logger.warning(
                "Goal schema validation failed; normalizing",
                extra={
                    "event": "shopper.schema_validation",
                    "goal_id": goal_uuid,
                    "reasons": validation_reasons,
                },
            )
            if budget is not None and budget <= 0:
                budget = None
            if region is not None and region not in VALID_REGIONS:
                region = None
            if urgency_days is not None and (urgency_days < 1 or urgency_days > MAX_URGENCY_DAYS):
                urgency_days = min(max(urgency_days or 3, 1), MAX_URGENCY_DAYS)

        latency_ms = int((time.perf_counter() - started) * 1000)
        logger.info(
            "Parsed shopper goal",
            extra={
                "event": "shopper.parse_goal",
                "goal_id": goal_uuid,
                "intent": intent,
                "budget_eur": budget,
                "region": region,
                "urgency_days": urgency_days,
                "latency_ms": latency_ms,
            },
        )
        return ShopperGoal(
            goal_id=goal_uuid,
            query=query,
            intent=intent,
            budget_eur=budget,
            region=region,
            urgency_days=urgency_days,
            clarified=True,
            latency_ms=latency_ms,
        )

    def parse_goal_with_memory(
        self,
        user_message: str,
        user_id: str,
        session_id: str,
        goal_id: str | None = None,
    ) -> ShopperGoal:
        """
        Memory-enhanced goal extraction: short-term context + user profile + episodic
        examples, then LLM parse (or fallback to rule-based parse_goal).
        """
        started = time.perf_counter()
        goal_uuid = goal_id or str(uuid4())

        from app.data.short_term_memory import (
            format_short_term_context,
            push_turn,
            read_session,
            session_key,
        )
        from app.data.user_profiles import get_by_user_id
        from app.data.goal_solution_links import search_similar, format_episodic_summaries
        from app.prompts.memory_prompts import build_shopper_prompt

        sk = session_key(user_id, session_id)
        turns = read_session(sk)
        short_term_context = format_short_term_context(turns, last_n=3)
        push_turn(sk, {"role": "user", "text": user_message, "ts": time.time()})

        user_profile = get_by_user_id(user_id)
        user_profile_summary = (user_profile or {}).get("summary") or "(no profile)"

        episodic_hits = search_similar(user_message, top_k=3, min_score=0.75)
        episodic_summaries = format_episodic_summaries(episodic_hits, max_lines=3)

        prompt = build_shopper_prompt(
            short_term_context=short_term_context,
            user_profile_summary=user_profile_summary,
            episodic_summaries=episodic_summaries,
            user_message=user_message,
            user_id=user_id,
        )

        try:
            from app.llm_client import generate as llm_generate
            raw = llm_generate(prompt, max_tokens=256, temperature=0.2)
            # Strip markdown code blocks if present
            text = raw.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            parsed = json.loads(text)
        except Exception as e:  # noqa: BLE001
            logger.warning("Shopper LLM parse failed, using rule-based: %s", e)
            push_turn(sk, {"role": "agent", "text": "(fallback)", "ts": time.time()})
            return self.parse_goal(user_message, goal_uuid)

        if parsed.get("clarify"):
            clarification = (parsed.get("clarification") or "").strip() or "Could you give more details?"
            push_turn(sk, {"role": "agent", "text": clarification, "ts": time.time()})
            latency_ms = int((time.perf_counter() - started) * 1000)
            return ShopperGoal(
                goal_id=goal_uuid,
                query=user_message,
                intent="purchase_bundle",
                budget_eur=None,
                region=None,
                urgency_days=None,
                clarified=False,
                latency_ms=latency_ms,
            )
        goal_text = parsed.get("goal_text") or user_message
        budget = parsed.get("budget")
        if budget is not None:
            budget = float(budget)
        delivery_days = parsed.get("delivery_days")
        region = parsed.get("region")
        if isinstance(region, str) and region.strip():
            region = region.strip()
            if region not in VALID_REGIONS:
                for r in VALID_REGIONS:
                    if r.lower() in region.lower():
                        region = r
                        break
        else:
            region = None
        intent = "purchase_bundle"
        valid, _ = _validate_goal_schema(intent, budget, region, delivery_days)
        if not valid and budget is not None and budget <= 0:
            budget = None
        if not valid and region is not None and region not in VALID_REGIONS:
            region = None
        push_turn(sk, {"role": "agent", "text": f"Goal: {goal_text[:100]}", "ts": time.time()})
        latency_ms = int((time.perf_counter() - started) * 1000)
        return ShopperGoal(
            goal_id=goal_uuid,
            query=goal_text,
            intent=intent,
            budget_eur=budget,
            region=region,
            urgency_days=delivery_days,
            clarified=True,
            latency_ms=latency_ms,
        )


__all__: Sequence[str] = ["ShopperAgent", "ShopperGoal"]

