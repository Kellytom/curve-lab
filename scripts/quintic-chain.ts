/**
 * quintic-chain.ts — place spans end to end and measure the join.
 *
 *   node scripts/quintic-chain.ts [--list]
 *
 * A chain is spans placed by rigid motion: each span is rotated so its start
 * tangent continues the previous span's end tangent, then translated so its
 * start sits on the previous end. Rotation and translation do not change the
 * signed curvature or its rate, so the join residual is exactly the difference
 * of the two stored frames — no re-fitting, nothing hidden.
 *
 * That gives the honest answer to "can these shapes be chained smoothly?":
 *   G1 is free (it is what the placement does);
 *   G2 is |Δκ| at the join;
 *   G3 is |Δ(dκ/ds)| at the join.
 *
 * Writes workbench/quintic-chain.json (the numbers) and
 * workbench/quintic-chain.svg (the chain, with the joins marked).
 */

import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";

type Point = [number, number];
type End = { p: Point; tangent: Point; kappa: number | null; rate: number | null };
type Span = { uid: string; kind: "quintic"; points: Point[]; weights: null; frame: { start: End; end: End } };
type Curve = { uid: string; family: string; group: string; name: string; spans: Span[]; closed: boolean };

const ROOT = path.resolve(import.meta.dirname, "..");
const DATA = path.join(ROOT, "workbench", "quintic-guides.json");
const OUT_JSON = path.join(ROOT, "workbench", "quintic-chain.json");
const OUT_SVG = path.join(ROOT, "workbench", "quintic-chain.svg");

const G2_TOLERANCE = 0.01; // relative: 1 % of the larger |kappa| at the join
const G3_TOLERANCE = 0.05; // relative to the larger |rate| at the join

const data = JSON.parse(readFileSync(DATA, "utf8")) as { curves: Curve[] };
const byUid = (uid: string): Curve => {
  const c = data.curves.find((x) => x.uid === uid);
  if (!c) throw new Error(`no curve ${uid}`);
  return c;
};

/** The chain the operator would actually draw: a Roman moulding run, then an S. */
const CHAIN = ["q6-cyma-reversa-05", "q6-cyma-recta-05", "q6-echinus-05", "q6-s-curve-05"];

type Placed = { uid: string; points: Point[]; start: End; end: End };

const rotate = (p: Point, c: number, s: number): Point => [p[0] * c - p[1] * s, p[0] * s + p[1] * c];
const angle = (v: Point) => Math.atan2(v[1], v[0]);

function place(spans: Span[]): Placed[] {
  const placed: Placed[] = [];
  let cursor: Point = [0, 0];
  let direction: Point = [1, 0]; // the chain starts heading right
  for (const span of spans) {
    const startTangent = span.frame.start.tangent;
    const turn = angle(direction) - angle(startTangent);
    const c = Math.cos(turn);
    const s = Math.sin(turn);
    const p0 = span.points[0];
    const points = span.points.map((p) => {
      const r = rotate([p[0] - p0[0], p[1] - p0[1]], c, s);
      return [cursor[0] + r[0], cursor[1] + r[1]] as Point;
    });
    const endPoint = points[5];
    const endDirection = rotate(span.frame.end.tangent, c, s);
    placed.push({
      uid: span.uid,
      points,
      // kappa and rate are rigid-motion invariant, so the stored values carry over
      start: { ...span.frame.start, p: points[0], tangent: rotate(startTangent, c, s) },
      end: { ...span.frame.end, p: endPoint, tangent: endDirection },
    });
    cursor = endPoint;
    direction = endDirection;
  }
  return placed;
}

const placed = place(CHAIN.map((uid) => byUid(uid).spans[0]));

type Join = {
  uid: string;
  between: [string, string];
  continuity: "G1" | "G2" | "G3";
  residual: { position: number; tangentDegrees: number; kappa: number; rate: number };
  relative: { kappa: number; rate: number };
  passes: { G1: boolean; G2: boolean; G3: boolean };
};

