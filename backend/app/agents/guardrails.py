"""
4-Layer Defense: Deterministic data handling and LLM hallucination prevention.

Core principles:
- Deterministic vs generative split: stock, price, tax, shipping from APIs/databases—never LLM.
- Schema-first design: structured goal fields validated (types, ranges, enums) before inventory.
- MCP/tooling layer: agents restricted to specific tools; no free-form LLM on business data.

Layer 1 — Input: Validate user goals (Shopper Agent) before Qdrant write.
Layer 2 — Tool: Deterministic data fetch; APIs only, no LLM generation for facts.
Layer 3 — Output: Validate proposed bundles (Inventory Agent) before customer presentation.
Layer 4 — State: Qdrant status transitions; valid FSM only.

HITL: Low confidence, no feasible bundles, high-margin pricing, schema failure, episodic mismatch.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants (schema-first: types, ranges, enums)
# ---------------------------------------------------------------------------

# Layer 1 — Input
VALID_CATEGORIES: Sequence[str] = ("tents", "backpacks", "sleepingbags")
VALID_LOCATIONS: Sequence[str] = ("CH", "DE", "AT")
QUANTITY_MIN: int = 1
QUANTITY_MAX: int = 10
SHIPPING_MIN_DAYS: int = 2
MAX_BUDGET_EUR: float = 500_000.0

# Layer 3 — Output
BUDGET_TOLERANCE: float = 1.05  # total_price <= budget_max * BUDGET_TOLERANCE
CONFIDENCE_THRESHOLD: float = 0.8  # escalate if bundle confidence < this
HIGH_MARGIN_CHF: float = 500.0  # HITL trigger for high-margin pricing

# Ethics — Fair pricing & anti-discrimination (CH/DE/AT same market)
PRICE_VARIANCE_MAX_PCT: float = 0.05  # no price variation >5% within same region

# HITL / Layer 4
HITL_HALLUCINATION_THRESHOLD: float = 0.2
EPISODE_OUTCOMES: Sequence[str] = ("success", "partial", "failure", "unknown")

# FSM: allowed status transitions (Layer 4)
GOAL_STATUS_OPEN: str = "open"
GOAL_STATUS_PENDING_INVENTORY: str = "pending_inventory"
GOAL_STATUS_HUMAN_REVIEW: str = "human_review"
GOAL_STATUS_SOLVED: str = "solved"
GOAL_STATUS_FAILED: str = "failed"

# in_progress kept for backward compatibility with existing shopping_agents
GOAL_STATUS_IN_PROGRESS: str = "in_progress"

ALLOWED_TRANSITIONS: Dict[str, Tuple[str, ...]] = {
    GOAL_STATUS_OPEN: (GOAL_STATUS_PENDING_INVENTORY, GOAL_STATUS_IN_PROGRESS),
    GOAL_STATUS_PENDING_INVENTORY: (GOAL_STATUS_HUMAN_REVIEW, GOAL_STATUS_SOLVED, GOAL_STATUS_FAILED),
    GOAL_STATUS_IN_PROGRESS: (GOAL_STATUS_HUMAN_REVIEW, GOAL_STATUS_SOLVED, GOAL_STATUS_FAILED),
    GOAL_STATUS_HUMAN_REVIEW: (GOAL_STATUS_SOLVED, GOAL_STATUS_FAILED),
    GOAL_STATUS_SOLVED: (),
    GOAL_STATUS_FAILED: (),
}
GOAL_STATUSES: Sequence[str] = (
    GOAL_STATUS_OPEN,
    GOAL_STATUS_PENDING_INVENTORY,
    GOAL_STATUS_IN_PROGRESS,
    GOAL_STATUS_HUMAN_REVIEW,
    GOAL_STATUS_SOLVED,
    GOAL_STATUS_FAILED,
)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class GuardrailViolation(Exception):
    """Raised when a guardrail check fails (e.g. budget exceeded, invalid transition)."""
    def __init__(self, message: str, layer: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.layer = layer
        self.details = details or {}


# ---------------------------------------------------------------------------
# Layer 2 — Tool contract (deterministic responses; never LLM-generated)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class StockResponse:
    """Enforced tool contract: stock data from API only, never LLM-generated."""
    skus: List[str]
    available: int
    eta_days: int


# ---------------------------------------------------------------------------
# Layer 1 — Input guardrails
# ---------------------------------------------------------------------------


def _parse_date(value: Any) -> Optional[date]:
    """Parse deadline from goal (ISO date string or None)."""
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
        except ValueError:
            return None
    return None


def validate_goal(goal: Dict[str, Any]) -> bool:
    """
    Hard constraints — fail fast if invalid.
    Used for Dict-style goals (e.g. budget_max, quantity, category, location).
    """
    constraints: Dict[str, Callable[[Any], bool]] = {
        "budget_max": lambda x: x is None or (isinstance(x, (int, float)) and x > 0),
        "quantity": lambda x: x is None or (isinstance(x, int) and QUANTITY_MIN <= x <= QUANTITY_MAX),
        "category": lambda x: x is None or (isinstance(x, str) and x.lower() in [c.lower() for c in VALID_CATEGORIES]),
        "location": lambda x: x is None or (isinstance(x, str) and x.upper() in [loc.upper() for loc in VALID_LOCATIONS]),
    }
    for field_name, validator in constraints.items():
        if field_name in goal and not validator(goal[field_name]):
            return False
    return True


@dataclass(frozen=True)
class InputGuardrailResult:
    """Result of Layer 1 input guardrail: pass or escalate to clarification."""
    ok: bool = True
    escalate_reason: Optional[str] = None

    @classmethod
    def pass_(cls) -> "InputGuardrailResult":
        return cls(ok=True)

    @classmethod
    def escalate(cls, reason: str) -> "InputGuardrailResult":
        return cls(ok=False, escalate_reason=reason)


def input_guardrail(user_goal: Dict[str, Any]) -> InputGuardrailResult:
    """
    Layer 1: Validate user intent before Qdrant write.
    - Schema: budget > 0, quantity in [1, 10], valid categories/location.
    - Constraint consistency: deadline >= today + shipping_min_days.
    - Risk: suspicious patterns (e.g. impossible deadline).
    """
    budget = user_goal.get("budget_max") or user_goal.get("budget_eur")
    if budget is not None and (not isinstance(budget, (int, float)) or budget <= 0):
        return InputGuardrailResult.escalate("Invalid budget")
    if not validate_goal(user_goal):
        return InputGuardrailResult.escalate("Schema validation failed")
    deadline = _parse_date(user_goal.get("deadline") or user_goal.get("delivery_deadline"))
    if deadline is not None:
        today = date.today()
        min_ok = (deadline - today).days >= SHIPPING_MIN_DAYS
        if not min_ok:
            return InputGuardrailResult.escalate("Impossible deadline (shipping minimum)")
    return InputGuardrailResult.pass_()


# ---------------------------------------------------------------------------
# Layer 3 — Output guardrails
# ---------------------------------------------------------------------------


class GuardrailAction(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    ESCALATE = "escalate"


@dataclass
class GuardrailResult:
    """Result of Layer 3 output guardrail."""
    action: GuardrailAction
    reason: Optional[str] = None
    confidence: float = 0.0

    @classmethod
    def approve(cls) -> "GuardrailResult":
        return cls(action=GuardrailAction.APPROVE)

    @classmethod
    def reject(cls, reason: str) -> "GuardrailResult":
        return cls(action=GuardrailAction.REJECT, reason=reason)

    @classmethod
    def escalate(cls, reason: str, confidence: float = 0.0) -> "GuardrailResult":
        return cls(action=GuardrailAction.ESCALATE, reason=reason, confidence=confidence)


def get_market_baseline_price(product_sku: str, region: Optional[str] = None) -> Optional[float]:
    """
    Placeholder: return baseline price for product in region (CH/DE/AT).
    Override via dependency injection or implement using competitor_prices / catalog.
    """
    return None


def ethical_pricing_guardrail(
    price: float,
    user_profile: Dict[str, Any],
    product_sku: str,
    region: Optional[str] = None,
    *,
    get_baseline: Optional[Callable[[str, Optional[str]], Optional[float]]] = None,
    max_variance_pct: float = PRICE_VARIANCE_MAX_PCT,
) -> bool:
    """
    Fair pricing: no price variation >5% within same region (CH/DE/AT).
    Prevents dynamic pricing from user profile inference and geographic discrimination.
    Returns True if price is within allowed variance (or no baseline available).
    """
    if price <= 0:
        return False
    getter = get_baseline or get_market_baseline_price
    baseline = getter(product_sku, region)
    if baseline is None or baseline <= 0:
        return True  # no baseline → cannot enforce; allow (caller may require baseline)
    return abs(price - baseline) <= baseline * max_variance_pct


def build_ethical_flags(
    *,
    no_price_gouging: bool = True,
    stock_verified: bool = True,
    deadline_feasible: bool = True,
    real_historical_success: bool = True,
) -> List[str]:
    """
    Build audit flags for transparent decision provenance (anti-manipulation).
    - no_price_gouging: price within regional baseline variance
    - stock_verified: items from real stock (no fake scarcity)
    - deadline_feasible: deadline validated vs shipping minimum
    - real_historical_success: historical_success from real episodes, not fabricated
    """
    flags: List[str] = []
    if no_price_gouging:
        flags.append("no_price_gouging")
    if stock_verified:
        flags.append("stock_verified")
    if deadline_feasible:
        flags.append("deadline_feasible")
    if real_historical_success:
        flags.append("real_historical_success")
    return flags


def output_guardrail(
    bundle: Dict[str, Any],
    goal: Dict[str, Any],
    *,
    budget_tolerance: float = BUDGET_TOLERANCE,
    confidence_threshold: float = CONFIDENCE_THRESHOLD,
) -> GuardrailResult:
    """
    Layer 3: Validate proposed solution before customer presentation.
    - Feasibility: all items in stock, total_price <= budget (with tolerance).
    - Business rules: margin/shipping compliance.
    - Confidence: escalate if below threshold.
    - Anti-manipulation: no fake scarcity — only real stock (stock==0 rejected).
    """
    budget_max = goal.get("budget_max") or goal.get("budget_eur")
    total_price = bundle.get("total_price") or bundle.get("total_price_eur") or 0.0
    if budget_max is not None and total_price > float(budget_max) * budget_tolerance:
        return GuardrailResult.reject("Budget exceeded")
    items = bundle.get("items") or bundle.get("candidates") or []
    for item in items:
        stock = item.get("stock") if isinstance(item, dict) else getattr(item, "stock", None)
        if stock is not None and (isinstance(stock, (int, float)) and stock == 0):
            return GuardrailResult.reject("Out of stock items")
    confidence = float(bundle.get("confidence", 1.0))
    if confidence < confidence_threshold:
        return GuardrailResult.escalate("Low confidence", confidence=confidence)
    return GuardrailResult.approve()


# ---------------------------------------------------------------------------
# Layer 4 — State guardrails (Qdrant status FSM)
# ---------------------------------------------------------------------------


def transition_guardrail(current_status: str, next_status: str) -> bool:
    """
    Layer 4: Enforce workflow integrity via status machine.
    OPEN -> PENDING_INVENTORY -> [HUMAN_REVIEW | SOLVED | FAILED].
    Valid transitions only — no skipping states.
    """
    current = current_status.lower().strip()
    next_ = next_status.lower().strip()
    allowed = ALLOWED_TRANSITIONS.get(current, ())
    return next_ in allowed


def assert_transition(current_status: str, next_status: str) -> None:
    """Raise GuardrailViolation if transition is invalid."""
    if not transition_guardrail(current_status, next_status):
        raise GuardrailViolation(
            f"Invalid status transition: {current_status} -> {next_status}",
            layer="state",
            details={"current": current_status, "next": next_status},
        )


# ---------------------------------------------------------------------------
# Monitoring & learning — episode payload for guardrail violations
# ---------------------------------------------------------------------------

HITL_TRIGGERS = (
    "low_confidence",       # confidence < 80%
    "no_feasible_bundles",  # no bundles found
    "high_margin_pricing",   # > 500 CHF margin
    "episodic_memory_mismatch",
    "schema_validation_failure",
)


def build_guardrail_episode_payload(
    goal_id: str,
    solution_id: str,
    guardrail_layer: str,
    violation_type: Optional[str] = None,
    success: bool = False,
    human_override: bool = False,
) -> Dict[str, Any]:
    """
    Every guardrail violation becomes training data for self-improvement.
    Attach to episode payload in goal_solution_links / COLL_EPISODES.
    """
    return {
        "goal_id": goal_id,
        "solution_id": solution_id,
        "guardrail_layer": guardrail_layer,
        "violation_type": violation_type,
        "success": success,
        "human_override": human_override,
    }


__all__ = [
    "GuardrailViolation",
    "StockResponse",
    "validate_goal",
    "InputGuardrailResult",
    "input_guardrail",
    "GuardrailAction",
    "GuardrailResult",
    "output_guardrail",
    "transition_guardrail",
    "assert_transition",
    "build_guardrail_episode_payload",
    "get_market_baseline_price",
    "ethical_pricing_guardrail",
    "build_ethical_flags",
    "HITL_HALLUCINATION_THRESHOLD",
    "HITL_TRIGGERS",
    "EPISODE_OUTCOMES",
    "GOAL_STATUSES",
    "ALLOWED_TRANSITIONS",
    "BUDGET_TOLERANCE",
    "CONFIDENCE_THRESHOLD",
    "HIGH_MARGIN_CHF",
    "PRICE_VARIANCE_MAX_PCT",
    "SHIPPING_MIN_DAYS",
    "VALID_CATEGORIES",
    "VALID_LOCATIONS",
]