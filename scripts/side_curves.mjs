// The side-curve sandbox: a curve related to the spine by the same construction, not a
// normal offset. This slice uses a direct similarity — scale s and rotation φ about the
// spine's bounding-box centre c — with live sliders, and measures it beside today's width rail.
//
//   node scripts/side_curves.mjs
//   http://127.0.0.1:4321/workbench/side-curves.html
//
// A similarity of a smooth spine is smooth. The gap is proportional, not constant:
//   q = c + s·R(φ)·(p − c)
//   |q − p| = |(sR − I)(p − c)|;  φ=0 → |s−1|·|p−c|;  s=1 → 2 sin(φ/2)·|p−c|.

import { createRequire } from "node:module";
import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";

const require = createRequire(import.meta.url);
const P = require("../workbench/plate_math.js");
const ROOT = path.resolve(import.meta.dirname, "..");
const registry = JSON.parse(readFileSync(path.join(ROOT, "workbench", "curve-registry.json"), "utf8"));

const CURVES = ["c-0269", "c-0273", "c-0350"];
const round = (value) => Number(Number(value).toFixed(2));

const spineOf = (record) => {
  if (record.speedX?.length || record.speedY?.length) {
    return P.spine(record.speedX, record.speedY, 700).map((s) => [s.x, s.y]);
  }
  const [x0, y0, x1, y1] = P.bbox(record.path);
  const size = Math.hypot(x1 - x0, y1 - y0) || 1;
  return P.refinePath(record.path, size / 900);
};

const turns = (points) => {
  let over10 = 0, over20 = 0;
  for (let i = 1; i < points.length - 1; i += 1) {
    const ax = points[i][0] - points[i - 1][0], ay = points[i][1] - points[i - 1][1];
    const bx = points[i + 1][0] - points[i][0], by = points[i + 1][1] - points[i][1];
    const t = Math.abs(Math.atan2(ax * by - ay * bx, ax * bx + ay * by));
    if (t > 0.17) over10 += 1;
    if (t > 0.35) over20 += 1;
  }
  return { over10, over20 };
};

const data = [];
for (const uid of CURVES) {
  const record = registry.curves.find((row) => row.uid === uid);
  const spine = spineOf(record);
  const group = P.pathGroup(record.path, { widthPercent: 1.5, plus: 2, minus: 2, profile: "bow" });
  const rails = group ? group.paths.slice(1) : [];
  const all = [...spine, ...rails.flat()];
  const [x0, y0, x1, y1] = P.bbox(all);
  const size = Math.hypot(x1 - x0, y1 - y0) || 1;
  data.push({
    uid, name: record.name,
    center: [round((x0 + x1) / 2), round((y0 + y1) / 2)],
    size: round(size),
    box: [round(x0), round(y0), round(x1), round(y1)],
    spine: spine.map(([x, y]) => [round(x), round(y)]),
    rails: rails.map((rail) => rail.map(([x, y]) => [round(x), round(y)])),
    turns: { spine: turns(spine), rail: rails.length ? turns(rails[0]) : null },
  });
  const t = data.at(-1).turns;
  console.log(`${uid} ${record.name}: spine ${t.spine.over10} turns>10°, width rail ${t.rail?.over10}`);
}

