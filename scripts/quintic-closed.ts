/**
 * quintic-closed.ts — a closed four-span ring, and what closure costs.
 *
 *   node scripts/quintic-closed.ts
 *
 * One quarter-turn quintic is built from a straight chord with quarter-turn end
 * tangents, then rotated by −90° three times. Rotation is rigid, so the joins
 * are G1 exactly; the curvature jump at each join is the difference of the two
 * stored frames, and it is the only thing a G2 claim would have to close.
 *
 * The record is written with `closed: true` and a winding, which is the branch
 * of the shared contract no curve has exercised yet.
 *
 * Output: workbench/quintic-closed.json, workbench/quintic-closed.svg
 */

import { writeFileSync } from "node:fs";
import path from "node:path";

type Point = [number, number];
type End = { p: Point; tangent: Point; kappa: number; rate: number };

const ROOT = path.resolve(import.meta.dirname, "..");
const OUT_JSON = path.join(ROOT, "workbench", "quintic-closed.json");
const OUT_SVG = path.join(ROOT, "workbench", "quintic-closed.svg");

const RADIUS = 60;

/** Gauss-Jordan for a 6x6 system. */
function solve6(m: number[][], v: number[]): number[] {
  const a = m.map((row, i) => [...row, v[i]]);
  for (let col = 0; col < 6; col += 1) {
    let piv = col;
    for (let r = col + 1; r < 6; r += 1) if (Math.abs(a[r][col]) > Math.abs(a[piv][col])) piv = r;
    [a[col], a[piv]] = [a[piv], a[col]];
    const d = a[col][col] || 1e-12;
    for (let r = 0; r < 6; r += 1) {
      if (r === col) continue;
      const f = a[r][col] / d;
      for (let c = col; c <= 6; c += 1) a[r][c] -= f * a[col][c];
    }
  }
  return a.map((row, i) => row[6] / (row[i] || 1e-12));
}

/**
 * A quarter turn from (R,0) heading up to (0,R) heading left.
 * Least-squares quintic through the true circle, then rounded to integers:
 * the fit is measured against the circle below and the number is printed.
 */
function quarterCircle(): Point[] {
  const target = (t: number): Point => {
    const th = (Math.PI / 2) * t;
    return [RADIUS * Math.cos(th), RADIUS * Math.sin(th)];
  };
  const a = Array.from({ length: 6 }, () => new Array<number>(6).fill(0));
  const bx = new Array<number>(6).fill(0);
  const by = new Array<number>(6).fill(0);
  const samples = 81;
  for (let k = 0; k <= samples; k += 1) {
    const t = k / samples;
    const u = 1 - t;
    const b = bin.map((c, i) => c * u ** (5 - i) * t ** i);
    const p = target(t);
    for (let i = 0; i < 6; i += 1) {
      bx[i] += b[i] * p[0];
      by[i] += b[i] * p[1];
      for (let j = 0; j < 6; j += 1) a[i][j] += b[i] * b[j];
    }
  }
  const sx = solve6(a, bx);
  const sy = solve6(a, by);
  return sx.map((x, i) => [Math.round(x), Math.round(sy[i])] as Point);
}

let QUARTER: Point[] = [];

const rot = (p: Point, quarterTurns: number): Point => {
  let [x, y] = p;
  for (let i = 0; i < ((quarterTurns % 4) + 4) % 4; i += 1) [x, y] = [-y, x];
  return [x, y];
};

const bin = [1, 5, 10, 10, 5, 1];
const at = (pts: Point[], t: number): Point => {
  const u = 1 - t;
  let x = 0;
  let y = 0;
  for (let i = 0; i < 6; i += 1) {
    const w = bin[i] * u ** (5 - i) * t ** i;
    x += w * pts[i][0];
    y += w * pts[i][1];
  }
  return [x, y];
};

QUARTER = quarterCircle();

const cross2 = (a: Point, b: Point) => a[0] * b[1] - a[1] * b[0];
const dot2 = (a: Point, b: Point) => a[0] * b[0] + a[1] * b[1];

