// The side-curve sandbox: a curve related to the spine by the same construction, not a
// normal offset. This first slice tries the simplest algorithmic relation — a similarity
// (scale and rotation about the centre) — beside today's width rail, and measures both.
//
//   node scripts/side_curves.mjs
//   open /workbench/side-curves.html  (the app serves it)
//
// The point is the smoothness: a similarity of a smooth spine is smooth, while a width rail
// amplifies the spine's curvature into kinks. The gap is reported honestly: a similarity
// holds a *proportional* gap, not a constant width.

import { createRequire } from "node:module";
import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";

const require = createRequire(import.meta.url);
const P = require("../workbench/plate_math.js");
const ROOT = path.resolve(import.meta.dirname, "..");
const registry = JSON.parse(readFileSync(path.join(ROOT, "workbench", "curve-registry.json"), "utf8"));

const CURVES = ["c-0269", "c-0273", "c-0350"];
const SCALED = 0.94;          // 6 % smaller about the centre
const ROTATED = 2;            // degrees about the centre

const spineOf = (record) => {
  if (record.speedX?.length || record.speedY?.length) {
    return P.spine(record.speedX, record.speedY, 500).map((s) => [s.x, s.y]);
  }
  const [x0, y0, x1, y1] = P.bbox(record.path);
  const size = Math.hypot(x1 - x0, y1 - y0) || 1;
  return P.refinePath(record.path, size / 700);
};

function transform(points, scale, degrees) {
  const [x0, y0, x1, y1] = P.bbox(points);
  const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2;
  const a = (degrees * Math.PI) / 180, c = Math.cos(a), s = Math.sin(a);
  return points.map(([x, y]) => {
    const dx = scale * (x - cx), dy = scale * (y - cy);
    return [cx + dx * c - dy * s, cy + dx * s + dy * c];
  });
}

function turns(points) {
  let over10 = 0, over20 = 0, worst = 0;
  for (let i = 1; i < points.length - 1; i += 1) {
    const ax = points[i][0] - points[i - 1][0], ay = points[i][1] - points[i - 1][1];
    const bx = points[i + 1][0] - points[i][0], by = points[i + 1][1] - points[i][1];
    const t = Math.abs(Math.atan2(ax * by - ay * bx, ax * bx + ay * by));
    if (t > 0.17) over10 += 1;
    if (t > 0.35) over20 += 1;
    worst = Math.max(worst, t);
  }
  return { over10, over20, worst: (worst * 180) / Math.PI };
}

const panels = [];
for (const uid of CURVES) {
  const record = registry.curves.find((row) => row.uid === uid);
  const spine = spineOf(record);
  const group = P.pathGroup(record.path, { widthPercent: 1.5, plus: 2, minus: 2, profile: "bow" });
  const rails = group ? group.paths.slice(1) : [];
  const scaled = transform(spine, SCALED, 0);
  const rotated = transform(spine, 1, ROTATED);
  const [x0, y0, x1, y1] = P.bbox([...spine, ...rails.flat(), ...scaled, ...rotated]);
  const size = Math.hypot(x1 - x0, y1 - y0) || 1;
  const gaps = (partner) => {
    const d = spine.map((p, i) => Math.hypot(p[0] - partner[i][0], p[1] - partner[i][1]));
    return { min: Math.min(...d), max: Math.max(...d), mean: d.reduce((a, b) => a + b, 0) / d.length };
  };
  const pct = (v) => (100 * v) / size;
  panels.push({
    uid, name: record.name, spine, rails, scaled, rotated, box: [x0, y0, x1, y1],
    size,
    m: {
      spine: turns(spine),
      rail: rails.length ? turns(rails[0]) : null,
      scaled: { ...turns(scaled), gap: gaps(scaled) },
      rotated: { ...turns(rotated), gap: gaps(rotated) },
    },
    pct,
  });
  console.log(`${uid} ${record.name}: spine ${panels.at(-1).m.spine.over10} turns>10°, ` +
    `rail ${panels.at(-1).m.rail?.over10}, scaled ${panels.at(-1).m.scaled.over10} ` +
    `(gap ${pct(panels.at(-1).m.scaled.gap.min).toFixed(2)}–${pct(panels.at(-1).m.scaled.gap.max).toFixed(2)} %)`);
}

const draw = (points, box, colour, width, dash = "") => {
  const [x0, y0, x1, y1] = box;
  const W = 320, k = (W * 0.94) / (x1 - x0 || 1);
  const H = Math.max(120, Math.round((y1 - y0) * k));
  const d = points.map(([x, y], i) =>
    `${i ? "L" : "M"}${(10 + (x - x0) * k).toFixed(1)},${(H - 10 - (y - y0) * k).toFixed(1)}`).join("");
  return { d, H, W, colour, width, dash };
};

