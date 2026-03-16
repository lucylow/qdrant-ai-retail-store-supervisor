package dev.dynamicvector.screens

import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.outlined.ArrowBack
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import dev.dynamicvector.components.*
import dev.dynamicvector.data.MockData
import dev.dynamicvector.model.*
import dev.dynamicvector.theme.DVColors
import dev.dynamicvector.theme.DVShapes
import dev.dynamicvector.theme.DVTypography

@Composable
fun SourcesHostScreen(onNavigateToDetail: (ExploreSource) -> Unit, onNavigateToFolderBrowser: () -> Unit) {
    var tab by remember { mutableStateOf(0) }
    var showAddLocal by remember { mutableStateOf(false) }
    Box(Modifier.fillMaxSize()) {
        Column(Modifier.fillMaxSize()) {
            Spacer(Modifier.height(44.dp))
            if (tab == 0) { var s by remember { mutableStateOf("") }; DVSearchBar(s, { s = it }, "Search my sources...", modifier = Modifier.padding(bottom = 4.dp)) } else Spacer(Modifier.height(8.dp))
            DVSegmentedControl(listOf("My sources", "Explore"), tab, onSelect = { tab = it })
            if (tab == 0) MySourcesView { showAddLocal = true } else ExploreView(onNavigateToDetail)
        }
        AddLocalSheet(showAddLocal, { showAddLocal = false }) { showAddLocal = false; onNavigateToFolderBrowser() }
    }
}

@Composable private fun MySourcesView(onAddLocal: () -> Unit) {
    LazyColumn(contentPadding = PaddingValues(bottom = 88.dp)) {
        item { SectionHeader("Connected sources") }
        MockData.connectedRepos.forEach { repo ->
            item {
                Row(Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 6.dp), Arrangement.SpaceBetween, Alignment.CenterVertically) {
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
                        Box(Modifier.size(8.dp).background(repo.type.colors().first, CircleShape)); Text(repo.name, style = DVTypography.H2.copy(fontSize = 14.sp))
                    }
                    Text("${repo.sources.size} ${repo.unitLabel}", style = DVTypography.Caption)
                }
            }
            items(repo.sources) { src ->
                Row(Modifier.padding(horizontal = 16.dp, vertical = 3.dp).fillMaxWidth().dvCard(12.dp).padding(horizontal = 14.dp, vertical = 12.dp), Arrangement.SpaceBetween, Alignment.CenterVertically) {
                    Column(Modifier.weight(1f, false), verticalArrangement = Arrangement.spacedBy(3.dp)) { Text(src.name, fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = DVColors.TextPrimary); Text(src.meta, style = DVTypography.Caption) }
                    Box(Modifier.size(8.dp).background(if (src.isOnline) DVColors.Accent else DVColors.TextHint, CircleShape))
                }
            }
            item { Spacer(Modifier.height(8.dp)) }
        }
        item { SectionHeader("Local sources") }
        items(MockData.localSources) { src ->
            Row(Modifier.padding(horizontal = 16.dp, vertical = 3.dp).fillMaxWidth().dvCard(12.dp).padding(horizontal = 14.dp, vertical = 12.dp), Arrangement.SpaceBetween, Alignment.CenterVertically) {
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically, modifier = Modifier.weight(1f, false)) {
                    Text(if (src.isFolder) "📁" else "📄", fontSize = 16.sp)
                    Column(verticalArrangement = Arrangement.spacedBy(3.dp)) { Text(src.displayName, fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = DVColors.TextPrimary); Text(src.meta, style = DVTypography.Caption) }
                }
                Box(Modifier.size(8.dp).background(DVColors.Accent, CircleShape))
            }
        }
        item {
            Row(Modifier.padding(horizontal = 16.dp, vertical = 8.dp).fillMaxWidth().border(1.dp, DVColors.Local.copy(0.3f), RoundedCornerShape(12.dp)).clickable(onClick = onAddLocal).padding(14.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                Box(Modifier.size(36.dp).background(DVColors.Local.copy(0.1f), RoundedCornerShape(10.dp)), contentAlignment = Alignment.Center) { Text("+", color = DVColors.Local, fontSize = 18.sp, fontWeight = FontWeight.Bold) }
                Column { Text("Add local source", fontSize = 13.sp, fontWeight = FontWeight.SemiBold, color = DVColors.Local); Text("Folders, files, or documents from this device", fontSize = 11.sp, color = DVColors.Local.copy(0.5f)) }
            }
        }
    }
}

