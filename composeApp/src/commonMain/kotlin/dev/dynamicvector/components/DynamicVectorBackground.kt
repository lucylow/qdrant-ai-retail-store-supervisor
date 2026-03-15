package dev.dynamicvector.components

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import kotlin.math.*
import kotlin.random.Random

// Grid matches reference: 70×70, spacing 0.28
private const val CO = 70
private const val SEP = 0.28f
private const val HALF_W = CO * SEP / 2f
private const val CYCLE = 16f

// Camera: perspective FOV=50° mapped to screen, at z=12 looking at origin
private const val CAM_Z = 12f
private const val CAM_LOOK_Y = 0.5f
private const val FOV_SCALE = 500f

private const val STAR_COUNT = 60
private const val STREAM_COUNT = 500

private val BG = Color(0xFF040410)

private fun ss(e0: Float, e1: Float, x: Float): Float {
    val t = ((x - e0) / (e1 - e0)).coerceIn(0f, 1f)
    return t * t * (3f - 2f * t)
}

// Color mapping from reference: cB = (nx+1)/2 where nx is -1..1
private fun gridColorRGB(nx: Float): Triple<Float, Float, Float> {
    val cB = (nx + 1f) / 2f
    return when {
        cB < 0.4f -> Triple(0.12f + cB * 0.5f, 0.5f + cB * 0.7f, 0.9f - cB * 0.2f)
        cB < 0.6f -> Triple(0.45f, 0.35f, 0.7f)
        else -> Triple(
            (0.5f + (cB - 0.6f) * 1.5f).coerceAtMost(1f),
            0.3f + cB * 0.2f,
            (0.4f - cB * 0.2f).coerceAtLeast(0f),
        )
    }
}

// Repository shape from reference exactly
private fun repoShape(nx: Float, nz: Float, t: Float): Float? {
    val r = sqrt(nx * nx + nz * nz)
    val R = 0.35f
    if (r > R) return null
    val e = ss(R, R - 0.08f, r)
    return 2.5f * 0.5f * e + sin(r * 20f + t * 2f) * 0.15f * e
}

// Morph blend from reference
private fun getBlend(t: Float): Float {
    val ct = t % CYCLE
    return when {
        ct < 3f -> 0f
        ct < 5f -> (ct - 3f) / 2f
        ct < 9f -> 1f
        ct < 11f -> 1f - (ct - 9f) / 2f
        else -> 0f
    }
}

private data class Star(val x: Float, val y: Float, val phase: Float, val speed: Float)

private class StreamParticle {
    var x = 0f; var y = 0f; var z = 0f
    var vx = 0f; var vy = 0f; var vz = 0f
    var life = 0f
    var cr = 0f; var cg = 0f; var cb = 0f

    fun reset(rng: Random) {
        val a = rng.nextFloat() * 6.2832f
        val r = 6f + rng.nextFloat() * 6f
        x = cos(a) * r
        y = (rng.nextFloat() - 0.3f) * 4f
        z = sin(a) * r
        val spd = 0.02f + rng.nextFloat() * 0.03f
        vx = -cos(a) * spd
        vy = (0f - y) * 0.005f
        vz = -sin(a) * spd
        life = rng.nextFloat()
        if (rng.nextBoolean()) { cr = 0.3f; cg = 0.8f; cb = 0.77f }
        else { cr = 0.48f; cg = 0.37f; cb = 0.65f }
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
        Array(STREAM_COUNT) { StreamParticle().also { it.reset(rng) } }
    }

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
        // Place mesh centered vertically, upside down — close to the logo area
        val screenCy = h * 0.38f

        drawRect(BG)

        // Stars
        for (star in stars) {
            val alpha = (0.3f + 0.4f * ((sin(time * star.speed + star.phase) + 1f) * 0.5f))
            drawCircle(Color.White.copy(alpha = alpha * 0.5f), 1f, Offset(star.x * w, star.y * h))
        }

        // Camera orbit (from reference)
        val camX = sin(time * 0.08f) * 2f
        val camY = 3.5f + sin(time * 0.12f) * 0.5f

        val mb = getBlend(time)

        // Pre-allocate arrays for projected positions
        val total = CO * CO
        val pxArr = FloatArray(total)
        val pyArr = FloatArray(total)
        val wYArr = FloatArray(total)
        val szArr = FloatArray(total)
        val crArr = FloatArray(total)
        val cgArr = FloatArray(total)
        val cbArr = FloatArray(total)
        val validArr = BooleanArray(total)

