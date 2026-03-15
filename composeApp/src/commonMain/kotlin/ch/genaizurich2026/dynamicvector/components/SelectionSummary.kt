package ch.genaizurich2026.dynamicvector.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import ch.genaizurich2026.dynamicvector.model.ContextAnswer

@Composable
fun SelectionSummary(
    selections: Map<String, List<ContextAnswer>>,
    fieldLabels: Map<String, String>,
    onRemove: (String, String) -> Unit,
    onEditField: (String) -> Unit,
    modifier: Modifier = Modifier,
) {
    val filledFields = selections.filter { it.value.isNotEmpty() }
    if (filledFields.isEmpty()) return

    val totalFilters = filledFields.values.sumOf { it.size }

    Surface(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        color = MaterialTheme.colorScheme.surface,
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outline),
        tonalElevation = 1.dp,
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = "YOUR QUERY \u00b7 $totalFilters filters",
                fontSize = 11.sp,
                fontWeight = FontWeight.Medium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                letterSpacing = 1.5.sp,
            )

            Spacer(Modifier.height(12.dp))

            filledFields.forEach { (fieldKey, answers) ->
                Row(
                    modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
                    verticalAlignment = Alignment.Top,
                ) {
                    Text(
                        text = (fieldLabels[fieldKey] ?: fieldKey).uppercase(),
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Medium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        letterSpacing = 0.8.sp,
                        modifier = Modifier.width(80.dp).padding(top = 4.dp),
                    )

                    FlowRow(
                        modifier = Modifier.weight(1f),
                        horizontalArrangement = Arrangement.spacedBy(6.dp),
                        verticalArrangement = Arrangement.spacedBy(6.dp),
                    ) {
                        answers.forEach { answer ->
                            Surface(
                                shape = RoundedCornerShape(8.dp),
                                color = MaterialTheme.colorScheme.secondary,
                            ) {
                                Row(
                                    modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp),
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.spacedBy(4.dp),
                                ) {
                                    Text(
                                        text = answer.label,
                                        fontSize = 12.sp,
                                        fontWeight = FontWeight.Medium,
                                        color = MaterialTheme.colorScheme.onSecondary,
                                    )
                                    Text(
                                        text = "\u2715",
                                        fontSize = 10.sp,
                                        color = MaterialTheme.colorScheme.onSecondary.copy(alpha = 0.5f),
                                        modifier = Modifier
                                            .clip(RoundedCornerShape(4.dp))
                                            .clickable { onRemove(fieldKey, answer.questionId) },
                                    )
                                }
                            }
                        }
                    }

                    Text(
                        text = "\u270E",
                        fontSize = 12.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier
                            .padding(start = 8.dp, top = 4.dp)
                            .clip(RoundedCornerShape(4.dp))
                            .clickable { onEditField(fieldKey) },
                    )
                }
            }
        }
    }
}
