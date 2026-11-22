// Side curves as per-construction partners — the only rule.
//
// A side curve is not a width offset and not a universal similarity: it is the same
// construction as the spine with one parameter changed. The plotting is d3 in the browser
// (served from the app's installed bundle at /api/d3js): scales, axes, curves and cap lines
// are d3's; the overlapping dots are only the stroke.
//
//   row      speed rows (u, v)                        speed × (1 ∓ d)  → position × (1 ∓ d)²
//   mobile   P(t) = r1(cos t, sin t) + r2(cos kt, …)  r → r ∓ d
//   hybrid   station = k · P(x, y) · (C(t)^p, S(t)^q) k → k ∓ d
//   double   the wonk half at radius r, mirrored       r → r ∓ d
//
//   node scripts/side_curves.mjs
//   http://127.0.0.1:4321/workbench/side-curves.html

import { createRequire } from "node:module";
import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";

const require = createRequire(import.meta.url);
const P = require("../workbench/plate_math.js");
const ROOT = path.resolve(import.meta.dirname, "..");
const registry = JSON.parse(readFileSync(path.join(ROOT, "workbench", "curve-registry.json"), "utf8"));

const PARAMS = {
  "c-0001": {
    kind: "speed",
    name: "speed scale (1 ∓ d) · position (1 ∓ d)²",
    formula: "the same speed rows u, v scaled by (1 ∓ d); the position is scaled by (1 ∓ d)² about the origin. Right 1 − d_R, left 1 + d_L.",
  },
  "c-0269": {
    kind: "scale",
    name: "arm length r → r ∓ d",
    formula: "P_d(t) = (r ∓ d)(cos t, sin t) + (r ∓ d)(cos 8t/3, sin 8t/3) = (1 ∓ d)·P(t)",
  },
  "c-0273": {
    kind: "scale",
    name: "half radius r → r ∓ d",
    formula: "the wonk-1 NW-1 half at radius r ∓ d, then mirrored across y = x by the same rule",
  },
  "c-0350": {
    kind: "scale",
    name: "middle weight k → k ∓ d",
    formula: "station = k·P(x, y)·(C(t)^1, S(t)^4); k → k ∓ d, so station_d = (1 ∓ d)·station",
  },
};

