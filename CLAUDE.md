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

- **Kotlin Multiplatform** with Compose Multiplatform (targets: Android, iOS, JVM Desktop, JS, WasmJS)
- **Package**: `ch.genaizurich2026.dynamicvector`
- **Module**: `:composeApp` (single shared module with platform-specific entry points)

## Build Commands

```
Android Debug:    ./gradlew :composeApp:assembleDebug
Desktop (JVM):    ./gradlew :composeApp:run
Web (Wasm):       ./gradlew :composeApp:wasmJsBrowserDevelopmentRun
iOS:              Open iosApp/ in Xcode
All compile check: ./gradlew :composeApp:compileKotlinJvm :composeApp:compileDebugKotlinAndroid :composeApp:compileKotlinIosSimulatorArm64
```

## Code Structure

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
