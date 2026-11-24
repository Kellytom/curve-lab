// The curve analysis: measure every stored curve so two can be compared as numbers.
//
// The TypeScript twin of `scripts/analyse_curves.py` (retired as this port landed). The exact
// numbers come from `measure.ts` (grid, bend, arc, chord, inflections, closest); a point path is
// sampled and says so. Crossings are crossing *pairs* from `crossings.ts`, kept only when a
// coarse and a fine pass agree (the same stability rule as `ph_crossings.stable_crossings`).

import { arcAndChord, metrics, type SpeedRow } from "./measure.ts";
import { crossingHits, type CrossingHit, type Point } from "./crossings.ts";

export type CurveRecord = {
  uid: string;
  name: string;
  family?: string | null;
  speedX?: number[];
  speedY?: number[];
  path?: Point[];
  step?: number;
  [key: string]: unknown;
};

export type Analysis = {
  uid: string;
  name: string;
  family: string | null | undefined;
  kind: "rows" | "path" | "error";
  method: "exact" | "sampled";
  degree: number;
  step: number;
  grid: string;
  bend: number;
  arc: number;
  chord: number;
  inflections: number;
  inflectionMax: number;
  closest: number;
  crossings: number;
  meetingPoints: number;
  bboxW: number;
  bboxH: number;
  area: number;
  maxCurvature: number | null;
  curvatureMedian: number;
  mirrorY: number;
  halfTurn: number;
  mirrorYX: number;
  error?: string;
};

const round = (value: number, places: number): number => {
  const factor = 10 ** places;
  return Math.round(value * factor) / factor;
};

export const SPINE_SAMPLES = 240;

// Horner, highest power first — the same arithmetic order as numpy's polyval, so the samples
// are bit-identical to the Python analyser's and the rounded areas agree.
const evaluate = (coefficients: number[], t: number): number => {
  let value = 0;
  for (let i = coefficients.length - 1; i >= 0; i -= 1) value = value * t + coefficients[i];
  return value;
};

// Sample the spine: the position is the integral of w squared, at the midpoint of each
// interval — the same rule the page uses, so a count here and a count on the page agree.
export function spinePoints(speedX: number[], speedY: number[], samples = SPINE_SAMPLES): Point[] {
  const size = Math.max(speedX.length, speedY.length);
  const u = [...speedX, ...Array(size - speedX.length).fill(0)];
  const v = [...speedY, ...Array(size - speedY.length).fill(0)];
  if (!u.some(Boolean) && !v.some(Boolean)) return [];
  let x = 0, y = 0;
  const points: Point[] = [[x, y]];
  for (let k = 0; k < samples; k += 1) {
    const t = (k + 0.5) / samples;
    const ux = evaluate(u, t);
    const vy = evaluate(v, t);
    x += (ux * ux - vy * vy) / samples;
    y += (2 * ux * vy) / samples;
    points.push([x, y]);
  }
  return points;
}

const pathPoints = (record: CurveRecord): Point[] => {
  const path = record.path;
  if (!Array.isArray(path) || path.length < 8) return [];
  return path.map(([x, y]) => [Number(x), Number(y)] as Point);
};

const bbox = (points: Point[]): [number, number, number, number] => {
  const xs = points.map((p) => p[0]);
  const ys = points.map((p) => p[1]);
  return [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)];
};

const polygonArea = (points: Point[]): number => {
  let area = 0;
  for (let i = 0; i < points.length - 1; i += 1) {
    const [x0, y0] = points[i];
    const [x1, y1] = points[i + 1];
    area += x0 * y1 - x1 * y0;
  }
  return Math.abs(area) / 2;
};

// Median curvature times the curve's size: scale-free, and robust. The maximum was useless on a
// nearly straight run with one tight turn; the median says how bent the curve is on average.
const curvatureMedian = (points: Point[]): number => {
  const values: number[] = [];
  for (let i = 1; i < points.length - 1; i += 1) {
    const [x0, y0] = points[i - 1];
    const [x1, y1] = points[i];
    const [x2, y2] = points[i + 1];
    const a = Math.hypot(x1 - x0, y1 - y0);
    const b = Math.hypot(x2 - x1, y2 - y1);
    const c = Math.hypot(x2 - x0, y2 - y0);
    if (a * b * c < 1e-9) continue;
    const cross = Math.abs((x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0));
    values.push((2 * cross) / (a * b * c));
  }
  values.sort((left, right) => left - right);
  return values.length ? values[Math.floor(values.length / 2)] : 0;
};

// Largest curvature times the size. A cusp is unbounded, so a value past 1e6 is reported as
// null rather than as a number nobody should compare.
const curvatureMax = (points: Point[]): number | null => {
  let peak = 0;
  for (let i = 1; i < points.length - 1; i += 1) {
    const [x0, y0] = points[i - 1];
    const [x1, y1] = points[i];
    const [x2, y2] = points[i + 1];
    const a = Math.hypot(x1 - x0, y1 - y0);
    const b = Math.hypot(x2 - x1, y2 - y1);
    const c = Math.hypot(x2 - x0, y2 - y0);
    if (a * b * c < 1e-9) continue;
    const cross = Math.abs((x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0));
    peak = Math.max(peak, (2 * cross) / (a * b * c));
  }
  return peak > 1e6 ? null : peak;
};