        for (xi in 0 until CO) {
            for (zi in 0 until CO) {
                val idx = xi * CO + zi
                val px = xi * SEP - HALF_W
                val pz = zi * SEP - HALF_W
                val nx = px / HALF_W  // -1..1
                val nz = pz / HALF_W  // -1..1

                // Wave function from reference
                var wY = sin(px * 0.5f + time * 0.7f) * cos(pz * 0.5f + time * 0.7f) * 0.8f
                wY += sin(px * 0.8f - time * 1.1f) * 0.5f
                wY += cos(pz * 0.6f + time * 0.9f) * 0.4f
                wY += sin((px + pz) * 0.4f + time * 1.3f) * 0.6f
                wY += sin(px * 1.5f + time * 1.8f) * cos(pz * 1.2f - time) * 0.3f
                wY += cos(px * 2.2f - time * 2.1f) * 0.2f
                wY += sin(pz * 1.8f + time * 1.5f) * 0.25f
                val pkt = exp(-((nx - 0.2f * sin(time * 0.3f)).let { it * it }) * 8f)
                wY += pkt * sin(px * 3f + time * 3f) * 0.7f

                // Repo morph from reference
                val rt = repoShape(nx, nz, time)
                var finalY: Float
                var cr: Float; var cg: Float; var cb: Float
                var sz: Float

                if (rt != null && mb > 0f) {
                    finalY = wY * (1f - mb) + rt * mb
                    val glow = mb * 0.7f
                    val r2 = sqrt(nx * nx + nz * nz)
                    val ring = sin(r2 * 30f - time * 3f) * 0.15f + 0.5f
                    cr = 0.3f + glow * 0.2f * ring
                    cg = 0.8f - glow * 0.15f
                    cb = 0.77f + glow * 0.1f
                    sz = 0.06f + mb * 0.04f * (1f - r2 / 0.35f).coerceAtLeast(0f)
                } else {
                    finalY = wY
                    val (r, g, b) = gridColorRGB(nx)
                    cr = r; cg = g; cb = b
                    sz = 0.05f + abs(wY) * 0.015f
                }

                wYArr[idx] = finalY
                crArr[idx] = cr; cgArr[idx] = cg; cbArr[idx] = cb
                szArr[idx] = sz

                // Project: camera at (camX, camY, CAM_Z), looking at (0, CAM_LOOK_Y, 0)
                val worldX = px - camX
                val worldY = finalY - camY + CAM_LOOK_Y
                val worldZ = pz

                val zd = CAM_Z - worldZ // distance from camera
                if (zd <= 0.5f) { validArr[idx] = false; continue }

                val scale = FOV_SCALE / zd
                // Positive worldY goes DOWN on screen (upside down)
                pxArr[idx] = worldX * scale + screenCx
                pyArr[idx] = worldY * scale + screenCy
                validArr[idx] = true

                // Fog: fade with distance
                val fog = (1f - (zd - 6f) * 0.012f).coerceIn(0.1f, 1f)
                crArr[idx] *= fog; cgArr[idx] *= fog; cbArr[idx] *= fog
            }
        }

        // Wireframe (from reference: opacity = 0.04 + mb*0.06)
        val wireAlpha = 0.04f + mb * 0.06f
        for (xi in 0 until CO) {
            for (zi in 0 until CO) {
                val idx = xi * CO + zi
                if (!validArr[idx]) continue
                val x1 = pxArr[idx]; val y1 = pyArr[idx]
                val lineColor = Color(crArr[idx] * 0.7f, cgArr[idx] * 0.7f, cbArr[idx] * 0.7f, wireAlpha)

                // Connect to z+1
                if (zi < CO - 1) {
                    val ni = idx + 1
                    if (validArr[ni]) {
                        drawLine(lineColor, Offset(x1, y1), Offset(pxArr[ni], pyArr[ni]), strokeWidth = 0.5f)
                    }
                }
                // Connect to x+1
                if (xi < CO - 1) {
                    val ni = (xi + 1) * CO + zi
                    if (validArr[ni]) {
                        drawLine(lineColor, Offset(x1, y1), Offset(pxArr[ni], pyArr[ni]), strokeWidth = 0.5f)
                    }
                }
            }
        }

        // Grid particles with additive-style rendering
        for (xi in 0 until CO) {
            for (zi in 0 until CO) {
                val idx = xi * CO + zi
                if (!validArr[idx]) continue
                val x1 = pxArr[idx]; val y1 = pyArr[idx]
                val zd = CAM_Z - (zi * SEP - HALF_W)
                val depthAlpha = (1f + zd * 0.03f).coerceIn(0.1f, 1f) * 0.85f
                val radius = (szArr[idx] * (200f / zd)).coerceIn(0.3f, 4f)

                drawCircle(
                    Color(crArr[idx], cgArr[idx], cbArr[idx], depthAlpha),
                    radius,
                    Offset(x1, y1),
                )
            }
        }

        // Stream particles — converge inward toward mesh center
        val sI = if (mb > 0.1f) 1f else 0.3f
        val streamRng = Random(((time * 10).toInt()).toLong() + 7)
        for (sp in streams) {
            // During convergence, add extra pull toward center
            if (mb > 0.1f) {
                val d = sqrt(sp.x * sp.x + sp.z * sp.z).coerceAtLeast(0.1f)
                val pull = mb * 0.01f
                sp.vx -= sp.x / d * pull
                sp.vz -= sp.z / d * pull
                sp.vy += (0f - sp.y) * 0.01f * mb
            }

            sp.x += sp.vx * sI
            sp.y += sp.vy
            sp.z += sp.vz * sI
            sp.life -= 0.004f * sI

            val d = sqrt(sp.x * sp.x + sp.z * sp.z)
            if (sp.life < 0f || d < 0.3f || d > 15f) {
                sp.reset(streamRng)
            }

            // Project stream particle
            val sx = sp.x - camX
            val sy = sp.y - camY + CAM_LOOK_Y
            val sz = sp.z
            val szd = CAM_Z - sz
            if (szd <= 0.5f) continue
            val sScale = FOV_SCALE / szd
            val spx = sx * sScale + screenCx
            val spy = sy * sScale + screenCy

            if (spx < -50f || spx > w + 50f || spy < -50f || spy > h + 50f) continue

            val stAlpha = (0.4f + mb * 0.5f) * 0.8f
            val stRadius = (0.12f * 200f / szd).coerceIn(0.4f, 3f)
            drawCircle(
                Color(sp.cr, sp.cg, sp.cb, stAlpha),
                stRadius,
                Offset(spx, spy),
            )
        }
    }
}