const html = `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>side curves — algorithmic partners</title>
<style>
body{margin:0;padding:24px;background:#faf8f2;color:#26221c;font:14px/1.5 system-ui,sans-serif}
h1{font-size:20px;margin:0 0 4px} .lead{color:#6b5b46;max-width:78ch}
.formula{background:#fffef9;border:1px solid #e6dccb;padding:12px 16px;margin:16px 0;font:13px/1.7 ui-monospace,Menlo,monospace;white-space:pre-wrap}
.grid{display:grid;grid-template-columns:minmax(0,1fr) 320px;gap:22px;align-items:start}
@media (max-width:900px){.grid{grid-template-columns:1fr}}
.picture{background:#fffef9;border:1px solid #eee3d3;padding:8px}
svg{width:100%;height:auto;display:block}
.controls{font:13px/1.6 ui-monospace,Menlo,monospace}
.controls label{display:grid;grid-template-columns:7rem 1fr 3.5rem;gap:8px;align-items:center;margin:0 0 10px}
.controls output{text-align:right}
.tabs{display:flex;gap:6px;margin:0 0 12px;flex-wrap:wrap}
.tabs button{font:12px/1.4 ui-monospace,Menlo,monospace;padding:4px 8px;background:#fffef9;border:1px solid #e6dccb;cursor:pointer}
.tabs button.on{background:#3f3a33;color:#faf8f2}
table{border-collapse:collapse;font:12px/1.5 ui-monospace,Menlo,monospace;margin-top:12px}
th,td{text-align:left;padding:3px 12px 3px 0;border-bottom:1px solid #eee3d3}
th{color:#6b5b46}
</style></head><body>
<h1>Side curves: algorithmic partners</h1>
<p class="lead">The spine and a curve related to it by a <b>direct similarity</b> — not a width
offset — with today's width rail for comparison. A similarity of a smooth spine is smooth; the
width rail adds the spine's curvature kinks to the edge. The gap is proportional, not constant;
the sliders make that visible.</p>
<div class="formula">q = c + s · R(φ) · (p − c)
R(φ) = [ cos φ  −sin φ ]
       [ sin φ   cos φ ]

q_x = c_x + s[(p_x − c_x) cos φ − (p_y − c_y) sin φ]
q_y = c_y + s[(p_x − c_x) sin φ + (p_y − c_y) cos φ]

gap(p) = |q − p| = |(sR − I)(p − c)|
  φ = 0:  gap = |s − 1| · |p − c|          (proportional to the radius)
  s = 1:  gap = 2 sin(φ/2) · |p − c|      (also proportional; zero at c)
c = the spine's bounding-box centre; s = scale; φ = rotation.</div>
<div class="tabs" id="tabs"></div>
<div class="grid">
  <div class="picture" id="picture"></div>
  <div class="controls">
    <label>scale s <input id="scale" type="range" min="0.80" max="1.20" step="0.005" value="0.94"><output id="scale-out">0.940</output></label>
    <label>rotation φ° <input id="rot" type="range" min="-15" max="15" step="0.5" value="0"><output id="rot-out">0.0</output></label>
    <label>centre <input id="centre" type="range" min="0" max="1" step="0.05" value="0.5"><output id="centre-out">0.50</output></label>
    <label>stroke <select id="stroke"><option value="dots" selected>dots</option><option value="line">line</option></select></label>
    <label>dot r px <input id="dot" type="range" min="0.6" max="2.4" step="0.1" value="1.6"><output id="dot-out">1.6</output></label>
    <p class="lead" style="font-size:12px">Centre moves along the bounding box's x axis:
      0.5 is its middle, 0 is the left edge, 1 the right. The gap is zero at the centre.</p>
    <table id="metrics"></table>
  </div>
</div>
<p class="lead" style="margin-top:24px">Generated by <code>scripts/side_curves.mjs</code>.
The rail is the plate's width law at 1.5 %, plus 2, minus 2, bow.</p>
<script>
const DATA = ${JSON.stringify(data)};
const state = { index: 0, s: 0.94, phi: 0, centreMix: 0.5, dots: true, dot: 1.6 };
const byId = (id) => document.getElementById(id);
const styleOf = () => ({ spine: "#2b2b2b", rail: "#b9b1a2", partner: "#8a3b2a" });

function centreOf(entry) {
  const [x0, y0, x1] = entry.box;
  return [x0 + (x1 - x0) * state.centreMix, (entry.box[1] + entry.box[3]) / 2];
}
function transform(points, c, s, phi) {
  const a = (phi * Math.PI) / 180, co = Math.cos(a), si = Math.sin(a);
  return points.map(([x, y]) => {
    const dx = s * (x - c[0]), dy = s * (y - c[1]);
    return [c[0] + dx * co - dy * si, c[1] + dx * si + dy * co];
  });
}
/* a similarity preserves every turn exactly, so the partner states the spine's own count */
function draw() {
  const entry = DATA[state.index];
  const c = centreOf(entry);
  const partner = transform(entry.spine, c, state.s, state.phi);
  const [x0, y0, x1, y1] = entry.box;
  const pad = 0.06 * Math.max(x1 - x0, y1 - y0);
  const W = 760, k = (W * 0.96) / (x1 - x0 + 2 * pad || 1);
  const H = Math.max(260, Math.round((y1 - y0 + 2 * pad) * k));
  const toD = (points) => points.map(([x, y], i) =>
    (i ? "L" : "M") + ((x - x0 + pad) * k).toFixed(1) + "," +
    (H - (y - y0 + pad) * k).toFixed(1)).join("");
  const colour = styleOf();
  // Dots without Béziers: a zero-length dash with a round cap, spaced closer than the dot
  // diameter, lays overlapping dots along the exact polyline. No curve fitting, no smoothing
  // of the geometry; only the drawn stroke.
  const stroke = (radius) => state.dots
    ? ' stroke-width="' + (2 * radius).toFixed(2) + '" stroke-linecap="round" stroke-dasharray="0.01 ' +
      (radius * 1.05).toFixed(2) + '"'
    : ' stroke-width="' + (2 * radius * 0.55).toFixed(2) +
      '" stroke-linecap="round" stroke-linejoin="round"';
  const paths = [
    ...entry.rails.map((rail) => '<path d="' + toD(rail) + '" fill="none" stroke="' + colour.rail +
      '" opacity="0.6"' + stroke(state.dot * 0.7) + '/>'),
    '<path d="' + toD(entry.spine) + '" fill="none" stroke="' + colour.spine + '"' + stroke(state.dot) + '/>',
    '<path d="' + toD(partner) + '" fill="none" stroke="' + colour.partner + '"' + stroke(state.dot) + '/>',
  ];
  byId("picture").innerHTML = '<svg viewBox="0 0 ' + W + ' ' + H + '" role="img">' + paths.join("") + '</svg>';

  const gaps = partner.map((p, i) => Math.hypot(p[0] - entry.spine[i][0], p[1] - entry.spine[i][1]));
  const pct = (v) => (100 * v / entry.size).toFixed(2);
  const at = entry.turns;
  byId("metrics").innerHTML =
    '<tr><th></th><th>turns &gt;10°</th><th>&gt;20°</th><th>gap min / mean / max %</th></tr>' +
    '<tr><td>' + entry.uid + '</td><td>' + at.spine.over10 + '</td><td>' + at.spine.over20 + '</td><td>spine</td></tr>' +
    '<tr><td>width rail</td><td>' + (at.rail?.over10 ?? "—") + '</td><td>' + (at.rail?.over20 ?? "—") + '</td><td>0.75 / 1.50 / 3.00</td></tr>' +
    '<tr><td>similarity</td><td>' + at.spine.over10 + '</td><td>' + at.spine.over20 + '</td><td>' +
      pct(Math.min(...gaps)) + ' / ' + pct(gaps.reduce((a,b)=>a+b,0)/gaps.length) + ' / ' + pct(Math.max(...gaps)) + '</td></tr>';
}
function wire() {
  const tabs = byId("tabs");
  DATA.forEach((entry, i) => {
    const button = document.createElement("button");
    button.textContent = entry.uid + " " + entry.name;
    button.addEventListener("click", () => {
      state.index = i;
      [...tabs.children].forEach((item, j) => item.classList.toggle("on", j === i));
      draw();
    });
    if (i === 0) button.classList.add("on");
    tabs.appendChild(button);
  });
  byId("scale").addEventListener("input", (event) => {
    state.s = Number(event.target.value);
    byId("scale-out").value = state.s.toFixed(3);
    draw();
  });
  byId("rot").addEventListener("input", (event) => {
    state.phi = Number(event.target.value);
    byId("rot-out").value = state.phi.toFixed(1);
    draw();
  });
  byId("centre").addEventListener("input", (event) => {
    state.centreMix = Number(event.target.value);
    byId("centre-out").value = state.centreMix.toFixed(2);
    draw();
  });
  byId("stroke").addEventListener("change", (event) => {
    state.dots = event.target.value === "dots";
    draw();
  });
  byId("dot").addEventListener("input", (event) => {
    state.dot = Number(event.target.value);
    byId("dot-out").value = state.dot.toFixed(1);
    draw();
  });
  draw();
}
wire();
</script>
</body></html>`;

writeFileSync(path.join(ROOT, "workbench", "side-curves.html"), html);
console.log("wrote workbench/side-curves.html");