// How far the point set is from its own mirror, as a share of its size.
const mirrorGap = (points: Point[], axis: "y" | "yx" | "half"): number => {
  if (points.length < 8) return 1;
  const [x0, y0, x1, y1] = bbox(points);
  const size = Math.max(x1 - x0, y1 - y0) || 1;
  let mapped: Point[];
  if (axis === "y") {
    const c = (x0 + x1) / 2;
    mapped = points.map(([x, y]) => [2 * c - x, y]);
  } else if (axis === "yx") {
    mapped = points.map(([x, y]) => [y, x]);
  } else {
    const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2;
    mapped = points.map(([x, y]) => [2 * cx - x, 2 * cy - y]);
  }
  const step = Math.max(1, Math.floor(points.length / 120));
  const every = points.filter((_point, index) => index % step === 0);
  let total = 0, count = 0;
  for (let i = 0; i < mapped.length; i += step) {
    const [px, py] = mapped[i];
    let best = Infinity;
    for (const [qx, qy] of every) {
      const distance = (px - qx) ** 2 + (py - qy) ** 2;
      if (distance < best) best = distance;
    }
    total += Math.sqrt(best);
    count += 1;
  }
  return round(total / Math.max(count, 1) / size, 4);
};

export function selfCrossings(speedX: number[], speedY: number[], samples: number): CrossingHit[] {
  return crossingHits(spinePoints(speedX, speedY, samples));
}

// A near-tangential touch appears and disappears as the sample count moves, so a crossing is
// kept only when the coarse pass finds it and the fine pass finds it again at the same pair.
export function stableCrossings(speedX: number[], speedY: number[],
  coarse = 600, fine = 2400): CrossingHit[] {
  const first = selfCrossings(speedX, speedY, coarse);
  if (!first.length) return [];
  const second = selfCrossings(speedX, speedY, fine);
  const kept: CrossingHit[] = [];
  for (const hit of first) {
    const match = second.find((other) =>
      Math.abs(hit.t1 - other.t1) < 0.02 && Math.abs(hit.t2 - other.t2) < 0.02);
    if (match) kept.push(match);
  }
  return kept;
}

export function analyse(record: CurveRecord): Analysis {
  let points = pathPoints(record);
  let kind: "rows" | "path" | "error" = "path";
  let method: "exact" | "sampled" = "sampled";
  const family = record.family_id ?? record.family;
  const result: Analysis = {
    uid: record.uid,
    name: record.name,
    family: typeof family === "string" ? family : null,
    kind,
    method,
    degree: 0,
    step: Number(record.step || 1),
    grid: "0",
    bend: 0,
    arc: 0,
    chord: 0,
    inflections: 0,
    inflectionMax: 0,
    closest: 0,
    crossings: 0,
    meetingPoints: 0,
    bboxW: 0,
    bboxH: 0,
    area: 0,
    maxCurvature: 0,
    curvatureMedian: 0,
    mirrorY: 1,
    halfTurn: 1,
    mirrorYX: 1,
  };

  const speedX = record.speedX ?? [];
  const speedY = record.speedY ?? [];
  if (speedX.length || speedY.length) {
    kind = "rows";
    points = spinePoints(speedX, speedY);
    try {
      const m = metrics(speedX as SpeedRow, speedY as SpeedRow);
      const { chordRe, chordIm } = arcAndChord(speedX as SpeedRow, speedY as SpeedRow);
      for (const value of [m.bend, m.arc, m.closest]) {
        if (!Number.isFinite(value)) throw new Error("a curved number is not finite");
      }
      result.kind = "rows";
      result.method = "exact";
      result.grid = String(Math.trunc(m.grid));
      result.bend = round(m.bend, 6);
      result.arc = round(m.arc, 6);
      result.chord = round(Math.hypot(chordRe, chordIm), 6);
      result.inflections = m.inflection_count;
      result.inflectionMax = m.inflection_max;
      result.closest = round(m.closest, 6);
    } catch (error) {
      result.method = "sampled";
      result.error = String(error instanceof Error ? error.message : error).slice(0, 120);
    }
  }

  result.kind = kind;
  if (points.length) {
    const [x0, y0, x1, y1] = bbox(points);
    result.bboxW = round(x1 - x0, 4);
    result.bboxH = round(y1 - y0, 4);
    result.area = round(polygonArea(points), 4);
    const size = Math.max(x1 - x0, y1 - y0) || 1;
    result.curvatureMedian = round(curvatureMedian(points) * size, 4);
    const peak = curvatureMax(points);
    const scaled = peak === null ? null : peak * size;
    result.maxCurvature = scaled === null || scaled > 1e6 ? null : round(scaled, 4);
    result.mirrorY = mirrorGap(points, "y");
    result.mirrorYX = mirrorGap(points, "yx");
    result.halfTurn = mirrorGap(points, "half");
    result.degree = speedX.length || speedY.length ? Math.max(speedX.length, speedY.length) - 1 : 0;
  }

  if (kind === "rows") {
    try {
      const hits = stableCrossings(speedX, speedY);
      result.crossings = hits.length;
      result.meetingPoints = new Set(hits.map((hit) =>
        `${round(hit.x, 1)},${round(hit.y, 1)}`)).size;
    } catch {
      // one bad curve must not stop the sweep
    }
  }
  return result;
}
