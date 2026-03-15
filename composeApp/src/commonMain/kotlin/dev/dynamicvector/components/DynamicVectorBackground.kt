package dev.dynamicvector.components

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import kotlin.math.*
import kotlin.random.Random

// 50×50 grid (2,500 pts) — same visual area as the Three.js 70×70 but ~2× fewer points
private const val GRID = 50
private const val SEP = 0.56f
private const val HALF = GRID * SEP / 2f
private const val TOTAL = GRID * GRID

private const val CAM_Z = 12f
private const val CAM_LOOK_Y = 0.5f
private const val FOV = 500f
private const val STAR_COUNT = 50
private val BG = Color(0xFF040410)

private data class Star(val x: Float, val y: Float, val phase: Float, val speed: Float)

/**
 * Pre-allocated per-frame buffers — avoids GC pressure from allocating
 * arrays inside Canvas{} every frame.
 */
private class Buffers {
    val sx = FloatArray(TOTAL)
    val sy = FloatArray(TOTAL)
    val cr = FloatArray(TOTAL)
    val cg = FloatArray(TOTAL)
    val cb = FloatArray(TOTAL)
    val sz = FloatArray(TOTAL)
    val ok = BooleanArray(TOTAL)

    // Pre-computed per-row (px-dependent) trig
    val sinPx05 = FloatArray(GRID)
    val sinPx08 = FloatArray(GRID)
    val sinPx15 = FloatArray(GRID)
    // Pre-computed per-row color
    val baseR = FloatArray(GRID)
    val baseG = FloatArray(GRID)
    val baseB = FloatArray(GRID)

    // Pre-computed per-column (pz-dependent) trig
    val cosPz05 = FloatArray(GRID)
    val cosPz06 = FloatArray(GRID)
    val cosPz12 = FloatArray(GRID)
}

