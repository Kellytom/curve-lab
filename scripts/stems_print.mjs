// Render the three-stem print sheet from the geometry JSON, in millimetres.
//
//   node scripts/stems_print.mjs
//
// The JSON is produced by scripts/stems_print.py.  The page is 215.9 x 279.4 mm
// (8.5 x 11 in), 12.7 mm margins, no page border.  One SVG unit is one mm.

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
const DOT = "#b23a2b";
const VASE = "#c9a441";
const VASE_EDGE = "#a8852f";

const STEM_STROKE = 0.46;   // ~1.3 pt
const DOT_R = 0.6;
const GUIDE_W = 0.2;
const LABEL_FONT = 2.4;
const TITLE_FONT = 3.0;
const RULER_FONT = 2.2;
const TICK_MAJOR = 2.3;
const TICK_MINOR = 1.3;

const data = JSON.parse(fs.readFileSync(DATA, "utf8"));
const W = data.page.width_mm;
const H = data.page.height_mm;
const MARGIN = data.page.margin_mm;

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
  const cellX = stem.cell.x_mm;
  const cellBottom = stem.cell.bottom_mm;
  const cellSide = stem.cell.side_mm;
  const cellTop = cellBottom - cellSide;
  const d = "M " + stem.points_page_mm
    .map(([x, y]) => `${x.toFixed(2)} ${y.toFixed(2)}`)
    .join(" L ");
  const [sx, sy] = stem.start_page_mm;
  const [ex, ey] = stem.end_page_mm;
  groups.push(`<g id="stem-${stem.label}">
    <path d="${squirclePath(cellX + cellSide / 2, cellTop + cellSide / 2,
                            cellSide / 2)}"
          fill="${VASE}" stroke="${VASE_EDGE}" stroke-width="${GUIDE_W}"/>
    <path d="${d}" fill="none" stroke="${INK}" stroke-width="${STEM_STROKE}"
          stroke-linejoin="round" stroke-linecap="round"/>
    <circle cx="${sx.toFixed(2)}" cy="${sy.toFixed(2)}" r="${DOT_R}"
            fill="none" stroke="${DOT}" stroke-width="0.25"/>
    <circle cx="${ex.toFixed(2)}" cy="${ey.toFixed(2)}" r="${DOT_R}"
            fill="none" stroke="${DOT}" stroke-width="0.25"/>
    <text x="${(cellX + cellSide / 2).toFixed(1)}"
          y="${(cellBottom + 3).toFixed(1)}" text-anchor="middle"
          font-size="${LABEL_FONT}" font-family="Georgia,serif"
          fill="${MUTED}">${stem.label}</text>
  </g>`);
}

// rulers in the 12.7 mm margins: bottom across the drawing width, side down
const bottom = [];
bottom.push(`<line x1="${MARGIN}" y1="271.8" x2="${W - MARGIN}" y2="271.8"
      stroke="${MUTED}" stroke-width="0.2"/>`);
for (let mm = 0; mm <= 190; mm += 5) {
  const x = MARGIN + mm;
  const h = mm % 20 === 0 ? TICK_MAJOR : TICK_MINOR;
  bottom.push(`<line x1="${x}" y1="271.8" x2="${x}" y2="${271.8 - h}"
      stroke="${MUTED}" stroke-width="0.18"/>`);
  if (mm % 20 === 0) {
    bottom.push(`<text x="${x}" y="276.5" text-anchor="middle"
        font-size="${RULER_FONT}" font-family="ui-monospace,Menlo,monospace"
        fill="${MUTED}">${mm}</text>`);
  }
}
bottom.push(`<text x="${MARGIN + 190}" y="276.5" text-anchor="middle"
      font-size="${RULER_FONT}" font-family="ui-monospace,Menlo,monospace"
      fill="${MUTED}">190</text>`);
bottom.push(`<text x="${W - MARGIN + 2.5}" y="276.5" font-size="${RULER_FONT}"
      font-family="ui-monospace,Menlo,monospace"
      fill="${MUTED}">mm</text>`);

const side = [];
side.push(`<line x1="7.6" y1="${MARGIN}" x2="7.6" y2="${H - MARGIN}"
      stroke="${MUTED}" stroke-width="0.2"/>`);
for (let mm = 0; mm <= 254; mm += 5) {
  const y = MARGIN + mm;
  const w = mm % 20 === 0 ? TICK_MAJOR : TICK_MINOR;
  side.push(`<line x1="7.6" y1="${y}" x2="${7.6 + w}" y2="${y}"
      stroke="${MUTED}" stroke-width="0.18"/>`);
  if (mm % 20 === 0) {
    side.push(`<text x="5.2" y="${y + 0.8}" text-anchor="end"
        font-size="${RULER_FONT}" font-family="ui-monospace,Menlo,monospace"
        fill="${MUTED}">${mm}</text>`);
  }
}
side.push(`<text x="5.2" y="${MARGIN + 254 + 0.8}" text-anchor="end"
      font-size="${RULER_FONT}" font-family="ui-monospace,Menlo,monospace"
      fill="${MUTED}">254</text>`);
side.push(`<text x="3.2" y="${MARGIN - 1.2}" font-size="${RULER_FONT}"
      font-family="ui-monospace,Menlo,monospace"
      fill="${MUTED}">mm</text>`);

const title = `three stems · ${data.stems
  .map((s) => `${s.label} ${s.preset}`)
  .join(" · ")}`;
const svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="215.9mm" height="279.4mm"
     viewBox="0 0 215.9 279.4">
  <rect x="0" y="0" width="${W}" height="${H}" fill="#fff"/>
  <text x="12.7" y="8" font-family="Georgia,serif" font-size="${TITLE_FONT}"
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
