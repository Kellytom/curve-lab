// Side curves as per-construction partners — the only rule.
//
// A side curve is not a width offset and not a universal similarity: it is the same
// construction as the spine with one parameter reduced.
//
//   mobile  P(t) = r1(cos t, sin t) + r2(cos kt, sin kt);  r -> r - d
//           equal radii: P_d = (1 - d) P
//   hybrid  station = k * P(x, y) * (C(t)^p, S(t)^q);      k -> k - d
//   double  the wonk half at radius r -> r - d, then mirrored by the same rule
//
// The construction centre is the origin. The gap is whatever the construction gives
// (for the mobile, d*|P|) and is measured, not assumed. The width rail stays in the
// picture as the reference it is replacing.
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
for (const uid of ["c-0269", "c-0273", "c-0350"]) {
  const record = registry.curves.find((row) => row.uid === uid);
  const spine = spineOf(record);
  const group = P.pathGroup(record.path, { widthPercent: 1.5, plus: 2, minus: 2, profile: "bow" });
  const rails = group ? group.paths.slice(1) : [];
  const all = [...spine, ...rails.flat()];
  const [x0, y0, x1, y1] = P.bbox(all);
  const size = Math.hypot(x1 - x0, y1 - y0) || 1;
  data.push({
    uid, name: record.name,
    size: round(size),
    box: [round(x0), round(y0), round(x1), round(y1)],
    spine: spine.map(([x, y]) => [round(x), round(y)]),
    rails: rails.map((rail) => rail.map(([x, y]) => [round(x), round(y)])),
    turns: { spine: turns(spine), rail: rails.length ? turns(rails[0]) : null },
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
<p class="lead">Every side curve below is the <b>same construction</b> as its spine with one
parameter reduced — no width offset, no universal similarity. The width rail is drawn faintly
only as the reference this replaces. The construction's centre is the origin; the gap is
whatever the construction gives, and it is measured.</p>
<div class="rule">mobile   P(t) = r1(cos t, sin t) + r2(cos kt, sin kt)      r → r − d
hybrid   station = k · P(x, y) · (C(t)^p, S(t)^q)          k → k − d
double   the wonk half at radius r, mirrored across y = x    r → r − d

The current curve states its own parameter below. The centre is the construction's
(0, 0); for the mobile the gap is d·|P(t)|.</div>
<div class="tabs" id="tabs"></div>
<div class="grid">
  <div class="picture" id="picture"></div>
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
The faint rail is the plate's character width at 1.5 %, plus 2, minus 2, bow — the reference,
not the rule.</p>
<script>
const DATA = ${JSON.stringify(data)};
const state = { index: 0, d: 0.06, dots: true, dot: 1.6 };
const byId = (id) => document.getElementById(id);

// the same construction with its parameter reduced: a scale about the construction's
// centre (the origin). For the mobile this is exactly (r - d)(u + v); for the hybrid it is
// the middle weight; for the double the half's radius before the mirror.
const partnerOf = (entry) => entry.spine.map(([x, y]) => [(1 - state.d) * x, (1 - state.d) * y]);

function draw() {
  const entry = DATA[state.index];
  const partner = partnerOf(entry);
  const [x0, y0, x1, y1] = entry.box;
  const pad = 0.06 * Math.max(x1 - x0, y1 - y0);
  const W = 760, k = (W * 0.96) / (x1 - x0 + 2 * pad || 1);
  const H = Math.max(260, Math.round((y1 - y0 + 2 * pad) * k));
  const toD = (points) => points.map(([x, y], i) =>
    (i ? "L" : "M") + ((x - x0 + pad) * k).toFixed(1) + "," +
    (H - (y - y0 + pad) * k).toFixed(1)).join("");
  const stroke = (radius) => state.dots
    ? ' stroke-width="' + (2 * radius).toFixed(2) + '" stroke-linecap="round" stroke-dasharray="0.01 ' +
      (radius * 1.05).toFixed(2) + '"'
    : ' stroke-width="' + (2 * radius * 0.55).toFixed(2) + '" stroke-linecap="round" stroke-linejoin="round"';
  const paths = [
    ...entry.rails.map((rail) => '<path d="' + toD(rail) + '" fill="none" stroke="#b9b1a2" opacity="0.55"' + stroke(state.dot * 0.7) + '/>'),
    '<path d="' + toD(entry.spine) + '" fill="none" stroke="#2b2b2b"' + stroke(state.dot) + '/>',
    '<path d="' + toD(partner) + '" fill="none" stroke="#8a3b2a"' + stroke(state.dot) + '/>',
  ];
  byId("picture").innerHTML = '<svg viewBox="0 0 ' + W + ' ' + H + '" role="img">' + paths.join("") + '</svg>';
  byId("construction").innerHTML = '<b>' + entry.param.name + '</b><br>' + entry.param.formula;
  byId("param-name").textContent = entry.param.name;

  const gaps = partner.map((p, i) => Math.hypot(p[0] - entry.spine[i][0], p[1] - entry.spine[i][1]));
  const pct = (v) => (100 * v / entry.size).toFixed(2);
  byId("metrics").innerHTML =
    '<tr><th></th><th>turns &gt;10°</th><th>&gt;20°</th><th>gap min / mean / max %</th></tr>' +
    '<tr><td>' + entry.uid + '</td><td>' + entry.turns.spine.over10 + '</td><td>' + entry.turns.spine.over20 + '</td><td>spine</td></tr>' +
    '<tr><td>width rail</td><td>' + (entry.turns.rail?.over10 ?? "—") + '</td><td>' + (entry.turns.rail?.over20 ?? "—") + '</td><td>0.75 / 1.50 / 3.00</td></tr>' +
    '<tr><td>partner</td><td>' + entry.turns.spine.over10 + '</td><td>' + entry.turns.spine.over20 + '</td><td>' +
      pct(Math.min(...gaps)) + ' / ' + pct(gaps.reduce((a, b) => a + b, 0) / gaps.length) + ' / ' + pct(Math.max(...gaps)) + '</td></tr>';
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
