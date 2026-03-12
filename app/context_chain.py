"""
Multi-hop retrieval support for complex queries.
"""

from typing import List, Dict, Any
import logging

from app.retriever import retrieve
from app.llm_client import generate

logger = logging.getLogger(__name__)


def extract_entity_queries(answer_text: str) -> List[str]:
    """
    Extract entity-like strings (product IDs, SKUs, key phrases) using the LLM when available.
    Falls back to a simple regex heuristic.
    """
    try:
        prompt = (
            "Extract up to 6 named entities, product SKUs, and short key phrases from "
            "the text. Return them as a comma-separated list.\n\nText:\n"
            f"{answer_text}"
        )
        out = generate(prompt, max_tokens=64, temperature=0.0)
        items = [s.strip() for s in out.replace("\n", ",").split(",") if s.strip()]
        return items[:6]
    except Exception:
        import re

        return re.findall(r"\\b[A-Z0-9]{3,}\\b", answer_text)[:6]


def chain_retrieve(
    profile: Dict[str, Any],
    question: str,
    hops: int = 2,
    collection: str | None = None,
) -> List[Dict[str, Any]]:
    """
    Iterative retrieval:
    - first hop: retrieve on the original question
    - next hops: extract entities from top docs and re-query
    Returns a deduplicated list of documents.
    """
    collection = collection or profile.get("collection") or "products"
    all_docs: List[Dict[str, Any]] = []

    q0 = question
    docs = retrieve(q0, collection=collection, top_k=20)
    all_docs.extend(docs)

    curr_text = " ".join(d.get("payload", {}).get("text", "") for d in docs[:3])

    for _hop in range(1, max(1, hops)):
        entities = extract_entity_queries(curr_text)
        if not entities:
            break
        for ent in entities:
            try:
                more = retrieve(ent, collection=collection, top_k=10)
                all_docs.extend(more)
            except Exception as e:
                logger.debug("chain_retrieve step failed for %s: %s", ent, e)
        curr_text = " ".join(d.get("payload", {}).get("text", "") for d in all_docs[:6])

    seen: set[str] = set()
    unique: List[Dict[str, Any]] = []
    for d in all_docs:
        did = d.get("id")
        if did in seen:
            continue
        seen.add(did)
        unique.append(d)
    return unique

