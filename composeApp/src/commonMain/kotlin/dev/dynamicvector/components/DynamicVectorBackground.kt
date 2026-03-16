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

// ═══════════════════════════════════════════════════════════════════════════════
// SINE LOOKUP TABLE (LUT)
//
// Instead of calling kotlin.math.sin() / cos() every frame (~2,800 calls),
// we pre-build a 2048-entry table of sin values covering one full period
// (0 to 2π). fsin() and fcos() convert any radian angle to a table index
// using bitwise AND for wrapping — this works for negative angles too,
// thanks to two's complement arithmetic. Each lookup is ~5–10× faster
// than a stdlib trig call on ARM.
// ═══════════════════════════════════════════════════════════════════════════════
private const val LUT_BITS = 11                         // 2^11 = 2048 entries
private const val LUT_SIZE = 1 shl LUT_BITS
private const val LUT_MASK = LUT_SIZE - 1               // bitmask for fast wrapping
private val LUT_SCALE = LUT_SIZE / (2f * PI.toFloat())  // radians → table index
private val SIN_LUT = FloatArray(LUT_SIZE) { sin(it.toDouble() * 2.0 * PI / LUT_SIZE).toFloat() }

/** Fast sine via LUT. Accepts any radian value (positive or negative). */
private fun fsin(x: Float): Float = SIN_LUT[(x * LUT_SCALE).toInt() and LUT_MASK]

/** Fast cosine — just sin shifted by π/2. */
private fun fcos(x: Float): Float = fsin(x + (PI.toFloat() * 0.5f))

// ═══════════════════════════════════════════════════════════════════════════════
// GRID CONFIGURATION
//
// The animation is a 50×50 grid of 3D points (2,500 total) that form a
// wave-displaced mesh, viewed from a slowly orbiting perspective camera.
// This is an optimized Compose Canvas port of the Three.js reference
// (dynamic_vector_repo_final.html), which used a 70×70 grid (4,900 pts).
//
// SEP controls the spacing between grid points in world units. A larger
// value spreads the same number of points over a wider area, ensuring
// the mesh edges stay off-screen without needing more points.
//
// HALF is half the total grid extent — the grid spans from -HALF to +HALF
// on both the X and Z axes.
// ═══════════════════════════════════════════════════════════════════════════════
private const val GRID = 50           // points per axis (50×50 = 2,500 total)
private const val SEP = 0.56f         // world-unit spacing between adjacent points
private const val HALF = GRID * SEP / 2f  // grid extends from -HALF to +HALF
private const val TOTAL = GRID * GRID     // total point count

// ═══════════════════════════════════════════════════════════════════════════════
// CAMERA
//
// The camera sits at Z=12 looking toward the origin, giving a top-down
// perspective view of the wave mesh. CAM_LOOK_Y offsets the look-at point
// slightly above the mesh plane. FOV controls the perspective projection
// strength (higher = more zoom / less perspective distortion).
// ═══════════════════════════════════════════════════════════════════════════════
private const val CAM_Z = 12f         // camera distance along Z axis
private const val CAM_LOOK_Y = 0.5f   // vertical offset of the look-at target
private const val FOV = 500f          // projection scale factor (pseudo field-of-view)

private const val STAR_COUNT = 180    // number of static background stars
private val BG = Color(0xFF8B1A1A)    // deep crimson — Swiss flag red field

// ═══════════════════════════════════════════════════════════════════════════════
// STAR — a single static background dot, positioned in normalized coords (0–1)
// ═══════════════════════════════════════════════════════════════════════════════
private data class Star(val x: Float, val y: Float, val radius: Float, val alpha: Float)

