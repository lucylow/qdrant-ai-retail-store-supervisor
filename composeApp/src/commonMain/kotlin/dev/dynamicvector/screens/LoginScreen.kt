package dev.dynamicvector.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay

@Composable
fun LoginScreen(
    onLogin: () -> Unit,
) {
    var isLoading by remember { mutableStateOf(false) }

    LaunchedEffect(isLoading) {
        if (isLoading) {
            delay(1000)
            isLoading = false
            onLogin()
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .statusBarsPadding()
            .padding(horizontal = 24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Spacer(Modifier.weight(1f))

        // Logo
        Box(
            modifier = Modifier
                .size(64.dp)
                .clip(RoundedCornerShape(16.dp))
                .background(MaterialTheme.colorScheme.primary),
            contentAlignment = Alignment.Center,
        ) {
            Text(
                text = "DV",
                fontSize = 22.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onPrimary,
            )
        }

        Spacer(Modifier.height(16.dp))

        Text(
            text = "Dynamic Vector",
            fontSize = 24.sp,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onBackground,
        )
        Text(
            text = "Multi-agent store manager",
            fontSize = 14.sp,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.padding(top = 4.dp),
        )

        Spacer(Modifier.height(48.dp))

        // GitHub SSO button
        Button(
            onClick = { isLoading = true },
            enabled = !isLoading,
            modifier = Modifier.fillMaxWidth().height(52.dp),
            shape = RoundedCornerShape(12.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = Color(0xFF24292F),
                contentColor = Color.White,
            ),
            elevation = ButtonDefaults.buttonElevation(defaultElevation = 0.dp),
        ) {
            if (isLoading) {
                CircularProgressIndicator(
                    modifier = Modifier.size(20.dp),
                    strokeWidth = 2.dp,
                    color = Color.White,
                )
            } else {
                Icon(
                    imageVector = GithubIcon,
                    contentDescription = "GitHub",
                    modifier = Modifier.size(20.dp),
                )
                Spacer(Modifier.width(8.dp))
                Text(
                    text = "Sign in with GitHub",
                    fontSize = 15.sp,
                    fontWeight = FontWeight.Medium,
                )
            }
        }

        Spacer(Modifier.height(12.dp))

        Text(
            text = "SSO is the only supported sign-in method",
            fontSize = 12.sp,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )

        Spacer(Modifier.weight(1f))

        // Version
        Text(
            text = "v0.1.0",
            fontSize = 12.sp,
            color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.5f),
            modifier = Modifier.padding(bottom = 24.dp),
        )
    }
}

private val GithubIcon: androidx.compose.ui.graphics.vector.ImageVector by lazy {
    androidx.compose.ui.graphics.vector.ImageVector.Builder(
        name = "GitHub",
        defaultWidth = 24.dp,
        defaultHeight = 24.dp,
        viewportWidth = 24f,
        viewportHeight = 24f,
    ).addPath(
        pathData = androidx.compose.ui.graphics.vector.PathData {
            moveTo(12f, 0.297f)
            curveTo(5.37f, 0.297f, 0f, 5.67f, 0f, 12.297f)
            curveTo(0f, 17.6f, 3.438f, 22.097f, 8.205f, 23.682f)
            curveTo(8.805f, 23.795f, 9.025f, 23.424f, 9.025f, 23.105f)
            curveTo(9.025f, 22.82f, 9.015f, 22.065f, 9.01f, 21.065f)
            curveTo(5.672f, 21.789f, 4.968f, 19.455f, 4.968f, 19.455f)
            curveTo(4.422f, 18.07f, 3.633f, 17.7f, 3.633f, 17.7f)
            curveTo(2.546f, 16.956f, 3.717f, 16.971f, 3.717f, 16.971f)
            curveTo(4.922f, 17.055f, 5.555f, 18.207f, 5.555f, 18.207f)
            curveTo(6.625f, 20.042f, 8.364f, 19.512f, 9.05f, 19.205f)
            curveTo(9.158f, 18.429f, 9.467f, 17.9f, 9.81f, 17.6f)
            curveTo(7.145f, 17.3f, 4.344f, 16.268f, 4.344f, 11.67f)
            curveTo(4.344f, 10.36f, 4.809f, 9.29f, 5.579f, 8.45f)
            curveTo(5.444f, 8.147f, 5.039f, 6.927f, 5.684f, 5.274f)
            curveTo(5.684f, 5.274f, 6.689f, 4.952f, 8.984f, 6.504f)
            curveTo(9.944f, 6.237f, 10.964f, 6.105f, 11.984f, 6.099f)
            curveTo(13.004f, 6.105f, 14.024f, 6.237f, 14.984f, 6.504f)
            curveTo(17.264f, 4.952f, 18.269f, 5.274f, 18.269f, 5.274f)
            curveTo(18.914f, 6.927f, 18.509f, 8.147f, 18.389f, 8.45f)
            curveTo(19.154f, 9.29f, 19.619f, 10.36f, 19.619f, 11.67f)
            curveTo(19.619f, 16.28f, 16.814f, 17.295f, 14.144f, 17.59f)
            curveTo(14.564f, 17.95f, 14.954f, 18.686f, 14.954f, 19.81f)
            curveTo(14.954f, 21.416f, 14.939f, 22.706f, 14.939f, 23.096f)
            curveTo(14.939f, 23.411f, 15.149f, 23.786f, 15.764f, 23.666f)
            curveTo(20.565f, 22.092f, 24f, 17.592f, 24f, 12.297f)
            curveTo(24f, 5.67f, 18.627f, 0.297f, 12f, 0.297f)
            close()
        },
        fill = androidx.compose.ui.graphics.SolidColor(Color.White),
    ).build()
}