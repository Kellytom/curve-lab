// The recipe that worked: a mirrored root pair, then a stack at one half.
//
// The TypeScript twin of `scripts/root_search.py`. The Python module stays for its one importer
// (`adder_roots.py`) until that moves; this module and `scripts/root_search.ts` are the script's
// new authority.
//
//     v(t) = (t - p/q)(t - (q-p)/q) [· (t - p2/q2)(t - (q2-p2)/q2)] · (t - 1/2)^m
//     u(t) = A + B(t^2 - t), default 1 - 2t + 2t^2    the x speed (the known good one)
//
// Every root r has a partner 1 - r, which keeps the curve symmetric about t = 1/2. Ranking:
// crossing pairs first (the knot measure), then inflections, then the cheapest grid.

import { metrics, type SpeedRow } from "./measure.ts";
import { stableCrossings } from "./curve-analysis.ts";

type Rat = { n: bigint; d: bigint };

const gcdBig = (a: bigint, b: bigint): bigint => (b ? gcdBig(b, a % b) : a < 0n ? -a : a);

const rat = (n: bigint, d: bigint = 1n): Rat => {
  if (d === 0n) throw new Error("a zero denominator");
  const sign = d < 0n ? -1n : 1n;
  const g = gcdBig(n, d) || 1n;
  return { n: (sign * n) / g, d: (sign * d) / g };
};

const ratMul = (a: Rat, b: Rat): Rat => rat(a.n * b.n, a.d * b.d);
const ratSub = (a: Rat, b: Rat): Rat => rat(a.n * b.d - b.n * a.d, a.d * b.d);
const ratAdd = (a: Rat, b: Rat): Rat => rat(a.n * b.d + b.n * a.d, a.d * b.d);

// (t - r) for each root, as whole-number coefficients after clearing every denominator.
export function polyFromRoots(roots: Rat[]): number[] {
  let coefficients: Rat[] = [rat(1n)];
  for (const root of roots) {
    const next: Rat[] = Array.from({ length: coefficients.length + 1 }, () => rat(0n));
    coefficients.forEach((coefficient, i) => {
      // ascending powers: (t - r) maps a_i t^i to a_i t^(i+1) - r a_i t^i
      next[i + 1] = ratAdd(next[i + 1], coefficient);
      next[i] = ratSub(next[i], ratMul(coefficient, root));
    });
    coefficients = next;
  }
  let scale = 1n;
  for (const coefficient of coefficients) {
    scale = (scale / gcdBig(scale, coefficient.d)) * coefficient.d;
  }
  return coefficients.map((coefficient) => Number(coefficient.n * (scale / coefficient.d)));
}

export type Second = { p: number; q: number } | null;

export function candidate(p: number, q: number, mid: number, second: Second = null,
  xRow: [number, number] = [1, 2]): { u: number[]; v: number[] } {
  const roots: Rat[] = [rat(BigInt(p), BigInt(q)), rat(BigInt(q - p), BigInt(q))];
  if (second) {
    roots.push(rat(BigInt(second.p), BigInt(second.q)),
      rat(BigInt(second.q - second.p), BigInt(second.q)));
  }
  roots.push(...Array.from({ length: mid }, () => rat(1n, 2n)));
  const v = polyFromRoots(roots);
  const [a, b] = xRow;
  const u = [a, -b, b]; // the x speed: A + B(t^2 - t)
  while (u.length < v.length) u.push(0);
  while (v.length < u.length) v.push(0);
  return { u, v };
}

export type Description = {
  grid: number;
  bend: number;
  inflections: number;
  crossings: number;
  places: number;
  error?: string;
};

export function describe(u: number[], v: number[]): Description {
  try {
    const m = metrics(u as SpeedRow, v as SpeedRow);
    const hits = stableCrossings(u, v);
    return {
      grid: Math.trunc(m.grid),
      bend: Math.round(m.bend * 1e4) / 1e4,
      inflections: m.inflection_count,
      crossings: hits.length,
      places: new Set(hits.map((hit) =>
        `${Math.round(hit.x * 10) / 10},${Math.round(hit.y * 10) / 10}`)).size,
    };
  } catch (error) {
    return { grid: 0, bend: 0, inflections: 0, crossings: 0, places: 0,
      error: String(error instanceof Error ? error.message : error).slice(0, 100) };
  }
}

// How near the centred drawing passes its own middle.
export function closestGrace(u: number[], v: number[], steps = 300): number {
  let x = 0, y = 0;
  const points: Array<[number, number, number]> = [];
  for (let k = 0; k < steps; k += 1) {
    const t = (k + 0.5) / steps;
    let ux = 0, vy = 0;
    u.forEach((coefficient, i) => { ux += coefficient * t ** i; });
    v.forEach((coefficient, i) => { vy += coefficient * t ** i; });
    x += (ux * ux - vy * vy) / steps;
    y += (2 * ux * vy) / steps;
    points.push([x, y, (k + 1) / steps]);
  }
  const xs = points.map((point) => point[0]);
  const ys = points.map((point) => point[1]);
  const cx = (Math.min(...xs) + Math.max(...xs)) / 2;
  const cy = (Math.min(...ys) + Math.max(...ys)) / 2;
  const size = Math.max(...points.map(([a, b]) => Math.max(Math.abs(a), Math.abs(b)))) || 1;
  const inner = points.filter(([, , t]) => t > 0.08 && t < 0.92)
    .map(([a, b]) => Math.hypot(a - cx, b - cy));
  return inner.length ? Math.min(...inner) / size : 9;
}

export type RootCandidate = {
  name: string;
  p: number;
  q: number;
  mid: number;
  u: number[];
  v: number[];
  grid: number;
  bend: number;
  inflections: number;
  crossings: number;
  places: number;
  grace: number;
};

export function search({ second = null, xRow = [1, 2] as [number, number] } = {}): RootCandidate[] {
  const rows: RootCandidate[] = [];
  const gcd = (a: number, b: number): number => (b ? gcd(b, a % b) : Math.abs(a) || 1);
  for (let q = 5; q <= 12; q += 1) {
    for (let p = 1; p <= Math.floor(q / 2); p += 1) {
      if (gcd(p, q) !== 1) continue;
      for (const mid of [1, 3, 5]) {
        const { u, v } = candidate(p, q, mid, second, xRow);
        const facts = describe(u, v);
        if (facts.error) continue;
        rows.push({
          name: `pair-${p}of${q}-mid${mid}`, p, q, mid, u, v,
          grid: facts.grid, bend: facts.bend, inflections: facts.inflections,
          crossings: facts.crossings, places: facts.places,
          grace: Math.round(closestGrace(u, v) * 1e4) / 1e4,
        });
      }
    }
  }
  rows.sort((left, right) => right.crossings - left.crossings
    || right.inflections - left.inflections
    || left.grid - right.grid);
  return rows;
}
