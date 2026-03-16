package ch.genaizurich2026.dynamicvector.ui.screens

import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import ch.genaizurich2026.dynamicvector.*
import ch.genaizurich2026.dynamicvector.ui.components.*

@Composable
fun DashboardHostScreen(
    events: List<QueryEvent>, savedQueries: List<SavedQuery>,
    onEventClick: (QueryEvent) -> Unit, onFilterTap: () -> Unit,
    onNewQueryTap: () -> Unit, onQueryTap: (SavedQuery) -> Unit, onToggleStar: (String) -> Unit,
) {
    var dashTab by remember { mutableStateOf(0) }
    Box(Modifier.fillMaxSize()) {
        Column(Modifier.fillMaxSize()) {
            Spacer(Modifier.height(44.dp))
            var search by remember { mutableStateOf("") }
            DVSearchBar(search, { search = it }, if (dashTab == 0) "Search events..." else "Search queries...", modifier = Modifier.padding(bottom = 4.dp))
            DVSegmentedControl(listOf("Results", "Queries"), dashTab) { dashTab = it }
            if (dashTab == 0) ResultsFeed(events, onEventClick, onFilterTap, onToggleStar) else SavedQueriesList(savedQueries, onQueryTap)
        }
        if (dashTab == 1) {
            FloatingActionButton(onClick = onNewQueryTap, containerColor = DVColors.Accent, contentColor = Color.White, shape = RoundedCornerShape(16.dp),
                modifier = Modifier.align(Alignment.BottomEnd).padding(end = 20.dp, bottom = 92.dp)
                    .shadow(12.dp, RoundedCornerShape(16.dp), ambientColor = DVColors.Accent.copy(0.3f), spotColor = DVColors.Accent.copy(0.15f))
            ) { Icon(Icons.Outlined.Add, "New query", modifier = Modifier.size(24.dp)) }
        }
    }
}

@Composable
private fun ResultsFeed(events: List<QueryEvent>, onEventClick: (QueryEvent) -> Unit, onFilterTap: () -> Unit, onToggleStar: (String) -> Unit) {
    var chips by remember { mutableStateOf(listOf("Stale", "Qdrant")) }
    LazyColumn(contentPadding = PaddingValues(bottom = 88.dp)) {
        item { Spacer(Modifier.height(4.dp)); FilterRow(chips.size, chips, onFilterTap) { chips = chips - it }; Spacer(Modifier.height(12.dp)) }
        items(events, key = { it.id }) { ev -> EventCard(ev, { onEventClick(ev) }, { onToggleStar(ev.id) }) }
    }
}

@Composable
private fun SavedQueriesList(queries: List<SavedQuery>, onQueryTap: (SavedQuery) -> Unit) {
    LazyColumn(contentPadding = PaddingValues(bottom = 88.dp)) {
        item { SectionHeader("Active queries") }
        items(queries, key = { it.id }) { q -> SavedQueryCard(q) { onQueryTap(q) } }
    }
}

@Composable
private fun SavedQueryCard(query: SavedQuery, onTap: () -> Unit) {
    Column(Modifier.padding(horizontal = 16.dp, vertical = 5.dp).fillMaxWidth()
        .background(DVColors.SurfaceVariant, RoundedCornerShape(16.dp)).border(1.dp, DVColors.CardBorder, RoundedCornerShape(16.dp))
        .clickable(onClick = onTap).padding(14.dp)
    ) {
        Row(Modifier.fillMaxWidth(), Arrangement.SpaceBetween, Alignment.CenterVertically) {
            Text(query.name, style = DVTypography.CardTitle.copy(fontSize = 14.sp), modifier = Modifier.weight(1f, false))
            Box(Modifier.background(DVColors.AccentDim, RoundedCornerShape(8.dp)).padding(horizontal = 8.dp, vertical = 3.dp)) {
                Text(query.compositionType.name, style = DVTypography.Badge.copy(color = DVColors.Accent, letterSpacing = 0.5.sp))
            }
        }
        Spacer(Modifier.height(6.dp))
        Text(query.goal, style = DVTypography.Body, maxLines = 2, overflow = TextOverflow.Ellipsis)
        Spacer(Modifier.height(8.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) { query.sources.forEach { SourceBadge(it) } }
        Spacer(Modifier.height(10.dp))
        Row(Modifier.fillMaxWidth(), Arrangement.SpaceBetween, Alignment.CenterVertically) {
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                Text("${query.stepCount} steps", style = DVTypography.Caption)
                Text(if (query.lastResultCount > 0) "${query.lastResultCount} results" else "Not run yet", style = DVTypography.Caption)
            }
            Box(Modifier.background(DVColors.Accent, RoundedCornerShape(10.dp)).padding(horizontal = 16.dp, vertical = 6.dp)) {
                Text("Run", fontSize = 12.sp, fontWeight = FontWeight.SemiBold, color = Color.White)
            }
        }
        if (query.schedule != null) {
            Spacer(Modifier.height(8.dp))
            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                Icon(Icons.Outlined.Schedule, null, tint = DVColors.Accent.copy(0.6f), modifier = Modifier.size(12.dp))
                Text(query.schedule, fontSize = 10.sp, color = DVColors.Accent.copy(0.6f))
            }
        }
    }
}
