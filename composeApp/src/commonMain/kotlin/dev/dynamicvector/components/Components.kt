package dev.dynamicvector.components

import androidx.compose.animation.core.*
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import dev.dynamicvector.model.*
import dev.dynamicvector.theme.DVColors
import dev.dynamicvector.theme.DVShapes
import dev.dynamicvector.theme.DVTypography

// ═══════════════════════════════════════════════════════════════════
// DVSearchBar
// ═══════════════════════════════════════════════════════════════════

@Composable
fun DVSearchBar(
    query: String,
    onQueryChange: (String) -> Unit,
    placeholder: String = "Search...",
    accentHighlight: Boolean = false,
    modifier: Modifier = Modifier,
) {
    OutlinedTextField(
        value = query, onValueChange = onQueryChange,
        placeholder = { Text(placeholder, color = if (accentHighlight) DVColors.Accent.copy(0.4f) else DVColors.TextHint, fontSize = 14.sp) },
        leadingIcon = { Icon(Icons.Outlined.Search, null, tint = if (accentHighlight) DVColors.Accent.copy(0.6f) else DVColors.IconMuted, modifier = Modifier.size(18.dp)) },
        singleLine = true,
        colors = OutlinedTextFieldDefaults.colors(
            focusedContainerColor = if (accentHighlight) DVColors.Accent.copy(0.04f) else DVColors.SurfaceVariant,
            unfocusedContainerColor = if (accentHighlight) DVColors.Accent.copy(0.04f) else DVColors.SurfaceVariant,
            focusedBorderColor = if (accentHighlight) DVColors.Accent.copy(0.12f) else DVColors.CardBorder,
            unfocusedBorderColor = if (accentHighlight) DVColors.Accent.copy(0.12f) else DVColors.CardBorder,
            cursorColor = DVColors.Accent, focusedTextColor = DVColors.TextPrimary, unfocusedTextColor = DVColors.TextPrimary,
        ),
        shape = RoundedCornerShape(DVShapes.SearchBarRadius),
        modifier = modifier.fillMaxWidth().padding(horizontal = 16.dp)
    )
}

// ═══════════════════════════════════════════════════════════════════
// StatusChip
// ═══════════════════════════════════════════════════════════════════

@Composable
fun StatusChip(status: QueryStatus) {
    val c = status.color()
    Row(
        modifier = Modifier.background(c.copy(0.12f), RoundedCornerShape(10.dp)).padding(horizontal = 10.dp, vertical = 3.dp),
        verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(4.dp)
    ) {
        if (status == QueryStatus.LIVE) {
            val alpha by rememberInfiniteTransition(label = "pulse").animateFloat(1f, 0.3f, infiniteRepeatable(tween(1000), RepeatMode.Reverse), label = "a")
            Box(Modifier.size(6.dp).background(c.copy(alpha = alpha), CircleShape))
        }
        Text(status.name.replaceFirstChar { it.uppercase() }, style = DVTypography.Badge.copy(color = c))
    }
}

// ═══════════════════════════════════════════════════════════════════
// SourceBadge
// ═══════════════════════════════════════════════════════════════════

@Composable
fun SourceBadge(type: SourceType, detail: String? = null) {
    val (text, bg, bd) = type.colors()
    Box(Modifier.background(bg, RoundedCornerShape(DVShapes.PillRadius)).border(1.dp, bd, RoundedCornerShape(DVShapes.PillRadius)).padding(horizontal = 8.dp, vertical = 3.dp)) {
        Text(if (detail != null) "${type.label()} · $detail" else type.label(), style = DVTypography.Badge.copy(color = text))
    }
}

// ═══════════════════════════════════════════════════════════════════
// MetricItem
// ═══════════════════════════════════════════════════════════════════

@Composable
fun MetricItem(label: String, value: String, isAccent: Boolean = false) {
    Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
        Text(label.uppercase(), style = DVTypography.Caption.copy(letterSpacing = 0.5.sp, fontSize = 10.sp))
        Text(value, style = DVTypography.MetricValue.copy(color = if (isAccent) DVColors.Accent else DVColors.TextPrimary))
    }
}

// ═══════════════════════════════════════════════════════════════════
// CardActionButton
// ═══════════════════════════════════════════════════════════════════

@Composable
fun CardActionButton(icon: ImageVector, onClick: () -> Unit) {
    Box(
        Modifier.size(32.dp).background(DVColors.SurfaceVariant, RoundedCornerShape(10.dp))
            .border(1.dp, DVColors.CardBorder, RoundedCornerShape(10.dp)).clickable(onClick = onClick),
        contentAlignment = Alignment.Center
    ) { Icon(icon, null, tint = DVColors.IconMutedLight, modifier = Modifier.size(15.dp)) }
}