// ═══════════════════════════════════════════════════════════════════════════════
// FRAME BUFFERS
//
// All per-frame mutable data is pre-allocated here ONCE via remember{}.
// This avoids creating thousands of temporary arrays inside Canvas{}
// every frame, which would cause GC pressure and frame drops on mobile.
//
// Layout:
//   Per-point arrays (TOTAL = 2,500 entries each):
//     sx, sy    — projected screen coordinates
//     cr, cg, cb — RGB color after fog is applied
//     sz        — point size in world units (converted to pixels during render)
//     ok        — visibility flag (false if behind camera or off-screen)
//
//   Per-row arrays (GRID = 50 entries each):
//     sinPx*    — pre-computed sine terms that only depend on the X position
//     baseR/G/B — base color per row (depends on normalized X, constant per row)
//
//   Per-column arrays (GRID = 50 entries each):
//     cosPz*    — pre-computed cosine terms that only depend on the Z position
//     fog       — depth fog multiplier (dims far-away points)
//     depthAlpha — alpha transparency based on depth
//     radScale  — pixel-size scale factor based on depth
// ═══════════════════════════════════════════════════════════════════════════════
private class Buffers {
    // Per-point (indexed by xi * GRID + zi)
    val sx = FloatArray(TOTAL)    // screen X after projection
    val sy = FloatArray(TOTAL)    // screen Y after projection
    val cr = FloatArray(TOTAL)    // red channel (0–1, fog-adjusted)
    val cg = FloatArray(TOTAL)    // green channel
    val cb = FloatArray(TOTAL)    // blue channel
    val sz = FloatArray(TOTAL)    // world-space point size
    val ok = BooleanArray(TOTAL)  // true if point is visible on screen

    // Per-row pre-computed trig (indexed by xi)
    val sinPx05 = FloatArray(GRID)  // sin(px * 0.5 + t*0.7) — used in wave term 1
    val sinPx08 = FloatArray(GRID)  // sin(px * 0.8 - t*1.1) * 0.5 — wave term 2
    val sinPx15 = FloatArray(GRID)  // sin(px * 1.5 + t*1.8) — used in wave term 5

    // Per-row base colors (indexed by xi) — shades of Swiss red across the mesh
    val baseR = FloatArray(GRID)
    val baseG = FloatArray(GRID)
    val baseB = FloatArray(GRID)

    // Per-column pre-computed trig (indexed by zi)
    val cosPz05 = FloatArray(GRID)  // cos(pz * 0.5 + t*0.7) — used in wave term 1
    val cosPz06 = FloatArray(GRID)  // cos(pz * 0.6 + t*0.9) * 0.4 — wave term 3
    val cosPz12 = FloatArray(GRID)  // cos(pz * 1.2 - t) — used in wave term 5

    // Per-column rendering params (indexed by zi) — only depend on depth, not X
    val fog = FloatArray(GRID)        // fog multiplier (1.0 = near/clear, 0.0 = far/faded)
    val depthAlpha = FloatArray(GRID) // alpha falloff with distance
    val radScale = FloatArray(GRID)   // perspective size scaling (larger when closer)
}

