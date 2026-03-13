## AI Retail Store Supervisor – Backend & Business Architecture Map

This document maps the existing backend (agents, Qdrant collections, and memory patterns) to the planned business and monetization entities. It is **descriptive only** – no runtime behavior is changed.

---

## 1. Current Backend Overview

- **Framework / entrypoint**
  - `app.main:app` – FastAPI app exposing:
    - `GET /health` (Qdrant health)
    - Product / episode / goal retrieval endpoints (RAG‑style search, not enumerated exhaustively here)
    - Routers:
      - `app.debug_endpoints.router` mounted under `/debug`
      - `app.multimodal.router` for visual / multimodal search
  - `Dockerfile` and `Makefile` run `uvicorn app.main:app` as the primary backend.

- **Qdrant client & collection bootstrap**
  - `app.qdrant_client` – central Qdrant adapter:
    - `get_qdrant_client()` – resilient client creation with health check
    - `ensure_collection()` / `ensure_named_vectors_collection()` – idempotent collection creation with HNSW tuning
    - `qdrant_health_check()` – used by `/health`
  - `app.data.collections.ensure_all_collections()` – creates core collections and semantic cache on startup.

- **Core multi‑agent orchestration**
  - `app.agents.supervisor.SupervisorAgent` (autonomous orchestrator):
    - Coordinates:
      - `ShopperAgent`
      - `InventoryAgent`
      - `PricingAgent`
      - `MerchandisingAgent`
      - `AuditAgent`
    - Persists:
      - Reasoning graphs (`ReasoningGraphStore`)
      - Episodic episodes (`EpisodicMemoryStore`)
    - Computes high‑level metrics (conversion rate, episode reuse rate).
  - Other supervisor variants in the same module:
    - Legacy/simple `SupervisorAgent` and `Supervisor` pipeline helper (orchestrating generic `Agent` implementations with retries, metrics and observability).

- **Specialized agents (non‑exhaustive, but key for monetization)**
  - `ShopperAgent` (`app.agents.shopper`):
    - Extracts structured `ShopperGoal` (intent, budget, region, urgency).
    - Has a memory‑augmented variant `parse_goal_with_memory` that:
      - Reads / writes short‑term conversation memory.
      - Pulls user profile and episodic goal‑solution episodes.
      - Uses an LLM wrapper (`app.llm_client`) to parse to JSON.
  - `InventoryAgent`, `MerchandisingAgent`, `PricingAgent`, `AuditAgent`, `AnalyticsAgent`, etc.:
    - Implement inventory search / bundle optimization, pricing optimization, merchandising content, safety / hallucination guardrails, and analytics.
    - These are the primary candidates for **module‑level monetization** (Inventory, Pricing, Merch, Audit, Forecasting, etc.).

- **Episodic memory, reasoning graphs, and metrics**
  - `app.data.episodic_memory.EpisodicMemoryStore` – episodic episodes backed by Qdrant.
  - `app.rag.reasoning_graphs.{ReasoningGraph, ReasoningGraphStore}` – graph of agent steps (nodes/edges, latency, success probability) stored in Qdrant.
  - `app.metrics` – computes global metrics such as:
    - Conversion rate
    - Episode reuse rate
  - `app.data.memory_events.record_episode_to_memory` – writes compact episodic summaries into a memory collection.

- **Multimodal / visual RAG**
  - `app.multimodal.schema` – defines:
    - `PRODUCTS_MULTIMODAL_COLLECTION` for multimodal product search.
    - Named‑vector configs (e.g., image + text vectors).
  - `app.multimodal.router` – FastAPI router exposing:
    - Visual / multimodal search APIs (candidates for a **VISUAL_RAG** monetized module).
  - `app.data.collections` also wires in:
    - `FASHION_CLIP_COLLECTION` (visual search, CLIP embeddings).
    - `app.multimodal.semantic_cache.ensure_semantic_cache_collection` (semantic cache).

