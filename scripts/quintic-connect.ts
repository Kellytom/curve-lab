/**
 * quintic-connect.ts — a chain whose joins are solved, not hoped for.
 *
 *   node scripts/quintic-connect.ts
 *
 * The earlier chain work (scripts/quintic-chain.ts) placed whole spans by rigid
 * motion: G1 was exact and the curvature jump was whatever the shapes happened to
 * give (39 % and 47 % on two joins). That answers "are these shapes chainable";
 * this answers the other question — "build the chain so the joins match".
 *
 * The connector is DeepSeek2's own solver, `quinticControls` in
 * app/src/lib/glue.ts: two free handle lengths, and a 4×4 solve that spends them
 * on the neighbours' curvature κ and its rate dκ/ds at both ends. So each span is
 * G3 by construction, and this script's job is to prove it rather than assume it:
 * every join is re-measured from the six control points with the same end-frame
 * maths the contract uses.
 *
 * Writes workbench/quintic-connect.json (stations, spans, measured joins) and
 * workbench/quintic-connect.svg.
 *
 * Limits, stated rather than hidden:
 *   - slopes are rational dy/dx; a **vertical** tangent is {n: 1, d: 0}, which works;
 *   - **`dkappa1` is negated** before the solve. Measured: asked for −0.0001 at the
 *     end, the span came back at +0.0001; the start rate was exact. glue.ts takes the
 *     end rate along the reversed direction while its κ is forward;
 *   - **use Pythagorean slopes** (3/4, 5/12, 20/21). `unitDirection` in glue.ts divides
 *     by the squared length instead of its root for every direction that is not a
 *     p-triple, so such a slope gives a vector of length 1/√l2 and the curvature the
 *     solver aims for lands 2√2 times too large. Measured, not guessed: slope 1 gave
 *     κ = 0.028284 where 0.01 was asked, and slope 3/4 gives it exactly.
 */

import { writeFileSync } from "node:fs";
import path from "node:path";
import { quinticControls, type Frac, type Point } from "../app/src/lib/glue.ts";
import { chainPathData, endFrame, quinticAt, selfCrossings, type Point as Pt } from "./lib/quintic-geometry.ts";

const ROOT = path.resolve(import.meta.dirname, "..");
const OUT_JSON = path.join(ROOT, "workbench", "quintic-connect.json");
const OUT_SVG = path.join(ROOT, "workbench", "quintic-connect.svg");

type Station = { x: number; y: number; slope: Frac; kappa: number; rate: number };

/** The datums: four stations, three spans, all slopes rational. */
const STATIONS: Station[] = [
  // Pythagorean slopes only: 3-4-5, 5-12-13, 3-4-5, 3-4-5. A slope that is not a
  // p-triple is mis-normalised by unitDirection (see the note at the top), and the
  // curvature the solver aims for comes out 2√2 times too large.
  { x: 0, y: 0, slope: { n: 3, d: 4 }, kappa: 0.0, rate: 0.0 },
  { x: 60, y: 28, slope: { n: 5, d: 12 }, kappa: 0.0008, rate: 0.00002 },
  { x: 95, y: 62, slope: { n: 0, d: 1 }, kappa: -0.0008, rate: -0.00001 },
  { x: 150, y: 40, slope: { n: -3, d: 4 }, kappa: 0.0, rate: 0.0 },
];

const spanUid = (i: number) => `span:${i}`;

type Built = {
  uid: string;
  points: Pt[];
  requested: { k0: number; r0: number; k1: number; r1: number };
  measured: { start: ReturnType<typeof endFrame>; end: ReturnType<typeof endFrame> };
};

const spans: Built[] = [];
for (let i = 0; i < STATIONS.length - 1; i += 1) {
  const a = STATIONS[i];
  const b = STATIONS[i + 1];
  const controls = quinticControls(
    { x: a.x, y: a.y },
    { x: b.x, y: b.y },
    a.slope,
    b.slope,
    // dkappa1 is negated: measured 2026-11-27, glue.ts takes the end rate along the
    // reversed direction while its curvature is forward. Passing it straight through
    // makes every join's rate residual 2× the rate (see the note at the top).
    { h0: 0.42, h1: 0.42, kappa0: a.kappa, kappa1: b.kappa, dkappa0: a.rate, dkappa1: -b.rate },
  );
  if (!controls) {
    console.error(`station ${i} -> ${i + 1}: no connector (a vertical slope?)`);
    process.exit(2);
  }
  const points = controls.map((p) => [p.x, p.y] as Pt);
  spans.push({
    uid: spanUid(i),
    points,
    requested: { k0: a.kappa, r0: a.rate, k1: b.kappa, r1: b.rate },
    measured: { start: endFrame(points, false), end: endFrame(points, true) },
  });
}

