package dev.dynamicvector.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Visibility
import androidx.compose.material.icons.filled.VisibilityOff
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import dev.dynamicvector.components.QuantumWaveFabric
import dev.dynamicvector.data.ApiClient
import kotlinx.coroutines.launch

@Composable
fun LoginScreen(
    onLoginSuccess: () -> Unit,
) {
    var username by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var passwordVisible by remember { mutableStateOf(false) }
    var isLoading by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    val scope = rememberCoroutineScope()

    val canSubmit = username.isNotBlank() && password.isNotBlank() && !isLoading

    val doLogin = {
        if (canSubmit) {
            isLoading = true
            error = null
            scope.launch {
                ApiClient.login(username, password)
                    .onSuccess { onLoginSuccess() }
                    .onFailure {
                        error = "Invalid username or password"
                        isLoading = false
                    }
            }
        }
    }

    Box(modifier = Modifier.fillMaxSize()) {
        // Layer 1: Animated background
        QuantumWaveFabric()

        // Layer 2: Login overlay
        Column(
            modifier = Modifier
                .fillMaxSize()
                .statusBarsPadding()
                .padding(horizontal = 32.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Spacer(Modifier.weight(1f))

            // Title — vector/matrix bracket notation
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(IntrinsicSize.Min),
            ) {
                // Left bracket [
                Box(
                    modifier = Modifier
                        .width(24.dp)
                        .fillMaxHeight()
                        .drawBehind {
                            val sw = 3.dp.toPx()
                            val c = Color(0xFFE0E0F0).copy(alpha = 0.5f)
                            drawLine(c, Offset(sw / 2, 0f), Offset(sw / 2, size.height), sw)
                            drawLine(c, Offset(0f, sw / 2), Offset(size.width, sw / 2), sw)
                            drawLine(c, Offset(0f, size.height - sw / 2), Offset(size.width, size.height - sw / 2), sw)
                        },
                )

                Column(
                    modifier = Modifier
                        .weight(1f)
                        .padding(vertical = 8.dp, horizontal = 8.dp),
                ) {
                    Text(
                        text = "Dynamic",
                        fontSize = 64.sp,
                        fontWeight = FontWeight.ExtraBold,
                        fontFamily = FontFamily.Monospace,
                        letterSpacing = (-1).sp,
                        color = Color(0xFFE0E0F0),
                        textAlign = TextAlign.Start,
                        modifier = Modifier.fillMaxWidth(),
                    )
                    Text(
                        text = "Vector",
                        fontSize = 40.sp,
                        fontWeight = FontWeight.Bold,
                        fontFamily = FontFamily.Monospace,
                        letterSpacing = 2.sp,
                        color = Color(0xFF4ECDC4),
                        textAlign = TextAlign.Start,
                        modifier = Modifier.fillMaxWidth(),
                    )
                }

                // Right bracket ]
                Box(
                    modifier = Modifier
                        .width(24.dp)
                        .fillMaxHeight()
                        .drawBehind {
                            val sw = 3.dp.toPx()
                            val c = Color(0xFFE0E0F0).copy(alpha = 0.5f)
                            drawLine(c, Offset(size.width - sw / 2, 0f), Offset(size.width - sw / 2, size.height), sw)
                            drawLine(c, Offset(0f, sw / 2), Offset(size.width, sw / 2), sw)
                            drawLine(c, Offset(0f, size.height - sw / 2), Offset(size.width, size.height - sw / 2), sw)
                        },
                )
            }

            Spacer(Modifier.height(48.dp))

            // Username field
            OutlinedTextField(
                value = username,
                onValueChange = { username = it; error = null },
                label = { Text("Username", fontFamily = FontFamily.Monospace) },
                singleLine = true,
                textStyle = TextStyle(fontFamily = FontFamily.Monospace, color = Color.White),
                keyboardOptions = KeyboardOptions(imeAction = ImeAction.Next),
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                colors = OutlinedTextFieldDefaults.colors(
                    unfocusedBorderColor = Color.White.copy(alpha = 0.3f),
                    focusedBorderColor = Color(0xFF4ECDC4),
                    unfocusedLabelColor = Color.White.copy(alpha = 0.5f),
                    focusedLabelColor = Color(0xFF4ECDC4),
                    cursorColor = Color(0xFF4ECDC4),
                    unfocusedTextColor = Color.White,
                    focusedTextColor = Color.White,
                ),
            )

            Spacer(Modifier.height(12.dp))

            // Password field
            OutlinedTextField(
                value = password,
                onValueChange = { password = it; error = null },
                label = { Text("Password", fontFamily = FontFamily.Monospace) },
                singleLine = true,
                textStyle = TextStyle(fontFamily = FontFamily.Monospace, color = Color.White),
                visualTransformation = if (passwordVisible) VisualTransformation.None else PasswordVisualTransformation(),
                keyboardOptions = KeyboardOptions(imeAction = ImeAction.Done),
                keyboardActions = KeyboardActions(onDone = { doLogin() }),
                trailingIcon = {
                    IconButton(onClick = { passwordVisible = !passwordVisible }) {
                        Icon(
                            imageVector = if (passwordVisible) Icons.Filled.VisibilityOff else Icons.Filled.Visibility,
                            contentDescription = if (passwordVisible) "Hide password" else "Show password",
                            tint = Color.White.copy(alpha = 0.5f),
                        )
                    }
                },
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                colors = OutlinedTextFieldDefaults.colors(
                    unfocusedBorderColor = Color.White.copy(alpha = 0.3f),
                    focusedBorderColor = Color(0xFF4ECDC4),
                    unfocusedLabelColor = Color.White.copy(alpha = 0.5f),
                    focusedLabelColor = Color(0xFF4ECDC4),
                    cursorColor = Color(0xFF4ECDC4),
                    unfocusedTextColor = Color.White,
                    focusedTextColor = Color.White,
                ),
            )

            // Error message
            error?.let {
                Spacer(Modifier.height(8.dp))
                Text(
                    text = it,
                    color = MaterialTheme.colorScheme.error,
                    fontSize = 13.sp,
                    fontFamily = FontFamily.Monospace,
                )
            }

            Spacer(Modifier.height(24.dp))

            // Sign In button
            Button(
                onClick = { doLogin() },
                enabled = canSubmit,
                modifier = Modifier.fillMaxWidth().height(52.dp),
                shape = RoundedCornerShape(12.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color(0xFF4ECDC4),
                    contentColor = Color(0xFF040410),
                    disabledContainerColor = Color(0xFF4ECDC4).copy(alpha = 0.3f),
                    disabledContentColor = Color(0xFF040410).copy(alpha = 0.4f),
                ),
                elevation = ButtonDefaults.buttonElevation(defaultElevation = 0.dp),
            ) {
                if (isLoading) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(20.dp),
                        strokeWidth = 2.dp,
                        color = Color(0xFF040410),
                    )
                } else {
                    Text(
                        text = "Sign In",
                        fontSize = 15.sp,
                        fontWeight = FontWeight.SemiBold,
                        fontFamily = FontFamily.Monospace,
                    )
                }
            }

            Spacer(Modifier.weight(1f))

            // Version
            Text(
                text = "v${dev.dynamicvector.BuildConfig.VERSION}",
                fontSize = 12.sp,
                color = Color.White.copy(alpha = 0.4f),
                modifier = Modifier.padding(bottom = 24.dp),
            )
        }
    }
}
