# Dynamic Vector

## Project Overview

Dynamic Vector is **Agent A** — a shopping assistant agent that interacts with customers to understand their needs and find the best products/services. It uses Qdrant as a vector database to store and retrieve context, enabling intelligent, personalized query results.

Agent A builds a user query through a multi-step conversational flow, then searches across configured **repositories** (data sources) to find matches. Each repository can have its own preferences (goals, price range, sustainability, brands, values) that shape how results are ranked.

## How Repositories Work

A repository is a data source that Agent A queries against. Each repository connects to one or more of:

- **Text sources** — documents, knowledge bases, or website content indexed into Qdrant
- **Scraped data** — product catalogs, pricing, and availability pulled from external sites
- **Location-aware results** — uses the user's location to surface nearby options, local inventory, and in-store pickup

Repositories store their connection endpoint and per-repo query preferences. When a user runs a query, Agent A combines the user's real-time filter selections with the repository's stored preferences to produce contextual, ranked results.

## Tech Stack

- **Kotlin Multiplatform** with Compose Multiplatform (targets: Android, iOS, JVM Desktop)
- **Package**: `ch.genaizurich2026.dynamicvector`
- **Module**: `:composeApp` (single shared module with platform-specific entry points)
- **Python/FastAPI** backend with multi-agent system, Qdrant vector DB, hybrid RAG (`backend/`)
- **React/TypeScript** frontend with Vite, shadcn/ui, TailwindCSS (`web/`)

## Monorepo Structure

```
├── composeApp/              # KMP (Android, iOS, Desktop only)
├── iosApp/                  # iOS Xcode project
├── gradle/, gradlew, etc.   # KMP build system
├── backend/                 # Python/FastAPI + agents + data pipelines
│   ├── app/                 #   FastAPI application + agents
│   ├── agents/              #   Agent demos/scripts
│   ├── scripts/             #   Data ingestion, seeding
│   ├── tests/               #   Python tests
│   ├── data/                #   Datasets (otto, retailrocket, amazon)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── README.md
├── web/                     # React/TypeScript frontend
│   ├── src/                 #   Pages, components, hooks, lib
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml
└── .env.example
```

## Build Commands

```
Android Debug:     ./gradlew :composeApp:assembleDebug
Desktop (JVM):     ./gradlew :composeApp:run
iOS:               Open iosApp/ in Xcode
KMP compile check: ./gradlew :composeApp:compileKotlinJvm :composeApp:compileDebugKotlinAndroid :composeApp:compileKotlinIosSimulatorArm64
Backend:           cd backend && uvicorn app.main:app --port 8000
Web frontend:      cd web && npm install && npm run dev
Docker (infra):    docker-compose up
```

## KMP Code Structure

```
composeApp/src/commonMain/kotlin/ch/genaizurich2026/dynamicvector/
├── App.kt                  — Main composable, navigation, theme
├── model/Models.kt         — Data classes (UserProfile, Repository, ShoppingQuery, etc.)
├── data/MockData.kt        — Dummy data for all screens
├── theme/Theme.kt          — Material3 light/dark theme
├── navigation/Navigation.kt — Screen sealed class, BottomNavTab enum
├── components/             — Shared UI components
│   ├── BottomNav.kt
│   ├── FilterChip.kt
│   ├── QueryBuilder.kt     — Multi-step agent query flow
│   ├── ResultCard.kt
│   └── SelectionSummary.kt
└── screens/                — Full-screen composables
    ├── LoginScreen.kt
    ├── HomeScreen.kt        — Saved queries + history tabs
    ├── NewQueryScreen.kt    — Query builder + results
    ├── ProfileScreen.kt     — User account info
    └── RepositoriesScreen.kt — Data sources with per-repo preferences
```

## Conventions

- All UI is in `commonMain` (shared across all platforms)
- Material3 with `compose.materialIconsExtended` for icons
- State-based navigation (no nav library) via `Screen` sealed class
- No network calls yet — all data is mock/dummy
- Backend code in `backend/` — do not modify logic, only infrastructure/config
- Web frontend in `web/` — React/TypeScript, do not modify logic