/** A join is the end of one span and the start of the next. */
const joins = spans.slice(0, -1).map((span, i) => {
  const next = spans[i + 1];
  const a = span.measured.end;
  const b = next.measured.start;
  const position = Math.hypot(b.p[0] - a.p[0], b.p[1] - a.p[1]);
  const ta = Math.atan2(a.tangent[1], a.tangent[0]);
  const tb = Math.atan2(b.tangent[1], b.tangent[0]);
  let deg = Math.abs(((ta - tb) * 180) / Math.PI);
  if (deg > 180) deg = 360 - deg;
  const dk = Math.abs(b.kappa - a.kappa);
  const dr = Math.abs(b.rate - a.rate);
  const kScale = Math.max(Math.abs(a.kappa), Math.abs(b.kappa)) || 1;
  const rScale = Math.max(Math.abs(a.rate), Math.abs(b.rate)) || 1;
  const relK = dk / kScale;
  const relR = dr / rScale;
  return {
    uid: `join:${i}`,
    a: { span: span.uid, end: "end" as const },
    b: { span: next.uid, end: "start" as const },
    continuity: position < 1e-9 && deg < 1e-6 && relK < 1e-6 && relR < 1e-6 ? "G3" : relK < 1e-6 ? "G2" : "G1",
    residual: { position, tangentDegrees: deg, kappa: dk, rate: dr },
    relative: { kappa: relK, rate: relR },
  };
});

/** Every station must be met exactly: that is the whole claim of a connector. */
const stationErrors = STATIONS.map((s, i) => {
  const at = i === 0 ? spans[0].measured.start : spans[i - 1].measured.end;
  const point = Math.hypot(at.p[0] - s.x, at.p[1] - s.y);
  const slopeReached = at.tangent[1] / (at.tangent[0] || 1e-12);
  const slopeWanted = s.slope.n / s.slope.d;
  return {
    station: i,
    position: point,
    slope: Math.abs(slopeReached - slopeWanted),
    kappa: Math.abs(at.kappa - s.kappa),
    rate: Math.abs(at.rate - s.rate),
  };
});

const record = {
  format: "curve-lab.connect/1",
  method: "quinticControls from app/src/lib/glue.ts; handles 0.42 chord; measured with scripts/lib/quintic-geometry.endFrame",
  stations: STATIONS,
  spans: spans.map((s) => ({
    uid: s.uid,
    kind: "quintic",
    points: s.points.map((p) => p.map((v) => +v.toFixed(6))),
    frame: {
      start: { ...s.measured.start, kappa: +s.measured.start.kappa.toFixed(9), rate: +s.measured.start.rate.toFixed(9) },
      end: { ...s.measured.end, kappa: +s.measured.end.kappa.toFixed(9), rate: +s.measured.end.rate.toFixed(9) },
    },
  })),
  joins: joins.map((j) => ({
    uid: j.uid,
    a: j.a,
    b: j.b,
    continuity: j.continuity,
    residual: {
      position: +j.residual.position.toExponential(3) as unknown as number,
      tangentDegrees: +j.residual.tangentDegrees.toExponential(3) as unknown as number,
      kappa: +j.residual.kappa.toExponential(3) as unknown as number,
      rate: +j.residual.rate.toExponential(3) as unknown as number,
    },
  })),
  stationErrors: stationErrors.map((e) => ({
    station: e.station,
    position: +e.position.toExponential(3) as unknown as number,
    slope: +e.slope.toExponential(3) as unknown as number,
    kappa: +e.kappa.toExponential(3) as unknown as number,
    rate: +e.rate.toExponential(3) as unknown as number,
  })),
  selfCrossings: spans.reduce((n, s) => n + selfCrossings(s.points, 200), 0),
};

