// Side curves as per-construction partners — the only rule.
//
// A side curve is not a width offset and not a universal similarity: it is the same
// construction as the spine with one parameter reduced.
//
//   mobile  P(t) = r1(cos t, sin t) + r2(cos kt, sin kt);  r -> r - d
//   hybrid  station = k * P(x, y) * (C(t)^p, S(t)^q);      k -> k - d
//   double  the wonk half at radius r -> r - d, then mirrored by the same rule
//
// The construction centre is the origin; the partner is the spine scaled about it. The
// curve is drawn by d3's centripetal Catmull-Rom (the standard plotting curve), then the
// dot stroke (a thin layer) lays overlapping dots along that path. No hand-rolled offset,
// no normal estimate, no curvature cap.
//
//   node scripts/side_curves.mjs
//   http://127.0.0.1:4321/workbench/side-curves.html

import { createRequire } from "node:module";
import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";

const require = createRequire(import.meta.url);
const P = require("../workbench/plate_math.js");
const d3 = await import(new URL("../app/node_modules/d3/dist/d3.mjs", import.meta.url).href);
const ROOT = path.resolve(import.meta.dirname, "..");
const registry = JSON.parse(readFileSync(path.join(ROOT, "workbench", "curve-registry.json"), "utf8"));

const PARAMS = {
  "c-0269": {
    name: "arm length r → r − d",
    formula: "P_d(t) = (r − d)(cos t, sin t) + (r − d)(cos 8t/3, sin 8t/3) = (1 − d)·P(t)",
  },
  "c-0273": {
    name: "half radius r → r − d",
    formula: "the wonk-1 NW-1 half at radius r − d, then mirrored across y = x by the same rule",
  },
  "c-0350": {
    name: "middle weight k → k − d",
    formula: "station = k·P(x, y)·(C(t)^1, S(t)^4);  k → k − d, so station_d = (1 − d)·station",
  },
};

const round = (value) => Number(Number(value).toFixed(4));
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
for (const uid of ["c-0269", "c-0273", "c-0350"]) {
  const record = registry.curves.find((row) => row.uid === uid);
  const spine = spineOf(record);
  const [x0, y0, x1, y1] = P.bbox(spine);
  const size = Math.hypot(x1 - x0, y1 - y0) || 1;
  const pad = 0.06 * size;
  const W = 760;
  const k = (W * 0.96) / (x1 - x0 + 2 * pad || 1);
  const H = Math.max(260, Math.round((y1 - y0 + 2 * pad) * k));
  const project = ([x, y]) => [(x - x0 + pad) * k, H - (y - y0 + pad) * k];
  const line = d3.line().x((p) => p[0]).y((p) => p[1]).curve(d3.curveCatmullRom.alpha(0.5));
  const projected = spine.map(project);
  const [cx, cy] = project([0, 0]);
  data.push({
    uid, name: record.name,
    size: round(size),
    W, H,
    centre: [round(cx), round(cy)],
    d: line(projected),
    spine: spine.map(([x, y]) => [round(x), round(y)]),
    turns: turns(spine),
    param: PARAMS[uid],
  });
}

