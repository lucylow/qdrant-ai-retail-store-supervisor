package dev.dynamicvector.screens

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.outlined.ArrowBack
import androidx.compose.material.icons.outlined.BookmarkBorder
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import dev.dynamicvector.components.QueryBuilder
import dev.dynamicvector.components.ResultCard
import dev.dynamicvector.data.mockResults
import dev.dynamicvector.data.shoppingQuestions
import dev.dynamicvector.model.ContextResultItem
import kotlinx.coroutines.delay
import kotlin.collections.plus

@Composable
fun NewQueryScreen(
    onBack: () -> Unit,
    showSnackbar: (String) -> Unit = {},
) {
    var results by remember { mutableStateOf(emptyList<dev.dynamicvector.model.ContextResultItem>()) }
    var hasSearched by remember { mutableStateOf(false) }
    var isSearching by remember { mutableStateOf(false) }
    var exclusions by remember { mutableStateOf(emptyList<String>()) }
    var showSaveDialog by remember { mutableStateOf(false) }
    var queryName by remember { mutableStateOf("") }
    var sortBy by remember { mutableStateOf("match") }

    LaunchedEffect(isSearching) {
        if (isSearching) {
            delay(800)
            val filtered = _root_ide_package_.dev.dynamicvector.data.mockResults.filter { r ->
                exclusions.none { ex -> r.title == ex || r.subtitle == ex }
            }
            results = filtered
            isSearching = false
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .statusBarsPadding(),
    ) {
        // Header
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(start = 8.dp, end = 20.dp, top = 8.dp, bottom = 12.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(4.dp),
        ) {
            IconButton(onClick = onBack) {
                Icon(
                    imageVector = Icons.AutoMirrored.Outlined.ArrowBack,
                    contentDescription = "Back",
                    tint = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            Text(
                text = "New Query",
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onBackground,
            )
        }

        // Scrollable content
        Column(
            modifier = Modifier
                .weight(1f)
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 20.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            _root_ide_package_.dev.dynamicvector.components.QueryBuilder(
                questions = _root_ide_package_.dev.dynamicvector.data.shoppingQuestions,
                onSearch = { _, _, _ ->
                    isSearching = true
                    hasSearched = true
                },
                exclusions = exclusions,
                onRemoveExclusion = { ex ->
                    exclusions = exclusions.filter { it != ex }
                },
            )

            // Results
            AnimatedVisibility(
                visible = hasSearched,
                enter = fadeIn(),
                exit = fadeOut(),
            ) {
                Column(
                    verticalArrangement = Arrangement.spacedBy(12.dp),
                ) {
                    Spacer(Modifier.height(8.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Text(
                            text = if (isSearching) "Searching\u2026" else "${results.size} Best Matches",
                            fontSize = 16.sp,
                            fontWeight = FontWeight.Medium,
                            color = MaterialTheme.colorScheme.onBackground,
                        )
                        if (!isSearching && results.isNotEmpty()) {
                            Row(
                                modifier = Modifier
                                    .clip(RoundedCornerShape(4.dp))
                                    .clickable { showSaveDialog = true }
                                    .padding(4.dp),
                                horizontalArrangement = Arrangement.spacedBy(4.dp),
                                verticalAlignment = Alignment.CenterVertically,
                            ) {
                                Icon(
                                    imageVector = Icons.Outlined.BookmarkBorder,
                                    contentDescription = null,
                                    modifier = Modifier.size(16.dp),
                                    tint = MaterialTheme.colorScheme.primary,
                                )
                                Text(
                                    text = "Save Query",
                                    fontSize = 12.sp,
                                    fontWeight = FontWeight.Medium,
                                    color = MaterialTheme.colorScheme.primary,
                                )
                            }
                        }
                    }

                    // Sort controls
                    if (!isSearching && results.isNotEmpty()) {
                        Row(
                            horizontalArrangement = Arrangement.spacedBy(6.dp),
                        ) {
                            listOf("match" to "Match", "price" to "Price", "rating" to "Rating").forEach { (key, label) ->
                                val selected = sortBy == key
                                Surface(
                                    shape = RoundedCornerShape(8.dp),
                                    color = if (selected) MaterialTheme.colorScheme.primary
                                    else MaterialTheme.colorScheme.surfaceVariant,
                                    modifier = Modifier
                                        .clip(RoundedCornerShape(8.dp))
                                        .clickable { sortBy = key },
                                ) {
                                    Text(
                                        text = label,
                                        fontSize = 12.sp,
                                        fontWeight = FontWeight.Medium,
                                        color = if (selected) MaterialTheme.colorScheme.onPrimary
                                        else MaterialTheme.colorScheme.onSurfaceVariant,
                                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
                                    )
                                }
                            }
                        }
                    }

                    if (isSearching) {
                        // Loading skeleton
                        repeat(3) {
                            Surface(
                                shape = RoundedCornerShape(12.dp),
                                color = MaterialTheme.colorScheme.surface,
                                tonalElevation = 1.dp,
                            ) {
                                Row(modifier = Modifier.padding(16.dp)) {
                                    Box(
                                        modifier = Modifier
                                            .size(56.dp)
                                            .clip(RoundedCornerShape(8.dp))
                                            .background(MaterialTheme.colorScheme.surfaceVariant),
                                    )
                                    Spacer(Modifier.width(14.dp))
                                    Column(
                                        modifier = Modifier.weight(1f),
                                        verticalArrangement = Arrangement.spacedBy(10.dp),
                                    ) {
                                        Box(
                                            modifier = Modifier
                                                .fillMaxWidth(0.75f)
                                                .height(14.dp)
                                                .clip(RoundedCornerShape(6.dp))
                                                .background(MaterialTheme.colorScheme.surfaceVariant),
                                        )
                                        Box(
                                            modifier = Modifier
                                                .fillMaxWidth(0.5f)
                                                .height(12.dp)
                                                .clip(RoundedCornerShape(6.dp))
                                                .background(MaterialTheme.colorScheme.surfaceVariant),
                                        )
                                        Box(
                                            modifier = Modifier
                                                .fillMaxWidth(0.25f)
                                                .height(14.dp)
                                                .clip(RoundedCornerShape(6.dp))
                                                .background(MaterialTheme.colorScheme.surfaceVariant),
                                        )
                                    }
                                }
                            }
                        }
                    } else {
                        val sortedResults = when (sortBy) {
                            "price" -> results.sortedBy { it.price ?: Double.MAX_VALUE }
                            "rating" -> results.sortedByDescending { it.rating ?: 0.0 }
                            else -> results.sortedByDescending { it.matchScore }
                        }
                        sortedResults.forEach { result ->
                            _root_ide_package_.dev.dynamicvector.components.ResultCard(
                                result = result,
                                onExclude = { r ->
                                    if (r.title !in exclusions) {
                                        exclusions = exclusions + r.title
                                        results = results.filter { it.id != r.id }
                                    }
                                },
                            )
                        }
                    }

                    Spacer(Modifier.height(16.dp))
                }
            }
        }
    }

    if (showSaveDialog) {
        AlertDialog(
            onDismissRequest = { showSaveDialog = false },
            title = { Text("Save Query") },
            text = {
                Column {
                    Text(
                        "Give your query a name so you can find it later.",
                        fontSize = 14.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                    Spacer(Modifier.height(12.dp))
                    OutlinedTextField(
                        value = queryName,
                        onValueChange = { queryName = it },
                        placeholder = { Text("e.g. Weekly Groceries") },
                        singleLine = true,
                        shape = RoundedCornerShape(12.dp),
                        modifier = Modifier.fillMaxWidth(),
                    )
                }
            },
            confirmButton = {
                Button(
                    onClick = {
                        showSaveDialog = false
                        showSnackbar("Query \"${queryName.ifBlank { "Untitled" }}\" saved")
                        queryName = ""
                    },
                    shape = RoundedCornerShape(12.dp),
                ) {
                    Text("Save")
                }
            },
            dismissButton = {
                OutlinedButton(
                    onClick = { showSaveDialog = false; queryName = "" },
                    shape = RoundedCornerShape(12.dp),
                ) {
                    Text("Cancel")
                }
            },
        )
    }
}
