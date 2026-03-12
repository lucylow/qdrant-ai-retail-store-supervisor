from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.context_manager import build_context_for_query

router = APIRouter()


@router.get("/context")
def debug_context(q: str, region: str = "global"):
    """
    Inspect assembled context for a given query.
    """
    profile_in = {
        "user": {"region": region},
        "agent": {"name": "debug"},
        "collection": "products",
    }
    ctx = build_context_for_query(profile_in, q)
    md = ctx["metadata"]
    selected_docs = [
        {"id": d.get("id"), "score": d.get("adj_score")}
        for d in ctx.get("selected_docs", [])
    ]
    return JSONResponse(
        {
            "prompt_preview": ctx["prompt"][:2000],
            "metadata": md,
            "selected_docs": selected_docs,
        }
    )

