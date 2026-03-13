"""
4-Layer Defense: Appropriate GenAI usage with deterministic guardrails.

Prevents LLM overreach and ensures production-safe behavior. Research-backed:
HITL <8% of goals need human review when these layers are applied.

Layer 1 — Input: Schema validation (budget>0, valid categories/regions).
    Applied in: ShopperAgent.parse_goal → _validate_goal_schema.
    Intent only; no business logic in LLM output.

Layer 2 — Tools: MCP/APIs only; no LLM generation for tool results.
    Inventory/pricing use Qdrant and external APIs; ranking is deterministic
    or confidence-scored with inventory APIs as source of truth.

Layer 3 — Output: Feasibility checks (stock, price constraints, policy).
    Applied in: AuditAgent.evaluate_plan + safety.validate_solution_against_policies.
    Bundle must respect budget; prices must pass brand policy.

Layer 4 — State: Qdrant status transitions; no skipping states.
    Reasoning graphs and episodic memory use defined outcomes (success/partial/failure).
    Workflow state machine enforced via payload filtering in Qdrant.

HITL: Goals with hallucination_score > HITL_HALLUCINATION_THRESHOLD are flagged
for human review (AuditResult.needs_human_review).
"""

from __future__ import annotations

# Re-export threshold for consistency (audit uses this)
HITL_HALLUCINATION_THRESHOLD: float = 0.2

# Valid workflow states for episodic/blackboard (Layer 4)
EPISODE_OUTCOMES = ("success", "partial", "failure", "unknown")
GOAL_STATUSES = ("open", "in_progress", "solved", "failed")

__all__ = [
    "HITL_HALLUCINATION_THRESHOLD",
    "EPISODE_OUTCOMES",
    "GOAL_STATUSES",
]
