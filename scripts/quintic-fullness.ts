/**
 * quintic-fullness.ts — what the extension's one control does, measured.
 *
 *   node scripts/quintic-fullness.ts
 *
 * The rule (the operator's, 2026-11-26): endpoints fixed, the four interior
 * points move from the chord toward the guide,
 *
 *     L_i = (1 - i/5) P0 + (i/5) P5
 *     P_i = (1 - α) L_i + α G_i
 *
 * At α = 0 the six points are collinear (a straight line); at α = 1 they are
 * the guide points themselves. This writes the five sets for five guides, so
 * the Inkscape extension can be checked against the same numbers, and draws
 * them so the slider can be judged by eye.
 *
 * Output: workbench/quintic-fullness.json (the fixture), workbench/quintic-fullness.svg
 */

import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { chainPathData, chainError, endFrame, quinticAt, type Point } from "./lib/quintic-geometry.ts";

const ROOT = path.resolve(import.meta.dirname, "..");
const DATA = path.join(ROOT, "workbench", "quintic-guides.json");
const OUT_JSON = path.join(ROOT, "workbench", "quintic-fullness.json");
const OUT_SVG = path.join(ROOT, "workbench", "quintic-fullness.svg");

const ALPHAS = [0, 0.25, 0.5, 0.75, 1] as const;
const GUIDES = ["q6-parabola-05", "q6-s-curve-05", "q6-cyma-recta-05", "q6-volute-05", "q6-loop-05"];

const data = JSON.parse(readFileSync(DATA, "utf8")) as {
  curves: { uid: string; family: string; spans: { points: Point[] }[] }[];
};

const chord = (p0: Point, p5: Point, i: number): Point => [
  (1 - i / 5) * p0[0] + (i / 5) * p5[0],
  (1 - i / 5) * p0[1] + (i / 5) * p5[1],
];

function blend(guide: Point[], alpha: number): Point[] {
  const p0 = guide[0];
  const p5 = guide[5];
  return guide.map((g, i) => {
    if (i === 0 || i === 5) return g;
    const l = chord(p0, p5, i);
    return [
      +((1 - alpha) * l[0] + alpha * g[0]).toFixed(6),
      +((1 - alpha) * l[1] + alpha * g[1]).toFixed(6),
    ] as Point;
  });
}

const rows = GUIDES.map((uid) => {
  const curve = data.curves.find((c) => c.uid === uid);
  if (!curve) throw new Error(`no guide ${uid}`);
  const guide = curve.spans[0].points;
  return {
    uid,
    family: curve.family,
    guide,
    values: ALPHAS.map((alpha) => {
      const points = blend(guide, alpha);
      return {
        alpha,
        points,
        chainError: +chainError(points, 6).toFixed(4),
        kappaStart: +endFrame(points, false).kappa.toFixed(6),
        kappaEnd: +endFrame(points, true).kappa.toFixed(6),
      };
    }),
  };
});

const record = {
  format: "curve-lab.fullness/1",
  degree: 5 as const,
  rule: "P_i = (1 - alpha) * L_i + alpha * G_i for i = 1..4; P0 and P5 fixed",
  alphas: ALPHAS,
  note: "A parity fixture for the Inkscape extension: the same six guide points at five fullness values. Points are exact quarters on this data, written to six decimals.",
  guides: rows,
};
writeFileSync(OUT_JSON, `${JSON.stringify(record, null, 1)}\n`);

/* ---------- the picture ---------- */
const W = 1400;
const H = 1000;
const marginLeft = 120;
const header = 96;
const footer = 44;
const cellW = (W - marginLeft - 24) / ALPHAS.length;
const cellH = (H - header - footer) / GUIDES.length;

const parts: string[] = [];
parts.push(`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">`);
parts.push(`<rect width="${W}" height="${H}" fill="#fff"/>`);
parts.push(`<g font-family="Helvetica, Arial, sans-serif">`);
parts.push(`<text x="24" y="30" font-size="20" font-weight="600">Fig. QF1 — fullness α: six guide points blended from the chord (α 0) to the curve (α 1)</text>`);
parts.push(`<text x="24" y="52" font-size="13" fill="#555">P_i = (1 − α)·L_i + α·G_i for i = 1…4; P0 and P5 fixed. Pale dots are the six control points; the dark line is the quintic drawn as a six-span cubic chain.</text>`);
parts.push(`<text x="24" y="72" font-size="13" fill="#555">This is the fixture in workbench/quintic-fullness.json: the extension's output at each α should match these points.</text>`);

ALPHAS.forEach((alpha, col) => {
  parts.push(`<text x="${marginLeft + col * cellW + cellW / 2}" y="${header - 8}" font-size="14" font-weight="600" text-anchor="middle">α = ${alpha}</text>`);
});

rows.forEach((row, r) => {
  const cellY = header + r * cellH;
  parts.push(`<text x="24" y="${cellY + cellH / 2}" font-size="13" fill="#333">${row.family}</text>`);
  row.values.forEach((value, col) => {
    const cellX = marginLeft + col * cellW;
    // one scale for every cell in the row, so the change is comparable
    const xs = row.guide.map((p) => p[0]);
    const ys = row.guide.map((p) => p[1]);
    const minX = Math.min(...xs);
    const maxX = Math.max(...xs);
    const minY = Math.min(...ys);
    const maxY = Math.max(...ys);
    const pad = 16;
    const scale = Math.min(
      (cellW - 2 * pad) / Math.max(1, maxX - minX),
      (cellH - 2 * pad) / Math.max(1, maxY - minY),
    );
    const ox = cellX + pad + ((cellW - 2 * pad) - (maxX - minX) * scale) / 2;
    const oy = cellY + pad + ((cellH - 2 * pad) - (maxY - minY) * scale) / 2;
    // y is flipped here and only here: model y-up, SVG y-down.
    const plot = (p: Point): string =>
      `${(ox + (p[0] - minX) * scale).toFixed(2)},${(oy + (maxY - p[1]) * scale).toFixed(2)}`;

    parts.push(`<rect x="${cellX + 2}" y="${cellY + 2}" width="${cellW - 4}" height="${cellH - 4}" fill="none" stroke="#e6e6e6"/>`);
    parts.push(`<path d="${chainPathData(value.points, 6, plot)}" fill="none" stroke="#123a63" stroke-width="1.6"/>`);
    for (const p of value.points) {
      const [x, y] = plot(p).split(",");
      parts.push(`<circle cx="${x}" cy="${y}" r="1.8" fill="#c0392b" fill-opacity="0.55"/>`);
    }
    parts.push(
      `<text x="${cellX + 8}" y="${cellY + cellH - 7}" font-size="10" fill="#8a8a8a">Δ ${value.chainError.toFixed(3)} · κ ${value.kappaStart.toFixed(2)}</text>`,
    );
  });
});

parts.push(`<text x="24" y="${H - 16}" font-size="12" fill="#666">x right, y up, grid units. One scale per row across the five α values, so the shapes can be compared. κ at the span's two ends, in 1/grid units.</text>`);
parts.push(`</g></svg>`);
writeFileSync(OUT_SVG, `${parts.join("\n")}\n`);

console.log(`guides: ${rows.length}, alphas: ${ALPHAS.join(", ")}`);
for (const row of rows) {
  console.log(
    `${row.family.padEnd(14)} ` +
      row.values.map((v) => `α${v.alpha}: κ ${v.kappaStart.toFixed(2)}`).join("  "),
  );
}