- **Shared memory patterns & blackboard**
  - Described in `docs/MULTI_AGENT_SHARED_MEMORY.md`:
    - `app.data.blackboard` – goal blackboard (central task board).
    - `app.data.goal_solution_links` – episodic goal→solution→outcome links.
    - `app.data.solutions_store` – per‑goal candidate solutions.
    - `app.data.product_search` – filtered product search and recommend.
    - `app.data.memory_collections` – defines and bootstraps memory collections.
    - `app.data.user_profiles`, `app.data.short_term_memory` – user and session context stores.

---

## 2. Current Qdrant Collections & Memory Layout

### 2.1 Core collections (`app.data.collections`)

- **`COLL_PRODUCTS` (`products`)**
  - Purpose: product catalog, filtered search (stock, region, price, category).
  - Vector: product embeddings (dimension 256, cosine).
  - Key payloads (per `MULTI_AGENT_SHARED_MEMORY.md`): `sku`, `stock`, `region`, `price`, `price_eur`, `last_updated`, `category`.

- **`COLL_GOALS` (`goals`)**
  - Purpose: blackboard / central task board for shopper and inventory.
  - Vector: text embeddings of goal text.
  - Key payloads: `goal_id`, `user_id`, `status`, `created_at`, `agent_role`.

- **`COLL_SOLUTIONS` (`solutions`)**
  - Purpose: candidate solutions per goal (bundles, plans).
  - Vector: solution summary embeddings.
  - Key payloads: `goal_id`, `status`, `created_at`.

- **`COLL_EPISODES` (`episodes`)**
  - Purpose: compact episodic statistics (e.g., outcome, margin, success scores).
  - Vector: low‑dimensional vector (size 4, DOT distance) for quick episodic retrieval.
  - Used by `EpisodicMemoryStore` and ROI‑style metrics.

- **`COLL_REASONING_GRAPHS` (`reasoning_graphs`)**
  - Purpose: store `ReasoningGraph` structures (nodes, edges, success prob, latency).
  - Used by supervisor for explainability and visualizations.

- **`COLL_COMPETITOR_PRICES` (`competitor_prices`)**
  - Purpose: pricing agent competitor context (prices, brands, markets).
  - Vector: 32‑dimensional embeddings (cosine).

- **Multimodal + semantic cache**
  - `PRODUCTS_MULTIMODAL_COLLECTION`
    - Named vectors: multimodal product representations (e.g., vision + text).
  - `FASHION_CLIP_COLLECTION`
    - Named vectors: `image`, `text` (CLIP 512d) for fashion visual search.
  - Semantic cache collection
    - Created via `ensure_semantic_cache_collection(client)` for high cache‑hit RAG.

### 2.2 Memory collections (`docs/MULTI_AGENT_SHARED_MEMORY.md` + `app.data.memory_collections`)

- **`goal_solution_links`**
  - Purpose: episodic memory linking goal → solution → outcome.
  - Payloads: `goalId`, `userId`, `solutionId`, `outcome`, `success`, `score`, `region`, `category`, `created_at`.
  - Used by:
    - `app.data.goal_solution_links.search_similar(...)` for episodic recall.

- **`procedural_memory`**
  - Purpose: learned routing and bundle patterns (procedural knowledge).
  - Payloads: `patternId`, `successRate`, `created_at`.

- **User & session memory**
  - `user_profiles` – per‑user preference and behavior summaries.
  - Short‑term session memory – chat turns with timestamps.

---

## 3. Planned Business Entities (Conceptual)

These entities **do not yet exist** as DB models or APIs; they are the target monetization‑layer abstractions. They will be implemented using a traditional database (SQLite/Postgres) plus Qdrant namespaces / prefixes for tenant isolation.

- **Tenant**
  - Represents a retailer (e.g., Coop, Migros, Manor, SMB).
  - Owns users, plans, enabled modules, and associated Qdrant namespaces.
  - Planned persistence:
    - RDBMS table `tenants(id, name, slug, status, created_at, updated_at)`.
    - Qdrant: tenant‑scoped collections or name prefixes, e.g. `tenant_{id}_products`.

- **User**
  - A human operator or system user within a tenant.
  - Mapped to:
    - Existing user profile and episodic records (e.g., `user_id` payload in Qdrant collections).
  - Future storage:
    - `users(id, tenant_id, email, role, status, ...)` with references into memory collections via IDs.