// ═══════════════════════════════════════════════════════════════════════════════
// MAIN COMPOSABLE
//
// Renders a full-screen animated background with:
//   1. A warm white background with 180 static red star dots
//   2. A 50×50 3D wave mesh with perspective projection
//   3. A subtle red wireframe connecting grid points
//   4. Red-toned point particles with depth-based fog and alpha
//
// The animation runs via withFrameNanos, which ties updates to the display
// refresh rate (typically 60 Hz). The `time` state variable drives all
// wave and camera motion.
// ═══════════════════════════════════════════════════════════════════════════════
@Composable
fun QuantumWaveFabric(modifier: Modifier = Modifier) {

    // ── STARS ──
    // Generated once with a fixed seed (42) for deterministic layout.
    // Positions are in normalized 0–1 coords, scaled to screen size at draw time.
    // Radii vary from 0.4–1.4 px, alpha from 0.08–0.30 for depth variety.
    // No per-frame math — completely static. Red-tinted on white bg.
    val stars = remember {
        val rng = kotlin.random.Random(42)
        Array(STAR_COUNT) {
            Star(
                x = rng.nextFloat(),
                y = rng.nextFloat(),
                radius = 0.4f + rng.nextFloat() * 1.0f,
                alpha = 0.08f + rng.nextFloat() * 0.22f,
            )
        }
    }
    // Pre-compute Color objects — white dots on red bg
    val starColors = remember {
        Array(STAR_COUNT) { Color.White.copy(alpha = stars[it].alpha) }
    }

    val buf = remember { Buffers() }
    val wirePath = remember { Path() }  // reused every frame — reset() then rebuild
    var time by remember { mutableFloatStateOf(0f) }

    // ── FRAME CLOCK ──
    // withFrameNanos runs once per display vsync. We compute a delta-time
    // clamped to [1ms, 50ms] to prevent time jumps from pauses or debugger halts.
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

        // Screen-space center for projection. screenCy at 38% places the
        // mesh's horizon in the upper third, so the mesh fills the lower portion.
        val screenCx = w * 0.5f
        val screenCy = h * 0.38f

        // Clear to warm white background
        drawRect(BG)

        // ── STARS ──
        // Draw 180 static red dots. No math per frame — just position × screen size.
        for (i in 0 until STAR_COUNT) {
            val s = stars[i]
            drawCircle(starColors[i], s.radius, Offset(s.x * w, s.y * h))
        }

        // ── CAMERA ORBIT ──
        // The camera slowly drifts side-to-side (X) and bobs up/down (Y),
        // matching the Three.js reference animation. The low frequencies
        // (0.08, 0.12) create a gentle, ambient motion.
        val camX = fsin(time * 0.08f) * 2f           // ±2 units horizontal drift
        val camY = 3.5f + fsin(time * 0.12f) * 0.5f  // 3.0–4.0 units above the mesh

        // ── CACHED TIME PRODUCTS ──
        // Each wave term uses time × a constant. Pre-multiplying avoids
        // redundant multiplications in the loops below.
        val t07 = time * 0.7f   // wave term 1 speed
        val t11 = time * 1.1f   // wave term 2 speed (counter-direction)
        val t09 = time * 0.9f   // wave term 3 speed
        val t13 = time * 1.3f   // wave term 4 speed (diagonal)
        val t18 = time * 1.8f   // wave term 5 speed (high frequency)

        // ═════════════════════════════════════════════════════════════════════
        // PHASE 1: PRE-COMPUTE PER-ROW VALUES
        //
        // Many wave terms depend only on px (the X world position), not pz.
        // By computing them once per row (50 iterations), we avoid recomputing
        // them for every point in that row (50× savings = 2,500 → 50 LUT reads).
        //
        // We also pre-compute the base color per row. The color gradient goes:
        //   Left edge  (cB < 0.4) → warm cream     (R:0.90–0.95, G:0.82–0.88, B:0.78–0.84)
        //   Center     (cB 0.4–0.6) → pure white   (R:1.0, G:1.0, B:1.0)
        //   Right edge (cB > 0.6) → cool pink-white (R:1.0, G:0.88–0.95, B:0.88–0.92)
        // ═════════════════════════════════════════════════════════════════════
        for (xi in 0 until GRID) {
            val px = xi * SEP - HALF     // world X position (centered at 0)
            val nx = px / HALF           // normalized X: -1.0 (left) to +1.0 (right)

            // Pre-compute the 3 row-dependent sine terms
            buf.sinPx05[xi] = fsin(px * 0.5f + t07)         // slow, wide oscillation
            buf.sinPx08[xi] = fsin(px * 0.8f - t11) * 0.5f  // medium wave, half amplitude
            buf.sinPx15[xi] = fsin(px * 1.5f + t18)         // faster ripple

            // Color gradient: map nx from [-1,1] to cB in [0,1]
            val cB = (nx + 1f) / 2f
            when {
                cB < 0.4f -> {
                    // Left side: warm cream/ivory
                    buf.baseR[xi] = 0.90f + cB * 0.12f
                    buf.baseG[xi] = 0.82f + cB * 0.15f
                    buf.baseB[xi] = 0.78f + cB * 0.15f
                }
                cB < 0.6f -> {
                    // Center: pure white
                    buf.baseR[xi] = 1.0f
                    buf.baseG[xi] = 1.0f
                    buf.baseB[xi] = 1.0f
                }
                else -> {
                    // Right side: cool pink-white
                    val t = (cB - 0.6f) / 0.4f
                    buf.baseR[xi] = 1.0f
                    buf.baseG[xi] = 0.95f - t * 0.07f
                    buf.baseB[xi] = 0.92f - t * 0.04f
                }
            }
        }

        // ═════════════════════════════════════════════════════════════════════
        // PHASE 2: PRE-COMPUTE PER-COLUMN VALUES
        //
        // Similarly, some wave terms depend only on pz (Z world position).
        // We also pre-compute depth-dependent rendering params here since
        // they're constant across all points in the same column:
        //
        //   fog       — linear approximation of exponential fog; fades points
        //               that are far from the camera (zDist > 6) toward white.
        //   depthAlpha — alpha transparency that fades with distance, matching
        //               the Three.js vAlpha shader uniform.
        //   radScale  — perspective size: closer points appear larger.
        // ═════════════════════════════════════════════════════════════════════
        for (zi in 0 until GRID) {
            val pz = zi * SEP - HALF     // world Z position
            buf.cosPz05[zi] = fcos(pz * 0.5f + t07)         // slow, wide oscillation
            buf.cosPz06[zi] = fcos(pz * 0.6f + t09) * 0.4f  // medium wave, reduced amplitude
            buf.cosPz12[zi] = fcos(pz * 1.2f - time)         // faster counter-oscillation

            // zDist = distance from camera to this column's Z plane
            val zDist = CAM_Z - pz
            buf.fog[zi] = (1f - (zDist - 6f) * 0.012f).coerceIn(0.1f, 1f)
            buf.depthAlpha[zi] = (1f - zDist * 0.03f).coerceIn(0.1f, 1f) * 0.85f
            buf.radScale[zi] = 200f / zDist
        }

        // ═════════════════════════════════════════════════════════════════════
        // PHASE 3: GRID COMPUTATION — WAVE DISPLACEMENT + PROJECTION
        //
        // For each of the 2,500 grid points we:
        //   1. Compute the wave height (Y displacement) by summing 5 terms
        //   2. Project the 3D world position onto 2D screen coords
        //   3. Cull points behind the camera or outside the viewport
        //   4. Apply fog to the base color (blending toward white bg)
        //
        // WAVE FUNCTION (5 terms, adapted from the Three.js 8-term version):
        //   Term 1: sin(px×0.5+t×0.7) × cos(pz×0.5+t×0.7) × 0.8
        //           → broad cross-directional wave (the dominant shape)
        //   Term 2: sin(px×0.8−t×1.1) × 0.5
        //           → X-axis traveling ripple
        //   Term 3: cos(pz×0.6+t×0.9) × 0.4
        //           → Z-axis traveling ripple
        //   Term 4: sin((px+pz)×0.4+t×1.3) × 0.6
        //           → diagonal wave (the only per-point LUT read)
        //   Term 5: sin(px×1.5+t×1.8) × cos(pz×1.2−t) × 0.3
        //           → high-frequency cross pattern for detail
        //
        // Terms 1, 2, 3, 5 use pre-computed row/column values.
        // Only term 4 requires a per-point LUT read (cross-axis dependency).
        //
        // PROJECTION:
        //   Simple perspective divide: screenPos = worldPos × (FOV / zDist) + center
        //   This matches how the Three.js PerspectiveCamera works internally.
        // ═════════════════════════════════════════════════════════════════════
        for (xi in 0 until GRID) {
            val px = xi * SEP - HALF
            for (zi in 0 until GRID) {
                val idx = xi * GRID + zi
                val pz = zi * SEP - HALF

                // Sum the 5 wave terms to get the Y (height) displacement
                var wY = buf.sinPx05[xi] * buf.cosPz05[zi] * 0.8f  // term 1: cross-wave
                wY += buf.sinPx08[xi]                                // term 2: X ripple
                wY += buf.cosPz06[zi]                                // term 3: Z ripple
                wY += fsin((px + pz) * 0.4f + t13) * 0.6f           // term 4: diagonal
                wY += buf.sinPx15[xi] * buf.cosPz12[zi] * 0.3f      // term 5: detail

                // Point size scales with wave height (taller peaks = bigger dots)
                buf.sz[idx] = 0.06f + abs(wY) * 0.018f

                // ── 3D → 2D PERSPECTIVE PROJECTION ──
                // Translate point relative to camera, then perspective-divide by depth
                val worldX = px - camX
                val worldY = wY - camY + CAM_LOOK_Y
                val zDist = CAM_Z - pz

                // Skip points behind or too close to the camera
                if (zDist <= 0.5f) { buf.ok[idx] = false; continue }

                val scale = FOV / zDist
                val projX = worldX * scale + screenCx
                val projY = worldY * scale + screenCy

                // Viewport culling: skip points projected outside the screen
                // (saves ~15–25% of draw calls on typical frames)
                if (projX < -10f || projX > w + 10f || projY < -10f || projY > h + 10f) {
                    buf.ok[idx] = false; continue
                }

                buf.sx[idx] = projX
                buf.sy[idx] = projY
                buf.ok[idx] = true

                // Fog blends base color toward red bg for distant points
                val fog = buf.fog[zi]
                buf.cr[idx] = buf.baseR[xi] * fog + (1f - fog) * 0.545f
                buf.cg[idx] = buf.baseG[xi] * fog + (1f - fog) * 0.102f
                buf.cb[idx] = buf.baseB[xi] * fog + (1f - fog) * 0.102f
            }
        }

        // ═════════════════════════════════════════════════════════════════════
        // PHASE 4: WIREFRAME
        //
        // Draws a subtle grid of lines connecting adjacent points to give
        // the mesh a "fabric" look. Instead of issuing thousands of individual
        // drawLine() calls (each a separate GPU command), we build a single
        // Path with moveTo/lineTo segments and draw it in one drawPath() call.
        //
        // wireStep=3 means we only draw every 3rd row/column of wires,
        // reducing path complexity by ~9× while keeping enough visual density
        // (the point particles carry the main visual weight).
        //
        // First loop: wires along the Z axis (connects zi to zi+1, fixed xi)
        // Second loop: wires along the X axis (connects xi to xi+1, fixed zi)
        // ═════════════════════════════════════════════════════════════════════
        wirePath.reset()
        val wireStep = 3
        // Z-direction wires (horizontal lines on screen)
        for (xi in 0 until GRID step wireStep) {
            for (zi in 0 until GRID - 1) {
                val idx = xi * GRID + zi
                val ni = idx + 1  // next point along Z
                if (buf.ok[idx] && buf.ok[ni]) {
                    wirePath.moveTo(buf.sx[idx], buf.sy[idx])
                    wirePath.lineTo(buf.sx[ni], buf.sy[ni])
                }
            }
        }
        // X-direction wires (depth lines on screen)
        for (zi in 0 until GRID step wireStep) {
            for (xi in 0 until GRID - 1) {
                val idx = xi * GRID + zi
                val ni = (xi + 1) * GRID + zi  // next point along X
                if (buf.ok[idx] && buf.ok[ni]) {
                    wirePath.moveTo(buf.sx[idx], buf.sy[idx])
                    wirePath.lineTo(buf.sx[ni], buf.sy[ni])
                }
            }
        }
        // Single draw call for the entire wireframe — white on red, subtle
        drawPath(wirePath, Color(1f, 1f, 1f, 0.05f), style = Stroke(0.5f))

        // ═════════════════════════════════════════════════════════════════════
        // PHASE 5: POINT PARTICLES (BACK-TO-FRONT)
        //
        // Draw each visible grid point as a small colored circle. We iterate
        // by column (zi) from far to near, which gives correct depth ordering
        // without an explicit sort — far points (high zDist, low zi) are drawn
        // first and get painted over by near points.
        //
        // Per-column values (depthAlpha, radScale) are read from the pre-computed
        // buffers to avoid redundant division/clamping in the inner loop.
        //
        // Each point's pixel radius = worldSize × (200 / zDist), clamped to
        // 0.3–4.0 px to prevent invisibly small or excessively large dots.
        // ═════════════════════════════════════════════════════════════════════
        for (zi in 0 until GRID) {
            val dAlpha = buf.depthAlpha[zi]  // fade with distance
            val rScale = buf.radScale[zi]    // perspective size scaling

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
