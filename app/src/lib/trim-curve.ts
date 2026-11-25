// Cutting a curve's legs off at rational fractions of its parameter.
//
// The operator, 2026-11-24: "cutting the legs off the curves using rational fractions of t".
// A stored curve is a list of stations in parameter order; t = 0 is the first station and t = 1
// the last (for a record with branches, each branch has its own 0 … 1, so the same cut applies to
// every branch). The cut is given as two fractions, t0 and t1, typed as p/q; the stations between
// them are kept, the legs outside are dropped, and the two cut points are placed exactly at the
// fractions by interpolating the one segment they fall on.
//
// Nothing here invents a curve: the kept stations are the record's own, and the two new endpoints
// lie on the segment between stations, which the record already says is approximate there.

export type Point = [number, number];

export interface Fraction {
  p: number;
  q: number;
  value: number;
  text: string;
}

export interface Range {
  from: Fraction;
  to: Fraction;
}

export interface TrimRun {
  kept: Point[];
  head: Point[];
  tail: Point[];
  keptStations: number;
  droppedStations: number;
}

export interface CutMark {
  point: Point;
  cut: "from" | "to";
}

export interface TrimmedRecord {
  branches: Point[][];
  path: Point[];
  head: Point[];
  tail: Point[];
  marks: CutMark[];
  keptStations: number;
  droppedStations: number;
}

export interface CurveLike {
  path?: Point[] | null;
  branches?: Point[][] | null;
}

export class FractionError extends Error {}

const integer = (text: unknown): boolean => /^\d+$/.test(String(text).trim());

// "1/4" or "3" — a decimal is refused on purpose: the cut is a rational fraction of t.
export function parseFraction(text: unknown): Fraction {
  const raw = String(text ?? "").trim();
  if (!raw) throw new FractionError("type a fraction, p/q");
  const parts = raw.split("/");
  if (parts.length > 2 || !parts.every(integer)) {
    throw new FractionError(`${raw} is not a whole-number fraction; write p/q, like 1/4`);
  }
  const p0 = Number(parts[0]);
  const q0 = parts.length === 2 ? Number(parts[1]) : 1;
  if (q0 === 0) throw new FractionError("the denominator cannot be zero");
  if (p0 > q0) throw new FractionError(`${raw} is past the end; t runs from 0 to 1`);
  // Lowest terms, always: 2/4 is shown and saved as 1/2, and 0 stays 0. The value is unchanged,
  // so the cut is the same; the record does not carry two names for one fraction.
  const gcd = (a: number, b: number): number => (b ? gcd(b, a % b) : a || 1);
  const divisor = gcd(p0, q0);
  const p = p0 / divisor;
  const q = q0 / divisor;
  return { p, q, value: p / q, text: q === 1 ? String(p) : `${p}/${q}` };
}

// The mirror pair of a fraction: p/q and (q − p)/q, ordered so the cut is a range. This is the
// operator's rule for a preset's other end (2026-11-24): "each time follow that algorithm of
// (num-denom)/denom for the end". 200/10001 pairs with 9801/10001; 3/5 pairs with 2/5.
export function mirrorPair(text: unknown): { from: string; to: string } {
  const fraction = parseFraction(text);
  const other = fraction.q - fraction.p;
  const low = Math.min(fraction.p, other);
  const high = Math.max(fraction.p, other);
  return {
    from: low === fraction.q ? "1" : `${low}/${fraction.q}`,
    to: high === fraction.q ? "1" : `${high}/${fraction.q}`,
  };
}

// The fractions a suggestion may pick: the thin p-triple cuts and the familiar sizes, all with a
// hypotenuse denominator, sorted by share. Kept short on purpose — a suggestion of 11/169 is
// technically nearest and useless to type or read.
export const TRIM_PAIRS: [number, number][] = [
  [1, 61], [1, 53], [1, 41], [1, 37], [2, 65], [2, 101], [1, 29], [1, 25], [2, 37],
  [1, 17], [3, 37], [1, 13], [3, 29], [8, 53], [5, 13], [2, 5], [3, 5], [200, 10001],
];

// The curvature at one station, scale-free (1 / length × the local step).
const curvatureAt = (a: Point, b: Point, c: Point): number => {
  const A = Math.hypot(b[0] - a[0], b[1] - a[1]);
  const B = Math.hypot(c[0] - b[0], c[1] - b[1]);
  const C = Math.hypot(c[0] - a[0], c[1] - a[1]);
  if (!A || !B || !C) return 0;
  const cross = Math.abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]));
  return (2 * cross) / (A * B * C);
};

const median = (values: number[]): number => {
  const sorted = [...values].sort((a, b) => a - b);
  return sorted.length ? sorted[Math.floor(sorted.length / 2)] : 0;
};

