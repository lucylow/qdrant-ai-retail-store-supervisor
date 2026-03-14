# Qdrant: Technical Value Mapped to This Codebase

This doc ties the **Qdrant technical/business/societal value** narrative to the Multi-Agent Store Manager implementation so you can reference it for demos and hackathon judging.

---

## 1. Technical Value: Semantic Search (Natural Language → Products)

**Value:** Exact match fails for "lightweight hiking shelter"; vector similarity returns tents.

**In this repo:**

| Concern | Where |
|--------|--------|
| Product embeddings & search | `app/agents/inventory.py`: `InventoryAgent.initial_search()` uses `embed_single(query)` then `client.search(COLL_PRODUCTS, query_vector=..., limit=32)`. |
| Collection | `app/data/collections.py`: `COLL_PRODUCTS` (vector_size=256, COSINE). |
| Embedding model | `app/config.py`: `MODELS.text_embedding_model` (e.g. all-mpnet-base-v2). |

---

## 2. Technical Value: Agent Memory (Shopper ↔ Inventory)

**Value:** Shopper creates goals; Inventory queries products and past bundles; shared memory in Qdrant.

**In this repo:**

| Concern | Where |
|--------|--------|
| Goals | `app/agents/shopper.py`: `ShopperGoal` (goal_id, query, intent, budget_eur, region, urgency_days). Config: `COLLECTIONS.goals`. |
| Products | `app/data/collections.py`: `COLL_PRODUCTS`. |
| Episodes & successful bundles | `app/data/episodic_memory.py`: `EpisodicMemoryStore` (COLL_EPISODES), `retrieve_similar_successful_skus()` for bias. |
| Reasoning graphs | `app/rag/reasoning_graphs.py`: `ReasoningGraphStore` (COLL_REASONING_GRAPHS), `retrieve_similar_graphs()`. |
| Inventory using episodic bias | `app/agents/inventory.py`: `initial_search(..., episodic_skus=...)`; candidates reordered so episodic SKUs rank higher. |

---

## 3. Technical Value: Episodic Learning

**Value:** Store goal → solution → outcome (e.g. purchased, 180 CHF); reuse for similar goals.

**In this repo:**

| Concern | Where |
|--------|--------|
| Recording episodes | `app/data/episodic_memory.py`: `EpisodicMemoryStore.record_episode()` writes to COLL_EPISODES (goal_id, outcome, success_prob, bundle_skus, etc.). |
| Success-weighted vector | Episodes use a small vector (size 4) with success_prob for DOT similarity; used for bias, not direct search. |
| Retrieving successful SKUs | `retrieve_similar_successful_skus(goal_query, k, min_success_prob)` → similar reasoning graphs → goal_ids → scroll episodes → return bundle_skus. |
| Research note | Comment references "92% conversion target" and "23% lift when biasing toward 92% conversion episodes". |

---

## 4. Technical Value: Hybrid Search (Vector + Metadata)

**Value:** e.g. `vector="camping tent" AND price < 200 AND region = Switzerland AND stock > 0` to avoid recommending unavailable items.

**In this repo:**

| Current state | Where |
|---------------|--------|
| Vector search | `app/agents/inventory.py`: `client.search(COLL_PRODUCTS, query_vector=qvec, limit=32)` — no `query_filter` yet. |
| Constraints in app | Budget and product filtering (price, quantity) are applied in Python in `optimize_bundle()` after retrieval. |
| **Enhancement** | Add Qdrant `query_filter` (e.g. `FieldCondition(price_eur < 200)`, `stock > 0`, `region`) so retrieval is already constrained and fewer irrelevant hits are returned. |

---

## 5. Business Value: Conversions, Personalization, Bundling

**Value:** Higher conversion (e.g. 4–6% vs 2–3%), personalized recommendations, intelligent bundling → higher AOV.

**In this repo:**

| Concern | Where |
|--------|--------|
| Semantic search → relevance | Inventory semantic search + episodic bias → better match to intent. |
| Bundling | `app/agents/inventory.py`: `optimize_bundle(goal, ctx)` builds bundle from candidates under budget. |
| User preferences | No dedicated `user_profiles` collection in `app/data/collections.py`; could be added and used for personalization embeddings. |
| Reranking for quality | `app/retriever.py`, `app/retrieval/hybrid/kg_qdrant.py`: cross-encoder reranker (`app/reranker`, `FEATURES.enable_reranker`) for better ordering. |

---

## 6. Multimodal & Multivector

**Value:** Search by text, image, voice; product + image embeddings.

**In this repo:**

| Concern | Where |
|--------|--------|
| Named vectors schema | `app/multimodal/schema.py`: `products_multimodal` with `textvector`, `imagevector`, `audiovector`, `videovector`. |
| Multivector search | `app/multimodal/search.py`: `multimodal_search()` runs one search per modality with `vector_name=name`, then RRF fusion — effectively multivector search. |
| Encoders | `app/multimodal/encoders.py`: `MultimodalProductEncoders` (text, image, audio). |
| Toggle | `app/config.py`: `FEATURES.enable_multimodal`. |

---

## 7. Reranking for Agentic RAG

**Value:** Reranking pipelines improve answer quality and reduce hallucinations.

**In this repo:**

| Concern | Where |
|--------|--------|
| Cross-encoder reranker | `app/reranker/cross_encoder.py`: `ProductionReranker`; `app/reranker.py`: `rerank(query, items, top_k)`. |
| Usage | `app/retriever.py`: rerank after retrieval; `app/retrieval/hybrid/kg_qdrant.py`: KG + Qdrant results fused then reranked. |
| Config | `app/config.py`: `FEATURES.enable_reranker`, `MODELS.cross_encoder_model`. |
| Service | `app/reranker/serve.py`: FastAPI `/rerank` endpoint. |

---

## 8. Collections Summary

| Collection | Purpose |
|------------|---------|
| `products` | Semantic product search (single vector). |
| `products_multimodal` | Text + image + audio + video vectors (named vectors). |
| `goals` | Shopper goals (config present; ensure created if used). |
| `solutions` | Config present. |
| `episodes` | Episodic memory (outcome, bundle_skus, success_prob). |
| `reasoning_graphs` | Agent reasoning graphs for similar-goal retrieval. |
| `competitor_prices` | Pricing signals. |

---

## Next Steps: Three Advanced Qdrant Capabilities

1. **Multivector search**  
   You already have the schema and RRF-based multivector search in `app/multimodal/search.py`. Possible upgrades: use Qdrant’s native multi-vector API (e.g. batch or named-vector search) for fewer round-trips, and add filter support (price, region, stock) to multimodal search.

2. **Reranking pipelines for agentic RAG**  
   You already use a cross-encoder after retrieval. Possible upgrades: integrate reranker into the agent loop (e.g. after each tool’s retrieval), add a Qdrant-side reranker if you use Qdrant’s pipeline API, or add self-improving reranker (you have `app/rag/self_improving.py` and `app/reranker/hard_negatives.py`).

3. **Distributed Qdrant for scale**  
   Currently single client in `app/qdrant_client.py`. For the narrative: document that moving to Qdrant Cloud or a clustered setup would scale the same collections and queries for large-scale ecommerce (more products, more concurrent agents, higher throughput).

If you want, we can (a) implement one of these (e.g. metadata filters in inventory search, or reranker in the supervisor flow), or (b) turn this into a one-page “Qdrant value” summary for your hackathon submission.
