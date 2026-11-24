// The glue sandbox: connectors between two curves whose end slopes differ.
//
// A cubic with its two inner control points placed along the two end directions cannot have the
// wrong slope: the ends are exact by construction. Slopes are entered as fractions ("3/4",
// "-7/24", "2"), so every direction is a pair of whole numbers, and a handle given as a
// percentage is a fraction with denominator 100. The control points printed are exact fractions;
// the picture is drawn from them in floating point and says so.
//
// The quintic kind is G3: the connector matches the neighbours' curvature and the rate it
// changes at, at both ends. Its derivation is in `quinticControls` and proven in
// tests/js/glue.test.ts.

export type Frac = { n: number; d: number };
export type Point = { x: number; y: number };
export type Direction = { x: number; y: number };
export type UnitDirection = Direction & { exact: boolean };
export type Handle = number | Frac;

const gcd = (a: number, b: number): number => (b ? gcd(b, a % b) : Math.abs(a));

export function frac(n: number, d = 1): Frac | null {
  if (!Number.isFinite(n) || !Number.isFinite(d) || d === 0) return null;
  const sign = d < 0 ? -1 : 1;
  const g = gcd(Math.abs(n), Math.abs(d)) || 1;
  return { n: (sign * n) / g, d: Math.abs(d) / g };
}

export const fracText = (f: Frac | null): string => (!f ? "—" : f.d === 1 ? `${f.n}` : `${f.n}/${f.d}`);
export const fracValue = (f: Frac | null): number => (f ? f.n / f.d : NaN);

// "3/4" or "-7/24" or "2" -> a reduced fraction
export function parseSlope(text: string): Frac | null {
  const clean = String(text || "").trim().replace(/\s+/g, "");
  const match = /^([+-]?\d+)(?:\/([+-]?\d+))?$/.exec(clean);
  if (!match) return null;
  const n = Number(match[1]);
  const d = match[2] === undefined ? 1 : Number(match[2]);
  return d === 0 ? null : frac(n, d);
}

// a slope as a direction pair: slope = rise / run, so the direction is (run, rise)
export function direction(slope: Frac | null): Direction | null {
  if (!slope) return null;
  return { x: slope.d, y: slope.n };
}

// A direction pair normalised to unit length. When the pair is a p-triple (its hypotenuse is
// whole — 4:3 gives 5, 24:-7 gives 25) the unit direction is rational and exact; otherwise it
// is divided by the squared length and is a float, which the sandbox says.
export function unitDirection(slope: Frac | null): UnitDirection | null {
  if (!slope) return null;
  const x = slope.d;
  const y = slope.n;
  const l2 = x * x + y * y;
  const root = Math.round(Math.sqrt(l2));
  if (root * root === l2 && root > 0) return { x: x / root, y: y / root, exact: true };
  return { x: x / l2, y: y / l2, exact: false };
}

const sizeOf = (value: Handle): number =>
  (typeof value === "object" ? fracValue(value) : Number(value));

// exact control points for a G1 cubic join. p0 and p3 are points, h0 and h1 are handle
// lengths as fractions of the chord; returns fractions.
export function controls(
  p0: Point, p3: Point, slope0: Frac | null, slope1: Frac | null, h0: Handle, h1: Handle,
): Point[] | null {
  const d0 = direction(slope0);
  const d1 = direction(slope1);
  if (!d0 || !d1) return null;
  const chord = Math.hypot(p3.x - p0.x, p3.y - p0.y);
  const H0 = chord * sizeOf(h0);
  const H1 = chord * sizeOf(h1);
  const u0 = unitDirection(slope0);
  const u1 = unitDirection(slope1);
  if (!u0 || !u1) return null;
  return [
    p0,
    { x: p0.x + H0 * u0.x, y: p0.y + H0 * u0.y },
    { x: p3.x - H1 * u1.x, y: p3.y - H1 * u1.y },
    p3,
  ];
}