const CURVES = ["c-0001", "c-0269", "c-0273", "c-0350"];
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
for (const uid of CURVES) {
  const record = registry.curves.find((row) => row.uid === uid);
  const spine = spineOf(record);
  const [x0, y0, x1, y1] = P.bbox(spine);
  data.push({
    uid, name: record.name,
    kind: PARAMS[uid].kind,
    size: round(Math.hypot(x1 - x0, y1 - y0) || 1),
    box: [round(x0), round(y0), round(x1), round(y1)],
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
.picture svg{width:100%;height:auto;display:block}
.picture .axis path,.picture .axis line{stroke:#d8cdbb}
.picture .axis text{fill:#7a6a55;font:10px ui-monospace,Menlo,monospace}
.picture .axis-label{fill:#6b5b46;font:11px ui-monospace,Menlo,monospace}
.controls{font:13px/1.6 ui-monospace,Menlo,monospace}
.controls label{display:grid;grid-template-columns:7rem 1fr 3.5rem;gap:8px;align-items:center;margin:0 0 10px}
.controls output{text-align:right}
.controls .toggle{display:flex;align-items:center;gap:8px;margin:0 0 10px}
.controls .toggle input{margin:0}
.construction{background:#fffef9;border:1px solid #e6dccb;padding:8px 10px;margin:0 0 12px;font:12px/1.6 ui-monospace,Menlo,monospace}
.tabs{display:flex;gap:6px;margin:0 0 12px;flex-wrap:wrap}
.tabs button{font:12px/1.4 ui-monospace,Menlo,monospace;padding:4px 8px;background:#fffef9;border:1px solid #e6dccb;cursor:pointer}
.tabs button.on{background:#3f3a33;color:#faf8f2}
.legend{display:flex;flex-direction:column;gap:4px;margin:0 0 14px;font:12px/1.6 ui-monospace,Menlo,monospace}
.legend > span{display:flex;align-items:center;gap:8px}
.swatch{display:inline-block;width:2.4rem;border-top:3pt solid;flex:none}
.swatch.spine{border-color:#2b2b2b}.swatch.right{border-color:#8a3b2a}.swatch.left{border-color:#2f5d8a}
.swatch.ends{border-color:#6b5b46}
table{border-collapse:collapse;font:12px/1.5 ui-monospace,Menlo,monospace;margin-top:12px}
th,td{text-align:left;padding:3px 12px 3px 0;border-bottom:1px solid #eee3d3}
th{color:#6b5b46}
</style></head><body>
<h1>Side curves: per-construction partners</h1>
<p class="lead">The side curves are the <b>same construction</b> as the spine with one parameter
changed: a smaller construction on the <b>right</b> (parameter − d_R) and a larger one on the
<b>left</b> (parameter + d_L). No width offset, no normal estimate, no curvature cap. d3 draws
the curves, axes and cap lines; the overlapping dots are only the stroke. The construction's
centre is the origin.</p>
<div class="rule">row      speed rows (u, v)                        speed × (1 ∓ d) → position × (1 ∓ d)²
mobile   P(t) = r1(cos t, sin t) + r2(cos kt, sin kt)   r → r ∓ d
hybrid   station = k · P(x, y) · (C(t)^p, S(t)^q)       k → k ∓ d
double   the wonk half at radius r, mirrored             r → r ∓ d

Right = the parameter reduced, left = increased, both about the construction centre (0, 0).
The current curve states its own parameter below.</div>
<div class="tabs" id="tabs"></div>
<div class="grid">
  <div class="picture"><svg id="picture" role="img" aria-label="side curves"></svg></div>
  <div class="controls">
    <div class="construction" id="construction"></div>
    <div class="legend">
      <span><i class="swatch spine"></i><span>spine</span></span>
      <span><i class="swatch right"></i><span>right · d_R <b id="dr-shown">0.040</b> · ×<b id="right-scale">0.960</b></span></span>
      <span><i class="swatch left"></i><span>left · d_L <b id="dl-shown">0.080</b> · ×<b id="left-scale">1.080</b></span></span>
      <span id="legend-ends"><i class="swatch ends"></i><span>the ends · one cap line each</span></span>
    </div>
    <label><span>right d_R</span>
      <input id="dr" type="range" min="0.01" max="0.20" step="0.01" value="0.04">
      <output id="dr-out">0.040</output></label>
    <label><span>left d_L</span>
      <input id="dl" type="range" min="0.01" max="0.20" step="0.01" value="0.08">
      <output id="dl-out">0.080</output></label>
    <label class="toggle"><input id="caps" type="checkbox" checked> close the ends</label>
    <label>stroke <select id="stroke"><option value="dots" selected>dots</option><option value="line">line</option></select></label>
    <label>dot r px <input id="dot" type="range" min="0.6" max="2.4" step="0.1" value="1.6"><output id="dot-out">1.6</output></label>
    <table id="metrics"></table>
  </div>
</div>
<p class="lead" style="margin-top:24px">Generated by <code>scripts/side_curves.mjs</code>.
The width rail is not drawn: it was the hand-rolled offset, and the per-construction partner
replaces it.</p>
<script src="/api/d3js"></script>
<script>
const DATA = ${JSON.stringify(data)};
const state = { index: 0, dR: 0.04, dL: 0.08, caps: true, dots: true, dot: 1.6 };
const byId = (id) => document.getElementById(id);
const W = 760, H = 520, M = { top: 22, right: 24, bottom: 40, left: 48 };

const svg = d3.select("#picture").attr("viewBox", "0 0 " + W + " " + H);
const gAxes = svg.append("g");
const gOrigin = svg.append("g");
const gCurves = svg.append("g");
const gCaps = svg.append("g");
const spine = gCurves.append("path").attr("id", "spine").attr("fill", "none").attr("stroke", "#2b2b2b")
  .attr("vector-effect", "non-scaling-stroke");
const right = gCurves.append("path").attr("id", "right").attr("fill", "none").attr("stroke", "#8a3b2a")
  .attr("vector-effect", "non-scaling-stroke");
const left = gCurves.append("path").attr("id", "left").attr("fill", "none").attr("stroke", "#2f5d8a")
  .attr("vector-effect", "non-scaling-stroke");
const capStart = gCaps.append("line").attr("id", "cap-start").attr("stroke", "#6b5b46").attr("stroke-width", 2.4)
  .attr("stroke-linecap", "round");
const capEnd = gCaps.append("line").attr("id", "cap-end").attr("stroke", "#6b5b46").attr("stroke-width", 2.4)
  .attr("stroke-linecap", "round");

const paint = (node, radius) => {
  node.attr("stroke-width", (state.dots ? 2 * radius : 2 * radius * 0.55).toFixed(2));
  node.attr("stroke-linecap", "round");
  if (state.dots) node.attr("stroke-dasharray", "0.01 " + (radius * 1.05).toFixed(2))
    .attr("stroke-linejoin", null);
  else node.attr("stroke-dasharray", null).attr("stroke-linejoin", "round");
};

function scalesFor(entry) {
  const [x0, y0, x1, y1] = entry.box;
  const sR = entry.kind === "speed" ? (1 - state.dR) ** 2 : 1 - state.dR;
  const sL = entry.kind === "speed" ? (1 + state.dL) ** 2 : 1 + state.dL;
  const points = [...entry.spine,
    ...entry.spine.map(([x, y]) => [x * sR, y * sR]),
    ...entry.spine.map(([x, y]) => [x * sL, y * sL]), [0, 0]];
  const pad = 0.06 * Math.max(x1 - x0, y1 - y0, 1);
  const x = d3.scaleLinear()
    .domain([d3.min(points, (p) => p[0]) - pad, d3.max(points, (p) => p[0]) + pad])
    .range([M.left, W - M.right]);
  const y = d3.scaleLinear()
    .domain([d3.min(points, (p) => p[1]) - pad, d3.max(points, (p) => p[1]) + pad])
    .range([H - M.bottom, M.top]);
  return { x, y, sR, sL };
}

function drawAxes(x, y) {
  gAxes.selectAll("*").remove();
  gAxes.append("g").attr("class", "axis")
    .attr("transform", "translate(0," + (H - M.bottom) + ")")
    .call(d3.axisBottom(x).ticks(6));
  gAxes.append("g").attr("class", "axis")
    .attr("transform", "translate(" + M.left + ",0)")
    .call(d3.axisLeft(y).ticks(6));
  gAxes.append("text").attr("class", "axis-label")
    .attr("x", W - M.right).attr("y", H - 14).attr("text-anchor", "end").text("x");
  gAxes.append("text").attr("class", "axis-label")
    .attr("x", 10).attr("y", M.top + 10).text("y");
}

function draw() {
  const entry = DATA[state.index];
  const { x, y, sR, sL } = scalesFor(entry);
  drawAxes(x, y);
  const line = d3.line().x((p) => x(p[0])).y((p) => y(p[1]))
    .curve(d3.curveCatmullRom.alpha(0.5));
  spine.attr("d", line(entry.spine));
  right.attr("d", line(entry.spine.map(([px, py]) => [px * sR, py * sR])));
  left.attr("d", line(entry.spine.map(([px, py]) => [px * sL, py * sL])));
  for (const node of [spine, right, left]) paint(node, state.dot);

  const place = ([px, py], s) => [x(px * s), y(py * s)];
  const ends = [entry.spine[0], entry.spine[entry.spine.length - 1]];
  const cap = (node, point) => {
    const a = place(point, sR), b = place(point, sL);
    node.attr("x1", a[0]).attr("y1", a[1]).attr("x2", b[0]).attr("y2", b[1])
      .attr("display", state.caps ? null : "none");
  };
  cap(capStart, ends[0]);
  cap(capEnd, ends[1]);
  const endsRow = byId("legend-ends");
  if (endsRow) endsRow.style.opacity = state.caps ? "1" : "0.35";

  gOrigin.selectAll("*").remove();
  if (x.domain()[0] <= 0 && x.domain()[1] >= 0 && y.domain()[0] <= 0 && y.domain()[1] >= 0) {
    gOrigin.append("circle").attr("cx", x(0)).attr("cy", y(0)).attr("r", 2.4)
      .attr("fill", "#6b5b46");
    gOrigin.append("text").attr("x", x(0) + 5).attr("y", y(0) - 5).attr("class", "axis-label")
      .text("0");
  }

  byId("construction").innerHTML = '<b>' + entry.param.name + '</b><br>' + entry.param.formula;
  const rightScale = entry.kind === "speed" ? sR : sR;
  byId("dr-shown").textContent = state.dR.toFixed(3);
  byId("dl-shown").textContent = state.dL.toFixed(3);
  byId("right-scale").textContent = rightScale.toFixed(3);
  byId("left-scale").textContent = sL.toFixed(3);

  const gaps = (s) => entry.spine.map(([px, py]) => Math.abs(1 - s) * Math.hypot(px, py));
  const pct = (v) => (100 * v / entry.size).toFixed(2);
  const gapText = (values) => pct(Math.min(...values)) + ' / ' +
    pct(values.reduce((a, b) => a + b, 0) / values.length) + ' / ' + pct(Math.max(...values));
  byId("metrics").innerHTML =
    '<tr><th></th><th>turns &gt;10°</th><th>&gt;20°</th><th>gap min / mean / max %</th></tr>' +
    '<tr><td>spine</td><td>' + entry.turns.over10 + '</td><td>' + entry.turns.over20 + '</td><td>—</td></tr>' +
    '<tr><td>right</td><td>' + entry.turns.over10 + '</td><td>' + entry.turns.over20 + '</td><td>' +
      gapText(gaps(sR)) + '</td></tr>' +
    '<tr><td>left</td><td>' + entry.turns.over10 + '</td><td>' + entry.turns.over20 + '</td><td>' +
      gapText(gaps(sL)) + '</td></tr>';
}

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
byId("dr").addEventListener("input", (event) => {
  state.dR = Number(event.target.value);
  byId("dr-out").value = state.dR.toFixed(3);
  draw();
});
byId("dl").addEventListener("input", (event) => {
  state.dL = Number(event.target.value);
  byId("dl-out").value = state.dL.toFixed(3);
  draw();
});
byId("caps").addEventListener("change", (event) => { state.caps = event.target.checked; draw(); });
byId("stroke").addEventListener("change", (event) => { state.dots = event.target.value === "dots"; draw(); });
byId("dot").addEventListener("input", (event) => {
  state.dot = Number(event.target.value);
  byId("dot-out").value = state.dot.toFixed(1);
  draw();
});
draw();
</script>
</body></html>`;

writeFileSync(path.join(ROOT, "workbench", "side-curves.html"), html);
console.log("wrote workbench/side-curves.html");
