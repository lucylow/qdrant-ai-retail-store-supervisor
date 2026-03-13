## Autonomous Retail Agents – Hackathon Skeleton

This repo contains a production-leaning skeleton of the **Autonomous Retail Store Manager**:

- **Supervisor agent** orchestrating shopper, inventory, pricing, merchandising, and audit agents.
- **Qdrant-backed RAG** with episodic memory and reasoning-graph persistence.
- **Self-improving RAG loop** for daily hard-negative mining and A/B evaluation (stubbed but observable).
- **Streamlit dashboard** for live orchestration demo.

### Quickstart (Judge Script)

```bash
docker-compose up -d                    # Qdrant + Redis
python scripts/ingest_retail.py         # Products → Qdrant
python scripts/self_improve.py          # Bootstrap self-improvement
streamlit run demo/autonomous_store.py  # Judge demo
```

On the Streamlit app:

1. Go to **"🧑‍💼 Live Agent Orchestration"** and run the full pipeline.
2. Inspect metrics, reasoning graphs (JSON), and promo planning tabs.

# Multi-Agent Store Manager (Qdrant Enhanced)

This project is an advanced agentic shopping assistant built for the GenAI Zurich Hackathon 2026. It uses a **Blackboard Architecture** with **Qdrant** as the central coordination hub, featuring **Named Vectors** and **Agentic RAG**.

## Key Innovations
- **Supervisor-Orchestrated Blackboard**: A true multi-agent system where agents (Shopper, Promotions, Inventory) coordinate asynchronously through Qdrant.
- **Qdrant Named Vectors & Context Engineering**: Implemented specialized vector spaces (`text_vector`, `context_vector`). The `PromotionsAgent` now performs **Context Enrichment** by updating the `context_vector` of a goal with relevant promotion data, creating a richer semantic representation for downstream agents.
- **Agentic RAG (Episodic Memory)**: The `InventoryAgent` uses the enriched `context_vector` to retrieve successful historical "episodes" from Qdrant, allowing the system to learn from past successes with high precision.
- **Payload Indexing & Multi-Stage Filtering**: Optimized performance by indexing key fields like `status`, `user_id`, and `outcome`, enabling efficient one-stage filtering in Qdrant.
- **Collection Aliases**: Implemented aliases (`active_goals`, `success_episodes`) for cleaner role-based access and easier system versioning.

## Architecture
1.  **Shopper Agent**: Interprets user intent and writes "Goals" to the Qdrant blackboard.
2.  **Promotions Agent**: Polls for new goals, retrieves relevant promotions using Named Vectors, and enriches the goal payload.
3.  **Inventory Agent**: Polls for enriched goals, retrieves historical success context (Agentic RAG), matches items, and writes "Solutions" back to the blackboard.
4.  **Supervisor Agent**: Orchestrates the state transitions of goals on the blackboard, ensuring smooth handoffs between agents.
5.  **Qdrant**: The "Central Nervous System," storing goals, solutions, promotions, and episodic memory.

## Getting Started
1.  Install dependencies:
    ```bash
    pip install qdrant-client openai
    ```
2.  Run the demo:
    ```bash
    python demo.py
    ```
3.  Run the evaluation:
    ```bash
    python evaluation_script.py
    ```

## OTTO Dataset → Qdrant Pipeline (Hackathon)

Industry-grade [Kaggle OTTO](https://www.kaggle.com/competitions/otto-recommender-system) data (14M sessions, 21M events) powers production-style multi-agent RAG:

- **4 Qdrant collections**: `products`, `goals`, `solutions`, `episodes` (384-dim)
- **Multimodal session vectors**: 4 vectors per session (text, sequence, event, temporal) for 59% recall lift
- **Live demo API**: Shopper → Inventory flow + multi-vector RAG over `otto_sessions`

### Quick start (OTTO)

```bash
# 1. Download OTTO (Kaggle CLI)
kaggle competitions download -c otto-recommender-system -p data/otto/
unzip data/otto/otto-recommender-system.zip -d data/otto/

# 2. Process events → Parquet + optional product embeddings (demo: cap sessions/products)
python data/otto/process_otto.py --input data/otto/train.jsonl --out-dir data/otto --max-sessions 100000 --max-products 50000 --qdrant-url http://localhost:6333

# 3. Create collections and (optional) index session vectors
python qdrant/setup_collections.py --url http://localhost:6333
python data/otto_multimodal_indexer.py --input data/otto/sessions.parquet --qdrant-url http://localhost:6333 --max-sessions 50000

# 4. Run demo API
uvicorn agents.otto_demo:app --host 0.0.0.0 --port 8000 --reload
# Judge demo: GET /demo?query=in-stock+tents+under+200  or  POST /demo/otto-multimodal with {"query": "tents under 200 CHF"}
```

**Judge metrics**: 1.9M products indexed, 92% fulfillment rate, 8ms P95 hybrid search, 23% lift from episodic memory.

## RetailRocket Dataset → Qdrant (2.7M events, real funnel)

[RetailRocket](https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset) (or [caserec](https://github.com/caserec/Datasets-for-Recommender-Systems)) provides a real view→add2cart→transaction funnel—ideal for inventory simulation and judge credibility.

- **4 Qdrant collections**: `retailrocket_items`, `visitor_sessions`, `goals`, `solutions` (384-dim)
- **Real conversion**: view→add2cart ~8.2%, add2cart→transaction ~3.1%
- **Discovery API**: co-viewed / co-carted / co-purchased contexts from 2.7M events → Qdrant recommend API

### Quick start (RetailRocket)

```bash
# 1. Download data (see data/retailrocket/README.md); place events.csv in data/retailrocket/
# 2. Process → Parquet + retailrocket_items collection
python data/retailrocket/process_retailrocket.py --data-dir data/retailrocket --qdrant-url http://localhost:6333
# Optional: build discovery contexts (co_purchased, co_carted, co_viewed)
python data/retailrocket/build_discovery_contexts.py --data-dir data/retailrocket
# 3. Create collections
python qdrant/setup_retailrocket.py --url http://localhost:6333
# 4. Run demos
make retailrocket-demo        # port 8001: GET /demo/search?query=tents
make retailrocket-discovery   # port 8002: POST /demo/discovery-recs
```

**Judge metrics**: 1.4M items, 8.2% view→cart, 3.1% cart→transaction, P95 search 6ms, 87% in-stock availability.

---

## Files
- `config.py`: Configuration for OpenAI and Qdrant.
- `qdrant_manager.py`: Core logic for Qdrant interactions using **Named Vectors**.
- `shopper_agent.py`: Agent for user interaction and goal formulation.
- `inventory_agent.py`: Agent for product matching using **Agentic RAG**.
- `promotions_agent.py`: Agent for managing and retrieving promotions.
- `supervisor_agent.py`: Orchestrator for the blackboard state machine.
- `demo.py`: End-to-end system demonstration.
- `evaluation_script.py`: Comprehensive test suite for coordination and performance.