writeFileSync(OUT_JSON, `${JSON.stringify(record, null, 1)}\n`);

/* ---------- the picture ---------- */

// The box comes from the curve, not the control points: a solver handle can sit far
// outside the drawing and would shrink it to a corner.
const all = spans.flatMap((s) => Array.from({ length: 41 }, (_, k) => quinticAt(s.points, k / 40)));
const xs = all.map((p) => p[0]);
const ys = all.map((p) => p[1]);
const minX = Math.min(...xs);
const maxX = Math.max(...xs);
const minY = Math.min(...ys);
const maxY = Math.max(...ys);
const W = 1200;
const H = 640;
const pad = 80;
const scale = Math.min((W - 2 * pad) / (maxX - minX || 1), (H - 2 * pad) / (maxY - minY || 1));
// y is flipped here and only here: model y-up, SVG y-down.
const plot = (p: Pt): string =>
  `${(pad + (p[0] - minX) * scale + (W - 2 * pad - (maxX - minX) * scale) / 2).toFixed(2)},${(H - pad - (p[1] - minY) * scale).toFixed(2)}`;

const colours = ["#123a63", "#1f7a4d", "#9c2f2f", "#4a3a8f"];
const parts: string[] = [];
parts.push(`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">`);
parts.push(`<rect width="${W}" height="${H}" fill="#fff"/>`);
parts.push(`<g font-family="Helvetica, Arial, sans-serif">`);
parts.push(`<text x="${pad}" y="34" font-size="20" font-weight="600">Fig. QN1 — three spans solved to G3 at every join</text>`);
parts.push(
  `<text x="${pad}" y="56" font-size="13" fill="#555">Handles 0.42 × chord, curvature and its rate met at both ends of each span. Worst curvature residual ${Math.max(...joins.map((j) => j.residual.kappa)).toExponential(1)}; measured from the control points, not from the solver.</text>`,
);
spans.forEach((span, i) => {
  parts.push(`<path d="${chainPathData(span.points, 6, plot)}" fill="none" stroke="${colours[i % colours.length]}" stroke-width="2.2"/>`);
});
STATIONS.forEach((s, i) => {
  const [x, y] = plot([s.x, s.y]).split(",");
  parts.push(`<circle cx="${x}" cy="${y}" r="6" fill="none" stroke="#c0392b" stroke-width="2"/>`);
  parts.push(`<text x="${+x + 10}" y="${+y - 10}" font-size="12" fill="#c0392b">S${i} κ ${s.kappa}</text>`);
  if (i < STATIONS.length - 1) {
    const mid = quinticAt(spans[i].points, 0.5);
    const [mx, my] = plot(mid).split(",");
    parts.push(`<text x="${mx}" y="${my}" font-size="11" fill="${colours[i % colours.length]}" text-anchor="middle">span ${i} · ${joins[i]?.continuity ?? ""}</text>`);
  }
});
parts.push(`<text x="${pad}" y="${H - 22}" font-size="12" fill="#666">x right, y up, arbitrary units. Red circles are the stations (position, slope, κ, dκ/ds). Each coloured run is one quintic span, drawn as a six-span cubic chain.</text>`);
parts.push(`</g></svg>`);
writeFileSync(OUT_SVG, `${parts.join("\n")}\n`);

/* ---------- report ---------- */

console.log(`${spans.length} spans, ${joins.length} joins`);
for (const s of stationErrors) {
  console.log(
    `  station ${s.station}: pos ${s.position.toExponential(1)}  slope ${s.slope.toExponential(1)}  ` +
      `κ ${s.kappa.toExponential(1)}  dκ ${s.rate.toExponential(1)}`,
  );
}
for (const j of joins) {
  console.log(
    `  ${j.continuity}  Δκ ${j.relative.kappa.toExponential(1)}  Δ(dκ/ds) ${j.relative.rate.toExponential(1)}  ` +
      `tangent ${j.residual.tangentDegrees.toExponential(1)}°  pos ${j.residual.position.toExponential(1)}`,
  );
}
console.log(`worst station residual: ${Math.max(...stationErrors.map((s) => Math.max(s.position, s.slope, s.kappa, s.rate))).toExponential(2)}`);
console.log(`self crossings in the chain: ${record.selfCrossings}`);
