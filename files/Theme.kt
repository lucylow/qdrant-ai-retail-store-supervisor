package ch.genaizurich2026.dynamicvector

import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

object DVColors {
    // Core backgrounds — warm dark
    val Background        = Color(0xFF0A0810)
    val Surface           = Color(0xFF120E18)
    val SurfaceVariant    = Color(0x0AFFFFFF)
    val CardGradientStart = Color(0x0DFFFFFF)
    val CardGradientEnd   = Color(0x05FFFFFF)
    val CardBorder        = Color(0x0FFFFFFF)
    val CardTopEdge       = Color(0x40E63946) // Swiss red at 25%

    // Primary accent — Swiss red
    val Accent       = Color(0xFFE63946)
    val AccentDim    = Color(0x1AE63946) // 10%
    val AccentBorder = Color(0x40E63946) // 25%
    val AccentDark   = Color(0xFFC12E3A) // darker red for gradients

    // Text
    val TextPrimary   = Color(0xFFF0F0F5)
    val TextSecondary = Color(0x73FFFFFF)
    val TextTertiary  = Color(0x4DFFFFFF)
    val TextHint      = Color(0x26FFFFFF)

    // Icons — explicit, never currentColor
    val IconMuted      = Color(0xFF7A7A90)
    val IconMutedLight = Color(0xFF8A8A9E)

    // Status
    val StatusLive   = Color(0xFFE63946) // Swiss red for Live
    val StatusDone   = Color(0xFF7AB87A)
    val StatusStale  = Color(0xFFF0B43C)
    val StatusFailed = Color(0xFFDC5050)

    // Source badges
    val Qdrant       = Color(0xFFA98AEF)
    val QdrantBg     = Color(0x267850DC)
    val QdrantBd     = Color(0x337850DC)
    val Apify        = Color(0xFF4CD9A0)
    val ApifyBg      = Color(0x1F00B478)
    val ApifyBd      = Color(0x2600B478)
    val LiveMap      = Color(0xFF6CB0F0)
    val LiveMapBg    = Color(0x1F3C8CF0)
    val LiveMapBd    = Color(0x263C8CF0)
    val Local        = Color(0xFFC8A850)
    val LocalBg      = Color(0x1FC8A050)
    val LocalBd      = Color(0x26C8A050)
    val HuggingFace  = Color(0xFFF0C840)
    val HuggingFaceBg = Color(0x1AFFC83C)
    val HuggingFaceBd = Color(0x26FFC83C)
    val Git          = Color(0xFFF07850)
    val GitBg        = Color(0x1AF07850)
    val GitBd        = Color(0x26F07850)

    // Star
    val StarActive = Color(0xFFF0B43C)
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