// the derivative of a cubic at t (Bezier), for checking the ends
export function derivative(p: Point[], t: number): Point {
  const mt = 1 - t;
  return {
    x: 3 * mt * mt * (p[1].x - p[0].x) + 6 * mt * t * (p[2].x - p[1].x) + 3 * t * t * (p[3].x - p[2].x),
    y: 3 * mt * mt * (p[1].y - p[0].y) + 6 * mt * t * (p[2].y - p[1].y) + 3 * t * t * (p[3].y - p[2].y),
  };
}

// the slope the drawn curve actually leaves with, as a float ratio
export const slopeAt = (p: Point[], t: number): number => {
  const d = derivative(p, t);
  return Math.abs(d.x) < 1e-12 ? Infinity : d.y / d.x;
};

// A rational Bézier: the same control points with weights. A negative or very large weight
// bends the curve and can make it loop, which is the "rational loop" the operator asked for.
export function rationalPoints(p: Point[], w: number[], n = 240): Point[] {
  const out: Point[] = [];
  for (let i = 0; i <= n; i += 1) {
    const t = i / n;
    const mt = 1 - t;
    const b = [mt ** 3, 3 * mt ** 2 * t, 3 * mt * t ** 2, t ** 3];
    const den = b[0] * w[0] + b[1] * w[1] + b[2] * w[2] + b[3] * w[3];
    if (Math.abs(den) < 1e-12) continue;
    out.push({
      x: (b[0] * w[0] * p[0].x + b[1] * w[1] * p[1].x + b[2] * w[2] * p[2].x + b[3] * w[3] * p[3].x) / den,
      y: (b[0] * w[0] * p[0].y + b[1] * w[1] * p[1].y + b[2] * w[2] * p[2].y + b[3] * w[3] * p[3].y) / den,
    });
  }
  return out;
}

export function cubicPoints(p: Point[], n = 240): Point[] {
  const out: Point[] = [];
  for (let i = 0; i <= n; i += 1) {
    const t = i / n;
    const mt = 1 - t;
    out.push({
      x: mt ** 3 * p[0].x + 3 * mt ** 2 * t * p[1].x + 3 * mt * t ** 2 * p[2].x + t ** 3 * p[3].x,
      y: mt ** 3 * p[0].y + 3 * mt ** 2 * t * p[1].y + 3 * mt * t ** 2 * p[2].y + t ** 3 * p[3].y,
    });
  }
  return out;
}

export function quinticPoints(p: Point[], n = 240): Point[] {
  const out: Point[] = [];
  for (let i = 0; i <= n; i += 1) {
    const t = i / n;
    const mt = 1 - t;
    const b = [mt ** 5, 5 * mt ** 4 * t, 10 * mt ** 3 * t ** 2, 10 * mt ** 2 * t ** 3,
      5 * mt * t ** 4, t ** 5];
    out.push({
      x: b.reduce((sum, weight, index) => sum + weight * p[index].x, 0),
      y: b.reduce((sum, weight, index) => sum + weight * p[index].y, 0),
    });
  }
  return out;
}

// where the drawn curve crosses itself, if it loops
export function crossings(points: Point[]): Point[] {
  const hits: Point[] = [];
  const cross = (a: Point, b: Point, c: Point, d: Point): Point | null => {
    const rx = b.x - a.x, ry = b.y - a.y;
    const qx = d.x - c.x, qy = d.y - c.y;
    const den = rx * qy - ry * qx;
    if (Math.abs(den) < 1e-12) return null;
    const t = ((c.x - a.x) * qy - (c.y - a.y) * qx) / den;
    const u = ((c.x - a.x) * ry - (c.y - a.y) * rx) / den;
    if (t <= 1e-6 || t >= 1 - 1e-6 || u <= 1e-6 || u >= 1 - 1e-6) return null;
    return { x: a.x + t * rx, y: a.y + t * ry };
  };
  for (let i = 0; i < points.length - 1; i += 2) {
    for (let j = i + 3; j < points.length - 1; j += 2) {
      const hit = cross(points[i], points[i + 1], points[j], points[j + 1]);
      if (hit) hits.push(hit);
    }
  }
  return hits;
}