const html = `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>side curves — per-construction partners</title>
<style>
body{margin:0;padding:24px;background:#faf8f2;color:#26221c;font:14px/1.5 system-ui,sans-serif}
h1{font-size:20px;margin:0 0 4px} .lead{color:#6b5b46;max-width:80ch}
.rule{background:#fffef9;border:1px solid #e6dccb;padding:12px 16px;margin:16px 0;font:13px/1.7 ui-monospace,Menlo,monospace;white-space:pre-wrap}
.grid{display:grid;grid-template-columns:minmax(0,1fr) 320px;gap:22px;align-items:start}
@media (max-width:900px){.grid{grid-template-columns:1fr}}
.picture{background:#fffef9;border:1px solid #eee3d3;padding:8px}
svg{width:100%;height:auto;display:block}
.controls{font:13px/1.6 ui-monospace,Menlo,monospace}
.controls label{display:grid;grid-template-columns:7rem 1fr 3.5rem;gap:8px;align-items:center;margin:0 0 10px}
.controls output{text-align:right}
.construction{background:#fffef9;border:1px solid #e6dccb;padding:8px 10px;margin:0 0 12px;font:12px/1.6 ui-monospace,Menlo,monospace}
.tabs{display:flex;gap:6px;margin:0 0 12px;flex-wrap:wrap}
.tabs button{font:12px/1.4 ui-monospace,Menlo,monospace;padding:4px 8px;background:#fffef9;border:1px solid #e6dccb;cursor:pointer}
.tabs button.on{background:#3f3a33;color:#faf8f2}
table{border-collapse:collapse;font:12px/1.5 ui-monospace,Menlo,monospace;margin-top:12px}
th,td{text-align:left;padding:3px 12px 3px 0;border-bottom:1px solid #eee3d3}
th{color:#6b5b46}
</style></head><body>
<h1>Side curves: per-construction partners</h1>
<p class="lead">The side curve is the <b>same construction</b> as its spine with one parameter
reduced — no width offset, no normal estimate, no curvature cap. The curve is drawn by
d3's centripetal Catmull-Rom; the overlapping dots are only the stroke. The construction's
centre is the origin; the partner is the spine scaled about it.</p>
<div class="rule">mobile   P(t) = r1(cos t, sin t) + r2(cos kt, sin kt)      r → r − d
hybrid   station = k · P(x, y) · (C(t)^p, S(t)^q)          k → k − d
double   the wonk half at radius r, mirrored across y = x    r → r − d

The current curve states its own parameter below. For the mobile the gap is d·|P(t)|.</div>
<div class="tabs" id="tabs"></div>
<div class="grid">
  <div class="picture">
    <svg id="picture" viewBox="0 0 760 600" role="img" aria-label="side curve">
      <path id="spine" fill="none" stroke="#2b2b2b" vector-effect="non-scaling-stroke"/>
      <path id="partner" fill="none" stroke="#8a3b2a" vector-effect="non-scaling-stroke"/>
    </svg>
  </div>
  <div class="controls">
    <div class="construction" id="construction"></div>
    <label><span id="param-name">reduction d</span>
      <input id="d" type="range" min="0.01" max="0.20" step="0.01" value="0.06">
      <output id="d-out">0.060</output></label>
    <label>stroke <select id="stroke"><option value="dots" selected>dots</option><option value="line">line</option></select></label>
    <label>dot r px <input id="dot" type="range" min="0.6" max="2.4" step="0.1" value="1.6"><output id="dot-out">1.6</output></label>
    <table id="metrics"></table>
  </div>
</div>
<p class="lead" style="margin-top:24px">Generated by <code>scripts/side_curves.mjs</code>.
The width rail is not drawn: it was the hand-rolled offset, and the per-construction partner
replaces it.</p>
<script>
const DATA = ${JSON.stringify(data)};
const state = { index: 0, d: 0.06, dots: true, dot: 1.6 };
const byId = (id) => document.getElementById(id);
const paint = (node, radius) => {
  node.setAttribute("stroke-width", (state.dots ? 2 * radius : 2 * radius * 0.55).toFixed(2));
  node.setAttribute("stroke-linecap", "round");
  if (state.dots) {
    node.setAttribute("stroke-dasharray", "0.01 " + (radius * 1.05).toFixed(2));
    node.removeAttribute("stroke-linejoin");
  } else {
    node.removeAttribute("stroke-dasharray");
    node.setAttribute("stroke-linejoin", "round");
  }
};

function draw() {
  const entry = DATA[state.index];
  const s = 1 - state.d;
  const svg = byId("picture");
  svg.setAttribute("viewBox", "0 0 " + entry.W + " " + entry.H);
  const spine = byId("spine");
  const partner = byId("partner");
  spine.setAttribute("d", entry.d);
  partner.setAttribute("d", entry.d);
  const [cx, cy] = entry.centre;
  partner.setAttribute("transform",
    "translate(" + cx + " " + cy + ") scale(" + s.toFixed(4) + ") translate(" + (-cx) + " " + (-cy) + ")");
  paint(spine, state.dot);
  paint(partner, state.dot);

  byId("construction").innerHTML = '<b>' + entry.param.name + '</b><br>' + entry.param.formula;
  byId("param-name").textContent = entry.param.name;

  const gaps = entry.spine.map(([x, y]) => state.d * Math.hypot(x, y));
  const pct = (v) => (100 * v / entry.size).toFixed(2);
  byId("metrics").innerHTML =
    '<tr><th></th><th>turns &gt;10°</th><th>&gt;20°</th><th>gap min / mean / max %</th></tr>' +
    '<tr><td>spine</td><td>' + entry.turns.over10 + '</td><td>' + entry.turns.over20 + '</td><td>—</td></tr>' +
    '<tr><td>partner</td><td>' + entry.turns.over10 + '</td><td>' + entry.turns.over20 + '</td><td>' +
      pct(Math.min(...gaps)) + ' / ' + pct(gaps.reduce((a, b) => a + b, 0) / gaps.length) + ' / ' +
      pct(Math.max(...gaps)) + '</td></tr>';
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
  byId("d").addEventListener("input", (event) => {
    state.d = Number(event.target.value);
    byId("d-out").value = state.d.toFixed(3);
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
