# CLAUDE.md — Dynamic Vector

> This file is the single source of truth for Claude Code working on this project.
> It contains both operational instructions (how to work) and the project spec (what to build).

---

## Quick Reference

- **Package**: `ch.genaizurich2026.dynamicvector`
- **Deadline**: March 18, 2026 (remote build phase ends)
- **On-site demo**: April 1–2, 2026, Volkshaus Zürich
- **Hackathon**: GenAI Zürich Hackathon 2026 — "From Prompt to Product"
- **Partner challenges**: Qdrant (primary), Apify, LiveMap

---

## Operational Instructions for Claude Code

### Build & Run Commands

```bash
# KMP Mobile
./gradlew :composeApp:assembleDebug                # Android debug APK
./gradlew :composeApp:run                           # Desktop (JVM)
./gradlew :composeApp:compileKotlinJvm :composeApp:compileDebugKotlinAndroid :composeApp:compileKotlinIosSimulatorArm64  # Compile check (no device needed)

# Backend
cd backend && pip install -r requirements.txt       # Install deps
cd backend && uvicorn app.main:app --port 8000      # Run server
cd backend && python seed.py                        # Seed Qdrant with demo data

# Web Frontend
cd web && npm install && npm run dev                # Dev server
```

### Compile Verification

After any KMP/Compose change, always run the compile check:
```bash
./gradlew :composeApp:compileKotlinJvm
```
This catches type errors, missing imports, and Compose compiler issues without needing an emulator.

For backend changes:
```bash
cd backend && python -c "from app.main import app; print('OK')"
```

### Code Style & Conventions

