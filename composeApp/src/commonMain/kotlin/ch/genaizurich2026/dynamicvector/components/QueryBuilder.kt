package ch.genaizurich2026.dynamicvector.components

import androidx.compose.animation.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.ChatBubbleOutline
import androidx.compose.material.icons.outlined.Close
import androidx.compose.material.icons.outlined.Edit
import androidx.compose.material.icons.outlined.Refresh
import androidx.compose.material.icons.outlined.Search
import androidx.compose.material.icons.automirrored.outlined.Send
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import ch.genaizurich2026.dynamicvector.data.agentQuestions
import ch.genaizurich2026.dynamicvector.data.typeLabels
import ch.genaizurich2026.dynamicvector.model.*

@Composable
fun QueryBuilder(
    onSearch: (List<QueryFilter>, String, List<String>) -> Unit,
    exclusions: List<String> = emptyList(),
    onRemoveExclusion: ((String) -> Unit)? = null,
    modifier: Modifier = Modifier,
) {
    var currentStep by remember { mutableStateOf(0) }
    var selections by remember { mutableStateOf(mapOf<FilterType, List<QueryFilter>>()) }
    var inputValue by remember { mutableStateOf("") }
    var refinements by remember { mutableStateOf(listOf<RefinementNote>()) }
    var isComplete by remember { mutableStateOf(false) }
    var editingStep by remember { mutableStateOf<Int?>(null) }
    var editingNoteId by remember { mutableStateOf<String?>(null) }
    var editingNoteText by remember { mutableStateOf("") }

    val totalSteps = agentQuestions.size
    val activeStep = editingStep ?: currentStep
    val currentQuestion = agentQuestions.getOrNull(activeStep)
    val allActiveFilters = selections.values.flatten()
    val canSearch = allActiveFilters.isNotEmpty() || refinements.isNotEmpty()

    fun isOptionSelected(optionId: String): Boolean =
        allActiveFilters.any { it.id == optionId }

    fun advanceStep() {
        if (editingStep != null) {
            editingStep = null
            return
        }
        if (currentStep < totalSteps - 1) {
            currentStep++
        } else {
            isComplete = true
        }
    }

    fun handleSelect(option: AgentOption) {
        val question = agentQuestions[activeStep]
        val type = question.type
        val filter = QueryFilter(
            id = option.id,
            type = type,
            label = option.label,
            value = option.value,
            active = true,
        )
        val current = selections[type].orEmpty()
        val exists = current.any { it.id == option.id }

        selections = if (question.multiSelect) {
            selections + (type to if (exists) current.filter { it.id != option.id } else current + filter)
        } else {
            selections + (type to if (exists) emptyList() else listOf(filter))
        }

        if (!question.multiSelect && !exists) {
            advanceStep()
        }
    }

    fun handleSkip() {
        val type = agentQuestions[activeStep].type
        selections = selections + (type to emptyList())
        advanceStep()
    }

    fun handleRemoveFilter(type: FilterType, id: String) {
        selections = selections + (type to (selections[type].orEmpty().filter { it.id != id }))
    }

    fun handleEditStep(stepIndex: Int) {
        editingStep = stepIndex
        isComplete = false
    }

    fun handleSendRefinement() {
        val text = inputValue.trim()
        if (text.isEmpty()) return
        refinements = refinements + RefinementNote(
            id = "ref-${refinements.size}",
            text = text,
        )
        inputValue = ""
    }

    fun handleDeleteRefinement(id: String) {
        refinements = refinements.filter { it.id != id }
    }

    fun handleSaveEditNote() {
        val noteId = editingNoteId ?: return
        val text = editingNoteText.trim()
        if (text.isEmpty()) {
            handleDeleteRefinement(noteId)
        } else {
            refinements = refinements.map {
                if (it.id == noteId) it.copy(text = text) else it
            }
        }
        editingNoteId = null
        editingNoteText = ""
    }

    fun handleSearch() {
        val allFilters = selections.values.flatten()
        val naturalQuery = refinements.joinToString(". ") { it.text }
        onSearch(allFilters, naturalQuery, exclusions)
    }

    fun handleReset() {
        currentStep = 0
        selections = emptyMap()
        inputValue = ""
        refinements = emptyList()
        isComplete = false
        editingStep = null
        editingNoteId = null
    }

    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        // Selection Summary
        if (allActiveFilters.isNotEmpty()) {
            SelectionSummary(
                selections = selections,
                typeLabels = typeLabels,
                onRemove = ::handleRemoveFilter,
                onEditType = { type ->
                    val idx = agentQuestions.indexOfFirst { it.type == type }
                    if (idx != -1) handleEditStep(idx)
                },
            )
        }

        // Exclusions
        if (exclusions.isNotEmpty()) {
            Surface(
                shape = RoundedCornerShape(12.dp),
                color = MaterialTheme.colorScheme.surface,
                border = BorderStroke(1.dp, MaterialTheme.colorScheme.error.copy(alpha = 0.2f)),
                tonalElevation = 1.dp,
            ) {
                Column(modifier = Modifier.padding(14.dp)) {
                    Text(
                        text = "EXCLUDED FROM RESULTS",
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Medium,
                        color = MaterialTheme.colorScheme.error,
                        letterSpacing = 1.5.sp,
                    )
                    Spacer(Modifier.height(8.dp))
                    FlowRow(
                        horizontalArrangement = Arrangement.spacedBy(6.dp),
                        verticalArrangement = Arrangement.spacedBy(6.dp),
                    ) {
                        exclusions.forEach { ex ->
                            Surface(
                                shape = RoundedCornerShape(8.dp),
                                color = MaterialTheme.colorScheme.error.copy(alpha = 0.1f),
                            ) {
                                Row(
                                    modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp),
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.spacedBy(4.dp),
                                ) {
                                    Text(
                                        text = ex,
                                        fontSize = 12.sp,
                                        fontWeight = FontWeight.Medium,
                                        color = MaterialTheme.colorScheme.error,
                                    )
                                    if (onRemoveExclusion != null) {
                                        Icon(
                                            imageVector = Icons.Outlined.Close,
                                            contentDescription = "Remove",
                                            modifier = Modifier
                                                .size(14.dp)
                                                .clip(RoundedCornerShape(4.dp))
                                                .clickable { onRemoveExclusion(ex) },
                                            tint = MaterialTheme.colorScheme.error.copy(alpha = 0.5f),
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        // Current question
        AnimatedVisibility(
            visible = !isComplete && currentQuestion != null,
            enter = fadeIn() + slideInVertically { it / 4 },
            exit = fadeOut() + slideOutVertically { -it / 4 },
        ) {
            if (currentQuestion != null) {
                Surface(
                    shape = RoundedCornerShape(12.dp),
                    color = MaterialTheme.colorScheme.surface,
                    border = BorderStroke(1.dp, MaterialTheme.colorScheme.primary.copy(alpha = 0.2f)),
                    tonalElevation = 2.dp,
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        // Question header
                        Row(
                            horizontalArrangement = Arrangement.spacedBy(10.dp),
                            verticalAlignment = Alignment.Top,
                        ) {
                            Box(
                                modifier = Modifier
                                    .size(28.dp)
                                    .clip(CircleShape)
                                    .background(MaterialTheme.colorScheme.primary),
                                contentAlignment = Alignment.Center,
                            ) {
                                Icon(
                                    imageVector = Icons.Outlined.ChatBubbleOutline,
                                    contentDescription = null,
                                    modifier = Modifier.size(14.dp),
                                    tint = MaterialTheme.colorScheme.onPrimary,
                                )
                            }
                            Column {
                                Text(
                                    text = currentQuestion.question,
                                    fontSize = 14.sp,
                                    fontWeight = FontWeight.Medium,
                                    color = MaterialTheme.colorScheme.onSurface,
                                )
                                Text(
                                    text = if (currentQuestion.multiSelect) "Select all that apply" else "Tap to select one",
                                    fontSize = 11.sp,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                                    modifier = Modifier.padding(top = 2.dp),
                                )
                            }
                        }

                        Spacer(Modifier.height(12.dp))

                        // Options
                        FlowRow(
                            horizontalArrangement = Arrangement.spacedBy(8.dp),
                            verticalArrangement = Arrangement.spacedBy(8.dp),
                        ) {
                            currentQuestion.options.forEach { option ->
                                QueryFilterChip(
                                    label = option.label,
                                    active = isOptionSelected(option.id),
                                    onToggle = { handleSelect(option) },
                                )
                            }
                        }

                        Spacer(Modifier.height(12.dp))

                        // Footer actions
                        HorizontalDivider(color = MaterialTheme.colorScheme.outline)
                        Spacer(Modifier.height(8.dp))

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically,
                        ) {
                            Text(
                                text = "Skip this",
                                fontSize = 12.sp,
                                fontWeight = FontWeight.Medium,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                                modifier = Modifier
                                    .clip(RoundedCornerShape(4.dp))
                                    .clickable { handleSkip() }
                                    .padding(4.dp),
                            )

                            if (currentQuestion.multiSelect) {
                                Text(
                                    text = "Continue \u203A",
                                    fontSize = 12.sp,
                                    fontWeight = FontWeight.Medium,
                                    color = MaterialTheme.colorScheme.primary,
                                    modifier = Modifier
                                        .clip(RoundedCornerShape(4.dp))
                                        .clickable { advanceStep() }
                                        .padding(4.dp),
                                )
                            }

                            if (editingStep != null && currentQuestion.multiSelect.not()) {
                                Text(
                                    text = "Done \u203A",
                                    fontSize = 12.sp,
                                    fontWeight = FontWeight.Medium,
                                    color = MaterialTheme.colorScheme.primary,
                                    modifier = Modifier
                                        .clip(RoundedCornerShape(4.dp))
                                        .clickable { editingStep = null }
                                        .padding(4.dp),
                                )
                            }
                        }

                        // Progress bar
                        Spacer(Modifier.height(12.dp))
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(4.dp),
                        ) {
                            agentQuestions.forEachIndexed { i, _ ->
                                val color = when {
                                    i < currentStep -> MaterialTheme.colorScheme.primary
                                    i == activeStep -> MaterialTheme.colorScheme.primary.copy(alpha = 0.4f)
                                    else -> MaterialTheme.colorScheme.surfaceVariant
                                }
                                Box(
                                    modifier = Modifier
                                        .weight(1f)
                                        .height(4.dp)
                                        .clip(RoundedCornerShape(2.dp))
                                        .background(color),
                                )
                            }
                        }
                    }
                }
            }
        }

        // Refinement notes
        if (currentStep > 0 || isComplete) {
            refinements.forEach { note ->
                Surface(
                    shape = RoundedCornerShape(12.dp),
                    color = MaterialTheme.colorScheme.primary.copy(alpha = 0.05f),
                    border = BorderStroke(1.dp, MaterialTheme.colorScheme.primary.copy(alpha = 0.15f)),
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 16.dp, vertical = 10.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        if (editingNoteId == note.id) {
                            OutlinedTextField(
                                value = editingNoteText,
                                onValueChange = { editingNoteText = it },
                                modifier = Modifier.weight(1f),
                                singleLine = true,
                                textStyle = LocalTextStyle.current.copy(fontSize = 14.sp),
                                keyboardOptions = KeyboardOptions(imeAction = ImeAction.Done),
                                keyboardActions = KeyboardActions(onDone = { handleSaveEditNote() }),
                            )
                        } else {
                            Text(
                                text = note.text,
                                fontSize = 14.sp,
                                color = MaterialTheme.colorScheme.onSurface,
                                modifier = Modifier.weight(1f),
                            )
                        }

                        if (editingNoteId != note.id) {
                            IconButton(
                                onClick = {
                                    editingNoteId = note.id
                                    editingNoteText = note.text
                                },
                                modifier = Modifier.size(32.dp),
                            ) {
                                Icon(
                                    imageVector = Icons.Outlined.Edit,
                                    contentDescription = "Edit",
                                    modifier = Modifier.size(16.dp),
                                    tint = MaterialTheme.colorScheme.onSurfaceVariant,
                                )
                            }
                        }
                        IconButton(
                            onClick = { handleDeleteRefinement(note.id) },
                            modifier = Modifier.size(32.dp),
                        ) {
                            Icon(
                                imageVector = Icons.Outlined.Close,
                                contentDescription = "Delete",
                                modifier = Modifier.size(16.dp),
                                tint = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                        }
                    }
                }
            }

            // Input field
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                OutlinedTextField(
                    value = inputValue,
                    onValueChange = { inputValue = it },
                    modifier = Modifier.weight(1f),
                    placeholder = {
                        Text(
                            "Add details to refine your search\u2026",
                            fontSize = 14.sp,
                        )
                    },
                    singleLine = true,
                    shape = RoundedCornerShape(12.dp),
                    keyboardOptions = KeyboardOptions(imeAction = ImeAction.Send),
                    keyboardActions = KeyboardActions(onSend = { handleSendRefinement() }),
                )
                Button(
                    onClick = { handleSendRefinement() },
                    enabled = inputValue.isNotBlank(),
                    shape = RoundedCornerShape(12.dp),
                    contentPadding = PaddingValues(12.dp),
                    modifier = Modifier.height(56.dp),
                ) {
                    Icon(
                        imageVector = Icons.AutoMirrored.Outlined.Send,
                        contentDescription = "Send",
                        modifier = Modifier.size(20.dp),
                    )
                }
            }
        }

        // Action buttons
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            if (currentStep > 0 || isComplete) {
                OutlinedButton(
                    onClick = { handleReset() },
                    shape = RoundedCornerShape(12.dp),
                    contentPadding = PaddingValues(horizontal = 16.dp, vertical = 14.dp),
                ) {
                    Icon(
                        imageVector = Icons.Outlined.Refresh,
                        contentDescription = "Reset",
                        modifier = Modifier.size(20.dp),
                    )
                }
            }
            Button(
                onClick = { handleSearch() },
                enabled = canSearch,
                modifier = Modifier.weight(1f),
                shape = RoundedCornerShape(12.dp),
                contentPadding = PaddingValues(vertical = 14.dp),
            ) {
                Row(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Icon(
                        imageVector = Icons.Outlined.Search,
                        contentDescription = null,
                        modifier = Modifier.size(20.dp),
                    )
                    Text(
                        "Find Best Options",
                        fontSize = 15.sp,
                        fontWeight = FontWeight.Medium,
                    )
                }
            }
        }
    }
}
