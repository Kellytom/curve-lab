/**
 * quintic-geometry.ts — the degree-5 maths, in one place.
 *
 * Four scripts now use the same six operations (evaluate, split, sub-curve,
 * four-station cubic, cubic chain, end frame). Keeping a copy in each script is
 * how two definitions of one number drift apart, so they live here and nowhere
 * else.
 *
 * Nothing in this file touches the file system or inkex: it is pure geometry.
 */

export type Point = [number, number];

/** Degree 5 is the only degree this project stores as six points. */
export const DEGREE = 5;

export const BINOMIAL5 = [1, 5, 10, 10, 5, 1];

/** B(t) of the six control points. */
export function quinticAt(points: Point[], t: number): Point {
  const u = 1 - t;
  let x = 0;
  let y = 0;
  for (let i = 0; i < 6; i += 1) {
    const w = BINOMIAL5[i] * u ** (5 - i) * t ** i;
    x += w * points[i][0];
    y += w * points[i][1];
  }
  return [x, y];
}

/** de Casteljau split at t: [the piece on [0,t], the piece on [t,1]], both exact. */
export function splitQuintic(points: Point[], t: number): [Point[], Point[]] {
  const left: Point[] = [];
  const right: Point[] = [];
  let row = points;
  for (let depth = 0; depth < 6; depth += 1) {
    left.push(row[0]);
    right.unshift(row[row.length - 1]);
    const next: Point[] = [];
    for (let i = 0; i < row.length - 1; i += 1) {
      next.push([
        row[i][0] + (row[i + 1][0] - row[i][0]) * t,
        row[i][1] + (row[i + 1][1] - row[i][1]) * t,
      ]);
    }
    row = next;
  }
  return [left, right];
}

/** The exact sub-quintic over [t0, t1]. */
export function subQuintic(points: Point[], t0: number, t1: number): Point[] {
  const [, afterStart] = splitQuintic(points, t0);
  const [middle] = splitQuintic(afterStart, (t1 - t0) / (1 - t0));
  return middle;
}

/**
 * The cubic through a quintic's values at u = 0, 1/3, 2/3, 1.
 * The inverse of the Bézier-at-those-stations map; error is O(h^5) per span.
 */
export function cubicThrough(f: (u: number) => Point): Point[] {
  const values = [0, 1 / 3, 2 / 3, 1].map(f);
  const m = [
    [1, 0, 0, 0],
    [-5 / 6, 3, -3 / 2, 1 / 3],
    [1 / 3, -3 / 2, 3, -5 / 6],
    [0, 0, 0, 1],
  ];
  return m.map((row) => {
    let x = 0;
    let y = 0;
    row.forEach((w, j) => {
      x += w * values[j][0];
      y += w * values[j][1];
    });
    return [x, y] as Point;
  });
}

/** The whole quintic as `spans` cubics, each exact at four stations. */
export function cubicChain(points: Point[], spans: number): Point[][] {
  const out: Point[][] = [];
  for (let s = 0; s < spans; s += 1) {
    const piece = subQuintic(points, s / spans, (s + 1) / spans);
    out.push(cubicThrough((u) => quinticAt(piece, u)));
  }
  return out;
}

/** Worst distance between the cubic chain and the true quintic, in grid units. */
export function chainError(points: Point[], spans: number, samples = 200): number {
  const chain = cubicChain(points, spans);
  let worst = 0;
  for (let k = 0; k <= samples; k += 1) {
    const t = k / samples;
    const truth = quinticAt(points, t);
    const s = Math.min(spans - 1, Math.floor(t * spans));
    const u = t * spans - s;
    const c = chain[s];
    const v = 1 - u;
    let x = 0;
    let y = 0;
    for (let i = 0; i < 4; i += 1) {
      const w = [1, 3, 3, 1][i] * v ** (3 - i) * u ** i;
      x += w * c[i][0];
      y += w * c[i][1];
    }
    worst = Math.max(worst, Math.hypot(x - truth[0], y - truth[1]));
  }
  return worst;
}

/** SVG path data for the cubic chain, using the caller's point formatter. */
export function chainPathData(points: Point[], spans: number, plot: (p: Point) => string): string {
  const chain = cubicChain(points, spans);
  return chain
    .map((c, i) => (i === 0 ? `M ${plot(c[0])} ` : "") + `C ${plot(c[1])} ${plot(c[2])} ${plot(c[3])}`)
    .join(" ");
}

export type EndFrame = {
  p: Point;
  /** un-normalised forward derivative: P1 - P0 at the start, P5 - P4 at the end */
  tangent: Point;
  /** signed curvature, 1/grid, positive turning left along the parameter */
  kappa: number;
  /** d(kappa)/ds, 1/grid^2 */
  rate: number;
};

const cross2 = (a: Point, b: Point) => a[0] * b[1] - a[1] * b[0];
const dot2 = (a: Point, b: Point) => a[0] * b[0] + a[1] * b[1];

/**
 * The end frame of a span, measured from its six points.
 * Reversing the control points gives the other end the same formula, but the
 * reversed walk has the opposite signed curvature, so the sign is flipped back:
 * both ends are reported along the forward parameter.
 */
export function endFrame(pointsIn: Point[], atEnd: boolean): EndFrame {
  const p = atEnd ? [...pointsIn].reverse() : pointsIn;
  const d1: Point = [5 * (p[1][0] - p[0][0]), 5 * (p[1][1] - p[0][1])];
  const d2: Point = [20 * (p[2][0] - 2 * p[1][0] + p[0][0]), 20 * (p[2][1] - 2 * p[1][1] + p[0][1])];
  const d3: Point = [
    60 * (p[3][0] - 3 * p[2][0] + 3 * p[1][0] - p[0][0]),
    60 * (p[3][1] - 3 * p[2][1] + 3 * p[1][1] - p[0][1]),
  ];
  const n = Math.hypot(d1[0], d1[1]);
  const sign = atEnd ? -1 : 1;
  const forward: Point = atEnd
    ? [pointsIn[5][0] - pointsIn[4][0], pointsIn[5][1] - pointsIn[4][1]]
    : [pointsIn[1][0] - pointsIn[0][0], pointsIn[1][1] - pointsIn[0][1]];
  return {
    p: p[0],
    tangent: forward,
    kappa: sign * (cross2(d1, d2) / n ** 3),
    rate: sign * (cross2(d1, d3) / n ** 4 - (3 * cross2(d1, d2) * dot2(d1, d2)) / n ** 6),
  };
}

/** How many times the drawn curve crosses itself, by a sampled polyline count. */
export function selfCrossings(points: Point[], samples = 240): number {
  const pts = Array.from({ length: samples + 1 }, (_, k) => quinticAt(points, k / samples));
  let count = 0;
  const orient = (a: Point, b: Point, c: Point) =>
    Math.sign((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]));
  for (let i = 0; i < pts.length - 1; i += 1) {
    for (let j = i + 2; j < pts.length - 1; j += 1) {
      if (i === 0 && j === pts.length - 2) continue;
      const a = pts[i];
      const b = pts[i + 1];
      const c = pts[j];
      const d = pts[j + 1];
      if (orient(a, b, c) !== orient(a, b, d) && orient(c, d, a) !== orient(c, d, b)) count += 1;
    }
  }
  return count;
}
