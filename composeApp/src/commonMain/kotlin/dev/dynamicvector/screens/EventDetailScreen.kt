package dev.dynamicvector.screens

import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.outlined.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import dev.dynamicvector.components.*
import dev.dynamicvector.model.*
import dev.dynamicvector.theme.DVColors
import dev.dynamicvector.theme.DVTypography

@Composable
fun EventDetailScreen(event: QueryEvent, onBack: () -> Unit) {
    LazyColumn(Modifier.fillMaxSize(), contentPadding = PaddingValues(top = 44.dp, bottom = 88.dp)) {
        item {
            Row(Modifier.clickable(onClick = onBack).padding(horizontal = 16.dp, vertical = 12.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Box(Modifier.size(32.dp).background(DVColors.Accent.copy(0.08f), RoundedCornerShape(10.dp)), contentAlignment = Alignment.Center) {
                    Icon(Icons.AutoMirrored.Outlined.ArrowBack, "Back", tint = DVColors.Accent, modifier = Modifier.size(16.dp))
                }
                Text("Back", color = DVColors.Accent, fontSize = 14.sp, fontWeight = FontWeight.Medium)
            }
        }
        item {
            Text(event.queryName, style = DVTypography.H1, modifier = Modifier.padding(horizontal = 16.dp))
            Text("Ran ${event.timeAgo} · ${event.resultCount} results · ${event.sources.size} sources", style = DVTypography.Caption, modifier = Modifier.padding(horizontal = 16.dp, vertical = 4.dp))
        }
        item { Row(Modifier.padding(horizontal = 16.dp, vertical = 8.dp), horizontalArrangement = Arrangement.spacedBy(6.dp)) { event.sources.forEach { SourceBadge(it) } } }
        item { SectionHeader("Top results") }
        itemsIndexed(event.results) { _, result ->
            Column(Modifier.padding(horizontal = 16.dp, vertical = 5.dp).fillMaxWidth()
                .background(Brush.linearGradient(listOf(DVColors.CardGradientStart, DVColors.CardGradientEnd)), RoundedCornerShape(16.dp))
                .border(1.dp, DVColors.CardBorder, RoundedCornerShape(16.dp)).padding(14.dp)
            ) {
                Text("#${result.rank} · ${result.category}", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = DVColors.Accent)
                Spacer(Modifier.height(6.dp))
                Text(result.name, style = DVTypography.CardTitle)
                Spacer(Modifier.height(4.dp))
                Text(result.description, style = DVTypography.Body, maxLines = 3, overflow = TextOverflow.Ellipsis)
                Spacer(Modifier.height(10.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                    result.tags.forEach { tag -> Box(Modifier.background(DVColors.SurfaceVariant, RoundedCornerShape(6.dp)).padding(horizontal = 8.dp, vertical = 3.dp)) { Text(tag, style = DVTypography.Badge.copy(color = DVColors.TextTertiary)) } }
                }
                Spacer(Modifier.height(10.dp))
                Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                    Text("Relevance", style = DVTypography.Caption, modifier = Modifier.width(60.dp))
                    LinearProgressIndicator(progress = { result.relevance }, modifier = Modifier.weight(1f).height(4.dp).clip(RoundedCornerShape(2.dp)), color = DVColors.Accent, trackColor = DVColors.SurfaceVariant)
                    Spacer(Modifier.width(10.dp))
                    Text("%.2f".format(result.relevance), fontSize = 13.sp, fontWeight = FontWeight.Bold, color = DVColors.Accent)
                }
                if (result.explanation.isNotBlank()) {
                    HorizontalDivider(Modifier.padding(vertical = 10.dp), thickness = 1.dp, color = DVColors.Accent.copy(0.08f))
                    Text(result.explanation, style = DVTypography.Caption.copy(color = DVColors.TextTertiary, lineHeight = 16.sp, fontStyle = FontStyle.Italic))
                }
            }
        }
    }
}
