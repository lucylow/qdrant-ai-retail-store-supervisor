package dev.dynamicvector.theme

import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

// ── Design system: Swiss Flag — red field, white elements ──

object DVColors {
    // Core backgrounds — deep Swiss red
    val Background        = Color(0xFF8B1A1A)   // deep crimson
    val Surface           = Color(0xFF7A1616)   // slightly darker red
    val SurfaceVariant    = Color(0x0FFFFFFF)   // white at 6%
    val CardGradientStart = Color(0x0DFFFFFF)   // white at 5%
    val CardGradientEnd   = Color(0x05FFFFFF)   // white at 2%
    val CardBorder        = Color(0x0FFFFFFF)   // white at 6%
    val CardTopEdge       = Color(0x40FFFFFF)   // white at 25%

    // Primary accent — White (inverted from red)
    val Accent       = Color(0xFFFFFFFF)
    val AccentDim    = Color(0x1AFFFFFF) // 10%
    val AccentBorder = Color(0x40FFFFFF) // 25%
    val AccentDark   = Color(0xFFE8D8D8) // warm off-white

    // Text — light on red
    val TextPrimary   = Color(0xFFF5F0F0)   // near-white
    val TextSecondary = Color(0xA6FFFFFF)   // white at 65%
    val TextTertiary  = Color(0x66FFFFFF)   // white at 40%
    val TextHint      = Color(0x33FFFFFF)   // white at 20%

    // Icons — explicit, never currentColor
    val IconMuted      = Color(0xFFCC9090)  // muted pink on red
    val IconMutedLight = Color(0xFFDDA0A0)  // slightly brighter

    // Status — white/pink shades on red bg
    val StatusLive   = Color(0xFFFFFFFF) // bright white
    val StatusDone   = Color(0xFFD4BCBC) // muted warm gray
    val StatusStale  = Color(0xFFFFD5D5) // pinkish white
    val StatusFailed = Color(0xFF3A0808) // very dark red (almost black)

    // Source badges — subtle white/cream variants to distinguish on red
    val Qdrant       = Color(0xFFFFFFFF) // pure white
    val QdrantBg     = Color(0x1AFFFFFF)
    val QdrantBd     = Color(0x26FFFFFF)
    val Apify        = Color(0xFFFFE8E0) // warm peach-white
    val ApifyBg      = Color(0x1AFFF0E8)
    val ApifyBd      = Color(0x26FFF0E8)
    val LiveMap      = Color(0xFFFFD8D0) // rose-white
    val LiveMapBg    = Color(0x1AFFD8D0)
    val LiveMapBd    = Color(0x26FFD8D0)
    val Local        = Color(0xFFE8D0C8) // muted cream
    val LocalBg      = Color(0x1AE8D0C8)
    val LocalBd      = Color(0x26E8D0C8)
    val HuggingFace  = Color(0xFFFFF0F0) // cool pink-white
    val HuggingFaceBg = Color(0x1AFFF0F0)
    val HuggingFaceBd = Color(0x26FFF0F0)
    val Git          = Color(0xFFD8C0C0) // silver-rose
    val GitBg        = Color(0x1AD8C0C0)
    val GitBd        = Color(0x26D8C0C0)

    // Star
    val StarActive = Color(0xFFFFFFFF)
}

object DVTypography {
    val H1 = TextStyle(fontSize = 20.sp, fontWeight = FontWeight.Bold, color = DVColors.TextPrimary, letterSpacing = (-0.3).sp)
    val H2 = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.SemiBold, color = DVColors.TextPrimary)
    val CardTitle = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.SemiBold, color = DVColors.TextPrimary)
    val Body = TextStyle(fontSize = 13.sp, fontWeight = FontWeight.Normal, color = DVColors.TextSecondary, lineHeight = 18.sp)
    val Caption = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Normal, color = DVColors.TextTertiary)
    val SectionLabel = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Bold, color = DVColors.TextTertiary, letterSpacing = 1.2.sp)
    val MetricValue = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.SemiBold, color = DVColors.TextPrimary)
    val Badge = TextStyle(fontSize = 10.sp, fontWeight = FontWeight.SemiBold, letterSpacing = 0.3.sp)
}

object DVShapes {
    val CardRadius = 20.dp
    val ChipRadius = 14.dp
    val ButtonRadius = 10.dp
    val PillRadius = 8.dp
    val BottomSheetRadius = 24.dp
    val SearchBarRadius = 16.dp
}

object DVElevation {
    val CardTonalElevation = 0.dp
    val CardShadowElevation = 8.dp
}

// Dark Swiss flag color scheme — red surfaces, white elements
private val SwissRedScheme = darkColorScheme(
    primary = DVColors.Accent,
    onPrimary = Color(0xFF8B1A1A),
    primaryContainer = Color(0xFF5A1010),
    onPrimaryContainer = Color.White,
    secondary = Color(0xFF6B1515),
    onSecondary = Color(0xFFE0C8C8),
    background = DVColors.Background,
    onBackground = DVColors.TextPrimary,
    surface = DVColors.Surface,
    onSurface = DVColors.TextPrimary,
    surfaceVariant = Color(0xFF6B1515),
    onSurfaceVariant = Color(0xFFCCA0A0),
    outline = Color(0xFFAA6060),
    outlineVariant = Color(0xFF5A1010),
    surfaceTint = Color.Transparent,
    error = Color(0xFFFFB4B4),
    onError = Color(0xFF3A0808),
)

@Composable
fun DynamicVectorTheme(
    content: @Composable () -> Unit,
) {
    MaterialTheme(
        colorScheme = SwissRedScheme,
        typography = Typography(),
        content = content,
    )
}
