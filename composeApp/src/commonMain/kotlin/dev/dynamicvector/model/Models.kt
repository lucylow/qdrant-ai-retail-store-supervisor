package dev.dynamicvector.model

// ── Context: the core abstraction over a knowledge domain ────────────────────

/**
 * What backs a Context's data.
 */
enum class ContextSourceType {
    /** Qdrant collection — products, documents, embeddings. */
    VECTOR_COLLECTION,
    /** Live web scraping agent — pulls fresh data on query. */
    SCRAPING_AGENT,
    /** Local or uploaded document repository. */
    DOCUMENT_STORE,
    /** The user's own profile — enriches other Contexts with defaults. */
    USER_PROFILE,
    /** External REST/GraphQL API. */
    API_ENDPOINT,
}

/**
 * Connection details for a Context's backing data source.
 */
data class ContextSourceConfig(
    val collectionName: String? = null,
    val endpoint: String? = null,
    val embeddingModel: String? = null,
    val defaultFilters: Map<String, String> = emptyMap(),
)

/**
 * A question that a Context needs answered to scope its search.
 * For example, a shopping Context asks about price range;
 * a documents Context might ask about date range or topic.
 */
data class ContextQuestion(
    val id: String,
    val fieldKey: String,
    val question: String,
    val options: List<dev.dynamicvector.model.ContextOption>,
    val required: Boolean = false,
    val multiSelect: Boolean = false,
)

data class ContextOption(
    val id: String,
    val label: String,
    val value: String,
)

/**
 * Describes a field that results from this Context will carry.
 */
data class ResultFieldSchema(
    val key: String,
    val label: String,
    val type: dev.dynamicvector.model.FieldType,
    val sortable: Boolean = false,
    val filterable: Boolean = false,
)

enum class FieldType {
    STRING, NUMBER, PRICE, RATING, BOOLEAN, URL, GEO_POINT, TAGS,
}

/**
 * A Context is the core type for interfacing with Qdrant.
 *
 * It determines:
 * - the special knowledge configured in the vector database
 * - what questions every query through this Context must answer
 * - the shape of results it produces
 *
 * A user's profile is itself a Context (sourceType = USER_PROFILE)
 * whose answers can enrich any other Context's queries.
 */
data class Context(
    val id: String,
    val name: String,
    val description: String,
    val sourceType: dev.dynamicvector.model.ContextSourceType,
    val sourceConfig: dev.dynamicvector.model.ContextSourceConfig,
    val questions: List<dev.dynamicvector.model.ContextQuestion>,
    val resultSchema: List<dev.dynamicvector.model.ResultFieldSchema>,
    val active: Boolean = true,
    val createdAt: String,
)

// ── Context composition ──────────────────────────────────────────────────────

/**
 * How two or more Contexts combine.
 *
 * - AND:     intersect — results must satisfy ALL contexts
 * - OR:      union — results from ANY context
 * - CHAIN:   pipeline — query → Context1 → result set → Context2
 * - ENRICH:  one Context augments another (e.g. user profile → shopping)
 */
enum class ContextCompositionType {
    AND,
    OR,
    CHAIN,
    ENRICH,
}

data class ContextComposition(
    val id: String,
    val name: String,
    val type: dev.dynamicvector.model.ContextCompositionType,
    val contextIds: List<String>,
)

// ── Query ────────────────────────────────────────────────────────────────────

/**
 * A user's answer to a [dev.dynamicvector.model.ContextQuestion].
 */
data class ContextAnswer(
    val questionId: String,
    val fieldKey: String,
    val selectedValues: List<String>,
    val label: String,
)

/**
 * A query executed against one or more Contexts.
 */
data class ContextQuery(
    val id: String,
    val name: String,
    val contextIds: List<String>,
    val composition: dev.dynamicvector.model.ContextComposition? = null,
    val answers: List<dev.dynamicvector.model.ContextAnswer>,
    val naturalLanguage: String,
    val exclusions: List<String> = emptyList(),
    val createdAt: String,
    val scheduled: Boolean = false,
    val scheduleInterval: String? = null,
    val lastRun: String? = null,
)

// ── Results ──────────────────────────────────────────────────────────────────

enum class TagColor {
    GREEN, BLUE, PURPLE,
}

data class ResultTag(
    val label: String,
    val color: dev.dynamicvector.model.TagColor,
)

/**
 * A single result item, generic across Context types.
 * Core display fields are typed; anything extra goes in [metadata].
 */
data class ContextResultItem(
    val id: String,
    val contextId: String,
    val matchScore: Int,
    val title: String,
    val subtitle: String,
    val price: Double? = null,
    val rating: Double? = null,
    val imageUrl: String? = null,
    val source: String,
    val tags: List<dev.dynamicvector.model.ResultTag>,
    val metadata: Map<String, String> = emptyMap(),
)

/**
 * The full result set from a query.
 *
 * [suggestedRefinements] are auto-generated questions derived from the
 * result distribution — answering one re-executes the query with tighter
 * filters, analogous to an INNER JOIN that narrows the set.
 */
data class ContextResultSet(
    val queryId: String,
    val items: List<dev.dynamicvector.model.ContextResultItem>,
    val totalCount: Int,
    val suggestedRefinements: List<dev.dynamicvector.model.ContextQuestion>,
    val executedAt: String,
)

// ── User profile ─────────────────────────────────────────────────────────────

/**
 * The user's account info.
 * [contextId] links to the USER_PROFILE Context whose stored answers
 * (location, preferred brands, budget, etc.) can enrich other Contexts.
 */
data class UserProfile(
    val name: String,
    val username: String,
    val email: String,
    val phone: String,
    val location: String,
    val memberSince: String,
    val contextId: String? = null,
)

// ── History ──────────────────────────────────────────────────────────────────

data class HistoryEntry(
    val id: String,
    val queryName: String,
    val ranAt: String,
    val resultCount: Int,
    val contextNames: List<String> = emptyList(),
)

// ── Sort ─────────────────────────────────────────────────────────────────────

enum class SortOption {
    MATCH, PRICE_ASC, PRICE_DESC, RATING,
}