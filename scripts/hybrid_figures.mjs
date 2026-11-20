// One figure per hybrid candidate, drawn by the app's own figure builder.
//
//   node scripts/hybrid_figures.mjs
//
// Reads workbench/hybrids.json (written by scripts/hybrid_figures.py) and writes
// app/public/hybrid-figures/<id>.svg with `figureSvg` — the same axes, grid, legend and
// cubic Bézier chain as Fig. 9 on /prime-mover/. No second SVG writer.

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { figureSvg } from "../app/src/lib/plot-figure.js";

const ROOT = path.resolve(import.meta.dirname, "..");
const DATA = path.join(ROOT, "workbench", "hybrids.json");
const OUT = path.join(ROOT, "app", "public", "hybrid-figures");
mkdirSync(OUT, { recursive: true });

const data = JSON.parse(readFileSync(DATA, "utf8"));
let written = 0;
for (const row of data.candidates) {
  if (!row.points || row.points.length < 2) continue;
  const xs = row.points.map(([x]) => x);
  const ys = row.points.map(([, y]) => y);
  const svg = figureSvg({
    key: row.id,
    title: row.id,
    equation: row.formula?.plain || "",
    legend: [{ label: `${row.crossings} crossing pairs`, colour: "#2f6fa8" }],
    paths: [{ name: row.id, colour: "#2f6fa8", points: row.points }],
    stations: [],
    bounds: [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)],
    samples: row.points.length,
  }, { width: 220 });
  // figureSvg is written for a page (width 100%); a file used by <img> needs its own
  // intrinsic size, so the viewBox numbers become width and height.
  const [, , vw, vh] = svg.match(/viewBox="([^"]+)"/)[1].split(/\s+/).length === 4
    ? svg.match(/viewBox="([^"]+)"/)[1].split(/\s+/)
    : [];
  const sized = svg
    .replace('width="100%"', `width="${vw || 220}" height="${vh || 220}"`)
    .replace(' style="height:auto"', "")
    // a file used by <img> is a standalone document and needs its namespace
    .replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" ');
  writeFileSync(path.join(OUT, `${row.id}.svg`), sized);
  written += 1;
}
console.log(`wrote ${written} figures with figureSvg`);
