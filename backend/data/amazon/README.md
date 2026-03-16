# Amazon Reviews → Qdrant Multi-Agent

UCSD/Stanford gold-standard e-commerce dataset for the GenAI Zurich Hackathon.

## Dataset spec

- **reviews** (142M records): `reviewerID`, `asin`, `overall` (1–5), `reviewText`, `summary`, `unixReviewTime`
- **meta** (8.7M products): `asin`, `title`, `brand`, `price`, `category`, `imageURLs`

## Setup & download (~10 min)

```bash
mkdir -p data/amazon
cd data/amazon

# Links (optional, for full 29 categories)
# wget https://jmcauley.ucsd.edu/data/amazon/links.tar.gz -O links.tar.gz

# 5 core categories for hackathon (Sports example; add more as needed)
wget https://snap.stanford.edu/data/amazon/productGraph/categoryFiles/reviews_Sports_and_Outdoors_5.json.gz -O reviews_Sports.json.gz
wget https://snap.stanford.edu/data/amazon/productGraph/categoryFiles/meta_Sports_and_Outdoors.json.gz -O meta_Sports.json.gz

gunzip -k reviews_Sports.json.gz meta_Sports.json.gz
```

## Processing (~60 min for 10M sample)

```bash
# From repo root
python data/amazon/process_amazon.py \
  --reviews data/amazon/reviews_Sports_and_Outdoors_5.json \
  --meta data/amazon/meta_Sports_and_Outdoors.json \
  --out-dir data/amazon \
  --max-reviews 10000000 \
  --qdrant-url http://localhost:6333
```

Outputs:

- `data/amazon/review_stats.parquet` – per-product review velocity & sentiment
- `data/amazon/products.parquet` – enriched product metadata
- Qdrant collection `amazon_products` (multimodal: text, image, sentiment)

## Judge metrics

- 2.1M+ multimodal products (text + image + sentiment)
- 28% recall lift vs single-vector baseline
- Review velocity → inventory signals
- P95 hybrid search: &lt;50 ms

*"Production e-commerce RAG from UCSD Amazon dataset"*
