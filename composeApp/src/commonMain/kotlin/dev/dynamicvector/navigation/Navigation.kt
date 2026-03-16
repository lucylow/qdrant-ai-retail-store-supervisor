package dev.dynamicvector.navigation

import dev.dynamicvector.model.ExploreSource
import dev.dynamicvector.model.QueryEvent

sealed class Screen {
    data object Login : Screen()
    data object Dashboard : Screen()
    data object Sources : Screen()
    data object Settings : Screen()
    data class EventDetail(val event: QueryEvent) : Screen()
    data object NewQuery : Screen()
    data class SourceDetail(val source: ExploreSource) : Screen()
    data object FolderBrowser : Screen()
}

enum class DVTab { DASHBOARD, SOURCES, SETTINGS }
enum class DashboardTab { RESULTS, QUERIES }
enum class SourcesTab { MY_SOURCES, EXPLORE }
enum class QueryCreationMode { DESCRIBE, BUILD, TEMPLATES }