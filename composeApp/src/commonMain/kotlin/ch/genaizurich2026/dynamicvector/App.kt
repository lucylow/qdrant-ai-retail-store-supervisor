package ch.genaizurich2026.dynamicvector

import androidx.compose.animation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import ch.genaizurich2026.dynamicvector.components.BottomNavBar
import ch.genaizurich2026.dynamicvector.navigation.BottomNavTab
import ch.genaizurich2026.dynamicvector.navigation.Screen
import ch.genaizurich2026.dynamicvector.screens.*
import ch.genaizurich2026.dynamicvector.theme.DynamicVectorTheme
import kotlinx.coroutines.launch

@Composable
fun App() {
    DynamicVectorTheme {
        var currentScreen by remember { mutableStateOf<Screen>(Screen.Login) }
        var selectedTab by remember { mutableStateOf(BottomNavTab.HOME) }
        val snackbarHostState = remember { SnackbarHostState() }
        val scope = rememberCoroutineScope()

        val showSnackbar: (String) -> Unit = { message ->
            scope.launch { snackbarHostState.showSnackbar(message) }
        }

        when (currentScreen) {
            is Screen.Login -> {
                LoginScreen(
                    onLogin = { currentScreen = Screen.Home },
                )
            }

            else -> {
                Box(modifier = Modifier.fillMaxSize()) {
                    Column(modifier = Modifier.fillMaxSize()) {
                        Box(modifier = Modifier.weight(1f)) {
                            when (currentScreen) {
                                is Screen.NewQuery -> {
                                    NewQueryScreen(
                                        onBack = {
                                            currentScreen = Screen.Home
                                            selectedTab = BottomNavTab.HOME
                                        },
                                        showSnackbar = showSnackbar,
                                    )
                                }
                                else -> {
                                    AnimatedContent(
                                        targetState = selectedTab,
                                        transitionSpec = {
                                            fadeIn() togetherWith fadeOut()
                                        },
                                    ) { tab ->
                                        when (tab) {
                                            BottomNavTab.HOME -> HomeScreen(
                                                onNewQuery = { currentScreen = Screen.NewQuery },
                                                showSnackbar = showSnackbar,
                                            )
                                            BottomNavTab.REPOSITORIES -> RepositoriesScreen(
                                                showSnackbar = showSnackbar,
                                            )
                                            BottomNavTab.PROFILE -> ProfileScreen(
                                                onSignOut = {
                                                    currentScreen = Screen.Login
                                                    selectedTab = BottomNavTab.HOME
                                                },
                                            )
                                        }
                                    }
                                }
                            }
                        }

                        BottomNavBar(
                            selectedTab = selectedTab,
                            onTabSelected = { tab ->
                                selectedTab = tab
                                currentScreen = when (tab) {
                                    BottomNavTab.HOME -> Screen.Home
                                    BottomNavTab.REPOSITORIES -> Screen.Repositories
                                    BottomNavTab.PROFILE -> Screen.Profile
                                }
                            },
                        )
                    }

                    // FAB for New Query - only on Home tab, not when already on NewQuery
                    if (selectedTab == BottomNavTab.HOME && currentScreen !is Screen.NewQuery) {
                        FloatingActionButton(
                            onClick = { currentScreen = Screen.NewQuery },
                            shape = CircleShape,
                            containerColor = MaterialTheme.colorScheme.primary,
                            contentColor = MaterialTheme.colorScheme.onPrimary,
                            modifier = Modifier
                                .padding(end = 20.dp, bottom = 92.dp)
                                .align(Alignment.BottomEnd),
                        ) {
                            Icon(
                                imageVector = Icons.Filled.Add,
                                contentDescription = "New Query",
                            )
                        }
                    }

                    // Snackbar host
                    SnackbarHost(
                        hostState = snackbarHostState,
                        modifier = Modifier
                            .align(Alignment.BottomCenter)
                            .padding(bottom = 80.dp),
                    )
                }
            }
        }
    }
}
