from __future__ import annotations

from fastapi import APIRouter, HTTPException

from agents.response_generator import MultilingualResponseGenerator
from agents.shopper_agent import MultilingualShopperAgent

router = APIRouter(prefix="/chat", tags=["multilingual"])


@router.post("/swiss")
async def multilingual_chat(query: str, tenant: str = "coop", region: str | None = None):
    """
    DE/FR/IT/EN → BGE-M3 → Qdrant search → bundle response in user language.
    """
    if not query:
        raise HTTPException(status_code=400, detail="query must not be empty")

    shopper = MultilingualShopperAgent()
    result = await shopper.process_query(query=query, tenant=tenant, region=region)

    response_gen = MultilingualResponseGenerator()
    final_response = response_gen.generate_response(
        solution=result.solution,
        detected_lang=result.detected_language,
        tenant=tenant,
    )

    return {
        "detected_language": result.detected_language,
        "original_query": result.query_original,
        "response": final_response,
        "confidence": result.confidence,
        "structured_goal": result.structured_goal,
    }

