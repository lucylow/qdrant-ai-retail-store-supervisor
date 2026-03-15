# Dynamic Vector

A multi-agent shopping assistant powered by Qdrant vector search. Built for the GenAI Zurich Hackathon 2026.

Dynamic Vector uses a conversational flow to understand customer needs, then searches across configured data sources using hybrid RAG to find personalized product matches.

## Architecture

```
┌─────────────────────┐     ┌──────────────────────┐
│  KMP Mobile App     │     │  React Web Frontend  │
│  (Android/iOS/JVM)  │     │  (Vite + shadcn/ui)  │
└────────┬────────────┘     └──────────┬───────────┘
         │                             │
         │    POST /token (JWT auth)   │
         └──────────┬──────────────────┘
                    ▼
         ┌─────────────────────┐
         │  server/             │  ← Lightweight auth server (no API keys needed)
         │  FastAPI + JWT       │
         └─────────────────────┘
                    │
                    ▼ (future)
         ┌─────────────────────┐
         │  backend/            │  ← Full multi-agent system (requires API keys)
         │  Qdrant + RAG       │
         └──┬──────────┬──────┘
            ▼          ▼
      ┌─────────┐ ┌─────────┐
      │ Qdrant  │ │  Redis  │
      └─────────┘ └─────────┘
```

## Monorepo Structure

```
├── composeApp/              # KMP app (Android, iOS, Desktop)
├── iosApp/                  # iOS Xcode project
├── server/                  # Lightweight FastAPI server (auth, health)
│   └── app/
│       ├── main.py          #   FastAPI entrypoint
│       └── auth.py          #   JWT auth (hardcoded demo accounts)
├── backend/                 # Full multi-agent system (requires API keys)
│   ├── app/                 #   FastAPI application + agents
│   │   ├── agents/          #   Shopper, Inventory, Pricing, Merchandising, Audit
│   │   └── routers/         #   Multilingual, voice, geospatial, checkout
│   ├── scripts/             #   Data ingestion, seeding
│   └── data/                #   Datasets
├── web/                     # React/TypeScript frontend
│   └── src/                 #   Pages, components, hooks
├── docker-compose.yml       # Run server + web with one command
└── .env.example             # Environment variables template (for backend/)
```

## Quick Start

### Option 1: Docker (recommended)

```shell
docker compose up --build
```

This starts:
- **Server** (auth + health) on http://localhost:8000
- **React web frontend** on http://localhost:8080

No API keys needed — the server module is self-contained.

### Option 2: Run services individually

**1. Start the server:**
```shell
cd server
pip install -r requirements.txt
uvicorn app.main:app --port 8000 --reload
```

**2. Start the web frontend:**
```shell
cd web
npm install
npm run dev
```

**3. Run the KMP mobile app** (see below).

### Running the full backend (optional)

The `backend/` module contains the full multi-agent system with Qdrant, RAG, and voice. It requires API keys configured in `.env` (see `.env.example`). It is not needed for frontend development.

```shell
cp .env.example .env
# Edit .env with your API keys
cd backend
pip install -r requirements.txt
uvicorn app.main:app --port 8000 --reload
```

## KMP Mobile App

The KMP app targets Android, iOS, and Desktop (JVM). Code structure:

- [commonMain](./composeApp/src/commonMain/kotlin) — Shared UI and logic across all platforms
- [androidMain](./composeApp/src/androidMain/kotlin) — Android-specific code
- [iosMain](./composeApp/src/iosMain/kotlin) — iOS-specific code
- [jvmMain](./composeApp/src/jvmMain/kotlin) — Desktop-specific code

### Build and Run Desktop (JVM)

```shell
./gradlew :composeApp:run
```

### Build and Run Android

```shell
./gradlew :composeApp:assembleDebug
```

Or use the run configuration in Android Studio / IntelliJ.

### Build and Run iOS

Open [/iosApp](./iosApp) in Xcode and run from there.

## Authentication

Auth uses hardcoded demo accounts with JWT tokens. All clients (KMP and React) authenticate against the same `POST /token` endpoint on the server. There is no registration route — this is intentional to block random visitors.

| Username | Password   | Intended Use               |
|----------|------------|----------------------------|
| `demo`   | `demo123`  | General testing            |
| `alice`  | `alice123` | Second persona             |
| `bob`    | `bob123`   | Third persona              |
| `judge`  | `judge123` | Hackathon judges           |

Accounts can be added/removed in `server/app/auth.py`.

## Server Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/token` | POST | Login (OAuth2 password flow) |
| `/users/me` | GET | Current user info (requires JWT) |
| `/health` | GET | Health check |

## Backend Endpoints (full system)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/query?q=...` | GET | Single-shot RAG answer |
| `/stream_query?q=...` | GET (SSE) | Streaming RAG answer |
| `/chat/swiss` | POST | Multilingual chat (DE/FR/IT/EN) |
| `/ws/voice/{tenant}` | WS | Bidirectional voice chat |
| `/products` | GET | Product catalog search |
| `/api/visual-search` | POST | CLIP image search |
| `/api/stores/nearby` | GET | Geospatial store locator |
| `/checkout/twint` | POST | TWINT payment |

## Backend Agents

- **ShopperAgent** — Extracts intent, budget, region, urgency from free-text queries
- **InventoryAgent** — Hybrid vector search on Qdrant, bundle optimization
- **PricingAgent** — Competitive pricing heuristics
- **MerchandisingAgent** — Promo text and layout generation
- **AuditAgent** — Hallucination detection + safety guardrails
- **Supervisor** — Orchestrates all agents in parallel phases

## Environment Variables

The `server/` module requires no environment variables.

The `backend/` module requires API keys. Copy `.env.example` to `.env` and fill in:

- `QDRANT_URL` / `QDRANT_API_KEY` — Qdrant Cloud connection
- `HF_TOKEN` — HuggingFace embeddings
- `OPENAI_API_KEY` — Whisper voice transcription
- `GROQ_API_KEY` — Agent reasoning (Mixtral)
- `REPLICATE_API_TOKEN` — Video keyframe embeddings
- `ELEVENLABS_API_KEY` — German TTS

## Tech Stack

- **Mobile:** Kotlin Multiplatform + Compose Multiplatform (Android, iOS, JVM Desktop)
- **Web:** React, TypeScript, Vite, shadcn/ui, TailwindCSS
- **Server:** Python, FastAPI, JWT auth
- **Backend:** Python, FastAPI, multi-agent orchestration
- **Vector DB:** Qdrant (hybrid text + image search)
- **Session Cache:** Redis (1hr TTL, max 10 turns)
- **HTTP Client (KMP):** Ktor Client
- **Auth:** JWT bearer tokens, hardcoded demo accounts
