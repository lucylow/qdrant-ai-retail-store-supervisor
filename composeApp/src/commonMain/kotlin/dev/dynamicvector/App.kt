package dev.dynamicvector

import androidx.compose.animation.*
import androidx.compose.animation.core.tween
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import dev.dynamicvector.components.BottomNavBar
import dev.dynamicvector.navigation.BottomNavTab
import dev.dynamicvector.navigation.Screen
import dev.dynamicvector.screens.*
import dev.dynamicvector.theme.DynamicVectorTheme
import kotlinx.coroutines.launch

@Composable
fun App() {
    _root_ide_package_.dev.dynamicvector.theme.DynamicVectorTheme {
        var currentScreen by remember {
            mutableStateOf<dev.dynamicvector.navigation.Screen>(
                _root_ide_package_.dev.dynamicvector.navigation.Screen.Login
            )
        }
        var selectedTab by remember { mutableStateOf(_root_ide_package_.dev.dynamicvector.navigation.BottomNavTab.HOME) }
        val snackbarHostState = remember { SnackbarHostState() }
        val scope = rememberCoroutineScope()

        val showSnackbar: (String) -> Unit = { message ->
            scope.launch { snackbarHostState.showSnackbar(message) }
        }

        val isLoggedIn = currentScreen !is dev.dynamicvector.navigation.Screen.Login

        AnimatedContent(
            targetState = isLoggedIn,
            transitionSpec = {
                fadeIn(
                    animationSpec = tween(durationMillis = 600, delayMillis = 100),
                ) togetherWith fadeOut(
                    animationSpec = tween(durationMillis = 500),
                )
            },
        ) { loggedIn ->
            if (!loggedIn) {
                _root_ide_package_.dev.dynamicvector.screens.LoginScreen(
                    onLoginSuccess = {
                        currentScreen = _root_ide_package_.dev.dynamicvector.navigation.Screen.Home
                    },
                )
            } else {
                Box(modifier = Modifier.fillMaxSize()) {
                    Column(modifier = Modifier.fillMaxSize()) {
                        Box(modifier = Modifier.weight(1f)) {
                            when (currentScreen) {
                                is dev.dynamicvector.navigation.Screen.NewQuery -> {
                                    _root_ide_package_.dev.dynamicvector.screens.NewQueryScreen(
                                        onBack = {
                                            currentScreen =
                                                _root_ide_package_.dev.dynamicvector.navigation.Screen.Home
                                            selectedTab =
                                                _root_ide_package_.dev.dynamicvector.navigation.BottomNavTab.HOME
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
                                            _root_ide_package_.dev.dynamicvector.navigation.BottomNavTab.HOME -> _root_ide_package_.dev.dynamicvector.screens.HomeScreen(
                                                onNewQuery = {
                                                    currentScreen =
                                                        _root_ide_package_.dev.dynamicvector.navigation.Screen.NewQuery
                                                },
                                                showSnackbar = showSnackbar,
                                            )

                                            _root_ide_package_.dev.dynamicvector.navigation.BottomNavTab.CONTEXTS -> _root_ide_package_.dev.dynamicvector.screens.ContextsScreen(
                                                showSnackbar = showSnackbar,
                                            )

                                            _root_ide_package_.dev.dynamicvector.navigation.BottomNavTab.PROFILE -> _root_ide_package_.dev.dynamicvector.screens.ProfileScreen(
                                                onSignOut = {
                                                    currentScreen =
                                                        _root_ide_package_.dev.dynamicvector.navigation.Screen.Login
                                                    selectedTab =
                                                        _root_ide_package_.dev.dynamicvector.navigation.BottomNavTab.HOME
                                                },
                                            )
                                        }
                                    }
                                }
                            }
                        }

                        _root_ide_package_.dev.dynamicvector.components.BottomNavBar(
                            selectedTab = selectedTab,
                            onTabSelected = { tab ->
                                selectedTab = tab
                                currentScreen = when (tab) {
                                    _root_ide_package_.dev.dynamicvector.navigation.BottomNavTab.HOME -> _root_ide_package_.dev.dynamicvector.navigation.Screen.Home
                                    _root_ide_package_.dev.dynamicvector.navigation.BottomNavTab.CONTEXTS -> _root_ide_package_.dev.dynamicvector.navigation.Screen.Contexts
                                    _root_ide_package_.dev.dynamicvector.navigation.BottomNavTab.PROFILE -> _root_ide_package_.dev.dynamicvector.navigation.Screen.Profile
                                }
                            },
                        )
                    }

                    // FAB for New Query - only on Home tab, not when already on NewQuery
                    if (selectedTab == _root_ide_package_.dev.dynamicvector.navigation.BottomNavTab.HOME && currentScreen !is dev.dynamicvector.navigation.Screen.NewQuery) {
                        FloatingActionButton(
                            onClick = {
                                currentScreen =
                                    _root_ide_package_.dev.dynamicvector.navigation.Screen.NewQuery
                            },
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
