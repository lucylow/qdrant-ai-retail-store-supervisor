package ch.genaizurich2026.dynamicvector

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import ch.genaizurich2026.dynamicvector.ui.components.DVBottomNav
import ch.genaizurich2026.dynamicvector.ui.screens.*
import ch.genaizurich2026.dynamicvector.ui.screens.sources.*

sealed class Screen {
    data object Dashboard : Screen()
    data object Sources : Screen()
    data object Settings : Screen()
    data class EventDetail(val event: QueryEvent) : Screen()
    data object NewQuery : Screen()
    data class SourceDetail(val source: ExploreSource) : Screen()
    data object FolderBrowser : Screen()
}

@Composable
fun DynamicVectorApp() {
    var currentTab by remember { mutableStateOf(DVTab.DASHBOARD) }
    var screen by remember { mutableStateOf<Screen?>(null) }
    var showFilters by remember { mutableStateOf(false) }
    var events by remember { mutableStateOf(MockData.events) }

    val toggleStar: (String) -> Unit = { id ->
        events = events.map { if (it.id == id) it.copy(isStarred = !it.isStarred) else it }
    }

    Scaffold(
        containerColor = DVColors.Background,
        bottomBar = {
            DVBottomNav(currentTab) { tab ->
                currentTab = tab
                screen = null
            }
        }
    ) { padding ->
        Box(Modifier.padding(padding).fillMaxSize()) {
            when (val s = screen) {
                is Screen.EventDetail -> EventDetailScreen(s.event) { screen = null }
                is Screen.NewQuery -> NewQueryScreen { screen = null }
                is Screen.SourceDetail -> SourceDetailScreen(s.source) { screen = null }
                is Screen.FolderBrowser -> FolderBrowserScreen { screen = null }
                else -> when (currentTab) {
                    DVTab.DASHBOARD -> DashboardHostScreen(
                        events = events,
                        savedQueries = MockData.savedQueries,
                        onEventClick = { screen = Screen.EventDetail(it) },
                        onFilterTap = { showFilters = true },
                        onNewQueryTap = { screen = Screen.NewQuery },
                        onQueryTap = { screen = Screen.NewQuery },
                        onToggleStar = toggleStar,
                    )
                    DVTab.SOURCES -> SourcesHostScreen(
                        onNavigateToDetail = { screen = Screen.SourceDetail(it) },
                        onNavigateToFolderBrowser = { screen = Screen.FolderBrowser },
                    )
                    DVTab.SETTINGS -> SettingsScreen()
                }
            }
        }
        FilterBottomSheet(showFilters) { showFilters = false }
    }
}
