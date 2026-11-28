/**
 * The quintic sandbox's maths: reduce a drawn stroke to six points, and give the
 * curve a width that thins at the ends and swells in the middle.
 *
 * The geometry of a quintic span (evaluation, sub-curves, the cubic chain, the
 * end frames, self-crossings) lives in `scripts/lib/quintic-geometry.ts` and is
 * re-exported here unchanged — one implementation for the sheet, the Inkscape
 * extension's fixture and this page. What is added is the part the page needs:
 *
 *   - reducing a polyline stroke to six points (even points, or a least-squares
 *     fit with parameter correction),
 *   - the fullness blend (the same formula the Inkscape dialog uses),
 *   - a width profile and the modulated offset outline: thin at the ends,
 *     thicker in the middle, or the reverse.
 *
 * Coordinates are **y up**, like the shared record; the page flips once at the
 * point of drawing (`toPage`).
 */

import { quinticAt, cubicChain, chainError, type Point } from "./quintic-geometry.ts";

export type { Point };
export { quinticAt, cubicChain, chainError };

export const DEGREE = 5;
export const COUNT = 6;
const BINOMIAL = [1, 5, 10, 10, 5, 1];

/** A width profile along t: `ends` at t = 0 and 1, `middle` at `peak`. */
export type WidthProfile = {
  ends: number;
  middle: number;
  peak: number; // 0..1, where the swell sits
  power: number; // 1 is a soft swell, 4 is a pointed leaf
};

export const DEFAULT_PROFILE: WidthProfile = { ends: 1, middle: 14, peak: 0.5, power: 1 };

/** One y flip, here: the model is y up, an SVG page is y down. */
export function toPage(p: Point): Point {
  return [p[0], -p[1]];
}

// ---------------------------------------------------------------------------
// the quintic and its derivatives
// ---------------------------------------------------------------------------

export function derivative(points: Point[], t: number): Point {
  const v = 1 - t;
  let x = 0;
  let y = 0;
  for (let i = 0; i < DEGREE; i += 1) {
    const w = DEGREE * [1, 4, 6, 4, 1][i] * v ** (4 - i) * t ** i;
    x += w * (points[i + 1][0] - points[i][0]);
    y += w * (points[i + 1][1] - points[i][1]);
  }
  return [x, y];
}

export function secondDerivative(points: Point[], t: number): Point {
  const v = 1 - t;
  let x = 0;
  let y = 0;
  for (let i = 0; i < DEGREE - 1; i += 1) {
    const w = DEGREE * (DEGREE - 1) * [1, 3, 3, 1][i] * v ** (3 - i) * t ** i;
    x += w * (points[i + 2][0] - 2 * points[i + 1][0] + points[i][0]);
    y += w * (points[i + 2][1] - 2 * points[i + 1][1] + points[i][1]);
  }
  return [x, y];
}

/** Signed curvature, 1/unit; positive turns left along increasing t. */
export function curvature(points: Point[], t: number): number {
  const d = derivative(points, t);
  const dd = secondDerivative(points, t);
  const speed = Math.hypot(d[0], d[1]);
  if (speed === 0) return 0;
  return (d[0] * dd[1] - d[1] * dd[0]) / speed ** 3;
}

/** The unit normal, pointing left of travel. */
export function normal(points: Point[], t: number): Point {
  const d = derivative(points, t);
  const speed = Math.hypot(d[0], d[1]) || 1;
  return [-d[1] / speed, d[0] / speed];
}