const joins: Join[] = [];
for (let i = 0; i < placed.length - 1; i += 1) {
  const a = placed[i].end;
  const b = placed[i + 1].start;
  const position = Math.hypot(b.p[0] - a.p[0], b.p[1] - a.p[1]);
  const ta = angle(a.tangent);
  const tb = angle(b.tangent);
  let deg = Math.abs(((ta - tb) * 180) / Math.PI);
  if (deg > 180) deg = 360 - deg;
  const kappa = Math.abs((b.kappa ?? 0) - (a.kappa ?? 0));
  const rate = Math.abs((b.rate ?? 0) - (a.rate ?? 0));
  const kappaScale = Math.max(Math.abs(a.kappa ?? 0), Math.abs(b.kappa ?? 0)) || 1;
  const rateScale = Math.max(Math.abs(a.rate ?? 0), Math.abs(b.rate ?? 0)) || 1;
  const relKappa = kappa / kappaScale;
  const relRate = rate / rateScale;
  const passes = {
    G1: position < 1e-9 && deg < 1e-6,
    G2: position < 1e-9 && deg < 1e-6 && relKappa <= G2_TOLERANCE,
    G3: position < 1e-9 && deg < 1e-6 && relKappa <= G2_TOLERANCE && relRate <= G3_TOLERANCE,
  };
  joins.push({
    uid: `join:${placed[i].uid}->${placed[i + 1].uid}`,
    between: [placed[i].uid, placed[i + 1].uid],
    continuity: passes.G3 ? "G3" : passes.G2 ? "G2" : "G1",
    residual: { position, tangentDegrees: deg, kappa, rate },
    relative: { kappa: relKappa, rate: relRate },
    passes,
  });
}

/* ---------- the picture ---------- */

const all = placed.flatMap((p) => p.points);
const minX = Math.min(...all.map((p) => p[0]));
const maxX = Math.max(...all.map((p) => p[0]));
const minY = Math.min(...all.map((p) => p[1]));
const maxY = Math.max(...all.map((p) => p[1]));
const W = 1200;
const H = 640;
const padX = 70;
const padTop = 96;
const padBottom = 96;
const scale = Math.min((W - 2 * padX) / (maxX - minX || 1), (H - padTop - padBottom) / (maxY - minY || 1));
// y is flipped here and only here: model y-up, SVG y-down.
const plot = (p: Point): string =>
  `${(padX + (p[0] - minX) * scale + (W - 2 * padX - (maxX - minX) * scale) / 2).toFixed(2)},${(H - padBottom - (p[1] - minY) * scale).toFixed(2)}`;

const colours = ["#123a63", "#1f7a4d", "#9c2f2f", "#4a3a8f"];
const parts: string[] = [];
parts.push(`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">`);
parts.push(`<rect width="${W}" height="${H}" fill="#fff"/>`);
parts.push(`<g font-family="Helvetica, Arial, sans-serif">`);
parts.push(`<text x="${padX}" y="34" font-size="20" font-weight="600">Fig. QC1 — four canon spans placed end to end, tangent-matched</text>`);
parts.push(
  `<text x="${padX}" y="56" font-size="13" fill="#555">Rigid placement: G1 is exact by construction. The number at each join is the curvature jump, as a share of the larger |κ|. G2 passes at 1 %.</text>`,
);
placed.forEach((sp, i) => {
  const d = `M ${plot(sp.points[0])} ` + cubicChainD(sp.points);
  parts.push(`<path d="${d}" fill="none" stroke="${colours[i % colours.length]}" stroke-width="2.2"/>`);
  const [x, y] = plot(sp.points[0]).split(",");
  parts.push(`<circle cx="${x}" cy="${y}" r="3.2" fill="${colours[i % colours.length]}"/>`);
});
joins.forEach((j, i) => {
  const [x, y] = plot(placed[i].end.p).split(",");
  const up = i % 2 === 0;
  const lx = +x + 10;
  const ly = up ? +y - 26 : +y + 30;
  parts.push(`<circle cx="${x}" cy="${y}" r="6" fill="none" stroke="#c0392b" stroke-width="1.8"/>`);
  parts.push(`<line x1="${x}" y1="${y}" x2="${lx - 2}" y2="${up ? ly + 4 : ly - 12}" stroke="#c0392b" stroke-width="0.8"/>`);
  parts.push(`<text x="${lx}" y="${ly}" font-size="12" fill="#c0392b">${j.continuity} · Δκ ${(j.relative.kappa * 100).toFixed(1)} %</text>`);
});
// legend and axis note
parts.push(`<g transform="translate(${padX},${H - 52})" font-size="12" fill="#333">`);
placed.forEach((sp, i) => {
  const x = i * 280;
  parts.push(`<line x1="${x}" y1="-4" x2="${x + 26}" y2="-4" stroke="${colours[i % colours.length]}" stroke-width="2.2"/>`);
  parts.push(`<text x="${x + 34}" y="0">${sp.uid.replace(/^q6-/, "").replace(":0", "")}</text>`);
});
parts.push(`</g>`);
parts.push(`<text x="${padX}" y="${H - 24}" font-size="12" fill="#666">x right, y up, grid units. Red circles are joins. The drawn path is a six-span cubic chain; the six control points of each span are the exact record.</text>`);
parts.push(`</g></svg>`);
writeFileSync(OUT_SVG, `${parts.join("\n")}\n`);