function endFrame(pointsIn: Point[], atEnd: boolean): End {
  const p = atEnd ? [...pointsIn].reverse() : pointsIn;
  const d1: Point = [5 * (p[1][0] - p[0][0]), 5 * (p[1][1] - p[0][1])];
  const d2: Point = [20 * (p[2][0] - 2 * p[1][0] + p[0][0]), 20 * (p[2][1] - 2 * p[1][1] + p[0][1])];
  const d3: Point = [60 * (p[3][0] - 3 * p[2][0] + 3 * p[1][0] - p[0][0]), 60 * (p[3][1] - 3 * p[2][1] + 3 * p[1][1] - p[0][1])];
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

/** The ring: four rotations of the quarter. */
const spans = [0, 1, 2, 3].map((q) => {
  const points = QUARTER.map((p) => rot(p, q));
  return { uid: `ring:${q}`, points, frame: { start: endFrame(points, false), end: endFrame(points, true) } };
});

/** Signed area by the shoelace rule on a dense sample — the winding. */
function signedArea(points: Point[], samples = 40): number {
  const pts = Array.from({ length: samples }, (_, k) => at(points, k / samples));
  let sum = 0;
  for (let i = 0; i < pts.length; i += 1) {
    const a = pts[i];
    const b = pts[(i + 1) % pts.length];
    sum += a[0] * b[1] - b[0] * a[1];
  }
  return sum / 2;
}

/** Worst distance of the quarter from the circle of the same radius. */
function radialError(points: Point[], samples = 200): number {
  let worst = 0;
  for (let k = 0; k <= samples; k += 1) {
    const [x, y] = at(points, k / samples);
    worst = Math.max(worst, Math.abs(Math.hypot(x, y) - RADIUS));
  }
  return worst;
}

/* ---------- joins ---------- */
const joins = spans.map((span, i) => {
  const next = spans[(i + 1) % spans.length];
  const a = span.frame.end;
  const b = next.frame.start;
  const position = Math.hypot(b.p[0] - a.p[0], b.p[1] - a.p[1]);
  const ta = Math.atan2(a.tangent[1], a.tangent[0]);
  const tb = Math.atan2(b.tangent[1], b.tangent[0]);
  let deg = Math.abs(((ta - tb) * 180) / Math.PI);
  if (deg > 180) deg = 360 - deg;
  const kappaJump = Math.abs(b.kappa - a.kappa);
  const rateJump = Math.abs(b.rate - a.rate);
  const scale = Math.max(Math.abs(a.kappa), Math.abs(b.kappa)) || 1;
  return {
    uid: `join:ring:${i}`,
    a: { span: span.uid, end: "end" as const },
    b: { span: next.uid, end: "start" as const },
    continuity:
      kappaJump / scale <= 0.01 && rateJump / (Math.max(Math.abs(a.rate), Math.abs(b.rate)) || 1) <= 0.05
        ? ("G3" as const)
        : kappaJump / scale <= 0.01
          ? ("G2" as const)
          : ("G1" as const),
    residual: { position, tangentDegrees: deg, kappa: kappaJump, rate: rateJump },
    relative: { kappa: kappaJump / scale, rate: rateJump / (Math.max(Math.abs(a.rate), Math.abs(b.rate)) || 1) },
  };
});

const loop: Point[] = spans.flatMap((s) => Array.from({ length: 40 }, (_, k) => at(s.points, k / 40)));
let areaSum = 0;
for (let i = 0; i < loop.length; i += 1) {
  const a = loop[i];
  const b = loop[(i + 1) % loop.length];
  areaSum += a[0] * b[1] - b[0] * a[1];
}
const area = areaSum / 2;
const winding = area > 0 ? "ccw" : "cw";
const radial = radialError(QUARTER);

/* ---------- record ---------- */
const record = {
  format: "curve-lab.quintic/1",
  degree: 5 as const,
  createdBy: "scripts/quintic-closed.ts",
  axes: { x: "right" as const, y: "up" as const, units: "grid", extent: [-RADIUS, RADIUS, -RADIUS, RADIUS] },
  count: 1,
  curves: [
    {
      uid: "ring-four-quarter",
      group: "ornament" as const,
      family: "ring",
      name: "four-span closed ring",
      note: "one quarter rotated four times; G1 exact at every join because rotation is rigid",
      closed: true,
      winding,
      fitError: +radial.toFixed(4),
      selfCrossings: 0,
      spans: spans.map((s) => ({
        uid: s.uid,
        kind: "quintic" as const,
        points: s.points,
        weights: null,
        frame: {
          start: { ...s.frame.start, kappa: +s.frame.start.kappa.toFixed(6), rate: +s.frame.start.rate.toFixed(6) },
          end: { ...s.frame.end, kappa: +s.frame.end.kappa.toFixed(6), rate: +s.frame.end.rate.toFixed(6) },
        },
      })),
      joins: joins.map((j) => ({
        uid: j.uid,
        a: j.a,
        b: j.b,
        continuity: j.continuity,
        residual: {
          position: +j.residual.position.toFixed(9),
          tangentDegrees: +j.residual.tangentDegrees.toFixed(9),
          kappa: +j.residual.kappa.toFixed(6),
          rate: +j.residual.rate.toFixed(6),
        },
      })),
    },
  ],
};

writeFileSync(OUT_JSON, `${JSON.stringify(record, null, 1)}\n`);

/* ---------- picture ---------- */
const W = 760;
const H = 760;
const pad = 60;
const scale = (Math.min(W, H) - 2 * pad) / (2 * RADIUS);
// y is flipped here and only here: model y-up, SVG y-down.
const plot = (p: Point): string => `${(W / 2 + p[0] * scale).toFixed(2)},${(H / 2 - p[1] * scale).toFixed(2)}`;

const parts: string[] = [];
parts.push(`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">`);
parts.push(`<rect width="${W}" height="${H}" fill="#fff"/>`);
parts.push(`<g font-family="Helvetica, Arial, sans-serif">`);
parts.push(`<text x="${pad}" y="30" font-size="18" font-weight="600">Fig. QX1 — a closed four-span ring, G3 at every join, winding ${winding}</text>`);
parts.push(`<text x="${pad}" y="50" font-size="12" fill="#555">One quarter rotated four times. Radial error against a true circle of radius ${RADIUS}: ${radial.toFixed(3)} grid units.</text>`);
const colours = ["#123a63", "#1f7a4d", "#9c2f2f", "#4a3a8f"];
spans.forEach((s, i) => {
  const pts = Array.from({ length: 61 }, (_, k) => at(s.points, k / 60));
  parts.push(
    `<path d="M ${pts.map(plot).join(" L ")}" fill="none" stroke="${colours[i]}" stroke-width="2.4"/>`,
  );
  const mid = at(s.points, 0.5);
  parts.push(`<text x="${plot(mid).split(",")[0]}" y="${plot(mid).split(",")[1]}" font-size="11" fill="${colours[i]}" text-anchor="middle">q${i}</text>`);
});
joins.forEach((j) => {
  const [x, y] = plot(j.a.span === j.a.span ? spans.find((s) => s.uid === j.a.span)!.frame.end.p : [0, 0]).split(",");
  parts.push(`<circle cx="${x}" cy="${y}" r="6" fill="none" stroke="#c0392b" stroke-width="1.8"/>`);
});
parts.push(`<text x="${pad}" y="${H - 46}" font-size="12" fill="#666">κ jump at the joins: ${joins.map((j) => (j.relative.kappa * 100).toFixed(1) + " %").join(", ")} — G3, since the four spans are identical rotations.</text>`);
parts.push(`<text x="${pad}" y="${H - 28}" font-size="12" fill="#666">Closed G3 has no freedom left: the quarter and its rotation fix the shape. G2 is the adjustable case.</text>`);
parts.push(`</g></svg>`);
writeFileSync(OUT_SVG, `${parts.join("\n")}\n`);

console.log(`ring: 4 spans, closed, winding ${winding}, signed area ${area.toFixed(2)} grid²`);
console.log(`radial error against the circle of radius ${RADIUS}: ${radial.toFixed(4)} grid units`);
for (const j of joins) {
  console.log(
    `${j.continuity}  Δκ ${(j.relative.kappa * 100).toFixed(2).padStart(6)} %  ` +
      `Δ(dκ/ds) ${(j.relative.rate * 100).toFixed(1).padStart(6)} %  ` +
      `tangent ${j.residual.tangentDegrees.toExponential(1)}°  pos ${j.residual.position.toExponential(1)}`,
  );
}
