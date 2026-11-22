// The row family's per-construction partners, at collection scale: a preview sheet.
//
// Each row curve is PH in its speed pair (u, v). The partner is the same construction with
// the speed scaled by (1 ∓ d), so the position scales by (1 ∓ d)² about the origin — no
// offset, no normal. This page renders the top row curves with a smaller (right) and a
// larger (left) partner, so the plates migration can be judged before it is switched.
//
//   node scripts/partner_preview.mjs
//   http://127.0.0.1:4321/workbench/partner-preview.html

import { createRequire } from "node:module";
import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";

const require = createRequire(import.meta.url);
const P = require("../workbench/plate_math.js");
const ROOT = path.resolve(import.meta.dirname, "..");
const registry = JSON.parse(readFileSync(path.join(ROOT, "workbench", "curve-registry.json"), "utf8"));
const exported = JSON.parse(readFileSync(path.join(ROOT, "data", "curves.json"), "utf8"));
const starsOf = new Map((exported.rows || []).map((row) => [row.uid, row.stars]));

const round = (value) => Number(Number(value).toFixed(4));
const turns = (points) => {
  let over10 = 0;
  for (let i = 1; i < points.length - 1; i += 1) {
    const ax = points[i][0] - points[i - 1][0], ay = points[i][1] - points[i - 1][1];
    const bx = points[i + 1][0] - points[i][0], by = points[i + 1][1] - points[i][1];
    if (Math.abs(Math.atan2(ax * by - ay * bx, ax * bx + ay * by)) > 0.35) over10 += 1;
  }
  return over10;
};

const allRows = registry.curves
  .filter((curve) => curve.kind === "rows" && (curve.speedX?.length || curve.speedY?.length))
  .sort((a, b) => (starsOf.get(b.uid) || 0) - (starsOf.get(a.uid) || 0) || a.uid.localeCompare(b.uid));
// one per family first, so the sheet shows the row families rather than twelve 10-star loops
const chosen = [];
const seenFamilies = new Set();
for (const curve of allRows) {
  const family = curve.family_id || curve.family || curve.uid;
  if (seenFamilies.has(family)) continue;
  seenFamilies.add(family);
  chosen.push(curve);
  if (chosen.length === 12) break;
}
for (const curve of allRows) {
  if (chosen.length === 12) break;
  if (!chosen.includes(curve)) chosen.push(curve);
}
const rows = chosen;

const data = rows.map((curve) => {
  const spine = P.spine(curve.speedX, curve.speedY, 500).map((s) => [s.x, s.y]);
  const [x0, y0, x1, y1] = P.bbox(spine);
  return {
    uid: curve.uid,
    name: curve.name,
    family: curve.family_id || curve.family || "",
    stars: starsOf.get(curve.uid) ?? null,
    size: round(Math.hypot(x1 - x0, y1 - y0) || 1),
    box: [round(x0), round(y0), round(x1), round(y1)],
    spine: spine.map(([x, y]) => [round(x), round(y)]),
    turns: turns(spine),
  };
});

const DR = 0.03; // the speed scale: right 1 − d, left 1 + d; position ×(1 ∓ d)²
const DL = 0.03;

