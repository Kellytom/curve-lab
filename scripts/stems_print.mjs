// Render the three-stem print sheet from the geometry JSON.
//
//   node scripts/stems_print.mjs
//
// The JSON is produced by scripts/stems_print.py; this file owns the SVG and
// the print wrapper.  No SVG library: the input is already a sampled polyline
// in page inches, so plain Node string building is the smallest thing that
// works.

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..");
const DATA = path.join(ROOT, "workbench", "stems-abc.json");
const OUT = path.join(ROOT, "workbench", "stems-abc.svg");
const HTML = path.join(ROOT, "workbench", "stems-abc.html");

const INK = "#2e2413";
const MUTED = "#7b6c4e";
const GUIDE = "#ece4cf";
const DOT = "#b23a2b";

const data = JSON.parse(fs.readFileSync(DATA, "utf8"));
const U = data.page.units_per_in ?? 100;
const W = data.page.width_in * U;
const H = data.page.height_in * U;
const MARGIN = data.page.margin_in * U;

function squirclePath(cx, cy, r, n = 4, steps = 160) {
  // |x/r|^n + |y/r|^n = 1; n=4 is the squircle used on the Euler-square page
  const pts = [];
  for (let i = 0; i <= steps; i++) {
    const t = (2 * Math.PI * i) / steps;
    const c = Math.cos(t);
    const s = Math.sin(t);
    const x = Math.sign(c) * Math.pow(Math.abs(c), 2 / n);
    const y = Math.sign(s) * Math.pow(Math.abs(s), 2 / n);
    pts.push([cx + r * x, cy + r * y]);
  }
  return "M " + pts.map(([x, y]) => `${x.toFixed(2)} ${y.toFixed(2)}`).join(" L ");
}

const groups = [];
for (const stem of data.stems) {
  const cellX = stem.cell.x_in * U;
  const cellBottom = stem.cell.bottom_in * U;
  const cellSide = stem.cell.side_in * U;
  const cellTop = cellBottom - cellSide;
  const d = "M " + stem.points_page_in
    .map(([x, y]) => `${(x * U).toFixed(2)} ${(y * U).toFixed(2)}`)
    .join(" L ");
  const [sx, sy] = stem.start_page_in.map((v) => v * U);
  const [ex, ey] = stem.end_page_in.map((v) => v * U);
  groups.push(`<g id="stem-${stem.label}">
    <path d="${squirclePath(cellX + cellSide / 2, cellTop + cellSide / 2,
                            cellSide / 2)}"
          fill="none" stroke="${GUIDE}" stroke-width="0.8"/>
    <path d="${d}" fill="none" stroke="${INK}" stroke-width="1.8"
          stroke-linejoin="round" stroke-linecap="round"/>
    <circle cx="${sx.toFixed(2)}" cy="${sy.toFixed(2)}" r="2.4"
            fill="none" stroke="${DOT}" stroke-width="1"/>
    <circle cx="${ex.toFixed(2)}" cy="${ey.toFixed(2)}" r="2.4"
            fill="none" stroke="${DOT}" stroke-width="1"/>
    <text x="${(cellX + cellSide / 2).toFixed(1)}"
          y="${(cellBottom + 12).toFixed(1)}" text-anchor="middle"
          font-size="9" font-family="Georgia,serif"
          fill="${MUTED}">${stem.label}</text>
  </g>`);
}

// rulers in the 0.5 in margins: bottom across the drawing width, side down
const bottom = [];
bottom.push(`<line x1="${MARGIN}" y1="1070" x2="${W - MARGIN}" y2="1070"
      stroke="${MUTED}" stroke-width="0.8"/>`);
for (let k = 0; k < 16; k++) {
  const x = MARGIN + 50 * k;
  const h = k % 2 === 0 ? 9 : 5;
  bottom.push(`<line x1="${x}" y1="1070" x2="${x}" y2="${1070 - h}"
      stroke="${MUTED}" stroke-width="0.7"/>`);
  if (k % 2 === 0) {
    bottom.push(`<text x="${x}" y="1090" text-anchor="middle" font-size="9"
        font-family="ui-monospace,Menlo,monospace"
        fill="${MUTED}">${k / 2}</text>`);
  }
}
bottom.push(`<text x="${W - MARGIN}" y="1090" text-anchor="middle"
      font-size="9" font-family="ui-monospace,Menlo,monospace"
      fill="${MUTED}">7.5</text>`);
bottom.push(`<text x="${W - MARGIN + 14}" y="1090" font-size="9"
      font-family="ui-monospace,Menlo,monospace"
      fill="${MUTED}">in</text>`);

const side = [];
side.push(`<line x1="30" y1="${MARGIN}" x2="30" y2="${H - MARGIN}"
      stroke="${MUTED}" stroke-width="0.8"/>`);
for (let k = 0; k < 21; k++) {
  const y = MARGIN + 50 * k;
  const w = k % 2 === 0 ? 9 : 5;
  side.push(`<line x1="30" y1="${y}" x2="${30 + w}" y2="${y}"
      stroke="${MUTED}" stroke-width="0.7"/>`);
  if (k % 2 === 0) {
    side.push(`<text x="22" y="${y + 3}" text-anchor="end" font-size="9"
        font-family="ui-monospace,Menlo,monospace"
        fill="${MUTED}">${k / 2}</text>`);
  }
}

const title = `three stems · ${data.stems
  .map((s) => `${s.label} ${s.preset}`)
  .join(" · ")}`;
const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="8.5in" height="11in" viewBox="0 0 ${W} ${H}">
  <rect x="0" y="0" width="${W}" height="${H}" fill="#fff"/>
  <text x="50" y="32" font-family="Georgia,serif" font-size="12"
        fill="${MUTED}">${title}</text>
  ${groups.join("\n  ")}
  ${bottom.join("\n  ")}
  ${side.join("\n  ")}
</svg>
`;

const html = `<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Stems a, b, c — 8.5 × 11</title>
<style>
@page { size: 8.5in 11in; margin: 0; }
html, body { margin: 0; background: #e6e0d2; }
.sheet { width: 8.5in; height: 11in; margin: 18px auto; background: #fff; }
.sheet svg { display: block; width: 100%; height: 100%; }
@media print { body { background: #fff; } .sheet { margin: 0; } }
</style></head><body>
<div class="sheet">
${svg}
</div>
</body></html>
`;

fs.writeFileSync(OUT, svg);
fs.writeFileSync(HTML, html);
console.log(OUT);
console.log(HTML);
