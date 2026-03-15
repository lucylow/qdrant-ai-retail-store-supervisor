package dev.dynamicvector.theme

import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

// ── Core palette (matches login screen aesthetic) ──
val Teal = Color(0xFF4ECDC4)
val TealDark = Color(0xFF3BA89F)
val Purple500 = Color(0xFF8B5CF6)
val Purple400 = Color(0xFFA78BFA)

// Near-black base (same as QuantumWaveFabric BG)
val SpaceBlack = Color(0xFF040410)

// Rating / score accents
val Amber500 = Color(0xFFF59E0B)
val Amber400 = Color(0xFFFBBF24)

// Match score indicators
val MatchHigh = Color(0xFF4ADE80)
val MatchMedium = Color(0xFFFBBF24)
val MatchLow = Color(0xFF6B7280)

// Tag colors (dark-mode friendly)
val TagGreen = Color(0xFF4ADE80)
val TagGreenBg = Color(0xFF0A2A1A)
val TagBlue = Color(0xFF60A5FA)
val TagBlueBg = Color(0xFF0A1A2A)
val TagPurple = Color(0xFFA78BFA)
val TagPurpleBg = Color(0xFF1A0A2A)

// Destructive
val Red500 = Color(0xFFFF6B6B)

private val DarkColorScheme = darkColorScheme(
    primary = Teal,
    onPrimary = SpaceBlack,
    primaryContainer = Color(0xFF0A1F1E),
    onPrimaryContainer = Teal,
    secondary = Color(0xFF12121F),
    onSecondary = Color(0xFFB0B0C0),
    secondaryContainer = Color(0xFF1A1A2E),
    onSecondaryContainer = Color(0xFFD0D0E0),
    tertiary = Purple500,
    background = SpaceBlack,
    onBackground = Color(0xFFE0E0F0),
    surface = Color(0xFF0D0D1A),
    onSurface = Color(0xFFE0E0F0),
    surfaceVariant = Color(0xFF15152A),
    onSurfaceVariant = Color(0xFF8B8BA0),
    outline = Color(0xFF2A2A40),
    outlineVariant = Color(0xFF15152A),
    error = Red500,
    onError = Color.White,
)

@Composable
fun DynamicVectorTheme(
    content: @Composable () -> Unit,
) {
    MaterialTheme(
        colorScheme = DarkColorScheme,
        typography = Typography(),
        content = content,
    )
}