// ---- the quintic G3 connector -------------------------------------------------------------

const cross2 = (a: Point, b: Point): number => a.x * b.y - a.y * b.x;
const dot2 = (a: Point, b: Point): number => a.x * b.x + a.y * b.y;
const length2 = (a: Point): number => Math.hypot(a.x, a.y);

// Gaussian elimination with partial pivoting; four unknowns, a stated case is well conditioned.
function solve4(a: number[][], rhs: number[]): number[] {
  const n = rhs.length;
  const m = a.map((row, i) => [...row, rhs[i]]);
  for (let c = 0; c < n; c += 1) {
    let p = c;
    for (let r = c + 1; r < n; r += 1) if (Math.abs(m[r][c]) > Math.abs(m[p][c])) p = r;
    [m[c], m[p]] = [m[p], m[c]];
    const d = m[c][c];
    if (Math.abs(d) < 1e-13) throw new Error("the quintic solve is singular");
    for (let k = c; k <= n; k += 1) m[c][k] /= d;
    for (let r = 0; r < n; r += 1) {
      if (r === c) continue;
      const f = m[r][c];
      for (let k = c; k <= n; k += 1) m[r][k] -= f * m[c][k];
    }
  }
  return m.map((row) => row[n]);
}

export type QuinticOptions = {
  h0?: Handle;
  h1?: Handle;
  kappa0?: number;
  kappa1?: number;
  dkappa0?: number;
  dkappa1?: number;
};

// A quintic has six control points (twelve numbers). P0 and P5 are the ends; P1 and P4 lie on
// the typed directions at distances a and b (the handles, the two free parameters). P2 and P3
// are solved so the curve matches the neighbours' signed curvature and its rate at both ends:
//
//   E0: u × (P2 − P0) = (5/4) κ0 a²
//   E1: v × (P3 − P5) = (5/4) κ1 b²
//   R0: (12/25a³) u × (P3 − 3P2 + 2P0) − (12/5a²) κ0 [u·(P2 − P0) − 2a] = dκ0
//   R1: −(12/25b³) v × (P2 − 3P3 + 2P5) − (12/5b²) κ1 [v·(P3 − P5) + 2b] = dκ1
//
// The four equations are linear in P2 and P3 once a and b are chosen, so one 4×4 solve finishes
// the connector. The test prints all six end conditions at 1e-9 for a stated case.
export function quinticControls(
  p0: Point, p5: Point, slope0: Frac | null, slope1: Frac | null,
  { h0 = 0.4, h1 = 0.4, kappa0 = 0, kappa1 = 0, dkappa0 = 0, dkappa1 = 0 }: QuinticOptions = {},
): Point[] | null {
  const u = unitDirection(slope0);
  const v = unitDirection(slope1);
  if (!u || !v) return null;
  const chord = Math.hypot(p5.x - p0.x, p5.y - p0.y) || 1;
  const a = chord * sizeOf(h0);
  const b = chord * sizeOf(h1);
  if (a < 1e-9 || b < 1e-9) return null;
  const a2 = a * a, a3 = a2 * a, b2 = b * b, b3 = b2 * b;
  const A: number[][] = [];
  const rhs: number[] = [];

  // E0: cross(u, P2 - P0) = (5/4) k0 a^2
  A.push([-u.y, u.x, 0, 0]);
  rhs.push((5 / 4) * kappa0 * a2 - (u.y * p0.x - u.x * p0.y));
  // E1: cross(v, P3 - P5) = (5/4) k1 b^2
  A.push([0, 0, -v.y, v.x]);
  rhs.push((5 / 4) * kappa1 * b2 - (v.y * p5.x - v.x * p5.y));
  // R0
  A.push([
    (12 / (25 * a3)) * 3 * u.y - (12 / (5 * a2)) * kappa0 * u.x,
    -(12 / (25 * a3)) * 3 * u.x - (12 / (5 * a2)) * kappa0 * u.y,
    -(12 / (25 * a3)) * u.y,
    (12 / (25 * a3)) * u.x,
  ]);
  rhs.push(dkappa0 - (12 / (25 * a3)) * 2 * cross2(u, p0)
    - (12 / (5 * a2)) * kappa0 * (dot2(u, p0) + 2 * a));
  // R1
  A.push([
    (12 / (25 * b3)) * v.y,
    -(12 / (25 * b3)) * v.x,
    -(12 / (25 * b3)) * 3 * v.y - (12 / (5 * b2)) * kappa1 * v.x,
    (12 / (25 * b3)) * 3 * v.x - (12 / (5 * b2)) * kappa1 * v.y,
  ]);
  rhs.push(dkappa1 + (12 / (25 * b3)) * 2 * cross2(v, p5)
    - (12 / (5 * b2)) * kappa1 * (dot2(v, p5) - 2 * b));

  const [x2, y2, x3, y3] = (() => {
    try {
      return solve4(A, rhs);
    } catch (error) {
      // A straight glue (zero curvature and rate at both ends, the ends collinear with the
      // direction) is underdetermined: every collinear control point gives κ = 0 and rate = 0.
      const flat = Math.abs(kappa0) < 1e-12 && Math.abs(kappa1) < 1e-12
        && Math.abs(dkappa0) < 1e-12 && Math.abs(dkappa1) < 1e-12;
      const collinear = Math.abs(u.x * (p5.y - p0.y) - u.y * (p5.x - p0.x)) < 1e-9;
      if (!flat || !collinear) throw error;
      return [p0.x + 2 * a * u.x, p0.y + 2 * a * u.y, p5.x - 2 * b * v.x, p5.y - 2 * b * v.y];
    }
  })();
  return [
    p0,
    { x: p0.x + a * u.x, y: p0.y + a * u.y },
    { x: x2, y: y2 },
    { x: x3, y: y3 },
    { x: p5.x - b * v.x, y: p5.y - b * v.y },
    p5,
  ];
}

