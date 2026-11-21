// Cubic Bezier fitting for a clothoid span, and the error that the fit costs.
//
// TypeScript port of `curve_lab/bezier.py` — the house's parabola rule: a cubic
// spanning one arc-length interval puts its handle along the end tangent with
// length |chord| / (3 cos^2(theta/2)), where theta is the angle between that
// tangent and the chord. Subdivision is adaptive and measured: a span is cut at
// its arclength midpoint while its measured deviation exceeds the tolerance.
//
// The point and tangent functions are passed in, so the same fitter serves the
// spine and each parallel rail — and the parity harness, which supplies a curve
// with a known geometry.

export type Point = [number, number];
export type PointFn = (s: number) => Point;
export type TangentFn = (s: number) => number;

export interface Span {
  s0: number; s1: number;
  p0: Point; c1: Point; c2: Point; p3: Point;
  clamped: boolean;
}

const GOLDEN = 0.6180339887498949;

/** One cubic from s0 to s1, on the parabola rule. The arm is bounded at
 * `max_arm` times the chord; a span that hits the bound is flagged. */
export function fitSpan(s0: number, s1: number, point: PointFn, tangent: TangentFn,
                        maxArm = 4.0): Span {
  const p0 = point(s0);
  const p3 = point(s1);
  const cx = p3[0] - p0[0], cy = p3[1] - p0[1];
  const chord = Math.hypot(cx, cy);
  if (chord < 1e-12) {
    return { s0, s1, p0, c1: p0, c2: p3, p3, clamped: false };
  }
  const limit = maxArm * chord;
  let clamped = false;
  const arm = (s: number): number => {
    const ux = Math.cos(tangent(s)), uy = Math.sin(tangent(s));
    let cos = (cx * ux + cy * uy) / chord;
    cos = Math.max(-1.0, Math.min(1.0, cos));
    const half = (1.0 + cos) / 2.0;
    const want = half > 1e-9 ? chord / (3.0 * half) : limit;
    if (want > limit) { clamped = true; return limit; }
    return want;
  };
  const a0 = arm(s0), a1 = arm(s1);
  const t0 = tangent(s0), t1 = tangent(s1);
  return {
    s0, s1, p0, p3,
    c1: [p0[0] + a0 * Math.cos(t0), p0[1] + a0 * Math.sin(t0)],
    c2: [p3[0] - a1 * Math.cos(t1), p3[1] - a1 * Math.sin(t1)],
    clamped,
  };
}

export function cubicAt(span: Span, t: number): Point {
  const u = 1.0 - t;
  const a = u * u * u, b = 3 * u * u * t, c = 3 * u * t * t, d = t * t * t;
  const [x0, y0] = span.p0, [x1, y1] = span.c1;
  const [x2, y2] = span.c2, [x3, y3] = span.p3;
  return [a * x0 + b * x1 + c * x2 + d * x3, a * y0 + b * y1 + c * y2 + d * y3];
}

/** Distance from a point to the curve over [s0, s1]: a coarse scan only
 * brackets the nearest arclength, and a golden-section search closes on it —
 * a sampled minimum is not a distance. */
export function distanceToCurve(x: number, y: number, s0: number, s1: number,
                                point: PointFn, coarse = 9, refine = 40): number {
  const span = s1 - s0;
  let bestS = s0, bestD = Infinity;
  for (let i = 0; i < coarse; i += 1) {
    const s = s0 + span * i / (coarse - 1);
    const [px, py] = point(s);
    const d = (x - px) ** 2 + (y - py) ** 2;
    if (d < bestD) { bestS = s; bestD = d; }
  }
  const step = span / (coarse - 1);
  let lo = Math.max(s0, bestS - step), hi = Math.min(s1, bestS + step);
  const g = GOLDEN;
  let m1 = hi - g * (hi - lo), m2 = lo + g * (hi - lo);
  let [px1, py1] = point(m1);
  let d1 = (x - px1) ** 2 + (y - py1) ** 2;
  let [px2, py2] = point(m2);
  let d2 = (x - px2) ** 2 + (y - py2) ** 2;
  for (let i = 0; i < refine; i += 1) {
    if (d1 < d2) {
      hi = m2; m2 = m1; d2 = d1;
      m1 = hi - g * (hi - lo);
      [px1, py1] = point(m1);
      d1 = (x - px1) ** 2 + (y - py1) ** 2;
    } else {
      lo = m1; m1 = m2; d1 = d2;
      m2 = lo + g * (hi - lo);
      [px2, py2] = point(m2);
      d2 = (x - px2) ** 2 + (y - py2) ** 2;
    }
  }
  return Math.sqrt(Math.min(d1, d2));
}

