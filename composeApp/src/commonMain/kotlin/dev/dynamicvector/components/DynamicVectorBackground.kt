package dev.dynamicvector.components

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import kotlin.math.PI
import kotlin.math.abs
import kotlin.math.sin

// ── Sine lookup table: replaces all sin()/cos() with fast array reads ──
private const val LUT_BITS = 11
private const val LUT_SIZE = 1 shl LUT_BITS       // 2048 entries
private const val LUT_MASK = LUT_SIZE - 1
private val LUT_SCALE = LUT_SIZE / (2f * PI.toFloat())
private val SIN_LUT = FloatArray(LUT_SIZE) { sin(it.toDouble() * 2.0 * PI / LUT_SIZE).toFloat() }

private fun fsin(x: Float): Float = SIN_LUT[(x * LUT_SCALE).toInt() and LUT_MASK]
private fun fcos(x: Float): Float = fsin(x + (PI.toFloat() * 0.5f))

// ── Grid config ──
private const val GRID = 50
private const val SEP = 0.56f
private const val HALF = GRID * SEP / 2f
private const val TOTAL = GRID * GRID

private const val CAM_Z = 12f
private const val CAM_LOOK_Y = 0.5f
private const val FOV = 500f
private const val STAR_COUNT = 180
private val BG = Color(0xFF040410)

private data class Star(val x: Float, val y: Float, val radius: Float, val alpha: Float)

private class Buffers {
    val sx = FloatArray(TOTAL)
    val sy = FloatArray(TOTAL)
    val cr = FloatArray(TOTAL)
    val cg = FloatArray(TOTAL)
    val cb = FloatArray(TOTAL)
    val sz = FloatArray(TOTAL)
    val ok = BooleanArray(TOTAL)

    val sinPx05 = FloatArray(GRID)
    val sinPx08 = FloatArray(GRID)
    val sinPx15 = FloatArray(GRID)
    val baseR = FloatArray(GRID)
    val baseG = FloatArray(GRID)
    val baseB = FloatArray(GRID)

    val cosPz05 = FloatArray(GRID)
    val cosPz06 = FloatArray(GRID)
    val cosPz12 = FloatArray(GRID)
    val fog = FloatArray(GRID)         // pre-computed per-column fog
    val depthAlpha = FloatArray(GRID)  // pre-computed per-column alpha
    val radScale = FloatArray(GRID)    // pre-computed per-column radius scale
}

@Composable
fun QuantumWaveFabric(modifier: Modifier = Modifier) {
    // Stars are static — pre-computed once, no per-frame trig
    val stars = remember {
        val rng = kotlin.random.Random(42)
        Array(STAR_COUNT) {
            Star(
                x = rng.nextFloat(),
                y = rng.nextFloat(),
                radius = 0.4f + rng.nextFloat() * 1.0f,
                alpha = 0.15f + rng.nextFloat() * 0.45f,
            )
        }
    }
    // Pre-compute star colors once (avoids Color.copy allocation per star per frame)
    val starColors = remember {
        Array(STAR_COUNT) { Color.White.copy(alpha = stars[it].alpha) }
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

        // ── Stars: static dots, zero per-frame math ──
        for (i in 0 until STAR_COUNT) {
            val s = stars[i]
            drawCircle(starColors[i], s.radius, Offset(s.x * w, s.y * h))
        }

        // Camera orbit
        val camX = fsin(time * 0.08f) * 2f
        val camY = 3.5f + fsin(time * 0.12f) * 0.5f

        val t07 = time * 0.7f
        val t11 = time * 1.1f
        val t09 = time * 0.9f
        val t13 = time * 1.3f
        val t18 = time * 1.8f

        // ── Pre-compute per-row trig (50 LUT reads instead of 2,500 sin calls) ──
        for (xi in 0 until GRID) {
            val px = xi * SEP - HALF
            val nx = px / HALF

            buf.sinPx05[xi] = fsin(px * 0.5f + t07)
            buf.sinPx08[xi] = fsin(px * 0.8f - t11) * 0.5f
            buf.sinPx15[xi] = fsin(px * 1.5f + t18)

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

        // ── Pre-compute per-column trig + fog + depth params ──
        for (zi in 0 until GRID) {
            val pz = zi * SEP - HALF
            buf.cosPz05[zi] = fcos(pz * 0.5f + t07)
            buf.cosPz06[zi] = fcos(pz * 0.6f + t09) * 0.4f
            buf.cosPz12[zi] = fcos(pz * 1.2f - time)

            val zDist = CAM_Z - pz
            buf.fog[zi] = (1f - (zDist - 6f) * 0.012f).coerceIn(0.1f, 1f)
            buf.depthAlpha[zi] = (1f - zDist * 0.03f).coerceIn(0.1f, 1f) * 0.85f
            buf.radScale[zi] = 200f / zDist
        }

        // ── Grid computation ──
        for (xi in 0 until GRID) {
            val px = xi * SEP - HALF
            for (zi in 0 until GRID) {
                val idx = xi * GRID + zi
                val pz = zi * SEP - HALF

                // 5-term wave (all LUT reads, no stdlib trig)
                var wY = buf.sinPx05[xi] * buf.cosPz05[zi] * 0.8f
                wY += buf.sinPx08[xi]
                wY += buf.cosPz06[zi]
                wY += fsin((px + pz) * 0.4f + t13) * 0.6f
                wY += buf.sinPx15[xi] * buf.cosPz12[zi] * 0.3f

                buf.sz[idx] = 0.06f + abs(wY) * 0.018f

                // 3D projection
                val worldX = px - camX
                val worldY = wY - camY + CAM_LOOK_Y
                val zDist = CAM_Z - pz
                if (zDist <= 0.5f) { buf.ok[idx] = false; continue }

                val scale = FOV / zDist
                val projX = worldX * scale + screenCx
                val projY = worldY * scale + screenCy

                if (projX < -10f || projX > w + 10f || projY < -10f || projY > h + 10f) {
                    buf.ok[idx] = false; continue
                }

                buf.sx[idx] = projX
                buf.sy[idx] = projY
                buf.ok[idx] = true

                // Apply pre-computed fog
                val fog = buf.fog[zi]
                buf.cr[idx] = buf.baseR[xi] * fog
                buf.cg[idx] = buf.baseG[xi] * fog
                buf.cb[idx] = buf.baseB[xi] * fog
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

        // ── Points: back-to-front ──
        for (zi in 0 until GRID) {
            val dAlpha = buf.depthAlpha[zi]
            val rScale = buf.radScale[zi]

            for (xi in 0 until GRID) {
                val idx = xi * GRID + zi
                if (!buf.ok[idx]) continue

                val radius = (buf.sz[idx] * rScale).coerceIn(0.3f, 4f)
                drawCircle(
                    Color(buf.cr[idx], buf.cg[idx], buf.cb[idx], dAlpha),
                    radius,
                    Offset(buf.sx[idx], buf.sy[idx]),
                )
            }
        }
    }
}