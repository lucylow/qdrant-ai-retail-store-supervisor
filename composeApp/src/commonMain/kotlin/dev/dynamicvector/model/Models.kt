package dev.dynamicvector.model

import androidx.compose.ui.graphics.Color
import dev.dynamicvector.theme.DVColors

enum class QueryStatus { LIVE, DONE, STALE, FAILED }
enum class SourceType { QDRANT, APIFY, LIVEMAP, LOCAL, GIT, HUGGINGFACE }
enum class CompositionType { PIPELINE, UNION, INTERSECTION }
enum class BlockType { SEARCH_QDRANT, SCRAPE_APIFY, FILTER_LOCATION, SET_BUDGET, SUGGEST, IF_OTHERWISE }

data class QueryEvent(
    val id: String,
    val queryName: String,
    val goal: String,
    val timeAgo: String,
    val status: QueryStatus,
    val sources: List<SourceType>,
    val resultCount: Int,
    val relevanceScore: Float,
    val isStarred: Boolean,
    val results: List<QueryResult> = emptyList(),
)

data class QueryResult(
    val rank: Int,
    val category: String,
    val name: String,
    val description: String,
    val tags: List<String>,
    val relevance: Float,
    val explanation: String,
)

data class SavedQuery(
    val id: String,
    val name: String,
    val goal: String,
    val compositionType: CompositionType,
    val sources: List<SourceType>,
    val stepCount: Int,
    val lastResultCount: Int = 0,
    val schedule: String? = null,
    val steps: List<PipelineStep> = emptyList(),
)

data class PipelineStep(
    val type: BlockType,
    val segments: List<StepSegment>,
)

sealed class StepSegment {
    data class TextPart(val text: String) : StepSegment()
    data class PillPart(val label: String) : StepSegment()
}

data class Repository(
    val name: String,
    val type: SourceType,
    val unitLabel: String,
    val sources: List<SavedSource>,
)

data class SavedSource(val name: String, val meta: String, val isOnline: Boolean = true)
data class LocalSource(val displayName: String, val meta: String, val isFolder: Boolean)

data class ExploreSource(
    val id: String,
    val name: String,
    val repoType: SourceType,
    val description: String,
    val providerInfo: String = "",
    val stats: List<Pair<String, String>>,
    val isBookmarked: Boolean = false,
    val isAlreadySaved: Boolean = false,
    val schema: List<SchemaField> = emptyList(),
    val sampleRecord: List<Pair<String, String>> = emptyList(),
)

data class SchemaField(val name: String, val type: String)
data class FileItem(val name: String, val isFolder: Boolean, val meta: String, val isSelected: Boolean = false)
data class QueryTemplate(val icon: String, val name: String, val description: String, val sources: List<SourceType>, val iconBg: Color)
data class AddLocalOption(val icon: String, val title: String, val description: String, val bgColor: Color)

fun SourceType.colors(): Triple<Color, Color, Color> = when (this) {
    SourceType.QDRANT      -> Triple(DVColors.Qdrant, DVColors.QdrantBg, DVColors.QdrantBd)
    SourceType.APIFY       -> Triple(DVColors.Apify, DVColors.ApifyBg, DVColors.ApifyBd)
    SourceType.LIVEMAP     -> Triple(DVColors.LiveMap, DVColors.LiveMapBg, DVColors.LiveMapBd)
    SourceType.LOCAL       -> Triple(DVColors.Local, DVColors.LocalBg, DVColors.LocalBd)
    SourceType.GIT         -> Triple(DVColors.Git, DVColors.GitBg, DVColors.GitBd)
    SourceType.HUGGINGFACE -> Triple(DVColors.HuggingFace, DVColors.HuggingFaceBg, DVColors.HuggingFaceBd)
}

fun SourceType.label(): String = when (this) {
    SourceType.QDRANT -> "Qdrant"; SourceType.APIFY -> "Apify"; SourceType.LIVEMAP -> "LiveMap"
    SourceType.LOCAL -> "Local"; SourceType.GIT -> "Git"; SourceType.HUGGINGFACE -> "HuggingFace"
}

fun QueryStatus.color(): Color = when (this) {
    QueryStatus.LIVE -> DVColors.StatusLive; QueryStatus.DONE -> DVColors.StatusDone
    QueryStatus.STALE -> DVColors.StatusStale; QueryStatus.FAILED -> DVColors.StatusFailed
}

fun BlockType.colors(): BlockColors = when (this) {
    BlockType.SEARCH_QDRANT   -> BlockColors(DVColors.Qdrant.copy(0.10f), DVColors.Qdrant.copy(0.20f), DVColors.Qdrant.copy(0.25f), DVColors.Qdrant)
    BlockType.SCRAPE_APIFY    -> BlockColors(DVColors.Apify.copy(0.08f), DVColors.Apify.copy(0.15f), DVColors.Apify.copy(0.20f), DVColors.Apify)
    BlockType.FILTER_LOCATION -> BlockColors(DVColors.LiveMap.copy(0.08f), DVColors.LiveMap.copy(0.15f), DVColors.LiveMap.copy(0.20f), DVColors.LiveMap)
    BlockType.SET_BUDGET      -> BlockColors(DVColors.StatusStale.copy(0.08f), DVColors.StatusStale.copy(0.15f), DVColors.StatusStale.copy(0.20f), DVColors.StatusStale)
    BlockType.SUGGEST         -> BlockColors(DVColors.Accent.copy(0.08f), DVColors.Accent.copy(0.15f), DVColors.Accent.copy(0.20f), DVColors.Accent)
    BlockType.IF_OTHERWISE    -> BlockColors(DVColors.TextTertiary.copy(0.08f), DVColors.TextTertiary.copy(0.15f), DVColors.TextTertiary.copy(0.20f), DVColors.TextTertiary)
}

data class BlockColors(val bg: Color, val border: Color, val pillBg: Color, val pillText: Color)
