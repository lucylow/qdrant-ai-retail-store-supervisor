"""
Prompt templates for memory-enhanced Shopper and Inventory agents.
"""

from __future__ import annotations

SHOPPER_SYSTEM = """You are Shopper. Use the following memory/context to extract a structured goal JSON or ask a one-sentence clarification.

SHORT_TERM_CONTEXT:
{short_term_context}

USER_PROFILE:
{user_profile_summary}

PAST_SUCCESS_EXAMPLES:
{episodic_summaries}

CURRENT_MESSAGE:
{user_message}

OUTPUT:
Return ONLY JSON. If ambiguous, return {{"clarify": true, "clarification": "one question"}}
Else return:
{{
  "goal_text": "...",
  "budget": <number|null>,
  "currency": "EUR",
  "delivery_days": <int|null>,
  "region": "string or null",
  "preferences": {{}},
  "user_id": "{user_id}"
}}
"""

INVENTORY_SYSTEM = """You are Inventory. Build up to 3 feasible solution bundles for this GOAL using the product snippets and precedents. Follow hard rules: drop any product with stock==0 and ensure region matches the goal region unless the procedural pattern allows relaxation.

GOAL:
{goal_json}

EPISODIC_PRECEDENTS:
{episodic_summaries}

PRODUCT_SNIPPETS (sku, name, stock, price, attrs):
{product_snippets}

MATCHING_PROCEDURAL_PATTERN:
{procedural_pattern}

TASK:
Return JSON array of bundles:
[
  {{"bundle_id": 1, "skus": ["SKU1", "SKU2"], "total_price": <float>, "feasible": true, "score": 0.0-1.0, "rationale": "..."}},
  ...
]
"""


def build_shopper_prompt(
    short_term_context: str,
    user_profile_summary: str,
    episodic_summaries: str,
    user_message: str,
    user_id: str,
) -> str:
    return SHOPPER_SYSTEM.format(
        short_term_context=short_term_context,
        user_profile_summary=user_profile_summary,
        episodic_summaries=episodic_summaries,
        user_message=user_message,
        user_id=user_id,
    )


def build_inventory_prompt(
    goal_json: str,
    episodic_summaries: str,
    product_snippets: str,
    procedural_pattern: str,
) -> str:
    return INVENTORY_SYSTEM.format(
        goal_json=goal_json,
        episodic_summaries=episodic_summaries,
        product_snippets=product_snippets,
        procedural_pattern=procedural_pattern,
    )
