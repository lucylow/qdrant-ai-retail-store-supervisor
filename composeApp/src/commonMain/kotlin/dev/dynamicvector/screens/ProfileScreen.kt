package dev.dynamicvector.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.outlined.HelpOutline
import androidx.compose.material.icons.automirrored.outlined.Logout
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import dev.dynamicvector.data.mockHistory
import dev.dynamicvector.data.mockProfile
import dev.dynamicvector.data.mockContexts
import dev.dynamicvector.data.mockSavedQueries

@Composable
fun ProfileScreen(
    onSignOut: () -> Unit = {},
) {
    val p = _root_ide_package_.dev.dynamicvector.data.mockProfile
    val scrollState = rememberScrollState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .statusBarsPadding()
            .verticalScroll(scrollState),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Spacer(Modifier.height(32.dp))

        // Avatar
        Box(
            modifier = Modifier
                .size(80.dp)
                .clip(CircleShape)
                .background(MaterialTheme.colorScheme.primary),
            contentAlignment = Alignment.Center,
        ) {
            Text(
                text = p.name.first().toString(),
                fontSize = 32.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onPrimary,
            )
        }

        Spacer(Modifier.height(12.dp))

        Text(
            text = p.name,
            fontSize = 22.sp,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onBackground,
        )

        Text(
            text = "@${p.username}",
            fontSize = 14.sp,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.padding(top = 2.dp),
        )

        Spacer(Modifier.height(20.dp))

        // Stats section
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp),
            horizontalArrangement = Arrangement.spacedBy(2.dp),
        ) {
            _root_ide_package_.dev.dynamicvector.screens.StatCard(
                "Queries",
                "${_root_ide_package_.dev.dynamicvector.data.mockSavedQueries.size}",
                Modifier.weight(1f),
                isFirst = true
            )
            _root_ide_package_.dev.dynamicvector.screens.StatCard(
                "Results",
                "${_root_ide_package_.dev.dynamicvector.data.mockHistory.sumOf { it.resultCount }}",
                Modifier.weight(1f)
            )
            _root_ide_package_.dev.dynamicvector.screens.StatCard(
                "Repos",
                "${_root_ide_package_.dev.dynamicvector.data.mockContexts.size}",
                Modifier.weight(1f),
                isLast = true
            )
        }

        Spacer(Modifier.height(24.dp))

        // Account info section
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(2.dp),
        ) {
            _root_ide_package_.dev.dynamicvector.screens.ProfileRow(
                icon = Icons.Outlined.Email,
                label = "Email",
                value = p.email,
                isFirst = true,
            )
            _root_ide_package_.dev.dynamicvector.screens.ProfileRow(
                icon = Icons.Outlined.Phone,
                label = "Phone",
                value = p.phone,
            )
            _root_ide_package_.dev.dynamicvector.screens.ProfileRow(
                icon = Icons.Outlined.LocationOn,
                label = "Location",
                value = p.location,
            )
            _root_ide_package_.dev.dynamicvector.screens.ProfileRow(
                icon = Icons.Outlined.CalendarMonth,
                label = "Member since",
                value = p.memberSince,
                isLast = true,
            )
        }

        Spacer(Modifier.height(24.dp))

        // Actions
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(2.dp),
        ) {
            _root_ide_package_.dev.dynamicvector.screens.ActionRow(
                icon = Icons.Outlined.Edit,
                label = "Edit Profile",
                isFirst = true,
            )
            _root_ide_package_.dev.dynamicvector.screens.ActionRow(
                icon = Icons.Outlined.Notifications,
                label = "Notifications",
            )
            _root_ide_package_.dev.dynamicvector.screens.ActionRow(
                icon = Icons.Outlined.Security,
                label = "Privacy & Security",
            )
            _root_ide_package_.dev.dynamicvector.screens.ActionRow(
                icon = Icons.AutoMirrored.Outlined.HelpOutline,
                label = "Help & Support",
                isLast = true,
            )
        }

        Spacer(Modifier.height(24.dp))

        // Sign out
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp),
        ) {
            _root_ide_package_.dev.dynamicvector.screens.ActionRow(
                icon = Icons.AutoMirrored.Outlined.Logout,
                label = "Sign Out",
                isFirst = true,
                isLast = true,
                isDestructive = true,
                onClick = onSignOut,
            )
        }

        Spacer(Modifier.height(24.dp))

        // Version footer
        Text(
            text = "Dynamic Vector v0.1.0",
            fontSize = 12.sp,
            color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.5f),
        )

        // Bottom spacer for nav bar
        Spacer(Modifier.height(80.dp))
    }
}

