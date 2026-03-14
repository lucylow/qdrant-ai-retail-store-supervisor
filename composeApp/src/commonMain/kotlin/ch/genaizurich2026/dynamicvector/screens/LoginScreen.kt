package ch.genaizurich2026.dynamicvector.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Visibility
import androidx.compose.material.icons.outlined.VisibilityOff
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay

@Composable
fun LoginScreen(
    onLogin: () -> Unit,
) {
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var showPassword by remember { mutableStateOf(false) }
    var isSignUp by remember { mutableStateOf(false) }
    var hasAttempted by remember { mutableStateOf(false) }
    var isLoading by remember { mutableStateOf(false) }

    val emailError = hasAttempted && (email.isBlank() || !email.contains("@"))
    val passwordError = hasAttempted && password.isBlank()

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
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Spacer(Modifier.height(48.dp))

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

        Spacer(Modifier.height(40.dp))

        // Email
        Column(modifier = Modifier.fillMaxWidth()) {
            Text(
                text = "EMAIL",
                fontSize = 11.sp,
                fontWeight = FontWeight.Medium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                letterSpacing = 1.sp,
                modifier = Modifier.padding(bottom = 6.dp),
            )
            OutlinedTextField(
                value = email,
                onValueChange = { email = it; if (hasAttempted) hasAttempted = false },
                modifier = Modifier.fillMaxWidth(),
                placeholder = { Text("you@example.com") },
                singleLine = true,
                shape = RoundedCornerShape(12.dp),
                isError = emailError,
                keyboardOptions = KeyboardOptions(
                    keyboardType = KeyboardType.Email,
                    imeAction = ImeAction.Next,
                ),
            )
            if (emailError) {
                Text(
                    text = "Enter a valid email address",
                    fontSize = 11.sp,
                    color = MaterialTheme.colorScheme.error,
                    modifier = Modifier.padding(start = 4.dp, top = 4.dp),
                )
            }
        }

        Spacer(Modifier.height(16.dp))

        // Password
        Column(modifier = Modifier.fillMaxWidth()) {
            Text(
                text = "PASSWORD",
                fontSize = 11.sp,
                fontWeight = FontWeight.Medium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                letterSpacing = 1.sp,
                modifier = Modifier.padding(bottom = 6.dp),
            )
            OutlinedTextField(
                value = password,
                onValueChange = { password = it; if (hasAttempted) hasAttempted = false },
                modifier = Modifier.fillMaxWidth(),
                placeholder = { Text("\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022") },
                singleLine = true,
                shape = RoundedCornerShape(12.dp),
                isError = passwordError,
                visualTransformation = if (showPassword) VisualTransformation.None else PasswordVisualTransformation(),
                keyboardOptions = KeyboardOptions(
                    keyboardType = KeyboardType.Password,
                    imeAction = ImeAction.Done,
                ),
                keyboardActions = KeyboardActions(onDone = {
                    hasAttempted = true
                    if (email.contains("@") && email.isNotBlank() && password.isNotBlank()) {
                        isLoading = true
                    }
                }),
                trailingIcon = {
                    IconButton(onClick = { showPassword = !showPassword }) {
                        Icon(
                            imageVector = if (showPassword) Icons.Outlined.VisibilityOff else Icons.Outlined.Visibility,
                            contentDescription = if (showPassword) "Hide password" else "Show password",
                            tint = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }
                },
            )
            if (passwordError) {
                Text(
                    text = "Password is required",
                    fontSize = 11.sp,
                    color = MaterialTheme.colorScheme.error,
                    modifier = Modifier.padding(start = 4.dp, top = 4.dp),
                )
            }
        }

        if (!isSignUp) {
            Text(
                text = "Forgot password?",
                fontSize = 12.sp,
                fontWeight = FontWeight.Medium,
                color = MaterialTheme.colorScheme.primary,
                modifier = Modifier
                    .align(Alignment.End)
                    .padding(top = 8.dp)
                    .clip(RoundedCornerShape(4.dp))
                    .clickable { }
                    .padding(4.dp),
            )
        }

        Spacer(Modifier.height(24.dp))

        // Sign in button
        Button(
            onClick = {
                hasAttempted = true
                if (email.contains("@") && email.isNotBlank() && password.isNotBlank()) {
                    isLoading = true
                }
            },
            enabled = !isLoading,
            modifier = Modifier.fillMaxWidth().height(52.dp),
            shape = RoundedCornerShape(12.dp),
        ) {
            if (isLoading) {
                CircularProgressIndicator(
                    modifier = Modifier.size(20.dp),
                    strokeWidth = 2.dp,
                    color = MaterialTheme.colorScheme.onPrimary,
                )
            } else {
                Text(
                    text = if (isSignUp) "Create Account" else "Sign In",
                    fontSize = 15.sp,
                    fontWeight = FontWeight.Medium,
                )
            }
        }

        // Toggle sign up / sign in
        Spacer(Modifier.height(16.dp))
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.Center,
        ) {
            Text(
                text = if (isSignUp) "Already have an account? " else "Don't have an account? ",
                fontSize = 14.sp,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Text(
                text = if (isSignUp) "Sign In" else "Sign Up",
                fontSize = 14.sp,
                fontWeight = FontWeight.Medium,
                color = MaterialTheme.colorScheme.primary,
                modifier = Modifier
                    .clip(RoundedCornerShape(4.dp))
                    .clickable { isSignUp = !isSignUp },
            )
        }

        // Divider
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 24.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            HorizontalDivider(modifier = Modifier.weight(1f))
            Text(
                text = "or continue with",
                fontSize = 12.sp,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(horizontal = 12.dp),
            )
            HorizontalDivider(modifier = Modifier.weight(1f))
        }

        // GitHub SSO
        Button(
            onClick = onLogin,
            modifier = Modifier.fillMaxWidth().height(48.dp),
            shape = RoundedCornerShape(12.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = Color(0xFF24292F),
                contentColor = Color.White,
            ),
            elevation = ButtonDefaults.buttonElevation(defaultElevation = 0.dp),
        ) {
            Icon(
                imageVector = GithubIcon,
                contentDescription = "GitHub",
                modifier = Modifier.size(20.dp),
            )
            Spacer(Modifier.width(8.dp))
            Text(
                text = "Continue with GitHub",
                fontSize = 14.sp,
                fontWeight = FontWeight.Medium,
            )
        }

        Spacer(Modifier.height(32.dp))
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
