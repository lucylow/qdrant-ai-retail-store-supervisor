package dev.dynamicvector.screens

import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import dev.dynamicvector.theme.DVColors
import dev.dynamicvector.theme.DVShapes
import dev.dynamicvector.theme.DVTypography

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FilterBottomSheet(isVisible: Boolean, onDismiss: () -> Unit) {
    if (!isVisible) return
    var orderBy by remember { mutableStateOf("Newest") }
    var statuses by remember { mutableStateOf(setOf("Stale")) }
    var dateRange by remember { mutableStateOf("Today") }
    var sourceFilter by remember { mutableStateOf(setOf("Qdrant")) }

    ModalBottomSheet(onDismissRequest = onDismiss, sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true),
        containerColor = DVColors.Surface, shape = RoundedCornerShape(topStart = DVShapes.BottomSheetRadius, topEnd = DVShapes.BottomSheetRadius),
        dragHandle = { Box(Modifier.padding(top = 12.dp, bottom = 8.dp).size(40.dp, 4.dp).background(DVColors.TextHint, RoundedCornerShape(2.dp))) }
    ) {
        Column(Modifier.padding(horizontal = 16.dp, vertical = 8.dp)) {
            Text("Filters", style = DVTypography.H2, modifier = Modifier.padding(bottom = 20.dp))
            FG("Order by", listOf("Newest", "Relevance", "Results ↓"), orderBy) { orderBy = it }
            FGM("Status", listOf("Live", "Done", "Stale", "Failed"), statuses) { s -> statuses = if (s in statuses) statuses - s else statuses + s }
            FG("Date range", listOf("Today", "This week", "This month", "All time"), dateRange) { dateRange = it }
            FGM("Sources used", listOf("Qdrant", "Apify", "LiveMap", "Local"), sourceFilter) { s -> sourceFilter = if (s in sourceFilter) sourceFilter - s else sourceFilter + s }
            Spacer(Modifier.height(16.dp))
            Button(onClick = onDismiss, colors = ButtonDefaults.buttonColors(containerColor = DVColors.Accent, contentColor = Color.White),
                shape = RoundedCornerShape(14.dp), modifier = Modifier.fillMaxWidth().height(48.dp)) {
                Text("Apply filters", fontWeight = FontWeight.Bold, fontSize = 14.sp)
            }
            Spacer(Modifier.height(24.dp))
        }
    }
}

@Composable private fun FG(label: String, options: List<String>, selected: String, onSelect: (String) -> Unit) {
    Column(Modifier.padding(bottom = 18.dp)) {
        Text(label.uppercase(), style = DVTypography.SectionLabel, modifier = Modifier.padding(bottom = 8.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(6.dp), modifier = Modifier.horizontalScroll(rememberScrollState())) {
            options.forEach { o -> val a = o == selected
                Box(Modifier.background(if (a) DVColors.AccentDim else DVColors.SurfaceVariant, RoundedCornerShape(10.dp)).border(1.dp, if (a) DVColors.AccentBorder else DVColors.CardBorder, RoundedCornerShape(10.dp)).clickable { onSelect(o) }.padding(horizontal = 14.dp, vertical = 6.dp)) {
                    Text(o, fontSize = 12.sp, color = if (a) DVColors.Accent else DVColors.TextTertiary)
                }
            }
        }
    }
}

@Composable private fun FGM(label: String, options: List<String>, selected: Set<String>, onToggle: (String) -> Unit) {
    Column(Modifier.padding(bottom = 18.dp)) {
        Text(label.uppercase(), style = DVTypography.SectionLabel, modifier = Modifier.padding(bottom = 8.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(6.dp), modifier = Modifier.horizontalScroll(rememberScrollState())) {
            options.forEach { o -> val a = o in selected
                Box(Modifier.background(if (a) DVColors.AccentDim else DVColors.SurfaceVariant, RoundedCornerShape(10.dp)).border(1.dp, if (a) DVColors.AccentBorder else DVColors.CardBorder, RoundedCornerShape(10.dp)).clickable { onToggle(o) }.padding(horizontal = 14.dp, vertical = 6.dp)) {
                    Text(o, fontSize = 12.sp, color = if (a) DVColors.Accent else DVColors.TextTertiary)
                }
            }
        }
    }
}
