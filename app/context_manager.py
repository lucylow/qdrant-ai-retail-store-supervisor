from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence

import hashlib
import json
import os
import time

import redis

from app.config import CONTEXT


_redis_client: redis.Redis | None = None


def _get_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=0,
        )
    return _redis_client


@dataclass(frozen=True)
class ContextChunk:
    id: str
    text: str
    score: float
    source: str


@dataclass(frozen=True)
class ManagedContext:
    text: str
    chunks: list[ContextChunk]
    fingerprint: str


def _fingerprint(query: str, chunk_ids: Sequence[str]) -> str:
    payload = {"q": query, "ids": list(chunk_ids)}
    raw = json.dumps(payload, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _cache_key(fingerprint: str) -> str:
    return f"ctx:{fingerprint}"


def load_cached_context(fingerprint: str) -> ManagedContext | None:
    r = _get_redis()
    raw = r.get(_cache_key(fingerprint))
    if not raw:
        return None
    data = json.loads(raw)
    chunks = [
        ContextChunk(
            id=item["id"],
            text=item["text"],
            score=float(item["score"]),
            source=item["source"],
        )
        for item in data["chunks"]
    ]
    return ManagedContext(text=data["text"], chunks=chunks, fingerprint=fingerprint)


def save_context(ctx: ManagedContext) -> None:
    r = _get_redis()
    payload = {
        "text": ctx.text,
        "chunks": [
            {
                "id": c.id,
                "text": c.text,
                "score": c.score,
                "source": c.source,
            }
            for c in ctx.chunks
        ],
        "ts": time.time(),
    }
    r.setex(
        _cache_key(ctx.fingerprint),
        CONTEXT.context_fingerprint_ttl_s,
        json.dumps(payload),
    )


def build_context(query: str, chunks: Sequence[ContextChunk]) -> ManagedContext:
    """
    Simple budgeted context builder that truncates to token budget heuristically.
    """
    sorted_chunks = sorted(chunks, key=lambda c: c.score, reverse=True)[
        : CONTEXT.max_context_documents
    ]
    texts: list[str] = []
    budget = CONTEXT.max_total_tokens
    for chunk in sorted_chunks:
        est_tokens = max(1, len(chunk.text.split()) // 0.75)
        if budget - est_tokens <= 0:
            break
        texts.append(chunk.text)
        budget -= est_tokens
    joined = "\n\n".join(texts)
    fp = _fingerprint(query, [c.id for c in sorted_chunks])
    ctx = ManagedContext(text=joined, chunks=sorted_chunks, fingerprint=fp)
    save_context(ctx)
    return ctx


__all__ = ["ContextChunk", "ManagedContext", "build_context", "load_cached_context"]

"""
Context Manager for Agentic RAG.

Responsibilities:
- Build context profiles (user, agent, task, product, policy).
- Rewrite and expand queries for robust retrieval.
- Score & rank retrieved documents with provenance awareness.
- Compress selected documents to fit token budgets.
- Assemble final prompt context with citation anchors.
"""

from typing import List, Dict, Any, Tuple
import hashlib
import time
import logging

from app.embeddings import embed_texts  # kept for future extensions
from app.config import CONTEXT
from app.retriever import retrieve
from app.generation.prompt_templates import build_prompt
from app.llm_client import generate
from app.context_cache import get_cache, set_cache
from app.context_chain import chain_retrieve

logger = logging.getLogger(__name__)


def fingerprint_context(items: List[str]) -> str:
    h = hashlib.sha256()
    for it in items:
        h.update(str(it).encode("utf-8"))
    return h.hexdigest()


def token_length_estimate(text: str) -> int:
    # very rough: 1 token ≈ 4 chars (GPT-style).
    return max(1, len(text) // 4)


def build_profile(context_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build an explicit profile for the retrieval & generation step.
    """
    profile: Dict[str, Any] = {
        "user": context_input.get("user", {}),
        "agent": context_input.get("agent", {"name": "default"}),
        "task": context_input.get("task", {}),
        "product": context_input.get("product", {}),
        "policy": context_input.get("policy", {}),
        "persona": context_input.get("persona", {}),
        "timestamp": int(time.time()),
    }
    profile["region"] = (
        profile["user"].get("region")
        or profile["product"].get("region")
        or "global"
    )
    profile["language"] = profile["user"].get("lang") or "en"
    if "collection" in context_input:
        profile["collection"] = context_input["collection"]
    return profile


def rewrite_query(profile: Dict[str, Any], query: str, expansion: bool = True) -> str:
    """
    Lightweight rewrite for clarity + optional expansion.
    """
    parts = [query]
    product = profile.get("product") or {}
    task = profile.get("task") or {}
    if product.get("title"):
        parts.append(product["title"])
    if task.get("intent"):
        parts.append(task["intent"])
    base = " | ".join(parts)

    if not expansion:
        return base

    try:
        prompt = (
            "Rewrite and expand this search query to include product, task, and region "
            "signals. Be concise.\n\nQuery: "
            f"{base}\n\nReturn a comma-separated list of search phrases."
        )
        out = generate(prompt, max_tokens=64, temperature=0.0)
        candidates = [s.strip() for s in out.replace("\n", ",").split(",") if s.strip()]
        if candidates:
            rewritten = candidates[0]
            profile["_query_expansions"] = candidates[1:]
            logger.debug("rewrite_query expansions=%s", candidates)
            return rewritten
    except Exception as e:
        logger.debug("rewrite_query LLM rewrite failed: %s", e)
    return base


def _overlap(q: str, text: str) -> float:
    qset = set(q.lower().split())
    tset = set((text or "").lower().split())
    if not qset or not tset:
        return 0.0
    return len(qset & tset) / len(qset)


def score_documents(
    retrieved: List[Dict[str, Any]],
    profile: Dict[str, Any],
    query: str,
) -> List[Dict[str, Any]]:
    """
    Adjust scores based on provenance, recency and lexical overlap.
    """
    trusted_sources = set(profile.get("policy", {}).get("trusted_sources", []))
    out: List[Dict[str, Any]] = []

    for r in retrieved:
        payload = r.get("payload") or {}
        text = payload.get("text", "") or ""
        base_score = float(r.get("score") or 0.0)
        o = _overlap(query, text)
        adj = base_score + 0.1 * o
        reasons = [f"base:{base_score:.3f}", f"overlap:{o:.3f}"]

        src = payload.get("source")
        if src and src in trusted_sources:
            adj *= CONTEXT.get("provenance_weight", 1.2)
            reasons.append("trusted_source")

        ts = payload.get("ts")
        if ts:
            age_days = (time.time() - ts) / (60 * 60 * 24)
            if age_days < 7:
                adj += 0.05
                reasons.append("recent")

        out.append({**r, "adj_score": adj, "score_reasons": reasons})

    out.sort(key=lambda x: x["adj_score"], reverse=True)
    return out


def select_documents_by_budget(
    scored_docs: List[Dict[str, Any]],
    token_budget: int,
    max_docs: int,
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Greedy selection over adj_score until budget or max_docs hit.
    """
    selected: List[Dict[str, Any]] = []
    tokens_used = 0
    for d in scored_docs:
        text = (d.get("payload") or {}).get("text", "") or ""
        est = token_length_estimate(text)
        if tokens_used + est > token_budget:
            continue
        selected.append(d)
        tokens_used += est
        if len(selected) >= max_docs:
            break
    return selected, tokens_used


def compress_document_text(text: str, target_tokens: int = 150) -> str:
    """
    Use the LLM to compress text to approximately target_tokens.
    """
    try:
        prompt = (
            f"Summarize the following passage in <= {max(20, target_tokens)} tokens, "
            "preserving factual statements and key numbers. Return the summary only.\n\n"
            f"PASSAGE:\n{text}"
        )
        summary = generate(prompt, max_tokens=max(32, target_tokens // 2), temperature=0.0)
        if not summary or not summary.strip():
            return " ".join(text.split()[: target_tokens * 4])
        return summary.strip()
    except Exception as e:
        logger.debug("compress_document_text fallback: %s", e)
        return " ".join(text.split()[: target_tokens * 4])


def compress_documents(
    selected_docs: List[Dict[str, Any]],
    per_doc_tokens: int = 150,
) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for d in selected_docs:
        payload = dict(d.get("payload") or {})
        txt = payload.get("text", "") or ""
        compressed = compress_document_text(txt, target_tokens=per_doc_tokens)
        payload["_compressed_text"] = compressed
        out.append(
            {
                **d,
                "payload": payload,
                "compressed_tokens": token_length_estimate(compressed),
            }
        )
    return out


def assemble_prompt(
    question: str,
    compressed_docs: List[Dict[str, Any]],
    profile: Dict[str, Any],
    system_prompt: str | None = None,
) -> Tuple[str, Dict[str, Any]]:
    """
    Build the final prompt for the generator, with explicit citations.
    """
    contexts: List[str] = []
    doc_index_map: Dict[int, Dict[str, Any]] = {}

    for i, d in enumerate(compressed_docs):
        payload = d.get("payload") or {}
        text = payload.get("_compressed_text") or payload.get("text", "") or ""
        contexts.append(f"[{i}] {text}")
        doc_index_map[i] = {
            "id": d.get("id"),
            "source": payload.get("source"),
            "source_url": payload.get("source_url"),
            "score": d.get("adj_score"),
        }

    profile_lines: List[str] = []
    persona = (profile.get("persona") or {}).get("short") or ""
    if persona:
        profile_lines.append(f"Persona: {persona}")
    region = profile.get("region")
    if region:
        profile_lines.append(f"Region: {region}")
    policy_flags = (profile.get("policy") or {}).get("flags") or []
    if policy_flags:
        profile_lines.append(f"PolicyFlags: {','.join(policy_flags)}")
    profile_block = "\n".join(profile_lines)

    system = (
        system_prompt
        or "You are a helpful retail assistant. Use only the context passages to answer and cite with [n]."
    )
    context_text = "\n\n".join(contexts)
    full_prompt = (
        f"{system}\n\n"
        f"Profile:\n{profile_block}\n\n"
        "Context passages (each passage is authoritative; cite them exactly using [n]):\n"
        f"{context_text}\n\n"
        f"QUESTION:\n{question}\n\n"
        "INSTRUCTION: Answer only using facts that can be found in the cited passages. "
        "For each factual claim include the citation index e.g. [0]. If you cannot answer "
        "from the passages, say 'I don't have sufficient information to answer.'"
    )
    metadata: Dict[str, Any] = {
        "doc_index_map": doc_index_map,
        "num_contexts": len(contexts),
    }
    return full_prompt, metadata


def build_context_for_query(
    context_input: Dict[str, Any],
    question: str,
    token_budget: int | None = None,
) -> Dict[str, Any]:
    """
    High-level function used by agents:
    - build profile
    - rewrite query
    - run retrieve (optional multi-hop)
    - score and select
    - compress and assemble
    - cache by fingerprint
    """
    profile = build_profile(context_input)
    rewritten = rewrite_query(profile, question)

    if profile.get("task", {}).get("multi_hop"):
        primary = chain_retrieve(
            profile,
            rewritten,
            hops=profile["task"].get("hops", 2),
            collection=context_input.get("collection"),
        )
    else:
        primary = retrieve(rewritten, collection=context_input.get("collection", "products"))

    expansions = profile.get("_query_expansions", [])
    for qexp in expansions:
        try:
            extra = retrieve(qexp, collection=context_input.get("collection", "products"))
            primary.extend(extra)
        except Exception as e:
            logger.debug("expansion retrieve failed for '%s': %s", qexp, e)

    seen: set[str] = set()
    unique: List[Dict[str, Any]] = []
    for r in primary:
        rid = r.get("id")
        if rid in seen:
            continue
        seen.add(rid)
        unique.append(r)

    scored = score_documents(unique, profile, rewritten)
    tot_budget = token_budget or CONTEXT.get("max_total_tokens", 2048)
    max_docs = CONTEXT.get("max_context_documents", 8)

    selected, used = select_documents_by_budget(
        scored,
        token_budget=tot_budget,
        max_docs=max_docs,
    )

    ids_for_fp = [str(d.get("id")) for d in selected]
    fp = fingerprint_context(ids_for_fp) if ids_for_fp else None
    if fp:
        cached = get_cache(fp)
        if cached:
            logger.debug("Context cache hit for fingerprint %s", fp)
            return cached

    per_doc_tokens = max(64, tot_budget // max(1, max_docs) // 2)
    compressed = compress_documents(selected, per_doc_tokens=per_doc_tokens)
    prompt, metadata = assemble_prompt(question, compressed, profile)
    metadata["fingerprint"] = fp
    metadata["tokens_used_est"] = used

    result = {
        "prompt": prompt,
        "metadata": metadata,
        "selected_docs": selected,
        "profile": profile,
    }
    if fp:
        set_cache(fp, result)
    return result


__all__ = [
    "build_profile",
    "rewrite_query",
    "fingerprint_context",
    "compress_document_text",
    "build_context_for_query",
]

