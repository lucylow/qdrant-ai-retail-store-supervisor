package dev.dynamicvector.navigation

sealed class Screen {
    data object Login : dev.dynamicvector.navigation.Screen()
    data object Home : dev.dynamicvector.navigation.Screen()
    data object NewQuery : dev.dynamicvector.navigation.Screen()
    data object Contexts : dev.dynamicvector.navigation.Screen()
    data object Profile : dev.dynamicvector.navigation.Screen()
}

enum class BottomNavTab(val label: String) {
    HOME("Home"),
    CONTEXTS("Contexts"),
    PROFILE("Profile"),
}
