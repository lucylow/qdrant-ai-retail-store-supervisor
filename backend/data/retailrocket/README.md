# RetailRocket → Qdrant Pipeline

Industry-standard recommender dataset: **2.7M events** (view → add2cart → transaction) for real conversion funnel and inventory simulation.

## Dataset spec

- **events.csv**: `timestamp`, `visitorid`, `event`, `itemid`, `transactionid`
- **item_properties.csv**: `timestamp`, `itemid`, `property`, `value` (e.g. categoryid, color)
- **category_tree.csv**: `categoryid`, `parentid`, `catname_en`

Real funnel: view→add2cart ~8.2%, add2cart→transaction ~3.1%.

## Download

**Option A – caserec (if available):**
```bash
mkdir -p data/retailrocket
cd data/retailrocket
wget -q "https://github.com/caserec/Datasets-for-Recommender-Systems/raw/master/RetailRocket/events.csv.gz" -O events.csv.gz
wget -q "https://github.com/caserec/Datasets-for-Recommender-Systems/raw/master/RetailRocket/item_properties.csv.gz" -O item_properties.csv.gz
wget -q "https://github.com/caserec/Datasets-for-Recommender-Systems/raw/master/RetailRocket/category_tree.csv.gz" -O category_tree.csv.gz
gunzip -f *.csv.gz
```

**Option B – Kaggle:**  
Download [RetailRocket ecommerce-dataset](https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset), unzip into `data/retailrocket/` so that `events.csv`, `item_properties.csv`, and `category_tree.csv` (if present) are in this directory.

## Process (Parquet + optional Qdrant)

```bash
# Parquet only (~5–10 min)
python data/retailrocket/process_retailrocket.py --data-dir data/retailrocket

# Parquet + Qdrant items collection (~15–25 min, requires Qdrant on localhost:6333)
python data/retailrocket/process_retailrocket.py --data-dir data/retailrocket --qdrant-url http://localhost:6333

# Demo cap (e.g. 100k events, 50k items)
python data/retailrocket/process_retailrocket.py --data-dir data/retailrocket --max-events 100000 --max-items 50000 --qdrant-url http://localhost:6333
```

## Outputs

- `data/retailrocket/events.parquet` – processed events
- `data/retailrocket/items.parquet` – items with category + funnel stats
- `data/retailrocket/inventory_signals.parquet` – per-item conversion rates
- `data/retailrocket/category_tree.parquet` – category hierarchy
- Qdrant collection `retailrocket_items` (if `--qdrant-url` set)

## Live demo

```bash
python qdrant/setup_retailrocket.py --url http://localhost:6333
uvicorn agents.retailrocket_demo:app --port 8001
# Judge demo: curl "http://localhost:8001/demo/search?query=tents"
```