/** Distance from a point to the quintic, in px. Coarse scan, then golden section. */
export function distanceToQuintic(p: Point, points: Point[], coarse = 64, refine = 24): number {
  const sq = (u: number) => {
    const q = quinticAt(points, u);
    return (q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2;
  };
  let best = sq(0);
  let bestU = 0;
  for (let k = 1; k <= coarse; k += 1) {
    const value = sq(k / coarse);
    if (value < best) {
      best = value;
      bestU = k / coarse;
    }
  }
  let lo = Math.max(0, bestU - 1 / coarse);
  let hi = Math.min(1, bestU + 1 / coarse);
  const phi = 0.6180339887498949;
  for (let i = 0; i < refine; i += 1) {
    const a = hi - (hi - lo) * phi;
    const b = lo + (hi - lo) * phi;
    if (sq(a) < sq(b)) hi = b;
    else lo = a;
  }
  const q = quinticAt(points, (lo + hi) / 2);
  return Math.hypot(q[0] - p[0], q[1] - p[1]);
}

// ---------------------------------------------------------------------------
// reducing a drawn stroke to six points
// ---------------------------------------------------------------------------

/** Points at even arc length along a drawn polyline, ends included. */
export function resamplePolyline(stroke: Point[], count: number): Point[] {
  if (stroke.length < 2) return [stroke[0] ?? [0, 0]];
  const lengths: number[] = [0];
  for (let i = 1; i < stroke.length; i += 1) {
    lengths.push(lengths[i - 1] + Math.hypot(stroke[i][0] - stroke[i - 1][0], stroke[i][1] - stroke[i - 1][1]));
  }
  const total = lengths[lengths.length - 1];
  if (total === 0) return [stroke[0]];
  const out: Point[] = [];
  let cursor = 0;
  for (let k = 0; k <= count; k += 1) {
    const target = (total * k) / count;
    while (cursor < lengths.length - 2 && lengths[cursor + 1] < target) cursor += 1;
    const span = lengths[cursor + 1] - lengths[cursor] || 1;
    const f = Math.min(1, Math.max(0, (target - lengths[cursor]) / span));
    out.push([
      stroke[cursor][0] + (stroke[cursor + 1][0] - stroke[cursor][0]) * f,
      stroke[cursor][1] + (stroke[cursor + 1][1] - stroke[cursor][1]) * f,
    ]);
  }
  return out;
}

/** Six points, evenly spaced through a chunk that is already even by arc length. */
export function sixPointsEven(chunk: Point[]): Point[] {
  const step = Math.floor((chunk.length - 1) / DEGREE) || 1;
  const out: Point[] = [];
  for (let i = 0; i < DEGREE; i += 1) out.push(chunk[Math.min(chunk.length - 1, i * step)]);
  out.push(chunk[chunk.length - 1]);
  return out;
}

/** Solve M P = Q for the six control points P, exactly through six samples. */
export function solveThroughSamples(samples: Point[]): Point[] {
  const n = COUNT;
  const m: number[][] = [];
  for (let k = 0; k < n; k += 1) {
    const t = k / DEGREE;
    const row: number[] = [];
    for (let i = 0; i < n; i += 1) row.push(BINOMIAL[i] * (1 - t) ** (DEGREE - i) * t ** i);
    row.push(samples[k][0], samples[k][1]);
    m.push(row);
  }
  for (let col = 0; col < n; col += 1) {
    let pivot = col;
    for (let r = col + 1; r < n; r += 1) if (Math.abs(m[r][col]) > Math.abs(m[pivot][col])) pivot = r;
    [m[col], m[pivot]] = [m[pivot], m[col]];
    const pv = m[col][col];
    if (Math.abs(pv) < 1e-12) {
      // coincident samples have no unique quintic: say so instead of returning
      // a curve that pretends to pass through them
      throw new Error("the six points do not define a unique quintic (they are coincident)");
    }
    m[col] = m[col].map((v) => v / pv);
    for (let r = 0; r < n; r += 1) {
      if (r === col) continue;
      const f = m[r][col];
      if (f) m[r] = m[r].map((v, j) => v - f * m[col][j]);
    }
  }
  return m.map((row) => [row[n], row[n + 1]] as Point);
}

/**
 * Least squares with Piegl & Tiller's parameter correction: the samples move
 * onto their nearest points, then the fit repeats. Ends pinned.
 */
export function fitLeastSquares(points: Point[], passes = 3): Point[] {
  const m = points.length;
  let ts = Array.from({ length: m }, (_, i) => i / (m - 1));
  const fit = (): Point[] => {
    const basis = ts.map((t) => [1, 2, 3, 4].map((i) => BINOMIAL[i] * (1 - t) ** (DEGREE - i) * t ** i));
    const p0 = points[0];
    const p5 = points[m - 1];
    const normal4: number[][] = [];
    for (let i = 0; i < 4; i += 1) {
      normal4.push([]);
      for (let j = 0; j < 4; j += 1) {
        let sum = 0;
        for (let k = 0; k < m; k += 1) sum += basis[k][i] * basis[k][j];
        normal4[i].push(sum);
      }
    }
    const axis = (a: 0 | 1): number[] => {
      const rhs: number[] = [];
      for (let i = 0; i < 4; i += 1) {
        let sum = 0;
        for (let k = 0; k < m; k += 1) {
          const t = ts[k];
          const known = (1 - t) ** DEGREE * p0[a] + t ** DEGREE * p5[a];
          sum += basis[k][i] * (points[k][a] - known);
        }
        rhs.push(sum);
      }
      const mm = normal4.map((row, i) => [...row, rhs[i]]);
      for (let c = 0; c < 4; c += 1) {
        let pivot = c;
        for (let r = c + 1; r < 4; r += 1) if (Math.abs(mm[r][c]) > Math.abs(mm[pivot][c])) pivot = r;
        [mm[c], mm[pivot]] = [mm[pivot], mm[c]];
        const pv = mm[c][c] || 1e-12;
        mm[c] = mm[c].map((v) => v / pv);
        for (let r = 0; r < 4; r += 1) {
          if (r === c) continue;
          const f = mm[r][c];
          if (f) mm[r] = mm[r].map((v, j) => v - f * mm[c][j]);
        }
      }
      return mm.map((row) => row[4]);
    };
    const x = axis(0);
    const y = axis(1);
    return [p0, ...x.map((v, i) => [v, y[i]] as Point), p5];
  };
  let control = fit();
  for (let pass = 0; pass < passes; pass += 1) {
    for (let k = 1; k < m - 1; k += 1) {
      const c = quinticAt(control, ts[k]);
      const d = derivative(control, ts[k]);
      const dd = secondDerivative(control, ts[k]);
      const delta: Point = [points[k][0] - c[0], points[k][1] - c[1]];
      const den = d[0] * d[0] + d[1] * d[1] + delta[0] * dd[0] + delta[1] * dd[1];
      if (Math.abs(den) < 1e-12) continue;
      const step = (delta[0] * d[0] + delta[1] * d[1]) / den;
      ts[k] = Math.min(ts[k + 1] - 1e-9, Math.max(ts[k - 1] + 1e-9, ts[k] + step));
    }
    control = fit();
  }
  return control;
}

const chord = (p0: Point, p5: Point, i: number): Point => [
  (1 - i / DEGREE) * p0[0] + (i / DEGREE) * p5[0],
  (1 - i / DEGREE) * p0[1] + (i / DEGREE) * p5[1],
];

/** The extension's one slider: P_i = (1 - α) L_i + α G_i, ends fixed. */
export function blendFullness(guide: Point[], alpha: number): Point[] {
  const a = Math.min(1, Math.max(0, alpha));
  const p0 = guide[0];
  const p5 = guide[DEGREE];
  return guide.map((g, i) => {
    if (i === 0 || i === DEGREE) return g;
    const l = chord(p0, p5, i);
    return [l[0] + (g[0] - l[0]) * a, l[1] + (g[1] - l[1]) * a] as Point;
  });
}

export type ReduceOptions = {
  mode: "even" | "lsq";
  spans: number;
  fullness: number;
  tolerance: number;
  perSpan?: number;
};

export type ReducedSpan = {
  control: Point[];
  cubics: number;
  chainMiss: number;
  strokeMiss: number;
};

/** Reduce a stroke to `spans` quintics and say how far each is from the stroke. */
export function reduceStroke(stroke: Point[], options: ReduceOptions): ReducedSpan[] {
  const spans = Math.max(1, Math.floor(options.spans));
  const perSpan = options.perSpan ?? 48;
  const samples = resamplePolyline(stroke, perSpan * spans);
  const out: ReducedSpan[] = [];
  for (let s = 0; s < spans; s += 1) {
    const start = s * perSpan;
    const chunk = samples.slice(start, start + perSpan + 1);
    if (chunk.length < COUNT) continue;
    const guide = options.mode === "lsq" ? fitLeastSquares(chunk) : solveThroughSamples(sixPointsEven(chunk));
    const control = blendFullness(guide, options.fullness);
    let cubics = 2;
    while (cubics < 32 && chainError(control, cubics) > options.tolerance) cubics *= 2;
    out.push({
      control,
      cubics,
      chainMiss: chainError(control, cubics),
      strokeMiss: Math.max(...chunk.map((p) => distanceToQuintic(p, control))),
    });
  }
  return out;
}

// ---------------------------------------------------------------------------
// the modulated offset: thin at the ends, thicker in the middle
// ---------------------------------------------------------------------------

/** How wide the stroke is at t. Zero-ish at both ends, `middle` at `peak`. */
export function widthAt(t: number, profile: WidthProfile): number {
  const clamped = Math.min(1, Math.max(0, t));
  const peak = Math.min(0.95, Math.max(0.05, profile.peak));
  const s = clamped <= peak ? clamped / peak : (1 - clamped) / (1 - peak);
  const bump = Math.pow(Math.sin((Math.PI / 2) * s), profile.power);
  return profile.ends + (profile.middle - profile.ends) * bump;
}

export type Outline = { left: Point[]; right: Point[]; widest: number; narrowest: number };

/**
 * The two sides of a variable-width stroke along the quintic, sampled.
 *
 * Each side is the curve pushed along its own normal by the width at that t.
 * Where the width changes quickly the two sides can cross; `crossings` in the
 * page reports that rather than hiding it — a width profile cannot be widened
 * past the curvature without folding.
 */
export function outline(points: Point[], profile: WidthProfile, samples = 120): Outline {
  const left: Point[] = [];
  const right: Point[] = [];
  let widest = 0;
  let narrowest = Infinity;
  for (let k = 0; k <= samples; k += 1) {
    const t = k / samples;
    const p = quinticAt(points, t);
    const n = normal(points, t);
    const w = widthAt(t, profile);
    widest = Math.max(widest, w);
    narrowest = Math.min(narrowest, w);
    left.push([p[0] + n[0] * w, p[1] + n[1] * w]);
    right.push([p[0] - n[0] * w, p[1] - n[1] * w]);
  }
  return { left, right, widest, narrowest: Number.isFinite(narrowest) ? narrowest : 0 };
}

/** Two constant-width rails, for comparison with the swell. */
export function rails(points: Point[], width: number, samples = 120): Outline {
  return outline(points, { ends: width, middle: width, peak: 0.5, power: 1 }, samples);
}

/** How many times a closed outline crosses itself: 0 is a clean stroke. */
export function outlineCrossings(sides: Outline): number {
  const poly = [...sides.left, ...sides.right.slice().reverse()];
  let count = 0;
  const orient = (a: Point, b: Point, c: Point) =>
    Math.sign((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]));
  for (let i = 0; i < poly.length - 1; i += 1) {
    for (let j = i + 2; j < poly.length - 1; j += 1) {
      if (i === 0 && j === poly.length - 2) continue;
      if (poly[i] === poly[i + 1] || poly[j] === poly[j + 1]) continue;
      const [a, b, c, d] = [poly[i], poly[i + 1], poly[j], poly[j + 1]];
      if (orient(a, b, c) !== orient(a, b, d) && orient(c, d, a) !== orient(c, d, b)) count += 1;
    }
  }
  return count;
}

/**
 * SVG path data through a sampled polyline, as a cubic Bezier chain
 * (Catmull-Rom tangents) — the house rule: a smooth curve, never a zigzag.
 */
export function catmullRomPath(points: Point[], plot: (p: Point) => string): string {
  if (points.length < 2) return "";
  const parts = [`M ${plot(points[0])}`];
  for (let i = 0; i < points.length - 1; i += 1) {
    const p0 = points[i - 1] ?? points[i];
    const p1 = points[i];
    const p2 = points[i + 1];
    const p3 = points[i + 2] ?? p2;
    const c1: Point = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6];
    const c2: Point = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6];
    parts.push(`C ${plot(c1)} ${plot(c2)} ${plot(p2)}`);
  }
  return parts.join(" ");
}

/** The closed outline of the variable-width stroke: butt caps at both ends. */
export function outlinePath(sides: Outline, plot: (p: Point) => string): string {
  const forward = catmullRomPath(sides.left, plot);
  const backward = catmullRomPath(sides.right.slice().reverse(), plot);
  const startRight = sides.right[sides.right.length - 1];
  return `${forward} L ${plot(startRight)} ${backward.replace(/^M [^C]*/, "")} Z`;
}
