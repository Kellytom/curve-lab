// Coupler curves: what a four-bar linkage draws.
//
// The TypeScript twin of `scripts/coupler_curves.py`. The Python module stays for
// `tests/test_crossing_calibration.py` until that moves; this module and the CLI are the
// script's new authority.
//
// A four-bar linkage is two fixed pivots, a crank, a coupler and a rocker. A point on the
// coupler traces a plane curve; these are the classic source of symmetric curves with many
// nodes. Sampled, not exact — cos and sin of a general angle are irrational, which the project's
// rule forbids claiming as exact.

import { crossingPairs, type Point } from "./crossings.ts";

export type Found = {
  r2: number;
  r3: number;
  r4: number;
  d: number;
  a: number;
  b: number;
  crossings: number;
  mirror: number;
  points?: Point[];
};

export function circleHit(bx: number, by: number, r3: number, ox: number, oy: number,
  r4: number, previous: Point | null = null): Point | null {
  const dx = ox - bx;
  const dy = oy - by;
  const d = Math.hypot(dx, dy);
  if (d === 0 || d > r3 + r4 || d < Math.abs(r3 - r4)) return null;
  const a = (r3 * r3 - r4 * r4 + d * d) / (2 * d);
  const h = Math.sqrt(Math.max(0, r3 * r3 - a * a));
  const mx = bx + (a * dx) / d;
  const my = by + (a * dy) / d;
  const rx = -dy / d;
  const ry = dx / d;
  const first: Point = [mx + h * rx, my + h * ry];
  const second: Point = [mx - h * rx, my - h * ry];
  if (previous === null) return first;
  // Keep the branch: a jump between them zigzags and invents crossings.
  return Math.hypot(first[0] - previous[0], first[1] - previous[1])
    <= Math.hypot(second[0] - previous[0], second[1] - previous[1]) ? first : second;
}

// A point of the unit circle from a rational slope t = tan(theta/2): cos and sin as exact
// rationals; with t = 1/2 the point is (3/5, 4/5), the 3-4-5 triple.
export function crankPoint([p, q]: [number, number]): Point {
  const den = q * q + p * p;
  return [(q * q - p * p) / den, (2 * p * q) / den];
}

export function trace(r2: number, r3: number, r4: number, ground: number,
  a: number, b: number, steps = 720): Point[] {
  const points: Point[] = [];
  let previous: Point | null = null;
  for (let k = 0; k <= steps; k += 1) {
    // A full turn matters more than rational points: walking a slope from -6 to 6 covers only a
    // short arc, and the curve retraced it, inventing crossings. cos/sin for now, and the figure
    // says sampled.
    const t = (2 * Math.PI * k) / steps;
    const bx = r2 * Math.cos(t);
    const by = r2 * Math.sin(t);
    const hit = circleHit(bx, by, r3, ground, 0, r4, previous);
    if (hit === null) return [];
    previous = hit;
    const [cx, cy] = hit;
    const ux = cx - bx;
    const uy = cy - by;
    points.push([bx + a * ux - b * uy, by + a * uy + b * ux]);
  }
  return points;
}

// Distance from the curve to its own mirror across the vertical axis.
export function symmetryGap(points: Point[]): number {
  if (!points.length) return 9;
  const xs = points.map((point) => point[0]);
  const ys = points.map((point) => point[1]);
  const cx = (Math.min(...xs) + Math.max(...xs)) / 2;
  const size = Math.max(Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys)) || 1;
  const mirrored = points.map(([x, y]) => [2 * cx - x, y] as Point);
  const step = Math.max(1, Math.floor(points.length / 90));
  const every = points.filter((_point, index) => index % step === 0);
  let total = 0;
  let count = 0;
  for (let i = 0; i < mirrored.length; i += step) {
    const [px, py] = mirrored[i];
    let best = Infinity;
    for (const [qx, qy] of every) {
      const distance = (px - qx) ** 2 + (py - qy) ** 2;
      if (distance < best) best = distance;
    }
    total += Math.sqrt(best);
    count += 1;
  }
  return Math.round((total / (count || 1) / size) * 1e4) / 1e4;
}

export type SearchOptions = { wide?: boolean; minCrossings?: number };

export function searchFound({ wide = false, minCrossings = 2 }: SearchOptions = {}): Found[] {
  const r2s = wide ? [1, 2, 3, 4] : [1, 2, 3];
  const r3s = wide ? [2, 3, 4, 5, 6] : [3, 4, 5];
  const r4s = wide ? [1, 2, 3, 4, 5] : [2, 3, 4];
  const grounds = wide ? [2, 3, 4, 5, 6] : [3, 4, 5];
  const a_s = wide ? [0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2] : [0.5, 1, 1.5];
  const b_s = wide ? [0.2, 0.4, 0.6, 0.8, 1, 1.2] : [0.3, 0.6, 0.9];

  const found: Found[] = [];
  for (const r2 of r2s) {
    for (const r3 of r3s) {
      for (const r4 of r4s) {
        for (const ground of grounds) {
          for (const a of a_s) {
            for (const b of b_s) {
              const points = trace(r2, r3, r4, ground, a, b);
              if (points.length < 8) continue;
              const crossings = crossingPairs(points);
              if (crossings < minCrossings) continue;
              found.push({
                r2, r3, r4, d: ground, a, b, crossings,
                mirror: symmetryGap(points),
                points: points.map(([x, y]) => [Math.round(x * 1e4) / 1e4, Math.round(y * 1e4) / 1e4]),
              });
            }
          }
        }
      }
    }
  }
  found.sort((left, right) => right.crossings - left.crossings || left.mirror - right.mirror);
  return found;
}

// A seeded generator for the random mode; not Python's Mersenne Twister, so its sample is its
// own — the default integer grid is the reproducible search.
export function seededRandom(seed: number): () => number {
  let state = seed >>> 0;
  return () => {
    state = (state + 0x6d2b79f5) >>> 0;
    let t = state;
    t = Math.imul(t ^ (t >>> 15), t | 1) >>> 0;
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// The random search: continuous linkages, filtered to the Grashof ones whose crank is shortest
// (without that the trace is a partial arc and no coupler curve is drawn).
export function searchRandom(count: number, minCrossings = 2, seed = 20261124): Found[] {
  const random = seededRandom(seed);
  const round3 = (value: number): number => Math.round(value * 1e3) / 1e3;
  const found: Found[] = [];
  for (let i = 0; i < count; i += 1) {
    const r2 = round3(0.3 + random() * 3.7);
    const r3 = round3(0.6 + random() * 6.4);
    const r4 = round3(0.3 + random() * 5.7);
    const ground = round3(0.6 + random() * 6.4);
    const a = round3(-2 + random() * 5);
    const b = round3(-2 + random() * 4);
    const links = [r2, r3, r4, ground].sort((left, right) => left - right);
    if (links[0] + links[3] > links[1] + links[2]) continue;
    if (r2 !== links[0]) continue;
    const points = trace(r2, r3, r4, ground, a, b);
    if (points.length < 700) continue;
    const crossings = crossingPairs(points);
    if (crossings >= minCrossings) {
      found.push({ r2, r3, r4, d: ground, a, b, crossings, mirror: symmetryGap(points), points });
    }
  }
  found.sort((left, right) => right.crossings - left.crossings || left.mirror - right.mirror);
  return found;
}
