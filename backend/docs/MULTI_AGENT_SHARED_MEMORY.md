# Multi-Agent Shared Memory (Qdrant)

This doc describes the Qdrant-backed shared memory patterns used for the Store Manager (Shopper + Inventory) and how they map to your design.

## Collections

| Collection | Purpose | Payload indexes |
|------------|---------|-----------------|
| **products** | Product catalog; filtered search (stock, region, price) | sku, stock, region, price, price_eur, last_updated, category |
| **goals** | Blackboard (central task board) | goal_id, user_id, status, created_at, agent_role |
| **solutions** | Candidate plans per goal | goal_id, status, created_at |
| **goal_solution_links** | Episodic memory (goal → solution → outcome) | goalId, userId, outcome, success, score, region, category, created_at |
| **procedural_memory** | Learned routing/bundle patterns | patternId, successRate, created_at |

## Patterns Implemented

### 1. Blackboard (Central Task Board)

- **Module:** `app.data.blackboard`
- **Usage:** Shopper writes goals; Inventory (or other agents) poll and update.
- **API:**
  - `write_goal(goal_text, user_id=..., status="open", agent_role="inventory")` → goal_id
  - `poll_goals_for_agent(agent_role, status="open")` → list of goals
  - `update_goal_status(goal_id, status, payload_update={...})` → bool
  - `search_similar_goals(goal_text, top_k, status=...)` → similar past goals

### 2. Episodic Memory (goal_solution_links)

- **Module:** `app.data.goal_solution_links`
- **Usage:** Store and retrieve goal→solution→outcome episodes for case-based planning.
- **API:**
  - `upsert_episode(goal_id, solution_id, user_id, goal_text, solution_summary, outcome, score, ...)` → episode_id
  - `search_similar(goal_text, top_k, outcome_filter="purchased", min_score=..., hnsw_ef=...)` → episodes
- **Episodic recall:** `hnsw_ef` can be increased at query time for higher recall (e.g. 192).

### 3. Solutions Store (per-goal candidate plans)

- **Module:** `app.data.solutions_store`
- **Usage:** Inventory writes candidate bundles; Shopper reads combined solution.
- **API:**
  - `upsert_solution(goal_id, bundle_summary, score_summary=..., bundles=..., status="candidate")` → solution_id
  - `get_solutions_for_goal(goal_id, status=..., limit=...)` → list of solutions

### 4. Filtered Product Search & Recommend

- **Module:** `app.data.product_search`
- **Usage:** Shopper/Inventory use server-side filters (stock, region, price) and optional Recommend API.
- **API:**
  - `search_products_filtered(query, limit, stock_gt=..., region=..., price_lte=..., price_gte=..., hnsw_ef=...)` → hits
  - `recommend_products(positive=[{"id": ...} or {"vector": ...}], negative=..., limit, query_filter=...)` → hits

## Shopper / Inventory Flows

- **Shopper:** Can write a goal to the blackboard via `blackboard.write_goal(...)`; present options using `product_search.search_products_filtered` with `region` and `price_lte` (budget).
- **Inventory:**  
  - **Episodic:** `goal_solution_links.search_similar(..., hnsw_ef=192)` for precedent episodes.  
  - **Filtered search:** `initial_search(query, region=goal.region, budget_eur=goal.budget_eur)` uses `search_products_filtered` under the hood when region/budget are set.  
  - **Solutions:** Can `solutions_store.upsert_solution(goal_id, ...)` after planning; Shopper can `get_solutions_for_goal(goal_id)`.

## Bootstrap

- `ensure_all_collections()` (e.g. from `app.main` or `app.data.collections`) creates **goals**, **products**, **solutions**, and other collections with correct vector sizes (goals/solutions use text embedding dimension).
- `ensure_memory_collections()` creates **goal_solution_links**, **procedural_memory**, **user_profiles** and their payload indexes.
- `ensure_shared_memory_indexes(client)` creates payload indexes on **products**, **goals**, and **solutions** (called from `ensure_all_collections`).

## Config

- **QDRANT:** `hnsw_m`, `hnsw_ef_construct` (index build); `hnsw_ef_search` used for episodic and filtered search when set.
- **COLLECTIONS:** `products`, `goals`, `solutions`, `episodes` (config names); `goal_solution_links` and `procedural_memory` are in `app.data.memory_collections`.
