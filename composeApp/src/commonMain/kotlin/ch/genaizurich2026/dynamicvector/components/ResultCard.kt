package ch.genaizurich2026.dynamicvector.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.graphics.Color
import ch.genaizurich2026.dynamicvector.model.ShoppingResult
import ch.genaizurich2026.dynamicvector.model.TagColor
import ch.genaizurich2026.dynamicvector.theme.*

@Composable
fun ResultCard(
    result: ShoppingResult,
    onExclude: ((ShoppingResult) -> Unit)? = null,
    modifier: Modifier = Modifier,
) {
    Surface(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        color = MaterialTheme.colorScheme.surface,
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outline),
        tonalElevation = 1.dp,
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            horizontalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            // Product image placeholder
            Box(
                modifier = Modifier
                    .size(56.dp)
                    .clip(RoundedCornerShape(8.dp))
                    .background(MaterialTheme.colorScheme.secondary),
                contentAlignment = Alignment.Center,
            ) {
                Text(text = "\uD83D\uDECD\uFE0F", fontSize = 20.sp)
            }

            Column(modifier = Modifier.weight(1f)) {
                // Name + match score
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.Top,
                ) {
                    Text(
                        text = result.name,
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Medium,
                        color = MaterialTheme.colorScheme.onSurface,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis,
                        modifier = Modifier.weight(1f),
                    )

                    Row(
                        horizontalArrangement = Arrangement.spacedBy(6.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        val scoreColor = when {
                            result.matchScore >= 90 -> MatchHigh
                            result.matchScore >= 75 -> MatchMedium
                            else -> MatchLow
                        }
                        Surface(
                            shape = RoundedCornerShape(6.dp),
                            color = scoreColor,
                        ) {
                            Text(
                                text = "${result.matchScore}%",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Medium,
                                color = Color.White,
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp),
                            )
                        }

                        if (onExclude != null) {
                            Text(
                                text = "\uD83D\uDC4E",
                                fontSize = 13.sp,
                                modifier = Modifier
                                    .clip(RoundedCornerShape(6.dp))
                                    .clickable { onExclude(result) }
                                    .padding(4.dp),
                            )
                        }
                    }
                }

                // Brand + source
                Text(
                    text = "${result.brand} \u00b7 ${result.source}",
                    fontSize = 12.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.padding(top = 2.dp),
                )

                // Price + rating
                Row(
                    modifier = Modifier.padding(top = 8.dp),
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text(
                        text = "$${result.price.formatPrice()}",
                        fontSize = 15.sp,
                        fontWeight = FontWeight.Medium,
                        color = MaterialTheme.colorScheme.onSurface,
                    )
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(4.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Text(
                            text = "\u2605",
                            fontSize = 12.sp,
                            color = Amber500,
                        )
                        Text(
                            text = result.rating.formatRating(),
                            fontSize = 12.sp,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                }

                // Tags
                if (result.tags.isNotEmpty()) {
                    FlowRow(
                        modifier = Modifier.padding(top = 8.dp),
                        horizontalArrangement = Arrangement.spacedBy(4.dp),
                        verticalArrangement = Arrangement.spacedBy(4.dp),
                    ) {
                        result.tags.forEach { tag ->
                            val (bgColor, textColor) = when (tag.color) {
                                TagColor.GREEN -> TagGreenBg to TagGreen
                                TagColor.BLUE -> TagBlueBg to TagBlue
                                TagColor.PURPLE -> TagPurpleBg to TagPurple
                            }
                            Surface(
                                shape = RoundedCornerShape(6.dp),
                                color = bgColor,
                            ) {
                                Text(
                                    text = tag.label,
                                    fontSize = 10.sp,
                                    fontWeight = FontWeight.Medium,
                                    color = textColor,
                                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp),
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}

private fun Double.formatPrice(): String {
    val whole = toLong()
    val cents = ((this - whole) * 100).toInt()
    return "$whole.${cents.toString().padStart(2, '0')}"
}

private fun Double.formatRating(): String {
    val whole = toLong()
    val decimal = ((this - whole) * 10).toInt()
    return "$whole.$decimal"
}