const html = `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>partner preview — the row family: draft A</title>
<style>
body{margin:0;padding:24px;background:#faf8f2;color:#26221c;font:14px/1.5 system-ui,sans-serif}
h1{font-size:20px;margin:0 0 4px} .lead{color:#6b5b46;max-width:82ch}
.legend{display:flex;gap:18px;align-items:center;margin:12px 0 18px;font:12px/1.6 ui-monospace,Menlo,monospace}
.legend span{display:flex;align-items:center;gap:8px}
.swatch{display:inline-block;width:2.4rem;border-top:3pt solid}
.swatch.spine{border-color:#2b2b2b}.swatch.right{border-color:#8a3b2a}.swatch.left{border-color:#2f5d8a}
.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}
@media (max-width:900px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
.card{margin:0;padding:10px;background:#fffef9;border:1px solid #eee3d3}
.card h2{font-size:14px;margin:0;font-weight:600}
.card .meta{font:11px/1.5 ui-monospace,Menlo,monospace;color:#7a6a55;margin:0 0 6px}
.card .meta b{color:#8a6a1f}
.card svg{width:100%;height:auto;display:block}
.card .gap{font:11px/1.5 ui-monospace,Menlo,monospace;color:#5a4a36;margin:4px 0 0}
.card .axis path,.card .axis line{stroke:#e2d7c4}
.card .axis text{fill:#8a7a63;font:9px ui-monospace,Menlo,monospace}
</style></head><body>
<h1>The row family's partners — a preview</h1>
<p class="lead">The 212 row curves are PH in their speed pair (u, v). The partner is the same
construction with the speed scaled: right <b>speed × (1 − ${DR.toFixed(2)})</b>, left
<b>speed × (1 + ${DL.toFixed(2)})</b>; the position scales by the square about the origin.
No width offset, no normal estimate, no curvature cap. The top row curves by stars are shown;
the plates migration can be judged from this sheet before it is switched.</p>
<p class="lead" style="margin-top:-6px">Axes are in units of each curve's largest radius, so
the shapes compare and the construction centre stays at 0.</p>
<div class="legend">
  <span><i class="swatch spine"></i> spine</span>
  <span><i class="swatch right"></i> right partner (speed × ${(1 - DR).toFixed(2)})</span>
  <span><i class="swatch left"></i> left partner (speed × ${(1 + DL).toFixed(2)})</span>
  <span>the ends are closed with a cap line</span>
</div>
<div class="grid" id="grid"></div>
<p class="lead" style="margin-top:22px">Generated by <code>scripts/partner_preview.mjs</code>.
The pairs are the same construction, not parallel curves.</p>
<script src="/api/d3js"></script>
<script>
const DATA = ${JSON.stringify(data)};
const DR = ${DR}, DL = ${DL};
const W = 340, H = 260, M = { top: 12, right: 12, bottom: 26, left: 34 };
const sR = (1 - DR) ** 2, sL = (1 + DL) ** 2;
const grid = d3.select("#grid");

for (const entry of DATA) {
  const card = grid.append("div").attr("class", "card");
  const stars = entry.stars ? entry.stars + "/10" : "none";
  card.append("h2").text(entry.uid + " " + entry.name);
  card.append("p").attr("class", "meta").text(
    (entry.family || "rows") + " | stars " + stars + " | sharp turns over 20 deg: " + entry.turns);
  const svg = card.append("svg").attr("viewBox", "0 0 " + W + " " + H);
  // one scale per card: its largest radius, so the construction centre stays at 0
  const unit = Math.max(...entry.spine.map(([px, py]) => Math.hypot(px, py)), 1e-9);
  const points = [...entry.spine,
    ...entry.spine.map(([x, y]) => [x * sR, y * sR]),
    ...entry.spine.map(([x, y]) => [x * sL, y * sL]), [0, 0]].map(([x, y]) => [x / unit, y / unit]);
  const pad = 0.05 * Math.max(
    d3.max(points, (p) => p[0]) - d3.min(points, (p) => p[0]),
    d3.max(points, (p) => p[1]) - d3.min(points, (p) => p[1]), 1e-9);
  const x = d3.scaleLinear()
    .domain([d3.min(points, (p) => p[0]) - pad, d3.max(points, (p) => p[0]) + pad])
    .range([M.left, W - M.right]);
  const y = d3.scaleLinear()
    .domain([d3.min(points, (p) => p[1]) - pad, d3.max(points, (p) => p[1]) + pad])
    .range([H - M.bottom, M.top]);
  const axes = svg.append("g");
  axes.append("g").attr("class", "axis").attr("transform", "translate(0," + (H - M.bottom) + ")")
    .call(d3.axisBottom(x).ticks(3));
  axes.append("g").attr("class", "axis").attr("transform", "translate(" + M.left + ",0)")
    .call(d3.axisLeft(y).ticks(3));
  const line = d3.line().x((p) => x(p[0])).y((p) => y(p[1]))
    .curve(d3.curveCatmullRom.alpha(0.5));
  const dots = (node, colour) => node.attr("fill", "none").attr("stroke", colour)
    .attr("stroke-width", 2.2).attr("stroke-linecap", "round")
    .attr("stroke-dasharray", "0.01 1.5");
  const at = (s) => entry.spine.map(([px, py]) => [px * s / unit, py * s / unit]);
  dots(svg.append("path").attr("d", line(at(1))), "#2b2b2b");
  dots(svg.append("path").attr("d", line(at(sR))), "#8a3b2a");
  dots(svg.append("path").attr("d", line(at(sL))), "#2f5d8a");
  const cap = (point) => {
    const a = [x(point[0] * sR / unit), y(point[1] * sR / unit)];
    const b = [x(point[0] * sL / unit), y(point[1] * sL / unit)];
    svg.append("line").attr("x1", a[0]).attr("y1", a[1]).attr("x2", b[0]).attr("y2", b[1])
      .attr("stroke", "#6b5b46").attr("stroke-width", 1.8).attr("stroke-linecap", "round");
  };
  cap(entry.spine[0]);
  cap(entry.spine[entry.spine.length - 1]);
  const gap = (s) => {
    const values = entry.spine.map(([px, py]) => Math.abs(1 - s) * Math.hypot(px, py));
    return (100 * values.reduce((a, b) => a + b, 0) / values.length / entry.size).toFixed(2);
  };
  card.append("p").attr("class", "gap")
    .text("mean gap | right " + gap(sR) + " % | left " + gap(sL) + " % of the curve's size");
}
</script>
<div class="draft-a" style="position:fixed;right:.75rem;bottom:.75rem;z-index:9999;background:#1b1b1b;color:#fff;font:12px/1.4 system-ui,sans-serif;padding:.35rem .6rem;border-radius:.25rem;opacity:.9">draft A</div>
</body></html>`;

writeFileSync(path.join(ROOT, "workbench", "partner-preview.html"), html);
console.log("wrote workbench/partner-preview.html", rows.length, "rows");
