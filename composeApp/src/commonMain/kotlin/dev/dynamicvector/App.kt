package dev.dynamicvector

import androidx.compose.animation.*
import androidx.compose.animation.core.tween
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import dev.dynamicvector.components.DVBottomNav
import dev.dynamicvector.data.ApiClient
import dev.dynamicvector.data.MockData
import dev.dynamicvector.navigation.DVTab
import dev.dynamicvector.navigation.Screen
import dev.dynamicvector.screens.*
import dev.dynamicvector.theme.DVColors
import dev.dynamicvector.theme.DynamicVectorTheme
import kotlinx.coroutines.launch

@Composable
fun App() {
    DynamicVectorTheme {
        var currentScreen by remember { mutableStateOf<Screen>(Screen.Login) }
        var currentTab by remember { mutableStateOf(DVTab.DASHBOARD) }
        var showFilters by remember { mutableStateOf(false) }
        var events by remember { mutableStateOf(MockData.events) }

        val isLoggedIn = currentScreen !is Screen.Login

        val toggleStar: (String) -> Unit = { id ->
            events = events.map { if (it.id == id) it.copy(isStarred = !it.isStarred) else it }
        }

        AnimatedContent(
            targetState = isLoggedIn,
            transitionSpec = {
                fadeIn(animationSpec = tween(durationMillis = 600, delayMillis = 100)) togetherWith
                        fadeOut(animationSpec = tween(durationMillis = 500))
            },
        ) { loggedIn ->
            if (!loggedIn) {
                LoginScreen(
                    onLoginSuccess = { currentScreen = Screen.Dashboard },
                )
            } else {
                Scaffold(
                    containerColor = DVColors.Background,
                    bottomBar = {
                        DVBottomNav(currentTab) { tab ->
                            currentTab = tab
                            currentScreen = when (tab) {
                                DVTab.DASHBOARD -> Screen.Dashboard
                                DVTab.SOURCES -> Screen.Sources
                                DVTab.SETTINGS -> Screen.Settings
                            }
                        }
                    }
                ) { padding ->
                    Box(Modifier.padding(padding).fillMaxSize()) {
                        when (val s = currentScreen) {
                            is Screen.EventDetail -> EventDetailScreen(s.event) { currentScreen = Screen.Dashboard; currentTab = DVTab.DASHBOARD }
                            is Screen.NewQuery -> NewQueryScreen { currentScreen = Screen.Dashboard; currentTab = DVTab.DASHBOARD }
                            is Screen.SourceDetail -> SourceDetailScreen(s.source) { currentScreen = Screen.Sources; currentTab = DVTab.SOURCES }
                            is Screen.FolderBrowser -> FolderBrowserScreen { currentScreen = Screen.Sources; currentTab = DVTab.SOURCES }
                            else -> when (currentTab) {
                                DVTab.DASHBOARD -> DashboardHostScreen(
                                    events = events,
                                    savedQueries = MockData.savedQueries,
                                    onEventClick = { currentScreen = Screen.EventDetail(it) },
                                    onFilterTap = { showFilters = true },
                                    onNewQueryTap = { currentScreen = Screen.NewQuery },
                                    onQueryTap = { currentScreen = Screen.NewQuery },
                                    onToggleStar = toggleStar,
                                )
                                DVTab.SOURCES -> SourcesHostScreen(
                                    onNavigateToDetail = { currentScreen = Screen.SourceDetail(it) },
                                    onNavigateToFolderBrowser = { currentScreen = Screen.FolderBrowser },
                                )
                                DVTab.SETTINGS -> SettingsScreen()
                            }
                        }
                    }
                    FilterBottomSheet(showFilters) { showFilters = false }
                }
            }
        }
    }
}
