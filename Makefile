# Multi-Agent Store Supervisor v5 - Dynamic Pricing + Inventory + Price Forecasting
# Production dynamic pricing: MARL + RAG; Inventory + joint optimization; 7-agent forecasting

.PHONY: dynamic-pricing-init dynamic-pricing-live ensure-collections
.PHONY: inventory-pricing-init inventory-pricing-live inventory-collections
.PHONY: price-forecasting-init price-forecasting-live
.PHONY: kg-stack-up kg-ingest-full kg-production
.PHONY: amazon-setup amazon-demo amazon-collections
.PHONY: retailrocket-setup retailrocket-demo retailrocket-discovery retailrocket-discovery-contexts
.PHONY: personalization-init personalization-live personalization-collections
.PHONY: fashion-visual-index fashion-visual-demo

# Fashion-MNIST → Qdrant CLIP visual search (70K images, ~15min)
fashion-visual-index:
	cd "$(shell pwd)" && python3 -m scripts.fashion_mnist_qdrant_loader
	@echo "Fashion visual index done. Run: make fashion-visual-demo"

fashion-visual-demo:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
	@echo "Open http://localhost:8000 and go to /visual-search (frontend) or POST /api/visual-search"

# Ensure Qdrant collections exist (including competitor_prices)
ensure-collections:
	cd "$(shell pwd)" && python3 -c "from app.data.collections import ensure_all_collections; ensure_all_collections(); print('Collections OK')"

# Inventory Qdrant collections (inventory_levels, reorder_history, stockout_events)
inventory-collections:
	cd "$(shell pwd)" && python3 scripts/inventory/setup_collections.py

# Quick MARL training + competitor data indexing
dynamic-pricing-init: ensure-collections
	python3 scripts/pricing/train_marl.py --quick
	python3 scripts/pricing/start_monitoring.py
	@echo "Dynamic pricing init done. Run: streamlit run demo/dynamic_pricing.py"

# Full production: init + start dashboard
dynamic-pricing-live: dynamic-pricing-init
	@echo "Starting live pricing dashboard..."
	streamlit run demo/dynamic_pricing.py

# Inventory + pricing: collections + joint model training
inventory-pricing-init: ensure-collections inventory-collections
	python3 scripts/inventory/train_joint_models.py --quick
	@echo "Inventory + pricing init done. Run: streamlit run demo/inventory_pricing.py"

# Full joint optimization stack: init + inventory-pricing dashboard
inventory-pricing-live: inventory-pricing-init
	@echo "Starting inventory + pricing dashboard..."
	streamlit run demo/inventory_pricing.py

# --- Knowledge Graph (Neo4j + Qdrant hybrid) ---
kg-stack-up:
	docker-compose -f docker-compose.kg.yml up -d
	@echo "Wait ~30s for Neo4j (7687) and Qdrant (6333), then: make kg-ingest-full"

kg-ingest-full:
	python3 scripts/kg/ingest_all.py
	@echo "KG ingest done. Run: streamlit run demo/kg_explorer.py"

kg-production: kg-stack-up
	@echo "Waiting for Neo4j and Qdrant..."
	@sleep 20
	$(MAKE) kg-ingest-full
	@echo "Starting KG Explorer..."
	streamlit run demo/kg_explorer.py

# --- Amazon Reviews -> Qdrant (UCSD dataset) ---
amazon-collections:
	python3 qdrant/setup_amazon_collections.py --url $${QDRANT_URL:-http://localhost:6333}

amazon-setup: amazon-collections
	@echo "Download Sports reviews/meta to data/amazon/ then run:"
	@echo "  python3 data/amazon/process_amazon.py --reviews data/amazon/reviews_Sports_and_Outdoors_5.json --meta data/amazon/meta_Sports_and_Outdoors.json --out-dir data/amazon --max-reviews 500000"

amazon-demo:
	uvicorn agents.amazon_demo:app --host 0.0.0.0 --port 8000

# --- Multi-Agent Price Forecasting (7 agents + ensemble) ---
price-forecasting-init: ensure-collections
	python3 scripts/forecasting/setup_collections.py
	python3 scripts/forecasting/train_ensemble.py --quick
	@echo "Price forecasting init done. Run: streamlit run demo/price_forecasting.py"

price-forecasting-live: price-forecasting-init
	@echo "Starting live price forecasting dashboard..."
	streamlit run demo/price_forecasting.py

# --- Hyper-Personalization (8-agent Customer 360) ---
personalization-collections:
	cd "$(shell pwd)" && python3 scripts/personalization/setup_collections.py

personalization-init: ensure-collections personalization-collections
	python3 scripts/personalization/train_preference_models.py --quick
	@echo "Personalization init done. Run: streamlit run demo/personalization_hub.py"

personalization-live: personalization-init
	@echo "Starting Hyper-Personalization Hub..."
	streamlit run demo/personalization_hub.py

# --- RetailRocket 2.7M events → Qdrant (real conversion funnel) ---
retailrocket-setup:
	mkdir -p data/retailrocket
	python3 qdrant/setup_retailrocket.py --url $${QDRANT_URL:-http://localhost:6333}
	@echo "Put events.csv (and item_properties.csv, category_tree.csv) in data/retailrocket/, then: make retailrocket-process"

retailrocket-process:
	python3 data/retailrocket/process_retailrocket.py --data-dir data/retailrocket --qdrant-url $${QDRANT_URL:-http://localhost:6333}
	@echo "Optional: python3 data/retailrocket/build_discovery_contexts.py --data-dir data/retailrocket"

retailrocket-demo:
	uvicorn agents.retailrocket_demo:app --host 0.0.0.0 --port 8001
	@echo "Judge demo: curl 'http://localhost:8001/demo/search?query=tents'"

retailrocket-discovery-contexts:
	python3 data/retailrocket/build_discovery_contexts.py --data-dir data/retailrocket

retailrocket-discovery:
	uvicorn agents.retailrocket_discovery_demo:app --host 0.0.0.0 --port 8002
	@echo "Judge demo: curl -X POST http://localhost:8002/demo/discovery-recs -H 'Content-Type: application/json' -d '{\"item_ids\": [12345, 67890], \"context\": \"co_purchased\"}'"

# --- GENAI-HACKATHON: Generative AI Enhancements (prompt templates, few-shot, CoT, validation, hallucination) ---
genai-benchmark:
	python3 scripts/genai_benchmark.py --samples 50
	@echo "Full benchmark: python3 scripts/genai_benchmark.py --dataset retail_qa_1000 --output results/genai_benchmark.json"

genai-fewshot-mine:
	python3 scripts/fewshot_mining.py --goal-count 100
	@echo "Mined examples for few-shot. Optional: --output demo_data/fewshot_examples.json"

genai-dashboard:
	@echo "Starting GenAI Dashboard (http://localhost:8501)..."
	streamlit run demo/genai_dashboard.py

genai-test:
	pytest tests/test_prompt_engineering.py -v

# One-click GenAI demo: start stack + dashboard (Qdrant + Redis already in docker-compose)
genai-demo: ensure-collections
	$(MAKE) genai-fewshot-mine
	@echo "Launch GenAI Dashboard: make genai-dashboard"
	@echo "Or: streamlit run demo/genai_dashboard.py"
