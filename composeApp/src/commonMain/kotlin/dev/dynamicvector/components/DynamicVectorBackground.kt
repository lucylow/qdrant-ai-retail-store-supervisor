package dev.dynamicvector.components

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import kotlin.math.*
import kotlin.random.Random

private const val GRID = 60
private const val SPACING = 0.28f
private const val FOV = 400f
private const val VIEW_DIST = 8f
private const val CYCLE = 16f
private const val STAR_COUNT = 40
private const val STREAM_COUNT = 120

private val TEAL = Color(0xFF4ECDC4)
private val PURPLE = Color(0xFF7B5EA7)
private val CORAL = Color(0xFFE07040)
private val BG = Color(0xFF040410)

private fun smoothstep(edge0: Float, edge1: Float, x: Float): Float {
    val t = ((x - edge0) / (edge1 - edge0)).coerceIn(0f, 1f)
    return t * t * (3f - 2f * t)
}

private fun lerpColor(a: Color, b: Color, t: Float): Color {
    val ct = t.coerceIn(0f, 1f)
    return Color(
        red = a.red + (b.red - a.red) * ct,
        green = a.green + (b.green - a.green) * ct,
        blue = a.blue + (b.blue - a.blue) * ct,
        alpha = a.alpha + (b.alpha - a.alpha) * ct,
    )
}

private fun gridColor(nx: Float): Color {
    return if (nx < 0.5f) lerpColor(TEAL, PURPLE, nx * 2f)
    else lerpColor(PURPLE, CORAL, (nx - 0.5f) * 2f)
}

private fun waveY(x: Float, z: Float, t: Float, nx: Float): Float {
    var y = sin(x * 0.5f + t * 0.7f) * cos(z * 0.5f + t * 0.7f) * 0.8f
    y += sin(x * 0.8f - t * 1.1f) * 0.5f
    y += cos(z * 0.6f + t * 0.9f) * 0.4f
    y += sin((x + z) * 0.4f + t * 1.3f) * 0.6f
    y += sin(x * 1.5f + t * 1.8f) * cos(z * 1.2f - t) * 0.3f
    y += cos(x * 2.2f - t * 2.1f) * 0.2f
    y += sin(z * 1.8f + t * 1.5f) * 0.25f
    val packetCenter = 0.2f * sin(t * 0.3f)
    val envelope = exp(-((nx - 0.5f - packetCenter).let { it * it }) * 8f)
    y += envelope * sin(x * 3f + t * 3f) * 0.7f
    return y
}

/**
 * Instead of replacing waves with a calm dome, this compresses and amplifies
 * the wave energy toward the center — the mesh stays turbulent but pulls inward
 * like data being sucked into a vortex/repository.
 */
private fun repoModulate(
    baseY: Float, nx: Float, nz: Float, t: Float, blend: Float
): Float {
    val dx = nx - 0.5f
    val dz = nz - 0.5f
    val r = sqrt(dx * dx + dz * dz)

    // Particles outside the convergence zone are unaffected
    val convergenceRadius = 0.55f
    if (r > convergenceRadius) return baseY

    // How strongly this point is inside the convergence zone (1.0 at center)
    val influence = smoothstep(convergenceRadius, convergenceRadius * 0.2f, r)
    val strength = influence * blend

    // Pull the wave upward (concentrate energy) rather than flattening it
    val lift = strength * 1.2f

    // Add swirling — angular displacement creates a vortex feel
    val angle = atan2(dz, dx)
    val swirl = sin(angle * 3f + t * 2.5f - r * 12f) * 0.4f * strength

    // Higher-frequency ripples inside the convergence zone
    val innerRipple = sin(r * 25f - t * 4f) * 0.2f * strength

    // The wave is still present but gets amplified and lifted at center
    val amplify = 1f + strength * 0.5f
    return baseY * amplify + lift + swirl + innerRipple
}

private fun morphBlend(t: Float): Float {
    val phase = t % CYCLE
    return when {
        phase < 3f -> 0f
        phase < 5f -> smoothstep(3f, 5f, phase)
        phase < 9f -> 1f
        phase < 11f -> 1f - smoothstep(9f, 11f, phase)
        else -> 0f
    }
}

private data class Star(val x: Float, val y: Float, val phase: Float, val speed: Float)

private class StreamParticle {
    var x = 0f; var y = 0f; var vx = 0f; var vy = 0f
    var life = 0f; var maxLife = 0f
    var color = TEAL
    var radius = 2f

