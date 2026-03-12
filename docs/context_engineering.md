## Context Engineering Architecture

This document describes the context-engineering layer added to `multi_agent_store_supervisor_v5_hybrid_rag`. The goal is to make retrieval and generation **grounded, concise, and auditable** via an explicit context lifecycle:

capture → profile → retrieve → score → compress → assemble → deliver.

### Components

- **`app.context_manager`**: core orchestrator:
  - `build_profile(context_input)` – normalize user/agent/task/product/policy into a profile.
  - `rewrite_query(profile, query)` – derives a retrieval query plus optional expansions.
  - `score_documents(retrieved, profile, query)` – provenance-aware score adjustment.
  - `select_documents_by_budget` – greedily selects docs under a token budget.
  - `compress_documents` – summarizes documents for dense, factual context.
  - `assemble_prompt` – builds the final prompt with explicit `[n]` citations.
  - `build_context_for_query` – high-level entrypoint used by agents and services.

- **`app.context_chain`**:
  - `chain_retrieve(profile, question, hops, collection)` – optional multi-hop retrieval used when `profile["task"]["multi_hop"]` is true.

- **`app.context_cache`**:
  - Caches assembled context objects keyed by a document-fingerprint to avoid redundant summarization work.

- **`app.generator.rag_answer`**:
  - End-to-end helper for agents and HTTP endpoints:
    - calls `build_context_for_query`,
    - sends the assembled prompt to the LLM,
    - extracts `[n]` citations and maps them back to provenance metadata.

- **Debugging**:
  - `app.debug_endpoints` exposes `/debug/context` to inspect assembled prompts.

### Configuration

Context settings live in `app.config.CONTEXT`:

- **`max_total_tokens`**: approximate token budget reserved for context.
- **`max_context_documents`**: max number of documents to include.
- **`min_document_score`**: lower bound for document scores (currently advisory).
- **`dense_summary_model`**: logical placeholder for a summarization backend.
- **`context_fingerprint_ttl`**: TTL in seconds for cached context entries.
- **`query_expansion_model`**: logical identifier for query-expansion behavior.
- **`hard_negative_margin`**: reserved for future hard-negative mining.
- **`provenance_weight`**: multiplicative boost for documents from trusted sources.

Tune these via environment variables (e.g. `CONTEXT_MAX_TOTAL_TOKENS`, `MAX_CONTEXT_DOCS`).

### How Context Is Built

1. **Profile building**
   - Input: `context_input` dict that may contain `user`, `agent`, `task`, `product`, `policy`, `persona`, `collection`.
   - Derived fields:
     - `region` – from user or product, default `"global"`.
     - `language` – from user, default `"en"`.

2. **Query rewriting & expansion**
   - Concatenates original query with product title and task intent.
   - Uses the LLM (via `app.llm_client.generate`) to generate a **comma-separated set of search phrases**.
   - First phrase becomes the primary rewritten query; remaining phrases are stored as `_query_expansions` for multi-query retrieval.

3. **Retrieval (single-hop or multi-hop)**
   - Default: `app.retriever.retrieve(rewritten, collection=context_input["collection"])`.
   - Multi-hop: when `context_input["task"]["multi_hop"]` is truthy:
     - `app.context_chain.chain_retrieve` runs:
       - initial query on the question,
       - extracts entities from top docs,
       - re-queries each entity and aggregates results.

4. **Scoring & selection**
   - `score_documents` computes an adjusted score based on:
     - base similarity score from Qdrant (`score`),
     - lexical overlap between query and doc text,
     - provenance match to any `policy["trusted_sources"]`,
     - recency (mild boost for documents younger than 7 days).
   - `select_documents_by_budget` greedily chooses documents sorted by `adj_score` while staying under:
     - `CONTEXT["max_total_tokens"]`, and
     - `CONTEXT["max_context_documents"]`.

5. **Compression**
   - `compress_document_text` uses the generic LLM client to summarize each document to `per_doc_tokens` (derived from the global budget).
   - Compressed text is stored in the document payload as `_compressed_text`.

6. **Prompt assembly**
   - Each compressed doc is prefixed with `[i]` where `i` is the passage index.
   - The profile is rendered as a small header (persona, region, policy flags).
   - The system prompt adds **strict grounding instructions**:
     - Answer only using facts in the context passages.
     - Include citations like `[0]` for each factual claim.
     - Respond with an explicit “I don't have sufficient information…” if the context is insufficient.
   - `metadata.doc_index_map` stores, for each `i`:
     - `id`, `source`, `source_url`, and `score`.

7. **Caching via fingerprints**
   - When documents are selected, their ids are hashed into a fingerprint.
   - If a cached entry exists for the fingerprint, the context is reused.
   - Otherwise, the new context object is stored in `app.context_cache` with a TTL.

### Debugging

- Start the API (after seeding data and installing dependencies), then call:
  - `GET /debug/context?q=return+policy+tent&region=Zurich`
  - Response includes:
    - `prompt_preview`: the first 2000 characters of the assembled prompt.
    - `metadata`: doc index map, fingerprint, token estimates.
    - `selected_docs`: ids and scores of selected documents.

Use this to:

- Verify that the right documents are being retrieved.
- Confirm that profile fields (e.g. `region`) are influencing selection.
- Inspect citation indices and their associated sources.

### Evaluation Harness

The evaluation script **`scripts/evaluate_contexts.py`** measures three key metrics:

- **Grounded fraction**: proportion of queries for which at least one provenance id matches the provided `gold_docs`.
- **Average number of contexts**: how many passages are typically included.
- **Average estimated tokens**: rough token cost of the selected context.

Usage:

```bash
python scripts/evaluate_contexts.py scripts/sample_queries.json
```

Where `scripts/sample_queries.json` has entries of the form:

```json
{
  "query": "What's the return policy for tent TENT_221?",
  "gold_docs": ["doc-id-1", "doc-id-2"],
  "user": { "region": "Zurich" }
}
```

The script writes `context_eval_results.json` with per-query diagnostics.

### Tests

Unit tests in `tests/test_context_manager.py` cover:

- Profile building (region propagation).
- Basic query rewriting without expansion.
- Deterministic fingerprints for identical item lists.
- Compression that shortens long texts.

Run:

```bash
pytest -q tests/test_context_manager.py
```

### Troubleshooting

- **No documents selected**:
  - Check that the collection name passed to `build_context_for_query` is correct.
  - Confirm Qdrant is running and collections are seeded.

- **Answers lack citations**:
  - Inspect `/debug/context` to ensure passages are correctly numbered and the prompt instructions are present.
  - Verify that your LLM respects bracketed citation patterns (e.g. `[0]`).

- **High token usage**:
  - Lower `CONTEXT_MAX_TOTAL_TOKENS` or `MAX_CONTEXT_DOCS`.
  - Reduce `per_doc_tokens` by decreasing the global budget or increasing the number of documents modestly.

This layer is intentionally generic so you can plug in different retrievers, rerankers, and LLM providers while keeping **profiles**, **compression**, and **provenance** behavior consistent.

