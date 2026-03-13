from __future__ import annotations

import asyncio

import numpy as np

from app.nlp_pipeline import SwissRetailNLP


def test_swiss_dairy_intent_minimal_nlp() -> None:
    """
    Basic guardrail: language detection + embedding + structured goal stub.

    This exercises the Phase 1 NLP pipeline (BGE-M3 + langdetect) on a
    representative Coop dairy query.
    """
    nlp = SwissRetailNLP()
    query = "Bio-Milch laktosefrei Zürich HB"
    result = asyncio.run(nlp.process(query, tenant="coop"))

    assert result["structured_goal"]["tenant"] == "coop"
    assert result["structured_goal"]["raw_query"] == query
    # langdetect returns IETF codes (e.g. 'de' for German)
    assert result["language"] in {"de", "de-DE", "unknown"}
    assert result["confidence"] > 0.70

    emb = np.array(result["embedding"], dtype="float32")
    # BGE-M3 embeddings are non-trivial vectors with reasonable norm
    assert emb.ndim == 1
    assert emb.size > 100
    assert float(np.linalg.norm(emb)) > 0.1


def test_cross_lingual_embedding_similarity() -> None:
    """
    Cross-lingual sanity check: German vs French version of the same dairy
    query should be closer to each other than to an unrelated electronics
    query in embedding space.
    """
    nlp = SwissRetailNLP()
    de_query = "Bio-Milch laktosefrei Zürich HB"
    fr_query = "Lait bio sans lactose Zurich HB"
    other_query = "Gaming Laptop 16GB RAM Zürich"

    de_res = asyncio.run(nlp.process(de_query, tenant="coop"))
    fr_res = asyncio.run(nlp.process(fr_query, tenant="coop"))
    other_res = asyncio.run(nlp.process(other_query, tenant="galaxus"))

    de_vec = np.array(de_res["embedding"], dtype="float32")
    fr_vec = np.array(fr_res["embedding"], dtype="float32")
    other_vec = np.array(other_res["embedding"], dtype="float32")

    def cosine(a, b) -> float:
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    dairy_xlingual = cosine(de_vec, fr_vec)
    dairy_vs_electronics = cosine(de_vec, other_vec)

    # Cross-lingual dairy queries should be substantially closer to each other.
    assert dairy_xlingual > dairy_vs_electronics
    assert dairy_xlingual > 0.4