export type EndCondition = { slope: number; kappa: number; rate: number };

// The six end conditions of a quintic: tangent slope, signed curvature and curvature rate at
// each end. The page prints them, the test compares them with the targets.
export function endConditions(p: Point[]): { start: EndCondition; end: EndCondition } {
  const at = (start: boolean): EndCondition => {
    const D1 = start
      ? { x: 5 * (p[1].x - p[0].x), y: 5 * (p[1].y - p[0].y) }
      : { x: 5 * (p[5].x - p[4].x), y: 5 * (p[5].y - p[4].y) };
    const D2 = start
      ? { x: 20 * (p[2].x - 2 * p[1].x + p[0].x), y: 20 * (p[2].y - 2 * p[1].y + p[0].y) }
      : { x: 20 * (p[5].x - 2 * p[4].x + p[3].x), y: 20 * (p[5].y - 2 * p[4].y + p[3].y) };
    const D3 = start
      ? { x: 60 * (p[3].x - 3 * p[2].x + 3 * p[1].x - p[0].x),
          y: 60 * (p[3].y - 3 * p[2].y + 3 * p[1].y - p[0].y) }
      : { x: 60 * (p[5].x - 3 * p[4].x + 3 * p[3].x - p[2].x),
          y: 60 * (p[5].y - 3 * p[4].y + 3 * p[3].y - p[2].y) };
    const l1 = length2(D1);
    const kappa = cross2(D1, D2) / l1 ** 3;
    const rate = cross2(D1, D3) / l1 ** 4 - (3 * cross2(D1, D2) * dot2(D1, D2)) / l1 ** 6;
    return { slope: D1.x === 0 ? Infinity : D1.y / D1.x, kappa, rate };
  };
  return { start: at(true), end: at(false) };
}
