# Dynamic Vector — Frontend

React app for Dynamic Vector: users broadcast intents on the map, providers receive requests and bid, users pick an offer.

## Quick setup

- **Node.js** 18+
- **Mapbox token:** `REACT_APP_MAPBOX_TOKEN` (optional; without it the map area shows a placeholder)
- **Backend base URL:** `REACT_APP_API_BASE` (e.g. `http://localhost:8000`)
- **WebSocket URL:** `REACT_APP_WS_BASE` (e.g. `ws://localhost:8000/ws`)

```bash
cd web/live-map
npm install
npm start
```

If `REACT_APP_API_BASE` is not set, the app runs in **demo mode**: intents and bids are simulated in the browser (localStorage + in-memory event bus). You can present the full flow without the FastAPI backend.

## Env vars

| Variable | Description |
|----------|-------------|
| `REACT_APP_MAPBOX_TOKEN` | Mapbox GL token for map tiles |
| `REACT_APP_API_BASE` | FastAPI base URL (e.g. `http://localhost:8000`). Empty = demo mode. |
| `REACT_APP_WS_BASE` | WebSocket base (e.g. `ws://localhost:8000`). Used for real-time events. |

## Backend integration

The frontend calls:

- **POST** `${API_BASE}/livemap/intent` — create intent (body: `user_id`, `text`, `lat`, `lon`, `radius_m`, `max_walk_minutes`, `ttl_minutes`, `exact_share`). Returns full intent including `intent_id`.
- **GET** `${API_BASE}/livemap/intent/{intent_id}/candidates` — list candidates (optional; used for user view).
- **POST** `${API_BASE}/livemap/intent/{intent_id}/bid` — provider submits bid (body: `provider_id`, `price_cents`, `eta_minutes`, `notes`).
- **POST** `${API_BASE}/livemap/intent/{intent_id}/choose` — user selects a bid (body: `{ "bid_id": "..." }`).
- **GET** `${API_BASE}/livemap/intent/{intent_id}/bids` — list bids for an intent (for user's offers panel).

WebSocket: backend can broadcast `intent.created` and `bid.submitted` to provider channels. Connect to e.g. `REACT_APP_WS_BASE/events`.

## Map

Uses **react-map-gl** (Mapbox GL). If you prefer no Mapbox, swap the map component for Leaflet + OSM tiles.

## Repo integration

This app lives under `web/live-map`. The main FastAPI app is in `app/`; livemap routes are in `app/livemap_api.py`. Add bid/choose endpoints there and optionally a WebSocket broadcaster for real-time provider updates.
