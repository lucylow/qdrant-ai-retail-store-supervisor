package ch.genaizurich2026.dynamicvector.navigation

sealed class Screen {
    data object Login : Screen()
    data object Home : Screen()
    data object NewQuery : Screen()
    data object Contexts : Screen()
    data object Profile : Screen()
}

enum class BottomNavTab(val label: String) {
    HOME("Home"),
    CONTEXTS("Contexts"),
    PROFILE("Profile"),
}
