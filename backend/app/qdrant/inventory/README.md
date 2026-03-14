# Qdrant Inventory Collections

This package defines and manages Qdrant collections used for **inventory**-related data:

- **inventory_levels**: current stock per SKU/warehouse (payload: `warehouse_id`, `sku`, `stock_level`, `last_updated`).
- **reorder_history**: reorder events (payload: `sku`, `supplier`, `order_qty`, `arrival_date`).
- **stockout_events**: stockout events (payload: `sku`, `stockout_date`, `lost_sales`).

See `collections.py` and `indexes.py` for setup.

---

## Streaming Inventory Updates into Qdrant

To keep search and agents aligned with live availability, inventory changes (WMS, orders, restocks) should update Qdrant in near real time.

### Event contract (suggestion)

Use a single schema that can drive both **KG** and **Qdrant**:

```json
{
  "type": "inventory",
  "sku": "SKU-123",
  "warehouse_id": "WH-01",
  "stock_level": 42,
  "timestamp": "2026-03-12T10:00:00Z"
}
```

### What to update

1. **Products collection** (if product points carry availability):
   - Update payload for the point whose payload `sku` (or `id`) matches:
     - `in_stock`: boolean (e.g. `stock_level > 0`).
     - `stock_level`: number (optional).
     - `last_updated`: timestamp or float.
   - Use `client.set_payload(collection_name, {"sku": sku}, {"in_stock": True, ...})` or upsert by point id if you store it.

2. **inventory_levels collection**:
   - Upsert a point per (sku, warehouse) with vector (e.g. existing 64-dim or a placeholder) and payload:
     - `sku`, `warehouse_id`, `stock_level`, `last_updated`.
   - Point id: e.g. `f"{sku}_{warehouse_id}"` for idempotent upserts.

### Pipeline options

- **Kafka / Redis Stream**: Consumer that reads inventory events and calls the update logic above (and optionally pushes the same event to `scripts/kg/continuous_sync.KGContinuousSync` for Neo4j).
- **Polling**: Periodic job that reads “recent changes” from a DB or API and applies the same update logic (higher latency, simpler ops).
- **Script stub**: e.g. `scripts/inventory/stream_to_qdrant.py` that:
  - Accepts a batch of events (or a path to a file / queue name).
  - For each event: update products payload and upsert into `inventory_levels`.
  - Can be wired to a real queue or run from cron.

### Consistency

- Prefer **one source of truth** (e.g. WMS or orders DB) emitting events; both KG sync (`scripts/kg/continuous_sync.py`) and this Qdrant updater consume the same stream (or a copy).
- Use idempotent upserts and `last_updated` so out-of-order events do not overwrite newer state if desired (e.g. only update if event timestamp > stored `last_updated`).

See **FEASIBILITY_AND_SCALABILITY.md** (repo root) for the scalability context and “Improvement 3”.
