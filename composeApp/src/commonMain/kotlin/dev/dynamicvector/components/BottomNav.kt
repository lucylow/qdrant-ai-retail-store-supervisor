package dev.dynamicvector.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Home
import androidx.compose.material.icons.outlined.Settings
import androidx.compose.material.icons.outlined.Storage
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import dev.dynamicvector.navigation.DVTab
import dev.dynamicvector.theme.DVColors

@Composable
fun DVBottomNav(currentTab: DVTab, onTabSelected: (DVTab) -> Unit) {
    Box(Modifier.fillMaxWidth().height(80.dp).background(Brush.verticalGradient(listOf(Color.Transparent, DVColors.Background.copy(0.95f), DVColors.Background)))) {
        NavigationBar(containerColor = Color.Transparent, modifier = Modifier.align(Alignment.BottomCenter)) {
            listOf(
                Triple(DVTab.DASHBOARD, Icons.Outlined.Home, "Dashboard"),
                Triple(DVTab.SOURCES, Icons.Outlined.Storage, "Sources"),
                Triple(DVTab.SETTINGS, Icons.Outlined.Settings, "Settings"),
            ).forEach { (tab, icon, label) ->
                NavigationBarItem(
                    selected = currentTab == tab, onClick = { onTabSelected(tab) },
                    icon = { Icon(icon, label, modifier = Modifier.size(22.dp)) },
                    label = { Text(label, fontSize = 10.sp) },
                    colors = NavigationBarItemDefaults.colors(
                        selectedIconColor = DVColors.Accent, selectedTextColor = DVColors.Accent,
                        unselectedIconColor = DVColors.IconMuted, unselectedTextColor = DVColors.IconMuted,
                        indicatorColor = Color.Transparent,
                    )
                )
            }
        }
    }
}