    fun reset(w: Float, h: Float, rng: Random) {
        // Spawn from edges
        val side = rng.nextInt(4)
        when (side) {
            0 -> { x = 0f; y = rng.nextFloat() * h }
            1 -> { x = w; y = rng.nextFloat() * h }
            2 -> { x = rng.nextFloat() * w; y = 0f }
            else -> { x = rng.nextFloat() * w; y = h }
        }
        val cx = w * 0.5f; val cy = h * 0.45f
        val dx = cx - x; val dy = cy - y
        val dist = sqrt(dx * dx + dy * dy).coerceAtLeast(1f)
        val speed = rng.nextFloat() * 2f + 1f
        vx = dx / dist * speed; vy = dy / dist * speed
        life = 0f; maxLife = dist / speed * (0.6f + rng.nextFloat() * 0.4f)
        color = when (rng.nextInt(3)) {
            0 -> TEAL
            1 -> PURPLE
            else -> lerpColor(TEAL, PURPLE, rng.nextFloat())
        }
        radius = rng.nextFloat() * 1.5f + 1.5f
    }
}

@Composable
fun DynamicVectorBackground(modifier: Modifier = Modifier) {
    val stars = remember {
        val rng = Random(42)
        Array(STAR_COUNT) {
            Star(rng.nextFloat(), rng.nextFloat(), rng.nextFloat() * 6.28f, 0.5f + rng.nextFloat() * 1.5f)
        }
    }

    val streams = remember {
        val rng = Random(99)
        Array(STREAM_COUNT) { StreamParticle().also { it.maxLife = -1f } }
    }

    var time by remember { mutableFloatStateOf(0f) }

    LaunchedEffect(Unit) {
        var lastNanos = 0L
        while (true) {
            withFrameNanos { nanos ->
                if (lastNanos != 0L) {
                    time += (nanos - lastNanos) / 1_000_000_000f
                }
                lastNanos = nanos
            }
        }
    }

    Canvas(modifier = modifier.fillMaxSize()) {
        val w = size.width
        val h = size.height
        val cx = w * 0.5f
        val cy = h * 0.45f

        // Background
        drawRect(BG)

        // Stars
        for (star in stars) {
            val alpha = (0.3f + 0.7f * ((sin(time * star.speed + star.phase) + 1f) * 0.5f)).coerceIn(0f, 1f)
            drawCircle(
                color = Color.White.copy(alpha = alpha * 0.6f),
                radius = 1.2f,
                center = Offset(star.x * w, star.y * h),
            )
        }

        // Camera orbit
        val camOffsetX = sin(time * 0.08f) * 2f
        val camOffsetY = sin(time * 0.12f) * 0.5f

        val blend = morphBlend(time)
        val halfGrid = GRID / 2f

        // Compute projected positions
        val projX = FloatArray(GRID * GRID)
        val projY = FloatArray(GRID * GRID)
        val depths = FloatArray(GRID * GRID)
        val colors = IntArray(GRID * GRID)

        for (iz in 0 until GRID) {
            for (ix in 0 until GRID) {
                val idx = iz * GRID + ix
                val nx = ix.toFloat() / (GRID - 1)
                val nz = iz.toFloat() / (GRID - 1)
                val gx = (ix - halfGrid) * SPACING
                val gz = (iz - halfGrid) * SPACING

                var gy = waveY(gx, gz, time, nx)

                // Apply convergence modulation instead of calm dome replacement
                if (blend > 0f) {
                    gy = repoModulate(gy, nx, nz, time, blend)
                }

                val worldX = gx - camOffsetX
                val worldY = gy + 3f - camOffsetY
                val worldZ = gz

                val zd = worldZ + VIEW_DIST
                if (zd <= 0.1f) {
                    projX[idx] = -9999f
                    projY[idx] = -9999f
                    depths[idx] = 0f
                    continue
                }
                val scale = FOV / zd
                projX[idx] = worldX * scale + cx
                projY[idx] = -worldY * scale + cy
                depths[idx] = zd

                // Brightness boost during convergence for center particles
                val dx = nx - 0.5f
                val dz = nz - 0.5f
                val distFromCenter = sqrt(dx * dx + dz * dz)
                val convergenceGlow = if (blend > 0f) {
                    blend * smoothstep(0.5f, 0f, distFromCenter) * 0.4f
                } else 0f

                val brightness = (abs(gy) * 0.6f + 0.15f + convergenceGlow).coerceIn(0f, 1f)
                val baseColor = gridColor(nx)
                val r = (baseColor.red * brightness * 255).toInt().coerceIn(0, 255)
                val g = (baseColor.green * brightness * 255).toInt().coerceIn(0, 255)
                val b = (baseColor.blue * brightness * 255).toInt().coerceIn(0, 255)
                val a = ((0.4f + brightness * 0.6f) * 255).toInt().coerceIn(0, 255)
                colors[idx] = (a shl 24) or (r shl 16) or (g shl 8) or b
            }
        }

        // Wireframe lines
        val wireAlpha = 0.06f + blend * 0.04f
        for (iz in 0 until GRID) {
            for (ix in 0 until GRID) {
                val idx = iz * GRID + ix
                val px = projX[idx]; val py = projY[idx]
                if (px < -9000f) continue

                val nx = ix.toFloat() / (GRID - 1)
                val lineColor = gridColor(nx).copy(alpha = wireAlpha)

                if (ix < GRID - 1) {
                    val ni = idx + 1
                    val npx = projX[ni]; val npy = projY[ni]
                    if (npx > -9000f) {
                        drawLine(lineColor, Offset(px, py), Offset(npx, npy), strokeWidth = 0.5f)
                    }
                }
                if (iz < GRID - 1) {
                    val ni = (iz + 1) * GRID + ix
                    val npx = projX[ni]; val npy = projY[ni]
                    if (npx > -9000f) {
                        drawLine(lineColor, Offset(px, py), Offset(npx, npy), strokeWidth = 0.5f)
                    }
                }
            }
        }

        // Particles (dots)
        for (iz in 0 until GRID) {
            for (ix in 0 until GRID) {
                val idx = iz * GRID + ix
                val px = projX[idx]; val py = projY[idx]
                if (px < -9000f) continue
                val zd = depths[idx]
                val radius = (FOV / zd * 0.03f).coerceIn(0.5f, 3.5f)
                val c = colors[idx]
                val color = Color(
                    red = ((c shr 16) and 0xFF) / 255f,
                    green = ((c shr 8) and 0xFF) / 255f,
                    blue = (c and 0xFF) / 255f,
                    alpha = ((c shr 24) and 0xFF) / 255f,
                )
                drawCircle(color, radius, Offset(px, py))
            }
        }

        // Data stream particles — coalescing inward
        // Intensity ramps up during convergence phase
        val streamIntensity = 0.3f + blend * 0.7f
        val streamRng = Random(((time * 60).toInt()).toLong())
        for (sp in streams) {
            if (sp.life >= sp.maxLife || sp.maxLife < 0f) {
                sp.reset(w, h, streamRng)
            }

            // Accelerate toward center as they get closer (gravity well effect)
            val dx = cx - sp.x
            val dy = cy - sp.y
            val dist = sqrt(dx * dx + dy * dy).coerceAtLeast(1f)
            val pull = (1f + 80f / dist) * streamIntensity
            sp.vx += dx / dist * 0.05f * pull
            sp.vy += dy / dist * 0.05f * pull

            // Speed cap
            val speed = sqrt(sp.vx * sp.vx + sp.vy * sp.vy)
            if (speed > 6f) {
                sp.vx = sp.vx / speed * 6f
                sp.vy = sp.vy / speed * 6f
            }

            sp.x += sp.vx * streamIntensity
            sp.y += sp.vy * streamIntensity
            sp.life += 0.016f

            val lifeRatio = (sp.life / sp.maxLife).coerceIn(0f, 1f)

            // Fade in at start, fade out near end, brighter when close to center
            val proximityGlow = (1f - (dist / (w * 0.5f)).coerceIn(0f, 1f))
            val fadeIn = smoothstep(0f, 0.1f, lifeRatio)
            val fadeOut = 1f - smoothstep(0.8f, 1f, lifeRatio)
            val alpha = fadeIn * fadeOut * (0.3f + proximityGlow * 0.5f) * streamIntensity

            // Particle grows slightly as it approaches center
            val r = sp.radius * (1f + proximityGlow * 0.5f)

            if (alpha > 0.02f) {
                drawCircle(
                    color = sp.color.copy(alpha = alpha.coerceIn(0f, 1f)),
                    radius = r,
                    center = Offset(sp.x, sp.y),
                )
                // Subtle glow halo on brighter particles
                if (alpha > 0.2f && proximityGlow > 0.4f) {
                    drawCircle(
                        color = sp.color.copy(alpha = (alpha * 0.2f).coerceIn(0f, 1f)),
                        radius = r * 2.5f,
                        center = Offset(sp.x, sp.y),
                    )
                }
            }

            // Reset if particle reached center
            if (dist < 15f) {
                sp.maxLife = -1f
            }
        }
    }
}