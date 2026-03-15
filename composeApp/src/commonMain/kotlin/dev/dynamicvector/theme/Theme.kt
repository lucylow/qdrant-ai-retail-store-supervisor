package dev.dynamicvector.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

// Primary palette
val Purple600 = Color(0xFF7C3AED)
val Purple500 = Color(0xFF8B5CF6)
val Purple400 = Color(0xFFA78BFA)
val Purple200 = Color(0xFFDDD6FE)
val Purple50 = Color(0xFFF5F3FF)

// Rating / score accents
val Amber500 = Color(0xFFF59E0B)
val Amber400 = Color(0xFFFBBF24)

// Match score indicators
val MatchHigh = Color(0xFF16A34A)
val MatchMedium = Color(0xFFD97706)
val MatchLow = Color(0xFF6B7280)

// Tag colors
val TagGreen = Color(0xFF16A34A)
val TagGreenBg = Color(0xFFDCFCE7)
val TagBlue = Color(0xFF2563EB)
val TagBlueBg = Color(0xFFDBEAFE)
val TagPurple = Color(0xFF7C3AED)
val TagPurpleBg = Color(0xFFEDE9FE)

// Destructive
val Red500 = Color(0xFFEF4444)
val Red50 = Color(0xFFFEF2F2)

private val LightColorScheme = lightColorScheme(
    primary = _root_ide_package_.dev.dynamicvector.theme.Purple600,
    onPrimary = Color.White,
    primaryContainer = _root_ide_package_.dev.dynamicvector.theme.Purple50,
    onPrimaryContainer = _root_ide_package_.dev.dynamicvector.theme.Purple600,
    secondary = Color(0xFFF1F5F9),
    onSecondary = Color(0xFF475569),
    secondaryContainer = Color(0xFFE2E8F0),
    onSecondaryContainer = Color(0xFF334155),
    tertiary = _root_ide_package_.dev.dynamicvector.theme.Purple400,
    background = Color(0xFFF8FAFC),
    onBackground = Color(0xFF0F172A),
    surface = Color.White,
    onSurface = Color(0xFF0F172A),
    surfaceVariant = Color(0xFFF1F5F9),
    onSurfaceVariant = Color(0xFF64748B),
    outline = Color(0xFFE2E8F0),
    outlineVariant = Color(0xFFF1F5F9),
    error = _root_ide_package_.dev.dynamicvector.theme.Red500,
    onError = Color.White,
)

private val DarkColorScheme = darkColorScheme(
    primary = _root_ide_package_.dev.dynamicvector.theme.Purple500,
    onPrimary = Color.White,
    primaryContainer = Color(0xFF1E1B2E),
    onPrimaryContainer = _root_ide_package_.dev.dynamicvector.theme.Purple200,
    secondary = Color(0xFF1E293B),
    onSecondary = Color(0xFF94A3B8),
    secondaryContainer = Color(0xFF334155),
    onSecondaryContainer = Color(0xFFCBD5E1),
    tertiary = _root_ide_package_.dev.dynamicvector.theme.Purple400,
    background = Color(0xFF0F172A),
    onBackground = Color(0xFFF1F5F9),
    surface = Color(0xFF1E293B),
    onSurface = Color(0xFFF1F5F9),
    surfaceVariant = Color(0xFF283548),
    onSurfaceVariant = Color(0xFF94A3B8),
    outline = Color(0xFF334155),
    outlineVariant = Color(0xFF1E293B),
    error = _root_ide_package_.dev.dynamicvector.theme.Red500,
    onError = Color.White,
)

@Composable
fun DynamicVectorTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit,
) {
    val colorScheme = if (darkTheme) _root_ide_package_.dev.dynamicvector.theme.DarkColorScheme else _root_ide_package_.dev.dynamicvector.theme.LightColorScheme

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography(),
        content = content,
    )
}