@Composable
private fun ProfileRow(
    icon: ImageVector,
    label: String,
    value: String,
    isFirst: Boolean = false,
    isLast: Boolean = false,
) {
    val shape = when {
        isFirst && isLast -> RoundedCornerShape(16.dp)
        isFirst -> RoundedCornerShape(topStart = 16.dp, topEnd = 16.dp, bottomStart = 4.dp, bottomEnd = 4.dp)
        isLast -> RoundedCornerShape(topStart = 4.dp, topEnd = 4.dp, bottomStart = 16.dp, bottomEnd = 16.dp)
        else -> RoundedCornerShape(4.dp)
    }

    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = shape,
        color = MaterialTheme.colorScheme.surface,
        tonalElevation = 1.dp,
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 14.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                modifier = Modifier.size(20.dp),
                tint = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Spacer(Modifier.width(14.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = label,
                    fontSize = 12.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
                Text(
                    text = value,
                    fontSize = 15.sp,
                    color = MaterialTheme.colorScheme.onSurface,
                    modifier = Modifier.padding(top = 1.dp),
                )
            }
        }
    }
}

@Composable
private fun StatCard(
    label: String,
    value: String,
    modifier: Modifier = Modifier,
    isFirst: Boolean = false,
    isLast: Boolean = false,
) {
    val shape = when {
        isFirst -> RoundedCornerShape(topStart = 16.dp, bottomStart = 16.dp, topEnd = 4.dp, bottomEnd = 4.dp)
        isLast -> RoundedCornerShape(topStart = 4.dp, bottomStart = 4.dp, topEnd = 16.dp, bottomEnd = 16.dp)
        else -> RoundedCornerShape(4.dp)
    }
    Surface(
        modifier = modifier,
        shape = shape,
        color = MaterialTheme.colorScheme.surface,
        tonalElevation = 1.dp,
    ) {
        Column(
            modifier = Modifier.padding(vertical = 16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text(
                text = value,
                fontSize = 22.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.primary,
            )
            Text(
                text = label,
                fontSize = 12.sp,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(top = 2.dp),
            )
        }
    }
}

@Composable
private fun ActionRow(
    icon: ImageVector,
    label: String,
    isFirst: Boolean = false,
    isLast: Boolean = false,
    isDestructive: Boolean = false,
    onClick: () -> Unit = {},
) {
    val shape = when {
        isFirst && isLast -> RoundedCornerShape(16.dp)
        isFirst -> RoundedCornerShape(topStart = 16.dp, topEnd = 16.dp, bottomStart = 4.dp, bottomEnd = 4.dp)
        isLast -> RoundedCornerShape(topStart = 4.dp, topEnd = 4.dp, bottomStart = 16.dp, bottomEnd = 16.dp)
        else -> RoundedCornerShape(4.dp)
    }

    val tint = if (isDestructive) MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.onSurfaceVariant
    val textColor = if (isDestructive) MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.onSurface

    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = shape,
        color = MaterialTheme.colorScheme.surface,
        tonalElevation = 1.dp,
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .clickable(onClick = onClick)
                .padding(horizontal = 16.dp, vertical = 14.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                modifier = Modifier.size(20.dp),
                tint = tint,
            )
            Spacer(Modifier.width(14.dp))
            Text(
                text = label,
                fontSize = 15.sp,
                color = textColor,
                modifier = Modifier.weight(1f),
            )
            Icon(
                imageVector = Icons.Outlined.ChevronRight,
                contentDescription = null,
                modifier = Modifier.size(20.dp),
                tint = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.4f),
            )
        }
    }
}
