package dev.dynamicvector.theme

import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

// ── Design system: Light Swiss — white field, red elements ──

object DVColors {
    // Core backgrounds — clean white
    val Background        = Color(0xFFFFFAF8)   // warm white
    val Surface           = Color(0xFFFFF5F0)   // very light warm
    val SurfaceVariant    = Color(0x0ADC2626)   // red at 4%
    val CardGradientStart = Color(0xFFFFFFFF)   // white
    val CardGradientEnd   = Color(0xFFFFF8F6)   // barely warm
    val CardBorder        = Color(0x15DC2626)   // red at 8%
    val CardTopEdge       = Color(0x50DC2626)   // Swiss red at 30%

    // Primary accent — Swiss Red
    val Accent       = Color(0xFFDC2626)
    val AccentDim    = Color(0x14DC2626) // 8%
    val AccentBorder = Color(0x30DC2626) // 19%
    val AccentDark   = Color(0xFFB91C1C) // darker red

    // Text — dark on white
    val TextPrimary   = Color(0xFF1A0808)   // near-black warm
    val TextSecondary = Color(0xFF6B3535)   // dark red-brown
    val TextTertiary  = Color(0xFF997070)   // medium red-brown
    val TextHint      = Color(0xFFCCA8A8)   // light muted red

    // Icons
    val IconMuted      = Color(0xFFB08080)  // muted rose
    val IconMutedLight = Color(0xFFC09090)

    // Status — all red shades
    val StatusLive   = Color(0xFFDC2626) // bright Swiss red
    val StatusDone   = Color(0xFF7F4040) // dark muted red
    val StatusStale  = Color(0xFFF87171) // salmon red
    val StatusFailed = Color(0xFF450A0A) // very dark red

    // Source badges — red shades
    val Qdrant       = Color(0xFF8B1A1A) // deep crimson
    val QdrantBg     = Color(0x128B1A1A)
    val QdrantBd     = Color(0x1A8B1A1A)
    val Apify        = Color(0xFFE11D48) // rose red
    val ApifyBg      = Color(0x12E11D48)
    val ApifyBd      = Color(0x1AE11D48)
    val LiveMap      = Color(0xFFB91C1C) // brick red
    val LiveMapBg    = Color(0x12B91C1C)
    val LiveMapBd    = Color(0x1AB91C1C)
    val Local        = Color(0xFF7F1D1D) // maroon
    val LocalBg      = Color(0x127F1D1D)
    val LocalBd      = Color(0x1A7F1D1D)
    val HuggingFace  = Color(0xFFEF4444) // coral red
    val HuggingFaceBg = Color(0x12EF4444)
    val HuggingFaceBd = Color(0x1AEF4444)
    val Git          = Color(0xFF991B1B) // dark cherry
    val GitBg        = Color(0x12991B1B)
    val GitBd        = Color(0x1A991B1B)

    // Star
    val StarActive = Color(0xFFDC2626)
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

// Light Swiss color scheme
private val SwissLightScheme = lightColorScheme(
    primary = DVColors.Accent,
    onPrimary = Color.White,
    primaryContainer = Color(0xFFFFE0E0),
    onPrimaryContainer = DVColors.Accent,
    secondary = Color(0xFFFFF0EE),
    onSecondary = Color(0xFF4A2020),
    background = DVColors.Background,
    onBackground = DVColors.TextPrimary,
    surface = DVColors.Surface,
    onSurface = DVColors.TextPrimary,
    surfaceVariant = Color(0xFFFFECE8),
    onSurfaceVariant = Color(0xFF6B3535),
    outline = Color(0xFFDDC0C0),
    outlineVariant = Color(0xFFFFE8E4),
    surfaceTint = Color.Transparent,
    error = Color(0xFF991B1B),
    onError = Color.White,
)

@Composable
fun DynamicVectorTheme(
    content: @Composable () -> Unit,
) {
    MaterialTheme(
        colorScheme = SwissLightScheme,
        typography = Typography(),
        content = content,
    )
}