// ═══════════════════════════════════════════════════════════════════
// StaleNudge
// ═══════════════════════════════════════════════════════════════════

@Composable
fun StaleNudge(onRerun: () -> Unit) {
    Row(
        Modifier.fillMaxWidth().background(DVColors.StatusStale.copy(0.08f), RoundedCornerShape(12.dp))
            .border(1.dp, DVColors.StatusStale.copy(0.15f), RoundedCornerShape(12.dp)).padding(horizontal = 14.dp, vertical = 10.dp),
        verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(10.dp)
    ) {
        Text("Source data changed since last run. Re-run for improved results.", style = DVTypography.Caption.copy(color = DVColors.StatusStale, lineHeight = 16.sp), modifier = Modifier.weight(1f))
        Button(onClick = onRerun, colors = ButtonDefaults.buttonColors(containerColor = DVColors.StatusStale, contentColor = DVColors.Background), shape = RoundedCornerShape(8.dp), contentPadding = PaddingValues(horizontal = 12.dp, vertical = 5.dp), modifier = Modifier.height(28.dp)) {
            Text("Re-run", fontSize = 11.sp, fontWeight = FontWeight.SemiBold)
        }
    }
}

// ═══════════════════════════════════════════════════════════════════
// EventCard — Levitating card with 3-layer shadow, Swiss red top edge
// ═══════════════════════════════════════════════════════════════════

@Composable
fun EventCard(event: QueryEvent, onClick: () -> Unit, onToggleStar: () -> Unit, onRerun: () -> Unit = {}) {
    Box(
        Modifier.padding(horizontal = 16.dp, vertical = 6.dp).fillMaxWidth()
            .drawBehind {
                drawRoundRect(Color.Black.copy(0.10f), cornerRadius = CornerRadius(20.dp.toPx()), topLeft = Offset(0f, 16.dp.toPx()), size = size.copy(height = size.height + 16.dp.toPx()))
                drawRoundRect(Color.Black.copy(0.15f), cornerRadius = CornerRadius(20.dp.toPx()), topLeft = Offset(0f, 8.dp.toPx()), size = size.copy(height = size.height + 8.dp.toPx()))
            }
            .clip(RoundedCornerShape(DVShapes.CardRadius))
            .background(Brush.linearGradient(listOf(DVColors.CardGradientStart, DVColors.CardGradientEnd)))
            .border(1.dp, DVColors.CardBorder, RoundedCornerShape(DVShapes.CardRadius))
            .clickable(onClick = onClick)
    ) {
        Box(Modifier.fillMaxWidth().height(1.dp).background(DVColors.CardTopEdge))
        Column(Modifier.padding(16.dp)) {
            Row(Modifier.fillMaxWidth(), Arrangement.SpaceBetween, Alignment.Top) {
                Text(event.queryName, style = DVTypography.CardTitle, modifier = Modifier.weight(1f, false))
                Text(event.timeAgo, style = DVTypography.Caption)
            }
            Spacer(Modifier.height(4.dp))
            Text(event.goal, style = DVTypography.Body, maxLines = 2, overflow = TextOverflow.Ellipsis)
            Spacer(Modifier.height(8.dp))
            StatusChip(event.status)
            Spacer(Modifier.height(8.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) { event.sources.forEach { SourceBadge(it) } }
            Spacer(Modifier.height(10.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(20.dp)) {
                MetricItem("Results", "${event.resultCount}")
                MetricItem("Relevance", "%.2f".format(event.relevanceScore), isAccent = true)
                MetricItem("Sources", "${event.sources.size}")
            }
            if (event.status == QueryStatus.STALE) { Spacer(Modifier.height(10.dp)); StaleNudge(onRerun) }
            Spacer(Modifier.height(12.dp))
            HorizontalDivider(thickness = 1.dp, color = Color.White.copy(0.04f))
            Spacer(Modifier.height(10.dp))
            Row(Modifier.fillMaxWidth(), Arrangement.SpaceBetween, Alignment.CenterVertically) {
                Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                    CardActionButton(Icons.Outlined.Refresh) {}
                    CardActionButton(Icons.Outlined.Edit) {}
                    CardActionButton(Icons.Outlined.Delete) {}
                }
                IconButton(onClick = onToggleStar, modifier = Modifier.size(32.dp)) {
                    Icon(if (event.isStarred) Icons.Outlined.Star else Icons.Outlined.StarBorder, "Star",
                        tint = if (event.isStarred) DVColors.StarActive else DVColors.IconMuted, modifier = Modifier.size(18.dp))
                }
            }
        }
    }
}

// ═══════════════════════════════════════════════════════════════════
// FilterRow
// ═══════════════════════════════════════════════════════════════════

@Composable
fun FilterRow(activeFilterCount: Int, activeChips: List<String>, onFilterTap: () -> Unit, onChipDismiss: (String) -> Unit) {
    Row(Modifier.fillMaxWidth().padding(horizontal = 16.dp), horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
        Row(
            Modifier.background(if (activeFilterCount > 0) DVColors.AccentDim else DVColors.SurfaceVariant, RoundedCornerShape(20.dp))
                .border(1.dp, if (activeFilterCount > 0) DVColors.AccentBorder else DVColors.CardBorder, RoundedCornerShape(20.dp))
                .clickable(onClick = onFilterTap).padding(horizontal = 14.dp, vertical = 6.dp),
            verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp)
        ) {
            Icon(Icons.Outlined.FilterList, "Filters", tint = if (activeFilterCount > 0) DVColors.Accent else DVColors.IconMuted, modifier = Modifier.size(14.dp))
            Text("Filters", fontSize = 12.sp, fontWeight = FontWeight.SemiBold, color = if (activeFilterCount > 0) DVColors.Accent else DVColors.IconMuted)
            if (activeFilterCount > 0) {
                Box(Modifier.size(18.dp).background(DVColors.Accent, CircleShape), contentAlignment = Alignment.Center) {
                    Text("$activeFilterCount", fontSize = 10.sp, fontWeight = FontWeight.Bold, color = Color.White)
                }
            }
        }
        activeChips.forEach { chip ->
            Row(Modifier.background(DVColors.SurfaceVariant, RoundedCornerShape(DVShapes.ChipRadius)).border(1.dp, DVColors.CardBorder, RoundedCornerShape(DVShapes.ChipRadius)).padding(horizontal = 10.dp, vertical = 5.dp),
                verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                Text(chip, style = DVTypography.Caption)
                Icon(Icons.Outlined.Close, "Remove", tint = DVColors.TextTertiary, modifier = Modifier.size(13.dp).clickable { onChipDismiss(chip) })
            }
        }
    }
}