@Composable private fun ExploreView(onPreview: (ExploreSource) -> Unit) {
    var filter by remember { mutableStateOf("All") }
    var bookmarks by remember { mutableStateOf(MockData.exploreSources.filter { it.isBookmarked }.map { it.id }.toSet()) }
    LazyColumn(contentPadding = PaddingValues(bottom = 88.dp)) {
        item { var q by remember { mutableStateOf("") }; DVSearchBar(q, { q = it }, "Search Qdrant, HuggingFace, Apify...", accentHighlight = true, modifier = Modifier.padding(vertical = 8.dp)) }
        item {
            LazyRow(contentPadding = PaddingValues(horizontal = 16.dp, vertical = 4.dp), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                items(listOf("All", "Qdrant", "HuggingFace", "Apify", "LiveMap")) { cat ->
                    val a = cat == filter
                    Box(Modifier.background(if (a) DVColors.AccentDim else DVColors.SurfaceVariant, RoundedCornerShape(20.dp)).border(1.dp, if (a) DVColors.AccentBorder else DVColors.CardBorder, RoundedCornerShape(20.dp)).clickable { filter = cat }.padding(horizontal = 14.dp, vertical = 6.dp)) {
                        Text(cat, fontSize = 12.sp, fontWeight = FontWeight.SemiBold, color = if (a) DVColors.Accent else DVColors.TextTertiary)
                    }
                }
            }
        }
        item { SectionHeader("Trending sources") }
        val sources = if (filter == "All") MockData.exploreSources else MockData.exploreSources.filter { it.repoType.label() == filter }
        items(sources, key = { it.id }) { src ->
            val bk = src.id in bookmarks
            Box(Modifier.padding(horizontal = 16.dp, vertical = 5.dp).fillMaxWidth().dvCard(16.dp)) {

                Column(Modifier.padding(14.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.padding(bottom = 6.dp)) {
                    Text(src.name, style = DVTypography.CardTitle.copy(fontSize = 14.sp), modifier = Modifier.weight(1f, false), maxLines = 1, overflow = TextOverflow.Ellipsis); SourceBadge(src.repoType)
                }
                Text(src.description, style = DVTypography.Body, maxLines = 3, overflow = TextOverflow.Ellipsis, modifier = Modifier.padding(bottom = 10.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(14.dp), modifier = Modifier.padding(bottom = 10.dp)) {
                    src.stats.forEach { (l, v) -> Column(verticalArrangement = Arrangement.spacedBy(2.dp)) { Text(l.uppercase(), fontSize = 9.sp, color = DVColors.TextHint, letterSpacing = 0.5.sp); Text(v, fontSize = 12.sp, fontWeight = FontWeight.SemiBold, color = DVColors.TextPrimary) } }
                }
                HorizontalDivider(thickness = 1.dp, color = DVColors.Accent.copy(0.08f)); Spacer(Modifier.height(10.dp))
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.End, verticalAlignment = Alignment.CenterVertically) {
                    if (src.isAlreadySaved) { Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(5.dp), modifier = Modifier.weight(1f)) { Icon(Icons.Outlined.Check, null, tint = DVColors.Accent, modifier = Modifier.size(14.dp)); Text("Already saved", fontSize = 11.sp, fontWeight = FontWeight.SemiBold, color = DVColors.Accent) } } else Spacer(Modifier.weight(1f))
                    if (!src.isAlreadySaved) { Box(Modifier.background(DVColors.SurfaceVariant, RoundedCornerShape(10.dp)).border(1.dp, DVColors.CardBorder, RoundedCornerShape(10.dp)).clickable { onPreview(src) }.padding(horizontal = 14.dp, vertical = 7.dp)) { Text("Preview", fontSize = 12.sp, color = DVColors.TextTertiary) }; Spacer(Modifier.width(8.dp)) }
                    Box(Modifier.size(34.dp).background(if (bk) DVColors.AccentDim else DVColors.SurfaceVariant, RoundedCornerShape(10.dp)).border(1.dp, if (bk) DVColors.Accent.copy(0.2f) else DVColors.CardBorder, RoundedCornerShape(10.dp)).clickable { bookmarks = if (src.id in bookmarks) bookmarks - src.id else bookmarks + src.id }, contentAlignment = Alignment.Center) {
                        Icon(if (bk) Icons.Outlined.Bookmark else Icons.Outlined.BookmarkBorder, "Bookmark", tint = if (bk) DVColors.Accent else DVColors.IconMuted, modifier = Modifier.size(16.dp))
                    }
                    if (!src.isAlreadySaved) { Spacer(Modifier.width(8.dp)); Row(Modifier.background(DVColors.Accent, RoundedCornerShape(10.dp)).padding(horizontal = 18.dp, vertical = 7.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp)) { Icon(Icons.Outlined.FileDownload, null, tint = Color.White, modifier = Modifier.size(14.dp)); Text("Pull", fontSize = 12.sp, fontWeight = FontWeight.SemiBold, color = Color.White) } }
                }
            }}
        }
    }
}

