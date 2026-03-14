"""
Tool-calling definitions for Apertus agentic flows.

Each tool maps to a real backend function. The Supervisor / agents emit
tool_call JSON; the dispatcher routes to the correct handler.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Callable, Dict, List, Optional

from app.llm.apertus_client import ToolDefinition

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------

RETAIL_TOOLS: List[ToolDefinition] = [
    ToolDefinition(
        name="search_qdrant_products",
        description=(
            "Semantic + hybrid search over the Qdrant products collection. "
            "Returns top-K product matches with sku, name, price, stock, score."
        ),
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Natural-language product query"},
                "limit": {"type": "integer", "default": 10},
                "region": {"type": "string", "description": "Swiss region filter (optional)"},
                "price_lte": {"type": "number", "description": "Max price in CHF (optional)"},
                "stock_gt": {"type": "integer", "description": "Min stock level (optional)"},
            },
            "required": ["query"],
        },
    ),
    ToolDefinition(
        name="search_episodes",
        description=(
            "Search episodic memory for past successful retail flows. "
            "Returns similar goal→bundle→outcome episodes for reasoning."
        ),
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "top_k": {"type": "integer", "default": 5},
                "outcome_filter": {
                    "type": "string",
                    "enum": ["success", "failure", "any"],
                    "default": "success",
                },
            },
            "required": ["query"],
        },
    ),
    ToolDefinition(
        name="check_stock",
        description="Check real-time stock level for a specific SKU at a given store/region.",
        parameters={
            "type": "object",
            "properties": {
                "sku": {"type": "string"},
                "region": {"type": "string", "default": "Zurich"},
            },
            "required": ["sku"],
        },
    ),
    ToolDefinition(
        name="get_holiday_multiplier",
        description=(
            "Return the demand multiplier for a product category on a given date. "
            "Swiss holidays: Christmas 4×, Easter 2.5×, Fondue season 1.5×."
        ),
        parameters={
            "type": "object",
            "properties": {
                "category": {"type": "string"},
                "date": {"type": "string", "format": "date", "description": "ISO date"},
            },
            "required": ["category"],
        },
    ),
    ToolDefinition(
        name="optimize_price",
        description="Run dynamic pricing optimiser for a set of SKUs given competitor context.",
        parameters={
            "type": "object",
            "properties": {
                "skus": {"type": "array", "items": {"type": "string"}},
                "competitor_prices": {
                    "type": "object",
                    "additionalProperties": {"type": "number"},
                    "description": "sku→competitor_price map",
                },
            },
            "required": ["skus"],
        },
    ),
    ToolDefinition(
        name="schedule_pickup",
        description=(
            "Find available pickup windows for a Swiss retail location. "
            "Parses Swiss datetime ('morgen 10h', '14:00') into 08:00-12:00 / 14:00-18:00 slots."
        ),
        parameters={
            "type": "object",
            "properties": {
                "location": {"type": "string"},
                "preferred_time": {"type": "string", "description": "Free-form Swiss time expression"},
                "date": {"type": "string", "format": "date"},
            },
            "required": ["location"],
        },
    ),
    ToolDefinition(
        name="create_twint_payment",
        description="Generate a TWINT QR code for checkout. Returns QR data + payment_id.",
        parameters={
            "type": "object",
            "properties": {
                "amount_chf": {"type": "number"},
                "order_id": {"type": "string"},
                "phone_hash": {"type": "string"},
            },
            "required": ["amount_chf", "order_id"],
        },
    ),
    ToolDefinition(
        name="detect_language",
        description="Detect the language of input text. Returns ISO 639-1 code (de/fr/it/en).",
        parameters={
            "type": "object",
            "properties": {
                "text": {"type": "string"},
            },
            "required": ["text"],
        },
    ),
]

# ---------------------------------------------------------------------------
# Tool dispatcher
# ---------------------------------------------------------------------------

# Handler registry: tool_name → callable(args) → result dict
_HANDLERS: Dict[str, Callable[..., Any]] = {}


def register_tool_handler(name: str, handler: Callable[..., Any]) -> None:
    """Register a backend function as a tool handler."""
    _HANDLERS[name] = handler


def dispatch_tool_call(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool call and return the result."""
    handler = _HANDLERS.get(tool_name)
    if handler is None:
        logger.warning("No handler registered for tool: %s", tool_name)
        return {"error": f"Unknown tool: {tool_name}"}
    try:
        result = handler(**arguments)
        return {"result": result} if not isinstance(result, dict) else result
    except Exception as e:
        logger.exception("Tool %s failed: %s", tool_name, e)
        return {"error": str(e)}


def dispatch_tool_calls(tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Dispatch a batch of tool calls from an LLM response."""
    results = []
    for tc in tool_calls:
        func = tc.get("function", tc)
        name = func.get("name", "")
        args_raw = func.get("arguments", "{}")
        if isinstance(args_raw, str):
            try:
                args = json.loads(args_raw)
            except json.JSONDecodeError:
                args = {}
        else:
            args = args_raw
        result = dispatch_tool_call(name, args)
        results.append({
            "tool_call_id": tc.get("id", ""),
            "name": name,
            "result": result,
        })
    return results


# ---------------------------------------------------------------------------
# Default handler registrations (lazy-loaded to avoid circular imports)
# ---------------------------------------------------------------------------

def _register_defaults() -> None:
    """Wire up real backend functions as tool handlers."""
    try:
        from app.services.holiday_inventory import get_holiday_multiplier
        register_tool_handler("get_holiday_multiplier", get_holiday_multiplier)
    except ImportError:
        pass

    try:
        from langdetect import detect as _detect_lang
        register_tool_handler("detect_language", lambda text: {"language": _detect_lang(text)})
    except ImportError:
        pass

    # Stub handlers for demo — replace with real implementations
    def _stub_search_products(query: str, limit: int = 10, **kw: Any) -> Dict[str, Any]:
        return {"products": [], "query": query, "note": "stub — wire to Qdrant"}

    def _stub_search_episodes(query: str, top_k: int = 5, **kw: Any) -> Dict[str, Any]:
        return {"episodes": [], "query": query, "note": "stub"}

    def _stub_check_stock(sku: str, region: str = "Zurich") -> Dict[str, Any]:
        return {"sku": sku, "region": region, "stock": -1, "note": "stub"}

    def _stub_optimize_price(skus: List[str], **kw: Any) -> Dict[str, Any]:
        return {"prices": {s: 0.0 for s in skus}, "note": "stub"}

    def _stub_schedule_pickup(location: str, **kw: Any) -> Dict[str, Any]:
        return {"location": location, "windows": ["08:00-12:00", "14:00-18:00"], "note": "stub"}

    def _stub_twint(amount_chf: float, order_id: str, **kw: Any) -> Dict[str, Any]:
        return {"qr_data": f"twint://pay?amount={amount_chf}&id={order_id}", "status": "pending"}

    for name, fn in [
        ("search_qdrant_products", _stub_search_products),
        ("search_episodes", _stub_search_episodes),
        ("check_stock", _stub_check_stock),
        ("optimize_price", _stub_optimize_price),
        ("schedule_pickup", _stub_schedule_pickup),
        ("create_twint_payment", _stub_twint),
    ]:
        if name not in _HANDLERS:
            register_tool_handler(name, fn)


_register_defaults()


__all__ = [
    "RETAIL_TOOLS",
    "ToolDefinition",
    "register_tool_handler",
    "dispatch_tool_call",
    "dispatch_tool_calls",
]