// ═══════════════════════════════════════════════════════════════════
// PipelineBlock
// ═══════════════════════════════════════════════════════════════════

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun PipelineBlock(step: PipelineStep) {
    val bc = step.type.colors()
    FlowRow(
        Modifier.padding(horizontal = 16.dp, vertical = 4.dp).fillMaxWidth()
            .background(bc.bg, RoundedCornerShape(14.dp)).border(1.dp, bc.border, RoundedCornerShape(14.dp)).padding(14.dp),
        horizontalArrangement = Arrangement.spacedBy(4.dp), verticalArrangement = Arrangement.spacedBy(4.dp)
    ) {
        step.segments.forEach { seg ->
            when (seg) {
                is StepSegment.TextPart -> Text(seg.text, fontSize = 13.sp, color = DVColors.TextSecondary, lineHeight = 24.sp)
                is StepSegment.PillPart -> Box(Modifier.background(bc.pillBg, RoundedCornerShape(DVShapes.PillRadius)).padding(horizontal = 10.dp, vertical = 2.dp)) {
                    Text(seg.label, fontSize = 12.sp, fontWeight = FontWeight.SemiBold, color = bc.pillText)
                }
            }
        }
    }
}

// ═══════════════════════════════════════════════════════════════════
// DVSegmentedControl
// ═══════════════════════════════════════════════════════════════════

@Composable
fun DVSegmentedControl(tabs: List<String>, activeIndex: Int, onSelect: (Int) -> Unit, modifier: Modifier = Modifier) {
    Row(modifier.padding(horizontal = 16.dp, vertical = 8.dp).fillMaxWidth().background(DVColors.SurfaceVariant, RoundedCornerShape(12.dp)).padding(3.dp)) {
        tabs.forEachIndexed { i, label ->
            Box(Modifier.weight(1f).background(if (i == activeIndex) DVColors.AccentDim else Color.Transparent, RoundedCornerShape(10.dp)).clickable { onSelect(i) }.padding(vertical = 9.dp), contentAlignment = Alignment.Center) {
                Text(label, fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = if (i == activeIndex) DVColors.Accent else DVColors.TextTertiary)
            }
        }
    }
}

// ═══════════════════════════════════════════════════════════════════
// SectionHeader
// ═══════════════════════════════════════════════════════════════════

@Composable
fun SectionHeader(text: String) {
    Text(text.uppercase(), style = DVTypography.SectionLabel, modifier = Modifier.padding(horizontal = 16.dp, vertical = 14.dp))
}