/** Worst distance from points on the cubic to the true curve under the span. */
export function spanError(span: Span, point: PointFn, samples = 17): number {
  const { s0, s1 } = span;
  let worst = 0.0;
  for (let i = 0; i < samples; i += 1) {
    const [x, y] = cubicAt(span, i / (samples - 1));
    worst = Math.max(worst, distanceToCurve(x, y, s0, s1, point));
  }
  return worst;
}

/** Adaptive fit of [s0, s1], redividing the worst span until it is under
 * tolerance. `split` is how many pieces a bad span is cut into. */
export function fitInterval(s0: number, s1: number, point: PointFn, tangent: TangentFn,
                            tol = 0.02, maxSpans = 64, split = 2): Span[] {
  if (split < 2) throw new Error(`split factor must be at least 2, got ${split}`);
  const spans: Span[] = [fitSpan(s0, s1, point, tangent)];
  const errors: number[] = [spanError(spans[0], point)];
  while (Math.max(...errors) > tol && spans.length < maxSpans) {
    const i = errors.indexOf(Math.max(...errors));
    const bad = spans.splice(i, 1)[0];
    errors.splice(i, 1);
    const pieces: Span[] = [];
    for (let k = 0; k <= split; k += 1) {
      const at = bad.s0 + (bad.s1 - bad.s0) * k / split;
      if (k > 0) {
        const previous = bad.s0 + (bad.s1 - bad.s0) * (k - 1) / split;
        pieces.push(fitSpan(previous, at, point, tangent));
      }
    }
    const kept = pieces.filter((p) => p.s1 > p.s0);
    if (!kept.length) break;
    spans.splice(i, 0, ...kept);
    errors.splice(i, 0, ...kept.map((p) => spanError(p, point)));
  }
  return spans;
}

/** Fit every segment of a chain, and report the numbers behind the drawing. */
export function fitChain(chain: { segments: Array<{ s_base: number; length: number }>;
                                 point: PointFn; tangent: (s: number) => number },
                         tol = 0.02, maxSpansPerSegment = 64, split = 2):
  { spans: Span[]; report: { spans: number; tol: number; split: number;
                             error_max: number; spans_per_segment: number[] } } {
  const spans: Span[] = [];
  const perSegment: number[] = [];
  for (const placed of chain.segments) {
    const s0 = placed.s_base, s1 = placed.s_base + placed.length;
    const tangent = (s: number): number => {
      // A boundary belongs to the next segment in the backend; step just
      // inside the segment so the fit never reads the next direction.
      let t = s;
      if (t >= s1) t = nextAfter(s1, s0);
      else if (t <= s0) t = nextAfter(s0, s1);
      return chain.tangent(t);
    };
    const fitted = fitInterval(s0, s1, chain.point, tangent,
                               tol, maxSpansPerSegment, split);
    spans.push(...fitted);
    perSegment.push(fitted.length);
  }
  const errors = spans.map((s) => spanError(s, chain.point));
  return {
    spans,
    report: {
      spans: spans.length, tol, split,
      error_max: errors.length ? Math.max(...errors) : 0.0,
      spans_per_segment: perSegment,
    },
  };
}

function nextAfter(from: number, toward: number): number {
  if (from === toward) return from;
  const buf = new ArrayBuffer(8);
  const view = new Float64Array(buf);
  const bits = new BigUint64Array(buf);
  view[0] = from;
  bits[0] += from < toward ? 1n : -1n;
  return view[0];
}

/** Spacing between the fitted path and the true curve, over a whole chain. */
export function pathDeviation(spans: Span[], point: PointFn, samplesPerSpan = 9): number {
  let worst = 0.0;
  for (const span of spans) {
    const { s0, s1 } = span;
    for (let i = 0; i < samplesPerSpan; i += 1) {
      const [x, y] = cubicAt(span, i / (samplesPerSpan - 1));
      worst = Math.max(worst, distanceToCurve(x, y, s0, s1, point));
    }
  }
  return worst;
}