@Composable
fun SourceDetailScreen(source: ExploreSource, onBack: () -> Unit) {
    val (heroColor, _, _) = source.repoType.colors()
    LazyColumn(Modifier.fillMaxSize(), contentPadding = PaddingValues(top = 44.dp, bottom = 88.dp)) {
        item { Row(Modifier.clickable(onClick = onBack).padding(horizontal = 16.dp, vertical = 12.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) { Box(Modifier.size(32.dp).background(DVColors.Accent.copy(0.08f), RoundedCornerShape(10.dp)), contentAlignment = Alignment.Center) { Icon(Icons.AutoMirrored.Outlined.ArrowBack, "Back", tint = DVColors.Accent, modifier = Modifier.size(16.dp)) }; Text("Source detail", style = DVTypography.H1.copy(fontSize = 18.sp)) } }
        item {
            Column(Modifier.padding(16.dp).fillMaxWidth().background(Brush.linearGradient(listOf(heroColor.copy(0.08f), heroColor.copy(0.02f))), RoundedCornerShape(16.dp)).border(1.dp, heroColor.copy(0.15f), RoundedCornerShape(16.dp)).padding(16.dp)) {
                SourceBadge(source.repoType); Spacer(Modifier.height(8.dp)); Text(source.name, style = DVTypography.H1.copy(fontSize = 18.sp)); Spacer(Modifier.height(4.dp))
                if (source.providerInfo.isNotBlank()) Text(source.providerInfo, style = DVTypography.Caption, modifier = Modifier.padding(bottom = 12.dp))
                Text(source.description, style = DVTypography.Body.copy(lineHeight = 20.sp), modifier = Modifier.padding(bottom = 14.dp))
                source.stats.chunked(2).forEach { row -> Row(Modifier.fillMaxWidth().padding(bottom = 8.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) { row.forEach { (l, v) -> Column(Modifier.weight(1f).background(DVColors.Accent.copy(0.05f), RoundedCornerShape(10.dp)).padding(horizontal = 12.dp, vertical = 10.dp)) { Text(l.uppercase(), fontSize = 10.sp, color = DVColors.TextHint, letterSpacing = 0.5.sp); Spacer(Modifier.height(4.dp)); Text(v, fontSize = 15.sp, fontWeight = FontWeight.Bold, color = DVColors.TextPrimary) } }; if (row.size == 1) Spacer(Modifier.weight(1f)) } }
            }
        }
        item {
            Row(Modifier.padding(horizontal = 16.dp, vertical = 4.dp).fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                Row(Modifier.weight(1f).height(50.dp).background(DVColors.Accent, RoundedCornerShape(14.dp)), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.Center) { Icon(Icons.Outlined.FileDownload, null, tint = Color.White, modifier = Modifier.size(18.dp)); Spacer(Modifier.width(8.dp)); Text("Pull to my sources", fontSize = 14.sp, fontWeight = FontWeight.Bold, color = Color.White) }
                Box(Modifier.size(50.dp).background(DVColors.SurfaceVariant, RoundedCornerShape(14.dp)).border(1.dp, DVColors.CardBorder, RoundedCornerShape(14.dp)), contentAlignment = Alignment.Center) { Icon(Icons.Outlined.BookmarkBorder, "Bookmark", tint = DVColors.IconMuted, modifier = Modifier.size(20.dp)) }
            }
        }
        if (source.schema.isNotEmpty()) {
            item { Spacer(Modifier.height(16.dp)); SectionHeader("Payload schema") }
            items(source.schema) { f -> Row(Modifier.padding(horizontal = 16.dp, vertical = 2.dp).fillMaxWidth().background(DVColors.SurfaceVariant, RoundedCornerShape(8.dp)).padding(horizontal = 12.dp, vertical = 8.dp), Arrangement.SpaceBetween) { Text(f.name, fontSize = 12.sp, fontWeight = FontWeight.SemiBold, color = DVColors.TextPrimary, fontFamily = FontFamily.Monospace); Text(f.type, fontSize = 11.sp, color = DVColors.TextTertiary, fontFamily = FontFamily.Monospace) } }
        }
        if (source.sampleRecord.isNotEmpty()) {
            item {
                Spacer(Modifier.height(16.dp)); SectionHeader("Sample record")
                Column(Modifier.padding(horizontal = 16.dp).fillMaxWidth().background(DVColors.SurfaceVariant, RoundedCornerShape(10.dp)).padding(12.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    source.sampleRecord.forEach { (k, v) -> Row { Text(k, fontSize = 11.sp, fontFamily = FontFamily.Monospace, color = heroColor); Text(": ", fontSize = 11.sp, fontFamily = FontFamily.Monospace, color = DVColors.TextTertiary); Text(v, fontSize = 11.sp, fontFamily = FontFamily.Monospace, color = if (v.startsWith("\"")) DVColors.TextPrimary else DVColors.AccentDark) } }
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable private fun AddLocalSheet(isVisible: Boolean, onDismiss: () -> Unit, onFolder: () -> Unit) {
    if (!isVisible) return
    val opts = listOf(AddLocalOption("📁", "Folder", "Index all files in a folder. Subfolders included.", DVColors.Local.copy(0.12f)), AddLocalOption("📄", "Files", "Pick individual PDFs, CSVs, text files.", DVColors.Apify.copy(0.12f)), AddLocalOption("📷", "Photo or scan", "Take a photo or scan. OCR extracts text.", DVColors.HuggingFace.copy(0.12f)), AddLocalOption("🔗", "URL or web page", "Paste a URL to crawl and index.", DVColors.Accent.copy(0.12f)))
    val actions = listOf(onFolder, onDismiss, onDismiss, onDismiss)
    ModalBottomSheet(onDismissRequest = onDismiss, sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true), containerColor = DVColors.Surface, shape = RoundedCornerShape(topStart = DVShapes.BottomSheetRadius, topEnd = DVShapes.BottomSheetRadius),
        dragHandle = { Box(Modifier.padding(top = 12.dp, bottom = 8.dp).size(40.dp, 4.dp).background(DVColors.TextHint, RoundedCornerShape(2.dp))) }) {
        Column(Modifier.padding(horizontal = 16.dp, vertical = 8.dp)) {
            Text("Add local source", style = DVTypography.H2.copy(fontSize = 16.sp), modifier = Modifier.padding(bottom = 6.dp)); Text("Choose what to index and make searchable.", style = DVTypography.Caption, modifier = Modifier.padding(bottom = 20.dp))
            opts.forEachIndexed { i, o ->
                Row(Modifier.fillMaxWidth().padding(bottom = 8.dp).background(DVColors.SurfaceVariant, RoundedCornerShape(14.dp)).border(1.dp, DVColors.CardBorder, RoundedCornerShape(14.dp)).clickable(onClick = actions[i]).padding(14.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(14.dp)) {
                    Box(Modifier.size(42.dp).background(o.bgColor, RoundedCornerShape(12.dp)), contentAlignment = Alignment.Center) { Text(o.icon, fontSize = 20.sp) }
                    Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(2.dp)) { Text(o.title, fontSize = 14.sp, fontWeight = FontWeight.SemiBold, color = DVColors.TextPrimary); Text(o.description, fontSize = 11.sp, color = DVColors.TextTertiary, lineHeight = 15.sp) }
                    Text("›", fontSize = 16.sp, color = DVColors.TextHint)
                }
            }
            Spacer(Modifier.height(16.dp))
        }
    }
}

@Composable
fun FolderBrowserScreen(onBack: () -> Unit) {
    var items by remember { mutableStateOf(MockData.folderItems) }
    val selected = items.filter { it.isSelected }
    val totalFiles = selected.sumOf { if (it.isFolder) (it.meta.split(" ").firstOrNull()?.toIntOrNull() ?: 0) else 1 }
    Column(Modifier.fillMaxSize()) {
        Spacer(Modifier.height(44.dp))
        Row(Modifier.padding(horizontal = 16.dp, vertical = 12.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            Box(Modifier.size(32.dp).background(DVColors.Accent.copy(0.08f), RoundedCornerShape(10.dp)).clickable(onClick = onBack), contentAlignment = Alignment.Center) { Icon(Icons.AutoMirrored.Outlined.ArrowBack, "Back", tint = DVColors.Accent, modifier = Modifier.size(16.dp)) }
            Text("Select folder", style = DVTypography.H1.copy(fontSize = 18.sp))
        }
        Row(Modifier.padding(horizontal = 16.dp, vertical = 4.dp).fillMaxWidth().background(DVColors.Local.copy(0.06f), RoundedCornerShape(10.dp)).border(1.dp, DVColors.Local.copy(0.12f), RoundedCornerShape(10.dp)).padding(horizontal = 12.dp, vertical = 8.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
            Icon(Icons.Outlined.Folder, null, tint = DVColors.Local, modifier = Modifier.size(14.dp)); Text("/storage/emulated/0/Documents", fontSize = 12.sp, color = DVColors.Local, fontFamily = FontFamily.Monospace, maxLines = 1)
        }
        Box(Modifier.padding(horizontal = 16.dp, vertical = 8.dp).fillMaxWidth().background(DVColors.Accent.copy(0.06f), RoundedCornerShape(10.dp)).border(1.dp, DVColors.Accent.copy(0.1f), RoundedCornerShape(10.dp)).padding(horizontal = 14.dp, vertical = 10.dp)) {
            Text("Select folders to index. Supported files will be chunked, embedded, and added to Qdrant.", fontSize = 11.sp, color = DVColors.Accent.copy(0.6f), lineHeight = 16.sp)
        }
        LazyColumn(Modifier.weight(1f), contentPadding = PaddingValues(bottom = 16.dp)) {
            items(items.size) { i ->
                val item = items[i]
                Row(Modifier.padding(horizontal = 16.dp, vertical = 2.dp).fillMaxWidth().background(DVColors.SurfaceVariant, RoundedCornerShape(12.dp)).border(1.dp, DVColors.CardBorder, RoundedCornerShape(12.dp)).clickable { items = items.toMutableList().also { it[i] = item.copy(isSelected = !item.isSelected) } }.padding(horizontal = 14.dp, vertical = 11.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text(if (item.isFolder) "📁" else "📄", fontSize = 20.sp); Text(item.name, fontSize = 13.sp, fontWeight = FontWeight.Medium, color = DVColors.TextPrimary, modifier = Modifier.weight(1f)); Text(item.meta, fontSize = 10.sp, color = DVColors.TextHint)
                    Box(Modifier.size(22.dp).then(if (item.isSelected) Modifier.background(DVColors.Accent, RoundedCornerShape(6.dp)) else Modifier.border(1.5.dp, DVColors.TextHint, RoundedCornerShape(6.dp))), contentAlignment = Alignment.Center) {
                        if (item.isSelected) Icon(Icons.Outlined.Check, null, tint = Color.White, modifier = Modifier.size(14.dp))
                    }
                }
            }
        }
        if (selected.isNotEmpty()) Box(Modifier.padding(16.dp).fillMaxWidth().background(DVColors.Accent, RoundedCornerShape(14.dp)).clickable(onClick = onBack).padding(vertical = 14.dp), contentAlignment = Alignment.Center) {
            Text("Add ${selected.size} folder${if (selected.size > 1) "s" else ""} ($totalFiles files)", fontSize = 14.sp, fontWeight = FontWeight.Bold, color = Color.White)
        }
    }
}