- **Agent**
  - Logical capabilities exposed by the system:
    - `shopper`, `inventory`, `pricing`, `merchandising`, `audit`, plus multimodal/forecasting agents.
  - Used for:
    - Feature gating (modules).
    - Usage tracking (`agent_invoked` events).
  - Existing implementation:
    - Concrete classes under `app.agents.*` and orchestrated by `SupervisorAgent`.

- **Plan**
  - Commercial plan assigned to a tenant (Free, Startup, Enterprise).
  - Captures:
    - Base price (CHF / month).
    - QPS limits, vector storage limits.
    - Included modules.
  - Planned persistence:
    - `plans(id, code, tier, max_qps, base_price_chf, overage_price_chf, vector_limit, created_at, updated_at)`.
    - `tenant_plans(id, tenant_id, plan_id, started_at, ended_at_nullable, billing_mode, ...)`.

- **Module**
  - Feature flags for add‑on capabilities:
    - Core: `CORE_SUPERVISOR`, `EPISODIC_MEMORY`, `SEMANTIC_CACHE`.
    - Add‑ons: `VISUAL_RAG`, `PRICING_AGENT`, `PROMO_AGENT`, `FORECAST_AGENT`, `VOICE_AGENT`, etc.
  - Planned persistence:
    - `tenant_modules(tenant_id, module_code, pricing_model, price_chf, created_at, disabled_at_nullable)` or JSONB field on tenant.

- **UsageRecord / UsageEvent**
  - Fine‑grained usage events for billing and observability.
  - Planned DB table:
    - `usage_events(id, tenant_id, event_type, quantity, ts, meta_json)`.
  - Event types:
    - `embedding_created`, `qdrant_query_executed`, `agent_invoked`, `episode_written`, `cache_hit`, `token_estimate`.
  - Will be emitted from:
    - Qdrant query wrappers, embedding generation functions, agent orchestrations, episodic writes, semantic cache hits, and later LLM wrappers.

- **Episode, Goal, Solution**
  - Already strongly represented in Qdrant:
    - `goals` / `solutions` / `goal_solution_links` / `episodes` / `reasoning_graphs`.
  - Planned business overlay:
    - Tenant‑scoped episodes and goals (via `tenant_id` in payloads and/or collection naming).
    - ROI analytics based on before/after episode metrics.

- **Product, InventorySignal**
  - Product and inventory signals exist today in:
    - `products`, `competitor_prices`, inventory‑related collections in `app.inventory` and scripts under `scripts/inventory` / `scripts/forecasting`.
  - Business overlay:
    - Use product and inventory events (e.g., stockouts, reorder events, price changes) to compute:
      - Stockout reduction.
      - Margin uplift.
      - Conversion improvements.

---

## 4. Mapping: Business Entities → Existing Code & Qdrant

This section links the future monetization view to the current implementation.

- **Tenant ↔ Qdrant collections**
  - Today:
    - Collections are global (`products`, `goals`, `solutions`, `episodes`, etc.).
  - Future:
    - Introduce tenant‑aware naming or namespaces:
      - Example: `tenant_{tenant_id}_products`, or a `tenant_id` payload field and filter.
    - Tenant model in RDBMS controls:
      - Which Qdrant collections/namespaces a tenant owns.
      - Max vector count and QPS per tenant.

- **User ↔ Profiles & episodic memory**
  - Existing:
    - `user_id` payload fields in:
      - `goal_solution_links`
      - `goals`
      - Possibly `user_profiles`.
    - `ShopperAgent.parse_goal_with_memory` uses:
      - `app.data.short_term_memory`
      - `app.data.user_profiles`
      - `app.data.goal_solution_links`
  - Future:
    - Users table keyed by tenant.
    - Stronger linkage between RDBMS user IDs and Qdrant user IDs.

