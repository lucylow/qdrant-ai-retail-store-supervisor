package ch.genaizurich2026.dynamicvector.screens

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.ui.graphics.Color
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.outlined.Notes
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import ch.genaizurich2026.dynamicvector.data.mockRepositories
import ch.genaizurich2026.dynamicvector.model.Repository
import ch.genaizurich2026.dynamicvector.model.RepositoryPreferences

@Composable
fun RepositoriesScreen(
    showSnackbar: (String) -> Unit = {},
) {
    val repos = mockRepositories
    var showAdd by remember { mutableStateOf(false) }
    var newName by remember { mutableStateOf("") }
    var newEndpoint by remember { mutableStateOf("") }
    var newDesc by remember { mutableStateOf("") }
    var editingRepo by remember { mutableStateOf<Repository?>(null) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .statusBarsPadding()
            .verticalScroll(rememberScrollState()),
    ) {
        // Header
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(start = 20.dp, end = 12.dp, top = 16.dp, bottom = 16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(
                text = "Repositories",
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onBackground,
            )
            FilledTonalIconButton(
                onClick = { showAdd = !showAdd },
            ) {
                Icon(
                    imageVector = Icons.Filled.Add,
                    contentDescription = "Add Repository",
                )
            }
        }

            // Add form
            AnimatedVisibility(visible = showAdd) {
                Surface(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp, vertical = 4.dp),
                    shape = RoundedCornerShape(16.dp),
                    color = MaterialTheme.colorScheme.surface,
                    tonalElevation = 2.dp,
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp),
                    ) {
                        Text(
                            text = "New Repository",
                            fontSize = 16.sp,
                            fontWeight = FontWeight.SemiBold,
                            color = MaterialTheme.colorScheme.onSurface,
                        )
                        FormField("NAME", newName, { newName = it }, "e.g. Product Catalog")
                        FormField("ENDPOINT URL", newEndpoint, { newEndpoint = it }, "https://api.example.com/data")
                        FormField("DESCRIPTION", newDesc, { newDesc = it }, "What data does this repository provide?")

                        Row(
                            modifier = Modifier.fillMaxWidth().padding(top = 4.dp),
                            horizontalArrangement = Arrangement.spacedBy(8.dp),
                        ) {
                            OutlinedButton(
                                onClick = {
                                    showAdd = false
                                    newName = ""
                                    newEndpoint = ""
                                    newDesc = ""
                                },
                                modifier = Modifier.weight(1f),
                                shape = RoundedCornerShape(12.dp),
                            ) {
                                Text("Cancel")
                            }
                            Button(
                                onClick = {
                                    showAdd = false
                                    newName = ""
                                    newEndpoint = ""
                                    newDesc = ""
                                },
                                modifier = Modifier.weight(1f),
                                shape = RoundedCornerShape(12.dp),
                                enabled = newName.isNotBlank() && newEndpoint.isNotBlank(),
                            ) {
                                Text("Save")
                            }
                        }
                    }
                }
            }

            // Repository list
            Column(
                modifier = Modifier.padding(horizontal = 16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                repos.forEach { repo ->
                    Surface(
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(16.dp),
                        color = MaterialTheme.colorScheme.surface,
                        tonalElevation = 1.dp,
                    ) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            // Header row
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                verticalAlignment = Alignment.Top,
                            ) {
                                Box(
                                    modifier = Modifier
                                        .size(40.dp)
                                        .background(
                                            MaterialTheme.colorScheme.primaryContainer,
                                            RoundedCornerShape(10.dp),
                                        ),
                                    contentAlignment = Alignment.Center,
                                ) {
                                    Icon(
                                        imageVector = Icons.Outlined.Storage,
                                        contentDescription = null,
                                        modifier = Modifier.size(20.dp),
                                        tint = MaterialTheme.colorScheme.onPrimaryContainer,
                                    )
                                }

                                Spacer(Modifier.width(12.dp))

                                Column(modifier = Modifier.weight(1f)) {
                                    Text(
                                        text = repo.name,
                                        fontSize = 16.sp,
                                        fontWeight = FontWeight.SemiBold,
                                        color = MaterialTheme.colorScheme.onSurface,
                                    )
                                    Text(
                                        text = repo.description,
                                        fontSize = 13.sp,
                                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                                        modifier = Modifier.padding(top = 2.dp),
                                    )
                                }

                                Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                                    IconButton(
                                        onClick = { editingRepo = repo },
                                        modifier = Modifier.size(32.dp),
                                    ) {
                                        Icon(
                                            imageVector = Icons.Outlined.Edit,
                                            contentDescription = "Edit",
                                            modifier = Modifier.size(18.dp),
                                            tint = MaterialTheme.colorScheme.onSurfaceVariant,
                                        )
                                    }
                                    IconButton(
                                        onClick = { showSnackbar("\"${repo.name}\" removed") },
                                        modifier = Modifier.size(32.dp),
                                    ) {
                                        Icon(
                                            imageVector = Icons.Outlined.Delete,
                                            contentDescription = "Delete",
                                            modifier = Modifier.size(18.dp),
                                            tint = MaterialTheme.colorScheme.onSurfaceVariant,
                                        )
                                    }
                                }
                            }

                            // Endpoint + connection status
                            Row(
                                modifier = Modifier.padding(top = 12.dp),
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(6.dp),
                            ) {
                                Box(
                                    modifier = Modifier
                                        .size(8.dp)
                                        .background(
                                            if (repo.preferences != null) Color(0xFF16A34A) else Color(0xFF9CA3AF),
                                            CircleShape,
                                        ),
                                )
                                Icon(
                                    imageVector = Icons.Outlined.Link,
                                    contentDescription = null,
                                    modifier = Modifier.size(14.dp),
                                    tint = MaterialTheme.colorScheme.primary,
                                )
                                Text(
                                    text = repo.endpoint,
                                    fontSize = 13.sp,
                                    color = MaterialTheme.colorScheme.primary,
                                    maxLines = 1,
                                    overflow = TextOverflow.Ellipsis,
                                )
                            }

                            // Preferences summary
                            repo.preferences?.let { prefs ->
                                HorizontalDivider(
                                    modifier = Modifier.padding(vertical = 12.dp),
                                    color = MaterialTheme.colorScheme.outline.copy(alpha = 0.3f),
                                )

                                Text(
                                    text = "QUERY PREFERENCES",
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.SemiBold,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                                    letterSpacing = 0.8.sp,
                                    modifier = Modifier.padding(bottom = 8.dp),
                                )

                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                ) {
                                    Text("Price range", fontSize = 13.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                                    Text(
                                        "\$${prefs.priceRange.first} \u2013 \$${prefs.priceRange.second}",
                                        fontSize = 13.sp,
                                        fontWeight = FontWeight.Medium,
                                        color = MaterialTheme.colorScheme.onSurface,
                                    )
                                }

                                Spacer(Modifier.height(4.dp))

                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                ) {
                                    Text("Sustainability", fontSize = 13.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                                    Text(
                                        prefs.sustainabilityPriority.replaceFirstChar { it.uppercase() },
                                        fontSize = 13.sp,
                                        fontWeight = FontWeight.Medium,
                                        color = MaterialTheme.colorScheme.onSurface,
                                    )
                                }

                                val allChips = prefs.goals + prefs.preferredBrands + prefs.values
                                if (allChips.isNotEmpty()) {
                                    Spacer(Modifier.height(8.dp))
                                    FlowRow(
                                        horizontalArrangement = Arrangement.spacedBy(6.dp),
                                        verticalArrangement = Arrangement.spacedBy(6.dp),
                                    ) {
                                        allChips.forEach { chip ->
                                            Surface(
                                                shape = RoundedCornerShape(16.dp),
                                                color = MaterialTheme.colorScheme.secondaryContainer,
                                            ) {
                                                Text(
                                                    text = chip,
                                                    fontSize = 12.sp,
                                                    fontWeight = FontWeight.Medium,
                                                    color = MaterialTheme.colorScheme.onSecondaryContainer,
                                                    modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp),
                                                )
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                Spacer(Modifier.height(96.dp))
            }
        }

    // Edit preferences dialog
    editingRepo?.let { repo ->
        EditPreferencesDialog(
            repo = repo,
            onDismiss = { editingRepo = null },
            onSave = { editingRepo = null },
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun EditPreferencesDialog(
    repo: Repository,
    onDismiss: () -> Unit,
    onSave: () -> Unit,
) {
    val prefs = repo.preferences ?: RepositoryPreferences(
        goals = emptyList(),
        preferredBrands = emptyList(),
        sustainabilityPriority = "medium",
        priceRange = Pair(0, 200),
        values = emptyList(),
        customNotes = "",
    )

    var goalsText by remember { mutableStateOf(prefs.goals.joinToString("\n")) }
    var brandsText by remember { mutableStateOf(prefs.preferredBrands.joinToString(", ")) }
    var valuesText by remember { mutableStateOf(prefs.values.joinToString(", ")) }
    var priceMin by remember { mutableStateOf(prefs.priceRange.first.toString()) }
    var priceMax by remember { mutableStateOf(prefs.priceRange.second.toString()) }
    var sustainability by remember { mutableStateOf(prefs.sustainabilityPriority) }
    var customNotes by remember { mutableStateOf(prefs.customNotes) }

    Dialog(onDismissRequest = onDismiss) {
        Surface(
            shape = RoundedCornerShape(24.dp),
            color = MaterialTheme.colorScheme.surface,
            tonalElevation = 6.dp,
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .heightIn(max = 600.dp)
                    .verticalScroll(rememberScrollState())
                    .padding(24.dp),
                verticalArrangement = Arrangement.spacedBy(20.dp),
            ) {
                // Title
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Column {
                        Text(
                            text = "Edit Preferences",
                            fontSize = 20.sp,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onSurface,
                        )
                        Text(
                            text = repo.name,
                            fontSize = 14.sp,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            modifier = Modifier.padding(top = 2.dp),
                        )
                    }
                    IconButton(onClick = onDismiss) {
                        Icon(
                            imageVector = Icons.Outlined.Close,
                            contentDescription = "Close",
                            tint = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                }

                HorizontalDivider(color = MaterialTheme.colorScheme.outline.copy(alpha = 0.3f))

                // Goals
                DialogSection(
                    icon = Icons.Outlined.Flag,
                    title = "Goals",
                    subtitle = "What should the agent optimize for?",
                ) {
                    OutlinedTextField(
                        value = goalsText,
                        onValueChange = { goalsText = it },
                        modifier = Modifier.fillMaxWidth(),
                        placeholder = { Text("One goal per line", fontSize = 14.sp) },
                        minLines = 2,
                        maxLines = 4,
                        shape = RoundedCornerShape(12.dp),
                    )
                }

                // Price Range
                DialogSection(
                    icon = Icons.Outlined.AttachMoney,
                    title = "Price Range",
                    subtitle = "Budget constraints for this source",
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(12.dp),
                    ) {
                        OutlinedTextField(
                            value = priceMin,
                            onValueChange = { priceMin = it },
                            modifier = Modifier.weight(1f),
                            label = { Text("Min") },
                            prefix = { Text("$") },
                            singleLine = true,
                            shape = RoundedCornerShape(12.dp),
                        )
                        OutlinedTextField(
                            value = priceMax,
                            onValueChange = { priceMax = it },
                            modifier = Modifier.weight(1f),
                            label = { Text("Max") },
                            prefix = { Text("$") },
                            singleLine = true,
                            shape = RoundedCornerShape(12.dp),
                        )
                    }
                }

                // Sustainability
                DialogSection(
                    icon = Icons.Outlined.Eco,
                    title = "Sustainability",
                    subtitle = "How important is sustainability?",
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        listOf("low", "medium", "high").forEach { level ->
                            val selected = sustainability == level
                            FilterChipButton(
                                label = level.replaceFirstChar { it.uppercase() },
                                selected = selected,
                                onClick = { sustainability = level },
                                modifier = Modifier.weight(1f),
                            )
                        }
                    }
                }

                // Preferred Brands
                DialogSection(
                    icon = Icons.Outlined.Loyalty,
                    title = "Preferred Brands",
                    subtitle = "Comma-separated brand names",
                ) {
                    OutlinedTextField(
                        value = brandsText,
                        onValueChange = { brandsText = it },
                        modifier = Modifier.fillMaxWidth(),
                        placeholder = { Text("e.g. Patagonia, Allbirds", fontSize = 14.sp) },
                        singleLine = true,
                        shape = RoundedCornerShape(12.dp),
                    )
                }

                // Values
                DialogSection(
                    icon = Icons.Outlined.Verified,
                    title = "Values",
                    subtitle = "Comma-separated values to prioritize",
                ) {
                    OutlinedTextField(
                        value = valuesText,
                        onValueChange = { valuesText = it },
                        modifier = Modifier.fillMaxWidth(),
                        placeholder = { Text("e.g. Eco-Friendly, Fair Trade", fontSize = 14.sp) },
                        singleLine = true,
                        shape = RoundedCornerShape(12.dp),
                    )
                }

                // Custom Notes
                DialogSection(
                    icon = Icons.AutoMirrored.Outlined.Notes,
                    title = "Custom Notes",
                    subtitle = "Additional instructions for the agent",
                ) {
                    OutlinedTextField(
                        value = customNotes,
                        onValueChange = { customNotes = it },
                        modifier = Modifier.fillMaxWidth(),
                        placeholder = { Text("Any extra context\u2026", fontSize = 14.sp) },
                        minLines = 2,
                        maxLines = 3,
                        shape = RoundedCornerShape(12.dp),
                    )
                }

                // Buttons
                Row(
                    modifier = Modifier.fillMaxWidth().padding(top = 4.dp),
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                ) {
                    OutlinedButton(
                        onClick = onDismiss,
                        modifier = Modifier.weight(1f),
                        shape = RoundedCornerShape(12.dp),
                    ) {
                        Text("Cancel")
                    }
                    Button(
                        onClick = onSave,
                        modifier = Modifier.weight(1f),
                        shape = RoundedCornerShape(12.dp),
                    ) {
                        Text("Save")
                    }
                }
            }
        }
    }
}

@Composable
private fun DialogSection(
    icon: ImageVector,
    title: String,
    subtitle: String,
    content: @Composable ColumnScope.() -> Unit,
) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                modifier = Modifier.size(18.dp),
                tint = MaterialTheme.colorScheme.primary,
            )
            Column {
                Text(
                    text = title,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = MaterialTheme.colorScheme.onSurface,
                )
                Text(
                    text = subtitle,
                    fontSize = 12.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }
        content()
    }
}

@Composable
private fun FilterChipButton(
    label: String,
    selected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val containerColor = if (selected) MaterialTheme.colorScheme.primary
    else MaterialTheme.colorScheme.surface
    val contentColor = if (selected) MaterialTheme.colorScheme.onPrimary
    else MaterialTheme.colorScheme.onSurfaceVariant

    Button(
        onClick = onClick,
        modifier = modifier,
        shape = RoundedCornerShape(10.dp),
        colors = ButtonDefaults.buttonColors(
            containerColor = containerColor,
            contentColor = contentColor,
        ),
        contentPadding = PaddingValues(vertical = 10.dp),
    ) {
        Text(label, fontSize = 13.sp, fontWeight = FontWeight.Medium)
    }
}

@Composable
private fun FormField(
    label: String,
    value: String,
    onValueChange: (String) -> Unit,
    placeholder: String,
) {
    Column {
        Text(
            text = label,
            fontSize = 11.sp,
            fontWeight = FontWeight.Medium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            letterSpacing = 1.sp,
            modifier = Modifier.padding(bottom = 6.dp),
        )
        OutlinedTextField(
            value = value,
            onValueChange = onValueChange,
            modifier = Modifier.fillMaxWidth(),
            placeholder = { Text(placeholder, fontSize = 14.sp) },
            singleLine = true,
            shape = RoundedCornerShape(12.dp),
        )
    }
}
