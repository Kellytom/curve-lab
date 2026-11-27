/**
 * quintic-closed.ts — a closed four-span ring, and what closure costs.
 *
 *   node scripts/quintic-closed.ts
 *
 * One quarter-turn quintic is fitted to a true quarter circle, rounded to
 * integers, then rotated by +90° three times. Rotation is rigid, so the joins
 * are exact in position and tangent; the curvature jump at each join is the
 * difference of the two stored frames, and it is the only thing a G2 claim
 * would have to close.
 *
 * The record is written with `closed: true` and a winding, which is the branch
 * of the shared contract no other curve in the tree exercises.
 *
 * Output: workbench/quintic-closed.json, workbench/quintic-closed.svg
 */

import { writeFileSync } from "node:fs";
import path from "node:path";
import { BINOMIAL5, endFrame, quinticAt, type Point } from "./lib/quintic-geometry.ts";

const ROOT = path.resolve(import.meta.dirname, "..");
const OUT_JSON = path.join(ROOT, "workbench", "quintic-closed.json");
const OUT_SVG = path.join(ROOT, "workbench", "quintic-closed.svg");

const RADIUS = 60;
const SPANS = 4;
const G2_TOLERANCE = 0.01;
const G3_TOLERANCE = 0.05;

/** Gauss-Jordan for the 6×6 fit. */
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

/** A quarter circle from (R,0) heading up to (0,R) heading left, as integers. */
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
    const b = BINOMIAL5.map((c, i) => c * u ** (5 - i) * t ** i);
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

const QUARTER = quarterCircle();

const rot = (p: Point, turns: number): Point => {
  let [x, y] = p;
  for (let i = 0; i < ((turns % 4) + 4) % 4; i += 1) [x, y] = [-y, x];
  return [x, y];
};

const spans = Array.from({ length: SPANS }, (_, q) => {
  const points = QUARTER.map((p) => rot(p, q));
  return {
    uid: `ring:${q}`,
    points,
    frame: { start: endFrame(points, false), end: endFrame(points, true) },
  };
});

/** Worst distance of the quarter from the circle of the same radius. */
function radialError(points: Point[], samples = 200): number {
  let worst = 0;
  for (let k = 0; k <= samples; k += 1) {
    const [x, y] = quinticAt(points, k / samples);
    worst = Math.max(worst, Math.abs(Math.hypot(x, y) - RADIUS));
  }
  return worst;
}

/** Signed area of the whole closed chain, by shoelace on a dense sample. */
function signedAreaOfChain(samplesPerSpan = 40): number {
  const loop = spans.flatMap((s) => Array.from({ length: samplesPerSpan }, (_, k) => quinticAt(s.points, k / samplesPerSpan)));
  let sum = 0;
  for (let i = 0; i < loop.length; i += 1) {
    const a = loop[i];
    const b = loop[(i + 1) % loop.length];
    sum += a[0] * b[1] - b[0] * a[1];
  }
  return sum / 2;
}

const angleOf = (v: Point) => Math.atan2(v[1], v[0]);

const joins = spans.map((span, i) => {
  const next = spans[(i + 1) % spans.length];
  const a = span.frame.end;
  const b = next.frame.start;
  const position = Math.hypot(b.p[0] - a.p[0], b.p[1] - a.p[1]);
  let deg = Math.abs(((angleOf(a.tangent) - angleOf(b.tangent)) * 180) / Math.PI);
  if (deg > 180) deg = 360 - deg;
  const kappaJump = Math.abs(b.kappa - a.kappa);
  const rateJump = Math.abs(b.rate - a.rate);
  const kappaScale = Math.max(Math.abs(a.kappa), Math.abs(b.kappa)) || 1;
  const rateScale = Math.max(Math.abs(a.rate), Math.abs(b.rate)) || 1;
  const relKappa = kappaJump / kappaScale;
  const relRate = rateJump / rateScale;
  const continuity = relKappa <= G2_TOLERANCE ? (relRate <= G3_TOLERANCE ? "G3" : "G2") : "G1";
  return {
    uid: `join:ring:${i}`,
    a: { span: span.uid, end: "end" as const },
    b: { span: next.uid, end: "start" as const },
    continuity,
    residual: { position, tangentDegrees: deg, kappa: kappaJump, rate: rateJump },
    relative: { kappa: relKappa, rate: relRate },
  };
});

