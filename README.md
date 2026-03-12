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

## Files
- `config.py`: Configuration for OpenAI and Qdrant.
- `qdrant_manager.py`: Core logic for Qdrant interactions using **Named Vectors**.
- `shopper_agent.py`: Agent for user interaction and goal formulation.
- `inventory_agent.py`: Agent for product matching using **Agentic RAG**.
- `promotions_agent.py`: Agent for managing and retrieving promotions.
- `supervisor_agent.py`: Orchestrator for the blackboard state machine.
- `demo.py`: End-to-end system demonstration.
- `evaluation_script.py`: Comprehensive test suite for coordination and performance.