const panelSvg = (panel, parts) => {
  const W = 320, k = (W * 0.94) / (panel.box[2] - panel.box[0] || 1);
  const H = Math.max(120, Math.round((panel.box[3] - panel.box[1]) * k));
  const toD = (points) => points.map(([x, y], i) =>
    `${i ? "L" : "M"}${(10 + (x - panel.box[0]) * k).toFixed(1)},${(H - 10 - (y - panel.box[1]) * k).toFixed(1)}`).join("");
  const body = parts.map(([points, colour, width, dash]) =>
    `<path d="${toD(points)}" fill="none" stroke="${colour}" stroke-width="${width}"` +
    `${dash ? ` stroke-dasharray="${dash}"` : ""} stroke-linecap="round" stroke-linejoin="round"/>`).join("");
  return `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img">${body}</svg>`;
};

const cards = panels.map((panel) => {
  const p = (v) => panel.pct(v).toFixed(2);
  return `<section class="curve">
    <h2><code>${panel.uid}</code> ${panel.name}</h2>
    <div class="panels">
      <figure><figcaption>spine</figcaption>${panelSvg(panel, [[panel.spine, "#2b2b2b", 1.4]])}</figure>
      <figure><figcaption>today: width rail</figcaption>${panelSvg(panel, [
        [panel.spine, "#cfc6b6", 1], ...panel.rails.map((rail) => [rail, "#8a6a1f", 1.2])])}</figure>
      <figure><figcaption>similarity ×${SCALED}</figcaption>${panelSvg(panel, [
        [panel.spine, "#cfc6b6", 1], [panel.scaled, "#8a3b2a", 1.6]])}</figure>
      <figure><figcaption>rotation ${ROTATED}°</figcaption>${panelSvg(panel, [
        [panel.spine, "#cfc6b6", 1], [panel.rotated, "#2f5d8a", 1.6]])}</figure>
    </div>
    <table>
      <tr><th></th><th>turns &gt;10°</th><th>&gt;20°</th><th>gap min / mean / max % of size</th></tr>
      <tr><td>spine</td><td>${panel.m.spine.over10}</td><td>${panel.m.spine.over20}</td><td>—</td></tr>
      <tr><td>width rail</td><td>${panel.m.rail?.over10 ?? "—"}</td><td>${panel.m.rail?.over20 ?? "—"}</td><td>0.75 / 1.5 / 3.0 (the law)</td></tr>
      <tr><td>similarity ×${SCALED}</td><td>${panel.m.scaled.over10}</td><td>${panel.m.scaled.over20}</td>
        <td>${p(panel.m.scaled.gap.min)} / ${p(panel.m.scaled.gap.mean)} / ${p(panel.m.scaled.gap.max)}</td></tr>
      <tr><td>rotation ${ROTATED}°</td><td>${panel.m.rotated.over10}</td><td>${panel.m.rotated.over20}</td>
        <td>${p(panel.m.rotated.gap.min)} / ${p(panel.m.rotated.gap.mean)} / ${p(panel.m.rotated.gap.max)}</td></tr>
    </table>
  </section>`;
}).join("");

const html = `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>side curves — algorithmic partners</title>
<style>
body{margin:0;padding:24px;background:#faf8f2;color:#26221c;font:14px/1.5 system-ui,sans-serif}
h1{font-size:20px;margin:0 0 4px} .lead{color:#6b5b46;max-width:70ch}
.curve{margin:28px 0 0;border-top:1px solid #e6dccb;padding-top:16px}
.panels{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}
figure{margin:0;background:#fffef9;border:1px solid #eee3d3;padding:6px}
figcaption{font:12px/1.4 ui-monospace,Menlo,monospace;color:#6b5b46;margin:0 0 4px}
svg{width:100%;height:auto;display:block}
table{margin-top:10px;border-collapse:collapse;font:12px/1.5 ui-monospace,Menlo,monospace}
th,td{text-align:left;padding:2px 12px 2px 0;border-bottom:1px solid #eee3d3}
th{color:#6b5b46;font-weight:600}
</style></head><body>
<h1>Side curves: algorithmic partners</h1>
<p class="lead">The same spine with a curve related by a similarity, beside today's width rail.
A similarity of a smooth spine is smooth; the width rail amplifies the spine's curvature into
kinks. The gap is proportional, not constant — the trade this sandbox is for. Scale
${SCALED}, rotation ${ROTATED}°.</p>
${cards}
<p class="lead" style="margin-top:24px">Generated by <code>scripts/side_curves.mjs</code>.</p>
</body></html>`;

writeFileSync(path.join(ROOT, "workbench", "side-curves.html"), html);
console.log("wrote workbench/side-curves.html");