- **Agents ↔ Modules**
  - Existing:
    - Agent implementations under `app.agents.*`, orchestrated by `SupervisorAgent`.
    - Visual / multimodal agent exposed via `app.multimodal.router` and visual demos.
    - Pricing, inventory, merchandising, audit, analytics, forecasting agents in respective modules.
  - Future:
    - Module flags controlling access to:
      - `SupervisorAgent` orchestration.
      - `PricingAgent` APIs (e.g., `/agents/pricing/optimize`).
      - Visual RAG routes (`VISUAL_RAG`).
      - Forecast and promo flows.

- **UsageRecord ↔ Existing metrics & logging**
  - Existing:
    - `app.agents.observability`, `app.metrics`, logging with `extra=` fields (latency, goal ids).
    - Qdrant usage is implicit inside:
      - `app.retriever`, `app.data.product_search`, `app.data.goal_solution_links`, etc.
  - Future:
    - Wrap:
      - Qdrant client queries.
      - Embedding generation (`app.embeddings`).
      - Agent orchestration (`SupervisorAgent.orchestrate`).
      - Episodic writes (`EpisodicMemoryStore.record_episode`).
    - Emit structured `UsageEvent` rows with `tenant_id` and quantities for billing.

- **Billing & ROI ↔ Episodes and metrics**
  - Existing:
    - Episodic memory, reasoning graphs, and metrics (`conversion_rate`, `episode_reuse_rate`).
  - Future:
    - `billing_snapshots` table for monthly snapshots per tenant.
    - Billing aggregator:
      - Uses usage events + plan definitions to compute:
        - Estimated monthly bill.
        - Payback and gross margin based on infra assumptions.
    - ROI analytics:
      - Compares baseline vs current episodes (e.g., conversion, stockout events, margin).

---

## 5. Where Monetization Hooks Will Attach

This section identifies **hook points** for the upcoming monetization and tenant work, without modifying code yet.

- **Tenant context**
  - API: FastAPI dependencies / middleware in `app.main`.
  - Planned:
    - `X-Tenant-Key` header resolving to `tenant_id`.
    - Injected into:
      - Retrievers (`app.retriever`, `app.data.product_search`).
      - Episodic stores (`EpisodicMemoryStore`, `ReasoningGraphStore`).
      - Agent orchestrations (`SupervisorAgent`).
      - Embedding and LLM clients.

- **Usage tracking**
  - Qdrant queries:
    - `app.qdrant_client` + modules that call `QdrantClient.search`, `scroll`, `recommend`, etc.
  - Embeddings:
    - `app.embeddings` and any helper scripts / services that encode text or multimodal features.
  - Agents:
    - `SupervisorAgent.orchestrate` plus direct agent entrypoints.
  - Episodes:
    - `EpisodicMemoryStore.record_episode` and memory events (`record_episode_to_memory`).
  - Semantic cache:
    - `app.multimodal.semantic_cache` and any other cache helpers.

- **Rate limiting & plan enforcement**
  - API layer in `app.main`:
    - To be extended with middleware/decorators enforcing:
      - QPS per tenant.
      - Daily vector/episode caps (Free, Startup tiers).

- **Module gating**
  - Agent entrypoints & routers:
    - Visual search endpoints (`app.multimodal.router`).
    - Pricing / forecasting / promo agent APIs.
    - Supervisor orchestration endpoints.
  - Will check:
    - `tenant_modules` and return 403 with module codes if disabled.

- **Audit trails**
  - Pricing, inventory, promo, and forecast agents:
    - Today: some logging of decisions and metrics.
  - Future:
    - Structured `AuditEvent` table populated on:
      - Each plan decision.
      - Human‑in‑the‑loop approvals / overrides.

---

## 6. Next Steps (Implementation Order)

The next backend steps will be implemented incrementally and tested along the way:

1. Introduce **Tenant**, **Plan**, and **Module** models (RDBMS + basic admin APIs).
2. Add a **usage tracking layer** (`UsageTracker`) and wire it into Qdrant, embedding, agent, and episodic paths.
3. Implement **billing aggregation** and tenant usage / billing estimate APIs.
4. Add **rate limiting** and **module gating** based on plans and modules.
5. Introduce **ROI analytics** based on episodes and product/inventory signals.
6. Add **audit logging** and **metrics endpoints** to support enterprise observability and sales demos.

