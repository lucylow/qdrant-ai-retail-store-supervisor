# Multi-Agent Store Manager: Advanced Blackboard Architecture with Hybrid RAG

## Overview
This project implements a sophisticated **Multi-Agent Store Manager** designed for the GenAI Zurich Hackathon 2026. The system utilizes a **Blackboard Architecture** where autonomous agents coordinate asynchronously through **Qdrant**, which serves as the "central nervous system" and shared semantic memory.

## Key Innovations

### 1. Supervisor-Orchestrated Blackboard Pattern
Unlike traditional linear chains or single-agent chatbots, this system uses a true multi-agent architecture. Agents operate as independent services that communicate by reading and writing to shared collections in Qdrant. A **Supervisor Agent** manages the state transitions of "Goals" on the blackboard, ensuring a smooth and scalable workflow.

### 2. Context Engineering with Named Vectors
We leverage Qdrant's **Named Vectors** (`text_vector` and `context_vector`) to perform advanced context engineering. 
- The **Shopper Agent** initializes the `text_vector` with the user's intent.
- The **Promotions Agent** performs **Context Enrichment** by retrieving relevant promotions and updating the `context_vector` with this new semantic information and specific reasoning hints.

### 3. Hybrid RAG with RRF Fusion
The **Inventory Agent** now employs a state-of-the-art **Hybrid RAG** mechanism:
- **Multi-Vector Retrieval**: It queries both the `text_vector` (intent-based) and `context_vector` (context-enriched) to capture different semantic dimensions.
- **RRF-Inspired Fusion**: We implement a Reciprocal Rank Fusion (RRF) algorithm to combine results from multiple vector spaces, significantly increasing the precision of product discovery and episodic memory retrieval.
- **Product Discovery RAG**: Real-time semantic search over a `products` collection using the fused hybrid results.

### 4. Optimized Performance with Payload Indexing
The system is designed for production scalability. We implement **Payload Indexing** on key fields such as `status`, `user_id`, and `outcome`. This enables Qdrant's **one-stage filtering**, combining high-speed vector search with precise metadata constraints.

## Architecture Components
- **Shopper Agent**: Formulates structured goals from natural language.
- **Promotions Agent**: Enriches goals with relevant marketing and discount context.
- **Inventory Agent**: Fulfills goals using **Hybrid RAG** and episodic learning.
- **Supervisor Agent**: Orchestrates the blackboard state machine.
- **Qdrant**: The shared semantic blackboard storing goals, solutions, products, and memory.

## Latest Improvements
- **Hybrid Search Implementation**: Added `hybrid_search` in `QdrantManager` to combine multiple semantic perspectives.
- **RRF Fusion Algorithm**: Implemented a ranking fusion logic to prioritize items that appear relevant across both raw intent and enriched context.
- **Enhanced Retrieval Precision**: The Inventory Agent now benefits from more accurate product matching and historical context retrieval.

## Getting Started
1. **Install Dependencies**: `pip install qdrant-client openai`
2. **Run Demo**: `python demo.py` - Demonstrates the full end-to-end asynchronous workflow.
3. **Run Evaluation**: `python evaluation_script.py` - Tests the system's coordination and performance across multiple scenarios.
