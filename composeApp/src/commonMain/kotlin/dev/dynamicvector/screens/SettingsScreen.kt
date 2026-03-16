package dev.dynamicvector.screens

import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import dev.dynamicvector.components.SectionHeader
import dev.dynamicvector.components.dvCard
import dev.dynamicvector.data.MockData
import dev.dynamicvector.theme.DVColors
import dev.dynamicvector.theme.DVTypography

@Composable
fun SettingsScreen() {
    var goals by remember { mutableStateOf(MockData.goals.toMutableList()) }
    var notif by remember { mutableStateOf(true) }
    var darkMode by remember { mutableStateOf(true) }

    LazyColumn(Modifier.fillMaxSize(), contentPadding = PaddingValues(top = 44.dp, bottom = 88.dp)) {
        item { Text("Settings", style = DVTypography.H1, modifier = Modifier.padding(16.dp)) }

        item { SectionHeader("User goals") }
        items(goals) { goal ->
            Row(Modifier.padding(horizontal = 16.dp, vertical = 4.dp).fillMaxWidth()
                .dvCard(12.dp)
                .padding(horizontal = 14.dp, vertical = 12.dp),
                horizontalArrangement = Arrangement.spacedBy(10.dp), verticalAlignment = Alignment.Top) {
                Text("◆", color = DVColors.Accent, fontSize = 14.sp)
                Text(goal, style = DVTypography.Body)
            }
        }
        item {
            Box(Modifier.padding(horizontal = 16.dp, vertical = 8.dp).fillMaxWidth()
                .border(1.dp, DVColors.Accent.copy(0.2f), RoundedCornerShape(12.dp))
                .clickable { goals = (goals + "New goal...").toMutableList() }.padding(10.dp), contentAlignment = Alignment.Center) {
                Text("+ Add goal", color = DVColors.Accent.copy(0.5f), fontSize = 12.sp)
            }
            Spacer(Modifier.height(12.dp))
        }

        item { SectionHeader("API keys") }
        items(listOf("Qdrant" to "qd7x", "Apify" to "ap3k", "Anthropic" to "sk2m")) { (name, mask) ->
            SRow(name, "••••••••••$mask") { Text("›", fontSize = 16.sp, color = DVColors.TextHint) }
        }

        item { Spacer(Modifier.height(8.dp)); SectionHeader("Preferences") }
        item { SRow("Default location", "Zürich, Switzerland") { Text("›", fontSize = 16.sp, color = DVColors.TextHint) } }
        item { SRow("Default currency", "CHF") { Text("›", fontSize = 16.sp, color = DVColors.TextHint) } }
        item { SRow("Notifications") { DVSw(notif) { notif = it } } }
        item { SRow("Dark mode") { DVSw(darkMode) { darkMode = it } } }

        item { Spacer(Modifier.height(8.dp)); SectionHeader("Connection status") }
        item {
            SRow("Backend", "api.helveticvector.ch") {
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                    Box(Modifier.size(8.dp).background(DVColors.Accent, CircleShape))
                    Text("Connected", color = DVColors.Accent, fontSize = 12.sp)
                }
            }
        }
    }
}

@Composable private fun SRow(title: String, subtitle: String? = null, trailing: @Composable () -> Unit = {}) {
    Row(Modifier.padding(horizontal = 16.dp, vertical = 3.dp).fillMaxWidth().dvCard(12.dp)
        .padding(horizontal = 16.dp, vertical = 14.dp),
        Arrangement.SpaceBetween, Alignment.CenterVertically) {
        Column(Modifier.weight(1f, false), verticalArrangement = Arrangement.spacedBy(2.dp)) {
            Text(title, fontSize = 14.sp, fontWeight = FontWeight.Medium, color = DVColors.TextPrimary)
            if (subtitle != null) Text(subtitle, style = DVTypography.Caption)
        }
        trailing()
    }
}

@Composable private fun DVSw(checked: Boolean, onChange: (Boolean) -> Unit) {
    Switch(checked, onChange, colors = SwitchDefaults.colors(checkedThumbColor = DVColors.Accent, checkedTrackColor = DVColors.Accent.copy(0.3f), uncheckedThumbColor = DVColors.TextTertiary, uncheckedTrackColor = DVColors.SurfaceVariant))
}
