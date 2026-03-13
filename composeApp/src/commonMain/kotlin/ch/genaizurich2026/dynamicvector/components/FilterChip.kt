package ch.genaizurich2026.dynamicvector.components

import androidx.compose.animation.animateColorAsState
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

@Composable
fun QueryFilterChip(
    label: String,
    active: Boolean,
    onToggle: () -> Unit,
    onRemove: (() -> Unit)? = null,
    modifier: Modifier = Modifier,
) {
    val backgroundColor by animateColorAsState(
        if (active) MaterialTheme.colorScheme.primary
        else MaterialTheme.colorScheme.surface
    )
    val contentColor by animateColorAsState(
        if (active) MaterialTheme.colorScheme.onPrimary
        else MaterialTheme.colorScheme.onSurfaceVariant
    )
    val borderColor by animateColorAsState(
        if (active) MaterialTheme.colorScheme.primary
        else MaterialTheme.colorScheme.outline
    )

    Surface(
        modifier = modifier
            .clip(RoundedCornerShape(8.dp))
            .clickable(onClick = onToggle),
        shape = RoundedCornerShape(8.dp),
        color = backgroundColor,
        border = if (!active) BorderStroke(1.dp, borderColor) else null,
        tonalElevation = if (active) 1.dp else 0.dp,
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(4.dp),
        ) {
            if (active) {
                Text(
                    text = "\u2713",
                    color = contentColor,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Bold,
                )
            }
            Text(
                text = label,
                color = contentColor,
                fontSize = 13.sp,
                fontWeight = FontWeight.Medium,
            )
            if (onRemove != null && active) {
                Text(
                    text = "\u2715",
                    color = contentColor.copy(alpha = 0.7f),
                    fontSize = 11.sp,
                    modifier = Modifier
                        .clip(RoundedCornerShape(4.dp))
                        .clickable { onRemove() }
                        .padding(start = 2.dp),
                )
            }
        }
    }
}