**Kotlin/Compose:**
- All UI code under `ch.genaizurich2026.dynamicvector.ui.*`
- Use `DVColors`, `DVTypography`, `DVShapes` constants directly — do NOT use `MaterialTheme.colorScheme`
- All icons: `androidx.compose.material.icons.outlined.*` with **explicit tint** (never rely on `LocalContentColor`)
- Inactive icons: `DVColors.IconMuted` (`#7A7A90`), active: `DVColors.Teal` (`#4ECDC4`)
- State management: `remember`/`mutableStateOf` for hackathon; no ViewModel layer needed yet
- Bottom sheets: `ModalBottomSheet` with `containerColor = DVColors.Surface`, `shape = RoundedCornerShape(topStart = 24.dp, topEnd = 24.dp)`
- Card shadows: use `Modifier.drawBehind` with manual `drawRoundRect`, NOT `Modifier.shadow` (M3 doesn't support multi-layer)
- FAB: manually positioned in `Box` with `Modifier.align(Alignment.BottomEnd)`, NOT `Scaffold.floatingActionButton`

**Python/Backend:**
- FastAPI with async endpoints
- Pydantic v2 models in `app/models/`
- Executor functions in `app/agents/` — one file per block type
- `PipelineContext` threads through all steps sequentially
- Qdrant client via `qdrant-client` library
- LLM calls: `anthropic` SDK, model = `claude-sonnet-4-20250514`
- Env vars in `.env`: `QDRANT_URL`, `QDRANT_API_KEY`, `ANTHROPIC_API_KEY`, `APIFY_TOKEN`

**TypeScript/React (web):**
- React 18 + TypeScript + Vite + TailwindCSS + shadcn/ui
- CSS custom properties map 1:1 to DVColors (see Web GUI Design section)
- Types in `src/types/index.ts` mirror Kotlin data models for JSON compat

### What NOT to Do

- Do NOT add authentication/login — hackathon demo, no auth needed
- Do NOT use `currentColor` or `inherit` for icon colors — causes invisible icons on dark bg
- Do NOT use `Modifier.shadow()` for levitating cards — use `drawBehind` with 3-layer manual shadows
- Do NOT put the FAB in `Scaffold.floatingActionButton` — it's conditional (only Dashboard > Queries tab)
- Do NOT use `MaterialTheme.colorScheme` — the app uses custom `DVColors` directly
- Do NOT add Redis unless explicitly needed — keep infra simple for demo
- Do NOT build auth, Git source type, or scheduled query execution — these are cut items
- Do NOT over-engineer state management — `remember`/`mutableStateOf` is fine for the hackathon

### File Locations

```
/
├── composeApp/src/commonMain/kotlin/ch/genaizurich2026/dynamicvector/
│   ├── App.kt                  — Root entry, Scaffold + bottom nav
│   ├── Models.kt               — All data classes
│   ├── MockData.kt             — Hardcoded demo data
│   ├── Theme.kt                — DVColors, DVTypography, DVShapes, DVElevation
│   ├── Navigation.kt           — Screen sealed class + Voyager
│   └── ui/
│       ├── components/          — EventCard, StatusChip, SourceBadge, StaleNudge, etc.
│       ├── screens/             — Dashboard, EventDetail, NewQuery, Settings, etc.
│       └── screens/sources/     — Sources tab screens
├── backend/
│   ├── app/main.py              — FastAPI app
│   ├── app/config.py            — Qdrant client init, encoder init
│   ├── app/agents/              — One executor per block type
│   ├── app/models/              — Pydantic models
│   ├── app/routes/              — API route handlers
│   ├── app/executor.py          — Pipeline runner
│   ├── app/context.py           — PipelineContext dataclass
│   └── seed.py                  — Qdrant demo data seeder
├── web/src/                     — React frontend (secondary)
└── CLAUDE.md                    — This file
```

### Integration Status (as of March 16, 2026)

| Integration | Status | Notes |
|---|---|---|
| KMP ↔ Backend HTTP | ❌ Not connected | All KMP data is mock |
| Backend ↔ Qdrant | ✅ Connected | Need `seed.py` run for demo data |
| Backend ↔ Apify MCP | ⚠️ Stub | Agent exists, not implemented |
| Backend ↔ LiveMap | ⚠️ Stub | Agent exists, not implemented |
| Pipeline execution engine | ⚠️ Stub | `executor.py` needs dispatch logic |
| Stale detection | ⚠️ Not implemented | Need timestamp comparison |
| Interactive React demo | ✅ Built | Full prototype in Claude artifacts |

### Build Priority — What to Work On

**P0 — Critical for demo (must have):**
1. `seed.py` — 30+ Swiss products in Qdrant
2. `execute_search_qdrant` — hybrid dense+sparse search
3. `execute_suggest` — Claude Sonnet reasoning with AI explanations
4. `/api/pipelines/run` — end-to-end pipeline execution
5. KMP `ActionBlockCard` + `ParameterPill` (Shortcuts-style blocks)
6. KMP Dashboard event feed + Event Detail with AI explanations

**P1 — Important for polish:**
7. `execute_scrape_apify` — at least one working Apify actor
8. `execute_filter_location` + `execute_set_budget`
9. KMP Describe tab — NL → blocks
10. Stale detection
11. Connect KMP ↔ Backend HTTP

**P2 — Cut if behind:**
12. Web compose workspace, NL parser, templates, scheduled queries, folder browser

**Already cut:** Web frontend (demo mobile only if needed), Git source, auth, scheduled execution

### Key Demo Moments to Protect

Two flows that must work flawlessly for judges:

1. **Stale → Re-run flow**: An event marked amber "Stale" → user taps Re-run → new event with improved relevance scores. This proves dynamic context.
2. **AI explanation cards**: Each result shows italic text explaining *why* it ranked — tied to user goals ("aligns with your sustainability preference"). This proves effective GenAI use.

---

## Project Spec

### What It Is

Dynamic Vector is a **goal-driven suggestion engine** that continuously finds what you're looking for by combining multiple data sources, AI reasoning, and real-world context like location and budget.

Central idea: **define what you want → define your sources → let the system find it, continuously.**

Unlike traditional search (query once, static results), Dynamic Vector runs persistent queries that re-evaluate as underlying data changes. The system gets smarter over time without user action.

The platform is **domain-agnostic by design**. Hackathon showcase focuses on Swiss retail (Qdrant challenge), but architecture works for finance, healthcare, logistics, B2B.

### Partner Challenges

1. **Qdrant** (primary) — Dynamic vector context as a living, evolving data layer
2. **Apify** — Web scraping actors as configurable data sources, feeding into Qdrant
3. **LiveMap** (livemap.ch) — Swiss geospatial intelligence for location filtering

### Core Concept: Queries

A query defines:
1. **Goal** — NL description of what the user wants
2. **Sources** — which repos to pull from (Qdrant collections, Apify actors, local docs, LiveMap)
3. **Parameters** — per-source filters discovered dynamically from source schema
4. **Composition** — Union (merge), Intersection (overlap), Pipeline (chain)
5. **Schedule** (optional) — recurring or one-time auto-execution

**User goals** (in Settings) are persistent NL preferences applied to ALL queries automatically.

### Query Lifecycle

1. User creates query (NL describe or manual build)
2. Query saved to user's list
3. User runs manually (or schedules)
4. Each run → **QueryEvent** (immutable snapshot of results)
5. Events accumulate in Dashboard feed
6. When source data changes → event marked **Stale** (amber nudge)
7. Re-run → new event with improved results

### Composition Types

- **Pipeline** (primary, demoed): Step A → Step B → Step C (e.g., Qdrant search → Apify scrape → location filter → budget filter → AI suggest)
- **Union**: Merge results from multiple sources
- **Intersection**: Only results appearing in multiple sources

### Source Repositories

| Repository | Contains | Examples |
|---|---|---|
| Qdrant | Vector collections | `products`, HuggingFace datasets |
| Apify | Web scraping actors | Price trackers, Google Maps scrapers |
| LiveMap | Geospatial sources | User GPS, saved locations |
| Local | User-uploaded files | PDFs, CSVs, markdown |
| HuggingFace | Public datasets | `Qdrant/hm_ecommerce_products` |
| Git | Remote repos | Knowledge bases, versioned data |

Parameters are **discovered dynamically per individual source** (not per type). Two Qdrant collections expose different params based on their payload schema.

### The Dynamic Context Differentiator

Sources are continuously updated: Apify re-crawls, users upload new docs, collections grow. A query's results **improve over time** without user action.

**Apify → Qdrant flow:** Actor scrapes → data chunked + embedded → upserted into Qdrant collection → subsequent queries search enriched collection. Every run potentially enriches future runs.

Surfaced via **Stale** status: amber indicator when source data changed since last run. Re-run shows before/after improvement — core demo proof.

---

## Design System — Space-black Material 3

### Color Tokens

| Token | Value | Usage |
|---|---|---|
| Background | `#040410` | App bg |
| Surface | `#0C0C1A` | Bottom sheets, modals |
| SurfaceVariant | `rgba(255,255,255,0.04)` | Inputs, ghost buttons |
| CardBorder | `rgba(255,255,255,0.06)` | Default card borders |
| CardTopEdge | `rgba(78,205,196,0.2)` | Teal highlight on event cards |
| Teal | `#4ECDC4` | Primary accent |
| TealDim | `rgba(78,205,196,0.1)` | Active filter bg |
| TealBorder | `rgba(78,205,196,0.25)` | Active chip borders |
| TextPrimary | `#f0f0f5` | Headings |
| TextSecondary | `rgba(255,255,255,0.45)` | Body text |
| TextTertiary | `rgba(255,255,255,0.3)` | Captions |
| TextHint | `rgba(255,255,255,0.15)` | Placeholders |
| IconMuted | `#7A7A90` | Inactive icons |
| IconMutedLight | `#8A8A9E` | Slightly brighter muted |

### Status Colors

| Status | Color | Bg (12% alpha) |
|---|---|---|
| Live | `#4ECDC4` | `rgba(78,205,196,0.12)` |
| Done | `#7AB87A` | `rgba(120,180,120,0.12)` |
| Stale | `#F0B43C` | `rgba(240,180,60,0.12)` |
| Failed | `#DC5050` | `rgba(220,80,80,0.12)` |

### Source Badge Colors

| Source | Text | Bg | Border |
|---|---|---|---|
| Qdrant | `#A98AEF` | `rgba(120,80,220,0.15)` | `rgba(120,80,220,0.2)` |
| Apify | `#4CD9A0` | `rgba(0,180,120,0.12)` | `rgba(0,180,120,0.15)` |
| LiveMap | `#6CB0F0` | `rgba(60,140,240,0.12)` | `rgba(60,140,240,0.15)` |
| Local | `#C8A850` | `rgba(200,160,80,0.12)` | `rgba(200,160,80,0.15)` |
| HuggingFace | `#F0C840` | `rgba(255,200,60,0.10)` | `rgba(255,200,60,0.15)` |
| Git | `#F07850` | `rgba(240,120,80,0.10)` | `rgba(240,120,80,0.15)` |

### Levitating Card Style

- Background: `linearGradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02))`
- Border: 1px `rgba(255,255,255,0.06)`, top edge overridden to `rgba(78,205,196,0.2)`
- Radius: 20dp
- Shadow: 3-layer via `Modifier.drawBehind` — `0,0,0 @ 0.20` at 16dp offset, `0.15` at 8dp, `0.10` at 4dp

### Typography

| Style | Size | Weight |
|---|---|---|
| H1 | 20sp | Bold |
| H2 | 16sp | SemiBold |
| CardTitle | 15sp | SemiBold |
| Body | 13sp | Normal |
| Caption | 11sp | Normal |
| Label | 12sp | SemiBold, uppercase, 1.2sp tracking |
| Badge | 10sp | SemiBold |
| MetricValue | 14sp | SemiBold |

---

## Navigation Structure

**3-tab bottom nav**: Dashboard (Home), Sources (Database), Settings (Gear)

Active = teal + glow. Inactive = `IconMuted` at 75% opacity. Gradient fade background.

**No header bar** on Dashboard — search bar flush at top (44dp status bar inset).

### Screen Map

```
Bottom Nav
├── Dashboard
│   ├── Results (default) — event card feed
│   │   ├── Event Card tap → Event Detail
│   │   └── Filters button → Filter Bottom Sheet
│   └── Queries — saved query list
│       ├── Query Card tap → Query Builder (Build mode)
│       └── FAB (+) → New Query screen
│           ├── Describe mode
│           ├── Build mode (Shortcuts-style blocks)
│           └── Templates mode
├── Sources
│   ├── My Sources (default) — connected repos + local
│   │   └── Add local source → bottom sheet → Folder Browser
│   └── Explore — discovery + search + pull
│       └── Preview → Source Detail
└── Settings — goals, API keys, preferences, connection
```

---

## Screen Specs

### Dashboard — Results View

- Search bar: flush top, "Search events...", `surfaceVariant` bg, 16dp radius
- Filter row: teal filter button with count badge + dismissible chips
- Event cards (levitating): header (name + time), goal text, status chip (Live has pulsing 6dp dot), source badges, metrics (Results/Relevance/Sources), stale nudge (amber, conditional), actions (refresh/edit/delete + star)

### Dashboard — Queries View

- Query cards: name + composition badge, goal, source badges, step count, "Run" button, schedule indicator
- FAB: 56×56dp teal, `+` icon, bottom-right, only on this view

### Event Detail

- Back button + query name H1 + time/count/sources caption
- Source badges with detail labels
- "TOP RESULTS" section
- Result cards: rank + category (teal), name, description, tag pills, relevance progress bar (teal fill), AI explanation (italic, below divider)
- Staggered fadeIn animation (0.08s per card)

### New Query — 3 Modes

- **Describe**: Teal AI panel, text area, "✦ Generate query" button, generated pipeline preview (color-coded steps with ↓ arrows)
- **Build**: Shortcuts-style blocks with inline parameter pills, "Add step" dashed button, text refinement field
- **Templates**: Amber search, category chips, 2-column grid of template cards

### Pipeline Block Types

| Type | Colors (bg/border/pill) |
|---|---|
| search_qdrant | Purple tones |
| scrape_apify | Green tones |
| filter_location | Blue tones |
| set_budget | Amber tones |
| suggest | Teal tones |
| if_otherwise | Gray tones |

Blocks use `FlowRow` for text + pill wrapping. Each pill is tappable. Blocks connected by "↓" arrows.

### Sources — My Sources

- Connected repos grouped by type with colored dots + count
- Local sources section
- "Add local source" amber dashed button → bottom sheet (Folder/Files/Photo/URL)

### Sources — Explore

- Own teal search bar (separate from My Sources search)
- Category chips: All, Qdrant, HuggingFace, Apify, Git, LiveMap
- Explore cards: name + badge, description, stats, actions (Preview/Bookmark/Pull)
- Source Detail: repo-colored hero, stats grid, Pull + Bookmark, schema, sample record

### Settings

- User goals: teal-bordered NL cards with ◆ icon + "Add goal" dashed button
- API keys: Qdrant/Apify/Anthropic (masked + chevron)
- Preferences: location, currency, notifications toggle, dark mode toggle
- Connection status: backend URL + green dot
- Switch: 44×24dp, teal thumb+track when on

### Filter Bottom Sheet

- Drag handle + "Filters" title
- Groups: Order by (single), Status (multi), Date range (single), Sources (multi)
- Selected pills: `tealDim` bg + teal text. Unselected: `surfaceVariant`
- Full-width "Apply filters" teal button

---

## Kotlin Implementation Reference

### DVColors Object

```kotlin
object DVColors {
    val Background     = Color(0xFF040410)
    val Surface        = Color(0xFF0C0C1A)
    val SurfaceVariant = Color(0x0DFFFFFF)
    val CardGradientStart = Color(0x0DFFFFFF)
    val CardGradientEnd   = Color(0x05FFFFFF)
    val CardBorder     = Color(0x0FFFFFFF)
    val CardTopEdge    = Color(0x334ECDC4)
    val Teal           = Color(0xFF4ECDC4)
    val TealDim        = Color(0x1A4ECDC4)
    val TealBorder     = Color(0x404ECDC4)
    val TextPrimary    = Color(0xFFF0F0F5)
    val TextSecondary  = Color(0x73FFFFFF)
    val TextTertiary   = Color(0x4DFFFFFF)
    val TextHint       = Color(0x26FFFFFF)
    val IconMuted      = Color(0xFF7A7A90)
    val IconMutedLight = Color(0xFF8A8A9E)
    val StatusLive     = Color(0xFF4ECDC4)
    val StatusDone     = Color(0xFF7AB87A)
    val StatusStale    = Color(0xFFF0B43C)
    val StatusFailed   = Color(0xFFDC5050)
    val Qdrant         = Color(0xFFA98AEF)
    val QdrantBg       = Color(0x267850DC)
    val Apify          = Color(0xFF4CD9A0)
    val ApifyBg        = Color(0x1F00B478)
    val LiveMap        = Color(0xFF6CB0F0)
    val LiveMapBg      = Color(0x1F3C8CF0)
    val Local          = Color(0xFFC8A850)
    val LocalBg        = Color(0x1FC8A050)
    val HuggingFace    = Color(0xFFF0C840)
    val HuggingFaceBg  = Color(0x1AFFC83C)
    val StarActive     = Color(0xFFF0B43C)
}
```

### Enumerations

```kotlin
enum class QueryStatus { LIVE, DONE, STALE, FAILED }
enum class SourceType { QDRANT, APIFY, LIVEMAP, LOCAL, GIT, HUGGINGFACE }
enum class CompositionType { PIPELINE, UNION, INTERSECTION }
enum class DVTab { DASHBOARD, SOURCES, SETTINGS }
enum class DashboardTab { RESULTS, QUERIES }
enum class SourcesTab { MY_SOURCES, EXPLORE }
enum class QueryCreationMode { DESCRIBE, BUILD, TEMPLATES }
enum class BlockType { SEARCH_QDRANT, SCRAPE_APIFY, FILTER_LOCATION, SET_BUDGET, SUGGEST, IF_OTHERWISE }
```

### Data Models

```kotlin
data class QueryEvent(
    val id: String, val queryName: String, val goal: String,
    val timeAgo: String, val status: QueryStatus, val sources: List<SourceType>,
    val resultCount: Int, val relevanceScore: Float, val isStarred: Boolean,
    val results: List<QueryResult> = emptyList(),
)

data class QueryResult(
    val rank: Int, val category: String, val name: String,
    val description: String, val tags: List<String>,
    val relevance: Float, val explanation: String,
)

data class SavedQuery(
    val id: String, val name: String, val goal: String,
    val compositionType: CompositionType, val sources: List<SourceType>,
    val stepCount: Int, val lastResultCount: Int = 0,
    val schedule: String? = null, val steps: List<PipelineStep> = emptyList(),
)

data class PipelineStep(val type: BlockType, val segments: List<StepSegment>)

sealed class StepSegment {
    data class TextPart(val text: String) : StepSegment()
    data class PillPart(val label: String, val onTap: () -> Unit = {}) : StepSegment()
}

data class ExploreSource(
    val id: String, val name: String, val repoType: SourceType,
    val description: String, val providerInfo: String = "",
    val stats: List<Pair<String, String>>,
    val isBookmarked: Boolean = false, val isAlreadySaved: Boolean = false,
    val schema: List<SchemaField> = emptyList(),
    val sampleRecord: List<Pair<String, String>> = emptyList(),
)
```

### Key Compose Patterns

**3-Layer Shadow (drawBehind):**
```kotlin
Modifier.drawBehind {
    drawRoundRect(Color.Black.copy(0.10f), cornerRadius = CornerRadius(20.dp.toPx()),
        topLeft = Offset(0f, 16.dp.toPx()), size = size.copy(height = size.height + 16.dp.toPx()))
    drawRoundRect(Color.Black.copy(0.15f), cornerRadius = CornerRadius(20.dp.toPx()),
        topLeft = Offset(0f, 8.dp.toPx()), size = size.copy(height = size.height + 8.dp.toPx()))
}
```

**Pulsing Live Dot:**
```kotlin
val alpha by rememberInfiniteTransition(label = "pulse").animateFloat(
    1f, 0.3f, infiniteRepeatable(tween(1000), RepeatMode.Reverse), label = "pulseAlpha")
Box(Modifier.size(6.dp).background(DVColors.StatusLive.copy(alpha), CircleShape))
```

**Dashed Border:**
```kotlin
Modifier.drawBehind {
    drawRoundRect(color, CornerRadius(14.dp.toPx()),
        style = Stroke(1.dp.toPx(), pathEffect = PathEffect.dashPathEffect(floatArrayOf(8.dp.toPx(), 4.dp.toPx()))))
}
```

**Pipeline Block (FlowRow):**
```kotlin
FlowRow(modifier = Modifier.background(blockBg, RoundedCornerShape(14.dp))
    .border(1.dp, blockBorder, RoundedCornerShape(14.dp)).padding(14.dp),
    horizontalArrangement = Arrangement.spacedBy(4.dp),
    verticalArrangement = Arrangement.spacedBy(4.dp)) {
    step.segments.forEach { when (it) {
        is StepSegment.TextPart -> Text(it.text, fontSize = 13.sp, color = DVColors.TextSecondary)
        is StepSegment.PillPart -> Box(Modifier.background(pillBg, RoundedCornerShape(8.dp))
            .clickable(onClick = it.onTap).padding(horizontal = 10.dp, vertical = 2.dp)) {
            Text(it.label, fontSize = 12.sp, fontWeight = FontWeight.SemiBold, color = pillText)
        }
    }}
}
```

---

## Backend Architecture

### Pipeline Execution

```
POST /api/pipelines/run { blocks: [...] }
  → Sequential executor
  → PipelineContext threads through each step
  → Each block dispatches to executor function
  → Final "suggest" block → Claude Sonnet reasoning
  → Returns QueryEvent with ranked results
```

### Executor Functions

| Block | Executor | Action |
|---|---|---|
| search_qdrant | `execute_search_qdrant()` | Hybrid search (dense all-MiniLM-L6-v2 384d + sparse bm25) |
| scrape_apify | `execute_scrape_apify()` | Run actor → upsert into Qdrant collection |
| filter_location | `execute_filter_location()` | Filter by distance from GPS coord |
| set_budget | `execute_set_budget()` | Filter by price range |
| suggest | `execute_suggest()` | Claude Sonnet: rank + explain results |
| if_otherwise | `execute_conditional()` | Branch pipeline on condition |

### Qdrant Schema — `products` Collection

```json
{
  "vectors": {
    "dense": { "size": 384, "distance": "Cosine" },
    "sparse": { "name": "bm25", "modifier": "idf" }
  },
  "payload_schema": {
    "name": "keyword", "brand": "keyword", "category": "keyword",
    "price": "float", "currency": "keyword", "description": "text",
    "location_city": "keyword", "location_lat": "float", "location_lon": "float",
    "retailer": "keyword", "tags": "keyword[]", "url": "keyword", "last_updated": "datetime"
  }
}
```

### API Endpoints

| Endpoint | Method | Priority |
|---|---|---|
| `/health` | GET | ✅ Done |
| `/api/pipelines/run` | POST | P0 |
| `/api/pipelines` | GET/POST | P1 |
| `/api/events` | GET | P1 |
| `/api/events/{id}` | GET | P1 |
| `/api/sources/qdrant/collections` | GET | P1 |
| `/api/sources/apify/actors` | GET | P2 |
| `/api/sources/livemap/location` | GET | P2 |
| `/api/goals` | GET/POST | P2 |
| `/api/pipelines/describe` | POST | P2 |

---

## Web GUI (Secondary Platform)

Uses same Space-black tokens as CSS custom properties:

```css
:root {
  --bg: #040410; --surface: #0C0C1A; --teal: #4ECDC4;
  --text-pri: #f0f0f5; --text-sec: rgba(255,255,255,0.45);
  --icon-muted: #7A7A90;
}
```

**Key differences from mobile:**
- Dashboard: split-pane (event list left + detail right)
- Compose: 3-column (source library + blocks + live preview)
- Parameter editing: popovers instead of inline expansion
- Tech: React 18 + TypeScript + Vite + TailwindCSS + shadcn/ui

---

## Demo Script — 8 Steps

1. **Goals**: Settings → show persistent NL goals
2. **Describe**: FAB → NL input → "✦ Generate" → pipeline preview
3. **Build**: Switch to Build tab → edit pills, reorder blocks
4. **Run**: "Save & run" → event appears with Live status
5. **Results** ⭐: Event Detail → ranked cards with AI explanations tied to goals
6. **Stale** ⭐: Older event → amber nudge → Re-run → improved scores
7. **Sources**: Connected repos, Explore → search, preview schema, pull
8. **Pitch**: "Static search → living suggestion engine. Context evolves. Results improve."

Steps 5 and 6 are the KEY demo moments — protect these above all else.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Mobile | KMP + Compose Multiplatform |
| Web | React 18 + TypeScript + Vite + Tailwind + shadcn/ui |
| Backend | Python 3.11+ / FastAPI |
| Vector DB | Qdrant Cloud |
| Dense embeddings | all-MiniLM-L6-v2 (384d) |
| Sparse embeddings | Qdrant/bm25 |
| LLM | Claude Sonnet (anthropic SDK) |
| Web scraping | Apify MCP |
| Geospatial | LiveMap AG |
| KMP Navigation | Voyager |