@Composable
fun QuantumWaveFabric(modifier: Modifier = Modifier) {
    val stars = remember {
        val rng = Random(42)
        Array(STAR_COUNT) {
            Star(rng.nextFloat(), rng.nextFloat(), rng.nextFloat() * 6.28f, 0.5f + rng.nextFloat() * 1.5f)
        }
    }
    val buf = remember { Buffers() }
    val wirePath = remember { Path() }
    var time by remember { mutableFloatStateOf(0f) }

    LaunchedEffect(Unit) {
        var lastNanos = 0L
        while (true) {
            withFrameNanos { nanos ->
                if (lastNanos != 0L) {
                    time += ((nanos - lastNanos) / 1_000_000_000f).coerceIn(0.001f, 0.05f)
                }
                lastNanos = nanos
            }
        }
    }

    Canvas(modifier = modifier.fillMaxSize()) {
        val w = size.width
        val h = size.height
        val screenCx = w * 0.5f
        val screenCy = h * 0.38f

        drawRect(BG)

        // ── Stars ──
        for (s in stars) {
            val a = 0.3f + 0.4f * ((sin(time * s.speed + s.phase) + 1f) * 0.5f)
            drawCircle(Color.White.copy(alpha = a * 0.5f), 1f, Offset(s.x * w, s.y * h))
        }

        // Camera orbit (matches Three.js)
        val camX = sin(time * 0.08f) * 2f
        val camY = 3.5f + sin(time * 0.12f) * 0.5f

        // Cached time multiplies
        val t07 = time * 0.7f
        val t11 = time * 1.1f
        val t09 = time * 0.9f
        val t13 = time * 1.3f
        val t18 = time * 1.8f

        // ── Pre-compute per-row trig (50 calls instead of 2,500) ──
        for (xi in 0 until GRID) {
            val px = xi * SEP - HALF
            val nx = px / HALF

            buf.sinPx05[xi] = sin(px * 0.5f + t07)
            buf.sinPx08[xi] = sin(px * 0.8f - t11) * 0.5f
            buf.sinPx15[xi] = sin(px * 1.5f + t18)

            // Color gradient based on x-position (teal → purple → warm)
            val cB = (nx + 1f) / 2f
            when {
                cB < 0.4f -> {
                    buf.baseR[xi] = 0.12f + cB * 0.5f
                    buf.baseG[xi] = 0.5f + cB * 0.7f
                    buf.baseB[xi] = 0.9f - cB * 0.2f
                }
                cB < 0.6f -> {
                    buf.baseR[xi] = 0.45f
                    buf.baseG[xi] = 0.35f
                    buf.baseB[xi] = 0.7f
                }
                else -> {
                    buf.baseR[xi] = (0.5f + (cB - 0.6f) * 1.5f).coerceAtMost(1f)
                    buf.baseG[xi] = 0.3f + cB * 0.2f
                    buf.baseB[xi] = (0.4f - cB * 0.2f).coerceAtLeast(0f)
                }
            }
        }

        // ── Pre-compute per-column trig ──
        for (zi in 0 until GRID) {
            val pz = zi * SEP - HALF
            buf.cosPz05[zi] = cos(pz * 0.5f + t07)
            buf.cosPz06[zi] = cos(pz * 0.6f + t09) * 0.4f
            buf.cosPz12[zi] = cos(pz * 1.2f - time)
        }

        // ── Grid computation ──
        for (xi in 0 until GRID) {
            val px = xi * SEP - HALF
            for (zi in 0 until GRID) {
                val idx = xi * GRID + zi
                val pz = zi * SEP - HALF

                // 5-term wave function (most impactful terms from the Three.js 8-term version)
                var wY = buf.sinPx05[xi] * buf.cosPz05[zi] * 0.8f  // cross-wave
                wY += buf.sinPx08[xi]                                // x-axis ripple
                wY += buf.cosPz06[zi]                                // z-axis ripple
                wY += sin((px + pz) * 0.4f + t13) * 0.6f            // diagonal wave
                wY += buf.sinPx15[xi] * buf.cosPz12[zi] * 0.3f      // high-freq cross

                buf.cr[idx] = buf.baseR[xi]
                buf.cg[idx] = buf.baseG[xi]
                buf.cb[idx] = buf.baseB[xi]
                buf.sz[idx] = 0.06f + abs(wY) * 0.018f

                // 3D perspective projection
                val worldX = px - camX
                val worldY = wY - camY + CAM_LOOK_Y
                val zDist = CAM_Z - pz
                if (zDist <= 0.5f) { buf.ok[idx] = false; continue }

                val scale = FOV / zDist
                val projX = worldX * scale + screenCx
                val projY = worldY * scale + screenCy

                // Viewport culling
                if (projX < -10f || projX > w + 10f || projY < -10f || projY > h + 10f) {
                    buf.ok[idx] = false; continue
                }

                buf.sx[idx] = projX
                buf.sy[idx] = projY
                buf.ok[idx] = true

                // Depth fog (linear approx of FogExp2)
                val fog = (1f - (zDist - 6f) * 0.012f).coerceIn(0.1f, 1f)
                buf.cr[idx] *= fog
                buf.cg[idx] *= fog
                buf.cb[idx] *= fog
            }
        }

        // ── Wireframe: single batched Path, every 3rd line ──
        wirePath.reset()
        val wireStep = 3
        for (xi in 0 until GRID step wireStep) {
            for (zi in 0 until GRID - 1) {
                val idx = xi * GRID + zi
                val ni = idx + 1
                if (buf.ok[idx] && buf.ok[ni]) {
                    wirePath.moveTo(buf.sx[idx], buf.sy[idx])
                    wirePath.lineTo(buf.sx[ni], buf.sy[ni])
                }
            }
        }
        for (zi in 0 until GRID step wireStep) {
            for (xi in 0 until GRID - 1) {
                val idx = xi * GRID + zi
                val ni = (xi + 1) * GRID + zi
                if (buf.ok[idx] && buf.ok[ni]) {
                    wirePath.moveTo(buf.sx[idx], buf.sy[idx])
                    wirePath.lineTo(buf.sx[ni], buf.sy[ni])
                }
            }
        }
        drawPath(wirePath, Color(0.21f, 0.56f, 0.54f, 0.04f), style = Stroke(0.5f))

        // ── Points: back-to-front for correct depth ordering ──
        for (zi in 0 until GRID) {
            val pz = zi * SEP - HALF
            val zDist = CAM_Z - pz
            val depthAlpha = (1f - zDist * 0.03f).coerceIn(0.1f, 1f) * 0.85f
            val radiusScale = 200f / zDist

            for (xi in 0 until GRID) {
                val idx = xi * GRID + zi
                if (!buf.ok[idx]) continue

                val radius = (buf.sz[idx] * radiusScale).coerceIn(0.3f, 4f)
                drawCircle(
                    Color(buf.cr[idx], buf.cg[idx], buf.cb[idx], depthAlpha),
                    radius,
                    Offset(buf.sx[idx], buf.sy[idx]),
                )
            }
        }
    }
}