# Geospatial mapping, navigation & logistics (Migros retail)

Backend + frontend for **store search**, **routing/ETA**, **isochrones**, **vehicle route planning**, and **real-time WebSocket** alerts. Tenant-aware (Migros, Coop, etc.).

## Environment variables

Set in `.env` or CI:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Postgres/PostGIS (e.g. `postgresql://postgres:postgres@localhost:5432/livemap`) |
| `REDIS_URL` | Redis (e.g. `redis://localhost:6379/0`) |
| `QDRANT_URL` | Qdrant (e.g. `http://localhost:6333`) |
| `MAPBOX_TOKEN` | Mapbox API token (optional; required for Mapbox directions/isochrone) |
| `OSRM_URL` | OSRM server URL (optional alternative to Mapbox) |
| `ROUTING_PROVIDER` | `mapbox` or `osrm` (default: `mapbox`) |
| `FASTAPI_HOST` / `FASTAPI_PORT` | Backend host/port |

Frontend (Vite): `VITE_API_BASE` — base URL for API (e.g. `http://localhost:8000` when backend runs on 8000 and frontend on 8080).

## Quick start

1. **Start services**
   ```bash
   docker compose -f docker-compose.geomap.yml up -d
   ```

2. **Apply migration**
   ```bash
   psql "$DATABASE_URL" -f migrations/002_create_geodb.sql
   ```
   If using the same DB as LiveMap intents, run `001_create_livemap_tables.sql` first (or ensure PostGIS is enabled).

3. **Seed Migros stores**
   ```bash
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/livemap python scripts/seed_migros_stores.py
   ```

4. **Run backend**
   ```bash
   export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/livemap
   export MAPBOX_TOKEN=your_mapbox_token   # or set OSRM_URL and ROUTING_PROVIDER=osrm
   uvicorn app.main:app --reload --port 8000
   ```

5. **Run frontend**
   ```bash
   npm run dev
   # For local dev with backend on 8000: VITE_API_BASE=http://localhost:8000 npm run dev
   ```
   Open **Store map** from the sidebar (`/store-map`) to see stores, routes, and logistics panel.

## API overview

- `GET /api/stores/nearby?lat=&lon=&radius_m=&limit=&tenant_id=` — stores within radius (PostGIS)
- `GET /api/stores/bbox?min_lat=&min_lon=&max_lat=&max_lon=&tenant_id=` — stores in bbox
- `GET /api/stores/{store_id}?tenant_id=` — store details
- `POST /api/routing/eta` — body: `from_lat`, `from_lon`, `to_store_id`, `profile?`, `intent_id?` (optional cache)
- `POST /api/routing/route` — body: `from_lat`, `from_lon`, `to_store_id`, `profile?` — returns Mapbox/OSRM route GeoJSON
- `GET /api/routing/isochrone?lat=&lon=&minutes=&profile=` — Mapbox isochrone
- `POST /api/logistics/plan` — body: `depot_lat`, `depot_lon`, `vehicle_count?`, `capacity?`, `tenant_id?` — greedy VRP, persists to `vehicle_routes`
- `WS /api/ws/{channel}` — real-time updates (e.g. channel `logistics` for inventory alerts)

## Real Migros data

Replace the sample list in `scripts/seed_migros_stores.py` with real store feeds (CSV/API). Ensure each row has `store_id`, `tenant_id`, `name`, `lat`, `lon`, and optional `address`, `city`, `postcode`, `categories`, `capabilities_text`, `capacity`. Use the same `INSERT ... ON CONFLICT` pattern to upsert.

## Production notes

- **Routing**: For offline Swiss routing, run OSRM with `switzerland-latest.osm.pbf` and set `OSRM_URL` and `ROUTING_PROVIDER=osrm`.
- **Optimization**: Replace the greedy solver in `app/geospatial/logistics.py` with Google OR-Tools VRP (capacity + time windows).
- **Alerts**: Call `app.geospatial.alerts.broadcast_inventory_alert(store_id, sku, qty)` when inventory drops below threshold (e.g. in ETL or a background job).
- **Semantic store search**: Use `app/geospatial/qdrant_stores.py` with a `provider_vectors` collection and multilingual embeddings on `capabilities_text`.
