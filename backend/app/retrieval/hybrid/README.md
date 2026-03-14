# Hybrid Retrieval

This package provides **hybrid** retrieval strategies that combine multiple signals for product and goal/solution search.

## Current Implementations

- **KG + Qdrant** (`kg_qdrant.py`): Structural KG reasoning → Qdrant vector search → reranking fusion.
- **Cypher RAG** (`cypher_rag.py`): Run Cypher (reasoner or raw), format as RAG context.

Existing “hybrid search” in the repo (e.g. `qdrant_manager.py`, `multimodal_rag.py`) is **multi-vector fusion** (e.g. `text_vector` + `context_vector`, or text + image named vectors) with RRF, not dense + sparse.

---

## Dense + Sparse (BM25-style) Hybrid — Design

For e-commerce catalogs, **keyword-exact** (SKU, brand, category) and **semantic** (intent) both matter. Qdrant supports:

- **Sparse vectors** (e.g. SPLADE, BM42): one vector per point for sparse retrieval.
- **Named vectors**: one dense (e.g. `text_vector`) and one sparse (e.g. `sparse_vector`) per point.
- **Hybrid query**: run dense and sparse search in one request and fuse (e.g. RRF).

### Suggested steps

1. **Collection**
   - Create (or extend) a products collection with both:
     - Dense: `VectorParams(size=384, distance=COSINE)` (existing text encoder).
     - Sparse: `VectorParams(size=0, distance=DOT, sparse_config=SparseVectorParams(...))`.
   - Or use a dedicated `products_hybrid` collection.

2. **Indexing**
   - Dense: existing pipeline (e.g. `embed_single(description)`).
   - Sparse: run a sparse encoder (e.g. SPLADE, BM42, or a simple token→idf style) on title + description; upsert sparse vector per point.

3. **Search**
   - Query: dense = embed(query), sparse = same sparse encoder(query).
   - Call Qdrant with both vectors (or two searches) and fuse with RRF (or weighted sum).
   - Expose as a single `dense_sparse_hybrid_search(collection, query, limit, filter)` used by product discovery and catalog APIs.

4. **Dependencies**
   - Add a sparse encoder (e.g. `splade`, or use Qdrant’s built-in sparse support with a chosen model). Keep dependency optional so current deployments remain unchanged.

### Interface sketch

```python
# app/retrieval/hybrid/dense_sparse.py (to implement)

def dense_sparse_hybrid_search(
    client: QdrantClient,
    collection_name: str,
    query: str,
    limit: int = 20,
    query_filter: Optional[Filter] = None,
    dense_weight: float = 0.5,
) -> List[ScoredPoint]:
    """Run dense + sparse search and fuse with RRF (or weighted)."""
    dense_vec = get_dense_embedding(query)
    sparse_vec = get_sparse_embedding(query)  # SPLADE/BM42
    # Qdrant 1.7+: query with both; or two searches + RRF
    ...
```

See **FEASIBILITY_AND_SCALABILITY.md** (repo root) for the overall scalability context.
