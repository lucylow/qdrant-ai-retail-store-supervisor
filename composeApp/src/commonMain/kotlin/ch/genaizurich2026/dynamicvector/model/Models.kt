package ch.genaizurich2026.dynamicvector.model

data class UserProfile(
    val name: String,
    val username: String,
    val email: String,
    val phone: String,
    val location: String,
    val memberSince: String,
)

data class QueryFilter(
    val id: String,
    val type: FilterType,
    val label: String,
    val value: String,
    val active: Boolean,
)

enum class FilterType {
    CATEGORY, BRAND, PRICE, RATING, LOCATION, SUSTAINABILITY, CUSTOM
}

data class ShoppingQuery(
    val id: String,
    val name: String,
    val filters: List<QueryFilter>,
    val naturalLanguage: String,
    val createdAt: String,
    val scheduled: Boolean,
    val scheduleInterval: String? = null,
    val lastRun: String? = null,
)

data class ShoppingResult(
    val id: String,
    val name: String,
    val brand: String,
    val price: Double,
    val rating: Double,
    val matchScore: Int,
    val tags: List<ResultTag>,
    val source: String,
)

data class ResultTag(
    val label: String,
    val color: TagColor,
)

enum class TagColor {
    GREEN, BLUE, PURPLE
}

data class RepositoryPreferences(
    val goals: List<String>,
    val preferredBrands: List<String>,
    val sustainabilityPriority: String,
    val priceRange: Pair<Int, Int>,
    val values: List<String>,
    val customNotes: String,
)

data class Repository(
    val id: String,
    val name: String,
    val endpoint: String,
    val description: String,
    val createdAt: String,
    val preferences: RepositoryPreferences? = null,
)

data class AgentQuestion(
    val id: String,
    val type: FilterType,
    val question: String,
    val options: List<AgentOption>,
    val multiSelect: Boolean = false,
)

data class AgentOption(
    val id: String,
    val label: String,
    val value: String,
)

data class RefinementNote(
    val id: String,
    val text: String,
)

data class HistoryEntry(
    val id: String,
    val queryName: String,
    val ranAt: String,
    val resultCount: Int,
)