function cubicChainD(points: Point[]): string {
  // Six cubic segments, each through four stations of the quintic: a smooth
  // drawing, not a polyline. The stations are exact; the joins are not visible.
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
  const split = (pts: Point[], t: number): [Point[], Point[]] => {
    const left: Point[] = [];
    const right: Point[] = [];
    let row = pts;
    for (let depth = 0; depth < 6; depth += 1) {
      left.push(row[0]);
      right.unshift(row[row.length - 1]);
      const next: Point[] = [];
      for (let i = 0; i < row.length - 1; i += 1) {
        next.push([row[i][0] + (row[i + 1][0] - row[i][0]) * t, row[i][1] + (row[i + 1][1] - row[i][1]) * t]);
      }
      row = next;
    }
    return [left, right];
  };
  const sub = (pts: Point[], t0: number, t1: number): Point[] => {
    const [, afterStart] = split(pts, t0);
    const [middle] = split(afterStart, (t1 - t0) / (1 - t0));
    return middle;
  };
  const cubicThrough = (f: (t: number) => Point): Point[] => {
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
  };
  const spans = 6;
  const parts: string[] = [];
  for (let s = 0; s < spans; s += 1) {
    const piece = sub(points, s / spans, (s + 1) / spans);
    const c = cubicThrough((u) => at(piece, u));
    parts.push(`C ${plot(c[1])} ${plot(c[2])} ${plot(c[3])}`);
  }
  return parts.join(" ");
}

writeFileSync(
  OUT_JSON,
  `${JSON.stringify(
    {
      format: "curve-lab.chain/1",
      tolerances: { g2RelativeKappa: G2_TOLERANCE, g3RelativeRate: G3_TOLERANCE },
      chain: placed.map((p) => ({ uid: p.uid, points: p.points.map((q) => q.map((v) => +v.toFixed(6))) })),
      joins,
    },
    null,
    1,
  )}\n`,
);

console.log("chain:", CHAIN.join(" -> "));
for (const j of joins) {
  console.log(
    `${j.continuity}  Δκ ${(j.relative.kappa * 100).toFixed(2).padStart(7)}%  ` +
      `Δ(dκ/ds) ${(j.relative.rate * 100).toFixed(1).padStart(7)}%  ` +
      `tangent ${j.residual.tangentDegrees.toExponential(1)}°  pos ${j.residual.position.toExponential(1)}`,
  );
}
const worstKappa = Math.max(...joins.map((j) => j.relative.kappa));
const worstRate = Math.max(...joins.map((j) => j.relative.rate));
console.log(`worst curvature jump ${(worstKappa * 100).toFixed(2)} %, worst rate jump ${(worstRate * 100).toFixed(1)} %`);