// A leg is the run at an end where the curvature stays roughly constant. The leg ends at the
// first station where the curvature moves away from that run's own value (a corner, a loop, a
// change of bend) — or where the run crosses another part of the curve. The operator's rule,
// 2026-11-24: "the curvature doesn't change much for the legs, then there is either a change in
// curvature or an intersection. from that point move back a little, and suggest a trim".
// The pull-back is 0.5 % of t, so the suggestion does not land on the noisy boundary.
const PULL_BACK = 0.005;
export function measureLegs(points: Point[]): { front: number; back: number; broke: { front: number; back: number } } | null {
  const n = points.length - 1;
  if (!Array.isArray(points) || n < 8) return null;
  const k: number[] = [];
  for (let i = 1; i < n; i += 1) k.push(curvatureAt(points[i - 1], points[i], points[i + 1]));
  const med = median(k);
  const walk = (from: number, step: number, base: number[], tol: number): number => {
    const startAt = from;
    for (let i = startAt; i >= 0 && i < k.length; i += step) {
      if (Math.abs(k[i] - median(base)) > tol) return i; // index into k
    }
    return -1;
  };
  const head = k.slice(0, Math.min(20, k.length));
  const tail = k.slice(Math.max(0, k.length - 20));
  const baseFront = median(head);
  const baseBack = median(tail);
  const tolFront = Math.max(0.3 * Math.max(baseFront, med), 0.05 * med);
  const tolBack = Math.max(0.3 * Math.max(baseBack, med), 0.05 * med);
  const frontAt = walk(0, 1, head, tolFront);
  const backAt = walk(k.length - 1, -1, tail, tolBack);
  // An end run longer than 45 % of the curve is the body itself (a closed loop has constant
  // curvature all the way round); it is not a leg and must not be cut. The cap keeps a "leg"
  // a leg: a trim always keeps the middle of the curve.
  const leg = (value: number): number => (value > 0.45 ? 0 : value);
  const front = leg(frontAt < 0 ? 0 : Math.max(0, (frontAt + 1) / n));
  const back = leg(backAt < 0 ? 0 : Math.max(0, (k.length - backAt) / n));
  return { front: Math.max(0, front - PULL_BACK), back: Math.max(0, back - PULL_BACK),
           broke: { front, back } };
}

// The smallest p-triple pair that clears the measured legs, after the pull-back.
export function recommendTrim(points: Point[]): { from: string; to: string; broke: { front: number; back: number } } | null {
  const measured = measureLegs(points);
  if (!measured) return null;
  const want = Math.max(measured.front, measured.back);
  if (want <= 0) return null;
  // the smallest share that clears the legs: the lattice is sorted by share, so the first is it
  const pair = TRIM_PAIRS.find(([p, q]) => p / q >= want);
  if (!pair) return null;
  return { from: `${pair[0]}/${pair[1]}`, to: `${pair[1] - pair[0]}/${pair[1]}`, broke: measured.broke };
}

export function parseRange(fromText: unknown, toText: unknown): Range {
  const from = parseFraction(fromText);
  const to = parseFraction(toText);
  if (!(from.value < to.value)) {
    throw new FractionError(`the front cut ${from.text} must come before the back cut ${to.text}`);
  }
  return { from, to };
}

// The segment a fraction falls on, and the exact point there.
function pointAt(points: Point[], fraction: number): Point {
  const last = points.length - 1;
  const x = fraction * last;
  const i = Math.min(last - 1, Math.floor(x));
  const f = x - i;
  const a = points[i];
  const b = points[i + 1];
  return [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f];
}

// One run: the kept stations with exact endpoints, and the two legs that were dropped.
export function trimRun(points: Point[], from: Fraction, to: Fraction): TrimRun | null {
  if (!Array.isArray(points) || points.length < 2) return null;
  const last = points.length - 1;
  const kept: Point[] = [];
  for (let i = 0; i <= last; i += 1) {
    const t = i / last;
    if (t > from.value && t < to.value) kept.push([points[i][0], points[i][1]]);
  }
  const start = pointAt(points, from.value);
  const end = pointAt(points, to.value);
  const head = points.slice(0, Math.floor(from.value * last) + 1).map((p): Point => [p[0], p[1]]);
  head.push(start);
  const tail: Point[] = [[...end] as Point];
  for (let i = Math.ceil(to.value * last); i <= last; i += 1) tail.push([points[i][0], points[i][1]]);
  return {
    kept: [start, ...kept, end],
    head, tail,
    keptStations: kept.length + 2,
    droppedStations: head.length + tail.length - 2,
  };
}

// The whole record: every branch is trimmed by the same fractions.
export function trimRecord(record: CurveLike, from: Fraction, to: Fraction): TrimmedRecord | null {
  const branches = Array.isArray(record.branches) && record.branches.length
    ? record.branches
    : record.path ? [record.path] : [];
  const runs = branches.map((branch) => trimRun(branch, from, to)).filter((run): run is TrimRun => Boolean(run));
  if (!runs.length) return null;
  const kept = runs.map((run) => run.kept);
  // Every branch has its own cut points, so every branch gets both marks: one red dot for the
  // front cut and one for the back cut, not a single pair for the first branch only.
  const marks: CutMark[] = runs.flatMap((run) => [
    { point: run.head[run.head.length - 1], cut: "from" as const },
    { point: run.tail[0], cut: "to" as const },
  ]);
  return {
    branches: kept,
    path: kept.flat(),
    head: runs.map((run) => run.head).flat(),
    tail: runs.map((run) => run.tail).flat(),
    marks,
    keptStations: runs.reduce((sum, run) => sum + run.keptStations, 0),
    droppedStations: runs.reduce((sum, run) => sum + run.droppedStations, 0),
  };
}

// The exact point at a fraction on the record's first run, for a readout.
export function pointAtFraction(record: CurveLike, fraction: Fraction): Point | null {
  const points = Array.isArray(record.branches) && record.branches.length
    ? record.branches[0] : record.path;
  return points ? pointAt(points, fraction.value) : null;
}