const area = signedAreaOfChain();
const winding = area > 0 ? "ccw" : "cw";
const radial = radialError(QUARTER);

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
      note: "one quarter fitted to a circle, rotated four times; rigid rotation makes every join exact",
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

/* ---------- the picture ---------- */
const W = 760;
const H = 780;
const pad = 60;
const scale = (Math.min(W, H - 40) - 2 * pad) / (2 * RADIUS);
// y is flipped here and only here: model y-up, SVG y-down.
const plot = (p: Point): string => `${(W / 2 + p[0] * scale).toFixed(2)},${((H - 60) / 2 - p[1] * scale).toFixed(2)}`;

const colours = ["#123a63", "#1f7a4d", "#9c2f2f", "#4a3a8f"];
const parts: string[] = [];
parts.push(`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">`);
parts.push(`<rect width="${W}" height="${H}" fill="#fff"/>`);
parts.push(`<g font-family="Helvetica, Arial, sans-serif">`);
parts.push(`<text x="${pad}" y="30" font-size="18" font-weight="600">Fig. QX1 — a closed four-span ring, ${joins[0].continuity} at every join, winding ${winding}</text>`);
parts.push(`<text x="${pad}" y="50" font-size="12" fill="#555">One quarter fitted to a circle of radius ${RADIUS} (radial error ${radial.toFixed(3)} grid units), rotated four times.</text>`);
spans.forEach((s, i) => {
  const pts = Array.from({ length: 61 }, (_, k) => quinticAt(s.points, k / 60));
  parts.push(`<path d="M ${pts.map(plot).join(" L ")}" fill="none" stroke="${colours[i]}" stroke-width="2.4"/>`);
  const mid = plot(quinticAt(s.points, 0.5)).split(",");
  parts.push(`<text x="${mid[0]}" y="${mid[1]}" font-size="11" fill="${colours[i]}" text-anchor="middle">q${i}</text>`);
  const end = plot(s.frame.end.p).split(",");
  parts.push(`<circle cx="${end[0]}" cy="${end[1]}" r="6" fill="none" stroke="#c0392b" stroke-width="1.8"/>`);
});
parts.push(`<text x="${pad}" y="${H - 46}" font-size="12" fill="#666">κ jump at the joins: ${joins.map((j) => (j.relative.kappa * 100).toFixed(1) + " %").join(", ")} — identical rotations, so the joins are ${joins[0].continuity}.</text>`);
parts.push(`<text x="${pad}" y="${H - 28}" font-size="12" fill="#666">Closed ${joins[0].continuity} has no freedom left: the quarter and its rotation fix the shape. G2 is the adjustable case.</text>`);
parts.push(`</g></svg>`);
writeFileSync(OUT_SVG, `${parts.join("\n")}\n`);

console.log(`ring: ${SPANS} spans, closed, winding ${winding}, signed area ${area.toFixed(2)} grid²`);
console.log(`radial error against the circle of radius ${RADIUS}: ${radial.toFixed(4)} grid units`);
for (const j of joins) {
  console.log(
    `${j.continuity}  Δκ ${(j.relative.kappa * 100).toFixed(2).padStart(6)} %  ` +
      `Δ(dκ/ds) ${(j.relative.rate * 100).toFixed(1).padStart(6)} %  ` +
      `tangent ${j.residual.tangentDegrees.toExponential(1)}°  pos ${j.residual.position.toExponential(1)}`,
  );
}
