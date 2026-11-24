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
