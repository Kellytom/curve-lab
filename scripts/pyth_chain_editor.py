"""Interactive triple-tangent chain editor.

    .venv/bin/python scripts/pyth_chain_editor.py

Writes `workbench/pythagorean-chain-editor.html`. Every number on the page is
recomputed in the browser from the same rules as `curve_lab/pyth_chain.py`, so
the page cannot drift from the model: change `n`, the `m` range, the step or the
handle rule and the chain, the grid size and the curvature report all follow.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGE = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Triple-tangent chain · integer editor</title>
<style>
:root{--paper:#fbf7ec;--ink:#2e2413;--muted:#7b6c4e;--rule:#d8ccae;--gold:#c9a441;--blue:#1f5fa8;--red:#8a3b12}
*{box-sizing:border-box}
body{margin:0;background:#f3eddf;color:var(--ink);font:16px/1.55 Georgia,serif}
main{max-width:1180px;margin:0 auto;padding:34px 22px 70px}
.eyebrow{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}
h1{font-size:32px;line-height:1.1;margin:0 0 7px}
h2{font-size:21px;margin:0 0 9px}
.lede{max-width:900px;color:var(--muted);margin:0 0 18px}
.panel{background:var(--paper);border:1px solid var(--rule);padding:15px 18px;margin:0 0 18px}
.controls{display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center;margin:0 0 10px;font:11px/1.4 ui-monospace,Menlo,monospace;color:var(--muted)}
.controls label{display:flex;gap:6px;align-items:center}
.controls input[type=range]{width:110px}
.controls button{border:1px solid var(--rule);background:var(--paper);color:var(--ink);padding:5px 9px;font:inherit;cursor:pointer}
.controls button:hover{background:#f4ecd7}
canvas{display:block;width:100%;height:auto;border:1px solid var(--rule);background:var(--paper);touch-action:none}
.readout{font:12px/1.7 ui-monospace,Menlo,monospace;color:var(--muted);margin:10px 0 0;white-space:pre-wrap}
.good{color:#3f7d4e;font-weight:600}
.bad{color:#a23b2a;font-weight:600}
table{border-collapse:collapse;width:100%;font:11px/1.5 ui-monospace,Menlo,monospace;margin:10px 0}
th,td{border:1px solid var(--rule);padding:5px 7px;text-align:right}
th{color:var(--muted);font-weight:400}
.small{font:12px/1.55 ui-monospace,Menlo,monospace;color:var(--muted)}
code{font:12px ui-monospace,Menlo,monospace;background:#f4ecd7;padding:1px 4px}
.pair{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}
.pair h3{font:13px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}
@media (max-width:860px){.pair{grid-template-columns:1fr}}
</style>
</head>
<body>
<main>
<p class="eyebrow">curve-lab · interactive chain probe</p>
<h1>Triple-tangent chain · integer editor</h1>
<p class="lede">The chain is built from arm vectors, not points: each triple becomes a tangent <code>Tₖ=(a,−b)</code>, the node step is <code>S·(Tₖ+Tₖ₊₁)</code>, and the handles are <code>Tₖ</code>. Because both sides of a join use the same vector, C1 is exact whatever you choose here. The two knobs that matter are <em>which</em> triples you take and <em>how long</em> the handles are.</p>

<section class="panel">
  <h2>Fig. E1 · drive it</h2>
  <div class="controls">
    <label>n <input id="n" type="range" min="1" max="8" step="1" value="2"><span id="nV">2</span></label>
    <label>m from <input id="m0" type="range" min="3" max="60" step="1" value="5"><span id="m0V">5</span></label>
    <label>m to <input id="m1" type="range" min="4" max="60" step="1" value="12"><span id="m1V">12</span></label>
    <label>step S <input id="S" type="range" min="1" max="6" step="1" value="2"><span id="SV">2</span></label>
    <label>handle h <input id="h" type="range" min="1" max="8" step="1" value="1"><span id="hV">1</span></label>
    <button id="g2" type="button">handles: uniform</button>
    <button id="zoom" type="button">zoom: whole chain</button>
    <button id="handles" type="button">handles: on</button>
    <button id="reset" type="button">reset</button>
  </div>
  <canvas id="cv" width="1120" height="620"></canvas>
  <p class="readout" id="out"></p>
</section>


<section class="panel">
  <h2>Fig. E2 · triangles stacked along b</h2>
  <p>Every triangle shares the vertical <code>b</code> leg, so heights step by exactly <code>2n</code> while widths grow quadratically. The far corners trace the parabola <code>a = b²/(4n²) − n²</code> — that edge is the stalk's taper, not a design choice. The sliders above drive this figure too.</p>
  <canvas id="cv2" width="1120" height="520"></canvas>
  <p class="readout" id="out2"></p>
  <table id="tbl2">
    <tr><th>m</th><th>a</th><th>b</th><th>c</th><th>Δb</th><th>b/a</th><th>angle</th></tr>
  </table>
</section>

<section class="panel">
  <h2>Fig. E3 · triangles chained along b, b on the x axis</h2>
  <p><code>b</code> is the x axis. Each triangle is normalised so that its <code>b</code> leg is the x step while its height keeps that triangle's own <code>a/b</code> shape; triangle <code>k</code> starts exactly where triangle <code>k−1</code> ends, so the apex chain is a rising stem. <em>One more step</em> makes the widths <code>1, 2, 3 …</code>; <em>equal</em> makes them all <code>1</code>. <code>n</code> comes from Fig. E1.</p>
  <div class="controls">
    <label>start m <input id="e3m" type="range" min="2" max="40" step="1" value="2"><span id="e3mV">2</span></label>
    <label>triangles <input id="e3k" type="range" min="2" max="6" step="1" value="3"><span id="e3kV">3</span></label>
    <button id="e3step" type="button">x step: one more each</button>
  </div>
  <canvas id="cv3" width="1120" height="520"></canvas>
  <p class="readout" id="out3"></p>
  <table id="tbl3"></table>
</section>

<section class="panel">
  <h2>Fig. S1 · the n=1 stem cut from the 3-4-5 seed</h2>
  <p>The band starts at <code>m=2</code> — the 3-4-5 itself, 53.13° — which is the tight end. A width is only legal while <code>d &lt; R_min</code>, the smallest radius of curvature anywhere on the chain, and that radius sits at the seed, so it sets the width for the whole stem. The rails are the true offset at ±d; the gap between them is measured, not assumed. <strong>Verdict:</strong> see the line under the figure.</p>
  <div class="controls">
    <label>triangles <input id="s1k" type="range" min="3" max="8" step="1" value="6"><span id="s1kV">6</span></label>
    <label>d / R_min <input id="s1d" type="range" min="0.2" max="0.9" step="0.05" value="0.6"><span id="s1dV">0.60</span></label>
  </div>
  <canvas id="cvs1" width="1120" height="560"></canvas>
  <p class="readout" id="outs1"></p>
</section>

<section class="panel">
  <h2>Fig. X · the two routes, side by side</h2>
  <p>Both routes make a stem, a spine or a chain; the names say what each one keeps <em>exact</em>, not what it is for. <strong>Turn-exact</strong> (<code>pythagorean-spiral/</code>) decides the turns and the points exactly, and fits the ink. <strong>Ink-exact</strong> (<code>curve_lab/pyth_chain.py</code>) draws with whole-number control points, and fits the turns.</p>

  <div class="pair">
    <div>
      <h3>Fig. X1a · turn-exact: the triangle is an angle</h3>
      <canvas id="x1a" width="560" height="360"></canvas>
      <p class="small">8-6-10: turn by <code>cos 4/5, sin 3/5</code>. Every turn divides by 5, so the point stays exact as a fraction.</p>
    </div>
    <div>
      <h3>Fig. X1b · ink-exact: the triangle is a vector</h3>
      <canvas id="x1b" width="560" height="360"></canvas>
      <p class="small">The same triangle, used as <code>T = (8, −6)</code>. Every step adds whole numbers, so the point stays an integer.</p>
    </div>
  </div>

  <div class="pair">
    <div>
      <h3>Fig. X2a · six chords, turn-exact</h3>
      <canvas id="x2a" width="560" height="360"></canvas>
      <p class="small" id="x2aNote"></p>
    </div>
    <div>
      <h3>Fig. X2b · six steps, ink-exact</h3>
      <canvas id="x2b" width="560" height="360"></canvas>
      <p class="small" id="x2bNote"></p>
    </div>
  </div>

  <div class="pair">
    <div>
      <h3>Fig. X3a · width, turn-exact</h3>
      <canvas id="x3a" width="560" height="360"></canvas>
      <p class="small">The rails offset the <em>polygon</em>. Equal chords mean one known length, so the offset is rational and joins with a miter.</p>
    </div>
    <div>
      <h3>Fig. X3b · width, ink-exact</h3>
      <canvas id="x3b" width="560" height="360"></canvas>
      <p class="small">The rails offset the <em>curve</em>. A unit normal needs a square root, so the rails are floating point — smooth, but not exact.</p>
    </div>
  </div>

  <table>
    <tr><th></th><th>turn-exact</th><th>ink-exact</th></tr>
    <tr><td>what you choose</td><td>chord length + whole-number turn counts</td><td>a list of integer tangent vectors</td></tr>
    <tr><td>the points</td><td>exact fractions; the denominator grows every turn</td><td>exact integers at scale 1</td></tr>
    <tr><td>the width</td><td>miter offset of the equal-chord polygon — rational</td><td>offset of the cubic — needs a square root, floating point</td></tr>
    <tr><td>what is approximate</td><td>the drawn cubic fit (~1.4%)</td><td>the turn at each join (C1; curvature jumps)</td></tr>
    <tr><td>good for</td><td>loops that must close, mirrors, LAC, placement</td><td>stems that must sit on the integer lattice</td></tr>
    <tr><td>the cost</td><td>denominators: 5⁶ = 15,625; a 761-triangle chain is 173 digits at 20 chords</td><td>no closure guarantee; the width is not exact</td></tr>
  </table>
</section>
<section class="panel">
  <h2>Grid guesstimate</h2>
  <p>These curves are long. The extent below is computed <em>before</em> drawing, from the same rule, so you know the grid you are committing to:</p>
  <p class="readout" id="grid"></p>
  <p class="small">Extent grows linearly with the step <code>S</code> and quadratically with the <code>m</code> range, because the arm vectors grow like <code>m²</code>. To land a target width, set <code>S ≈ target / (extent at S=1)</code>; the readout prints that value.</p>
</section>

<section class="panel">
  <h2>The tangents you selected</h2>
  <table id="tbl">
    <tr><th>#</th><th>m</th><th>triple (a,b,c)</th><th>angle</th><th>tangent Tₖ</th><th>node Nₖ</th></tr>
  </table>
</section>

<section class="panel">
  <h2>What the page is asserting</h2>
  <p><strong>C1 is exact</strong> in every configuration, including the uniform-handle one: the derivative at a join is <code>3h·Tₖ</code> from both sides. <strong>G2 is not</strong> free — with a single handle length the curvature jumps; the <em>per-node</em> handles button solves <code>Cₖ(S−hₖ)=Cₖ₊₁(S−hₖ₊₂)</code>, which drives the measured gap to zero but makes the handles rational, so the control points stop being integers.</p>
  <p class="small">Integer C1, rational G2 — the same trade the page <code>pythagorean-families.html</code> records in Fig. C1/C2. Model: <code>curve_lab/pyth_chain.py</code>. This page recomputes everything live in JavaScript; if the two ever disagree, the page is wrong.</p>
</section>
</main>
<script>
const cv = document.getElementById('cv'), ctx = cv.getContext('2d');
const out = document.getElementById('out'), gridOut = document.getElementById('grid');
const tbl = document.getElementById('tbl');
const st = { n: 2, m0: 5, m1: 12, S: 2, h: 1, g2: false, zoom: false, handles: true };

function tangents() {
  const t = [];
  for (let m = Math.max(3, st.m0); m <= st.m1; m++) {
    const a = m * m - st.n * st.n, b = 2 * m * st.n;
    if (a <= 0) continue;
    t.push({ a, b, c: m * m + st.n * st.n, m });   // b is the triple leg, +y up

  }
  return t;
}

function handles(T, S) {
  const C = [];
  for (let k = 0; k + 1 < T.length; k++) C.push(T[k].a * T[k + 1].b - T[k].b * T[k + 1].a);
  if (!st.g2) return T.map(() => st.h);
  const h = [1, 1];
  for (let k = 0; k + 2 < T.length; k++) {
    h.push(C[k] === 0 || C[k + 1] === 0 ? 1 : S - (C[k] / C[k + 1]) * (S - h[k]));
  }
  return h.slice(0, T.length);
}

function build() {
  const T = tangents();
  if (T.length < 2) return null;
  const S = st.S, h = handles(T, S);
  const nodes = [[0, 0]];
  for (let k = 0; k + 1 < T.length; k++) {
    const d = [S * (T[k].a + T[k + 1].a), -S * (T[k].b + T[k + 1].b)];
    nodes.push([nodes[k][0] + d[0], nodes[k][1] + d[1]]);
  }
  const spans = [];
  for (let k = 0; k + 1 < T.length; k++) {
    const p0 = nodes[k], p3 = nodes[k + 1], h0 = h[k], h1 = h[k + 1];
    spans.push([p0,
      [p0[0] + h0 * T[k].a, p0[1] - h0 * T[k].b],
      [p3[0] - h1 * T[k + 1].a, p3[1] + h1 * T[k + 1].b], p3]);
  }
  return { T, h, nodes, spans };
}

function kappa(c, t) {
  const [p0, p1, p2, p3] = c;
  let u, w;
  if (t === 0) { u = [p1[0] - p0[0], p1[1] - p0[1]]; w = [p2[0] - 2 * p1[0] + p0[0], p2[1] - 2 * p1[1] + p0[1]]; }
  else { u = [p3[0] - p2[0], p3[1] - p2[1]]; w = [p3[0] - 2 * p2[0] + p1[0], p3[1] - 2 * p2[1] + p1[1]]; }
  const n2 = u[0] * u[0] + u[1] * u[1];
  if (n2 === 0) return 0;
  return (2 / 3) * (u[0] * w[1] - u[1] * w[0]) / Math.pow(n2, 3);
}

function stats(d) {
  const jumps = [];
  for (let k = 0; k + 1 < d.spans.length; k++) {
    const l = kappa(d.spans[k], 1), r = kappa(d.spans[k + 1], 0);
    const s = Math.max(Math.abs(l), Math.abs(r));
    jumps.push(s === 0 ? 0 : Math.abs(l - r) / s);
  }
  jumps.sort((x, y) => x - y);
  const pts = d.spans.flat();
  const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]);
  const w = Math.max(...xs) - Math.min(...xs), ht = Math.max(...ys) - Math.min(...ys);
  const maxAbs = Math.max(...xs.map(Math.abs), ...ys.map(Math.abs));
  return {
    spans: d.spans.length, nodes: d.nodes.length, w, ht, maxAbs,
    digits: Math.floor(Math.log10(maxAbs || 1)) + 1,
    med: jumps.length ? jumps[Math.floor(jumps.length / 2)] : 0,
    max: jumps.length ? jumps[jumps.length - 1] : 0,
    integer: !st.g2,
  };
}

function draw(d, s) {
  const dpr = window.devicePixelRatio || 1;
  const W = cv.clientWidth, H = Math.round(W * 0.55);
  cv.width = W * dpr; cv.height = H * dpr;
  cv.style.height = H + 'px';
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, W, H);

  const view = st.zoom && d.spans.length > 4 ? d.spans.slice(0, 4) : d.spans;
  const pts = view.flat();
  const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]);
  const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
  const pad = 46;
  const sc = Math.min((W - 2 * pad) / Math.max(1, x1 - x0), (H - 2 * pad) / Math.max(1, y1 - y0));
  const put = p => [pad + (p[0] - x0) * sc, H - pad - (p[1] - y0) * sc];  // +y up, flipped here

  // grid: a round step near 1/8 of the view
  const raw = Math.max(x1 - x0, y1 - y0) / 8;
  const mag = Math.pow(10, Math.floor(Math.log10(raw || 1)));
  const step = [1, 2, 5, 10].map(k => k * mag).find(v => v >= raw) || mag;
  ctx.strokeStyle = '#e8dfc9'; ctx.lineWidth = 1;
  for (let gx = Math.ceil(x0 / step) * step; gx <= x1; gx += step) {
    const a = put([gx, y0]), b = put([gx, y1]);
    ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke();
  }
  for (let gy = Math.ceil(y0 / step) * step; gy <= y1; gy += step) {
    const a = put([x0, gy]), b = put([x1, gy]);
    ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke();
  }
  ctx.fillStyle = '#7b6c4e'; ctx.font = '11px ui-monospace,Menlo,monospace';
  ctx.fillText('grid step ' + step.toLocaleString(), pad, 16);
  ctx.fillText('x →', W - 34, H - 10);
  ctx.fillText('y ↑', 12, 34);

  // handles and control polygon
  if (st.handles) {
    ctx.strokeStyle = '#b9aa88'; ctx.setLineDash([4, 4]); ctx.lineWidth = 1;
    for (const [p0, p1, p2, p3] of view) {
      const a = put(p0), b = put(p1), c = put(p3), e = put(p2);
      ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(c[0], c[1]); ctx.lineTo(e[0], e[1]); ctx.stroke();
    }
    ctx.setLineDash([]);
  }

  // the chain
  ctx.strokeStyle = '#8a3b12'; ctx.lineWidth = 3; ctx.lineJoin = 'round';
  ctx.beginPath();
  for (const [p0, p1, p2, p3] of view) {
    const a = put(p0), b = put(p1), c = put(p2), e = put(p3);
    if (a === put(view[0][0])) ctx.moveTo(a[0], a[1]);
    ctx.bezierCurveTo(b[0], b[1], c[0], c[1], e[0], e[1]);
  }
  ctx.stroke();

  // nodes
  for (const n of d.nodes) {
    const q = put(n);
    ctx.fillStyle = '#fbf7ec'; ctx.strokeStyle = '#2e2413'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.arc(q[0], q[1], 4.6, 0, 7); ctx.fill(); ctx.stroke();
  }
  // first and last node labels
  const lab = (p, txt, dx, dy) => {
    const q = put(p);
    ctx.font = '11px ui-monospace,Menlo,monospace';
    const w = ctx.measureText(txt).width;
    const x = Math.min(Math.max(q[0] + dx, 6), W - w - 6);
    const y = Math.min(Math.max(q[1] + dy, 14), H - 8);
    ctx.strokeStyle = '#fbf7ec'; ctx.lineWidth = 3; ctx.strokeText(txt, x, y);
    ctx.fillStyle = '#2e2413'; ctx.fillText(txt, x, y);
  };
  const first = d.nodes[0], last = d.nodes[d.nodes.length - 1];
  lab(first, 'N0 (' + first[0].toLocaleString() + ', ' + first[1].toLocaleString() + ')', 8, -8);
  lab(last, 'N' + (d.nodes.length - 1) + ' (' + Math.round(last[0]).toLocaleString() + ', ' + Math.round(last[1]).toLocaleString() + ')', -8, 16);
}

function table(d) {
  const rows = ['<tr><th>#</th><th>m</th><th>triple (a,b,c)</th><th>angle</th><th>tangent Tₖ</th><th>node Nₖ</th></tr>'];
  const n = Math.min(d.T.length, 8);
  for (let k = 0; k < n; k++) {
    const t = d.T[k], nd = d.nodes[k];
    const ang = (Math.atan2(t.b, t.a) * 180 / Math.PI).toFixed(2) + '°';
    rows.push('<tr><td>' + (k + 1) + '</td><td>' + t.m + '</td><td>(' + t.a + ', ' + (-t.b) + ', ' + t.c + ')</td><td>' + ang +
      '</td><td>(' + t.a + ', ' + (-t.b) + ')</td><td>(' + nd[0].toLocaleString() + ', ' + nd[1].toLocaleString() + ')</td></tr>');
  }
  if (d.T.length > n) rows.push('<tr><td colspan="6">… ' + (d.T.length - n) + ' more</td></tr>');
  tbl.innerHTML = rows.join('');
}


// ---- Fig. E2: triangles nested on a shared b leg -------------------------
const cv2 = document.getElementById('cv2'), ctx2 = cv2.getContext('2d');
const out2 = document.getElementById('out2'), tbl2 = document.getElementById('tbl2');

function drawTri(T) {
  if (!T.length) return;
  const dpr = window.devicePixelRatio || 1;
  const W = cv2.clientWidth, H = Math.round(W * 0.46);
  cv2.width = W * dpr; cv2.height = H * dpr; cv2.style.height = H + 'px';
  ctx2.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx2.clearRect(0, 0, W, H);

  const bMax = Math.max(...T.map(t => t.b));
  const aMax = Math.max(...T.map(t => t.a));
  const pad = 54;
  const sc = Math.min((W - 2 * pad) / Math.max(1, aMax), (H - 2 * pad) / Math.max(1, bMax));
  const put = p => [pad + p[0] * sc, H - pad - p[1] * sc];   // +y up, flipped here

  // parabola a = b^2/(4n^2) - n^2, the envelope of the far corners
  ctx2.strokeStyle = '#a23b2a'; ctx2.setLineDash([6, 5]); ctx2.lineWidth = 1.6;
  ctx2.beginPath();
  for (let i = 0; i <= 80; i++) {
    const b = (bMax * i) / 80;
    const a = (b * b) / (4 * st.n * st.n) - st.n * st.n;
    const q = put([Math.max(0, a), b]);
    i === 0 ? ctx2.moveTo(q[0], q[1]) : ctx2.lineTo(q[0], q[1]);
  }
  ctx2.stroke(); ctx2.setLineDash([]);

  // the triangles, sharing the vertical a=0 leg
  for (const t of T) {
    const o = put([0, 0]), top = put([0, t.b]), far = put([t.a, t.b]);
    ctx2.strokeStyle = '#2e2413'; ctx2.lineWidth = 1.3;
    ctx2.beginPath(); ctx2.moveTo(o[0], o[1]); ctx2.lineTo(top[0], top[1]); ctx2.lineTo(far[0], far[1]); ctx2.stroke();
    ctx2.strokeStyle = '#1f5fa8'; ctx2.lineWidth = 1.1;
    ctx2.beginPath(); ctx2.moveTo(o[0], o[1]); ctx2.lineTo(far[0], far[1]); ctx2.stroke();
  }

  // polyline of far corners = the arm attachment curve
  ctx2.strokeStyle = '#c9a441'; ctx2.lineWidth = 2.4;
  ctx2.beginPath();
  T.forEach((t, i) => { const q = put([t.a, t.b]); i ? ctx2.lineTo(q[0], q[1]) : ctx2.moveTo(q[0], q[1]); });
  ctx2.stroke();

  // label the first and last far corner with their integers
  const corner = (t, dx, dy, anchor) => {
    const q = put([t.a, t.b]);
    const txt = 'm=' + t.m + ' (' + t.a + ', ' + t.b + ')';
    ctx2.font = '11px ui-monospace,Menlo,monospace';
    const w = ctx2.measureText(txt).width;
    const x = Math.min(Math.max(q[0] + dx, 6), W - w - 6);
    const y = Math.min(Math.max(q[1] + dy, 14), H - 8);
    ctx2.strokeStyle = '#fbf7ec'; ctx2.lineWidth = 3; ctx2.strokeText(txt, x, y);
    ctx2.fillStyle = '#2e2413'; ctx2.fillText(txt, x, y);
  };
  corner(T[0], 6, -8, 'start');
  corner(T[T.length - 1], -6, 18, 'end');

  ctx2.fillStyle = '#7b6c4e'; ctx2.font = '11px ui-monospace,Menlo,monospace';
  ctx2.fillText('b \u2191 (step 2n = ' + (2 * st.n) + ')', 8, 18);
  ctx2.fillText('a \u2192', W - 40, H - 10);
  ctx2.fillText('b max ' + bMax.toLocaleString() + ' \u00b7 a max ' + aMax.toLocaleString(), pad, H - 14);

  const rows = ['<tr><th>m</th><th>a</th><th>b</th><th>c</th><th>\u0394b</th><th>b/a</th><th>angle</th></tr>'];
  const show = Math.min(T.length, 12);
  for (let i = 0; i < show; i++) {
    const t = T[i], prev = i ? T[i - 1] : null;
    const db = prev ? t.b - prev.b : '\u2014';
    const ang = (Math.atan2(t.b, t.a) * 180 / Math.PI).toFixed(2) + '\u00b0';
    rows.push('<tr><td>' + t.m + '</td><td>' + t.a.toLocaleString() + '</td><td>' + t.b.toLocaleString() +
      '</td><td>' + t.c.toLocaleString() + '</td><td>' + db + '</td><td>' + (t.b / t.a).toFixed(3) +
      '</td><td>' + ang + '</td></tr>');
  }
  tbl2.innerHTML = rows.join('');

  const first = T[0], last = T[T.length - 1];
  out2.innerHTML = 'triangles <b>' + T.length + '</b> \u00b7 b ' + first.b.toLocaleString() + ' \u2192 ' +
    last.b.toLocaleString() + ' (range ' + (last.b - first.b).toLocaleString() + ', step ' + (2 * st.n) + ')' +
    '\nwidth a ' + first.a.toLocaleString() + ' \u2192 ' + last.a.toLocaleString() + ' (range ' +
    (last.a - first.a).toLocaleString() + ') \u00b7 b/a falls ' + (first.b / first.a).toFixed(2) + ' \u2192 ' +
    (last.b / last.a).toFixed(2);
}

// ---- Fig. E3: triangles chained along b, b on the x axis ----------------
const cv3 = document.getElementById('cv3'), ctx3 = cv3.getContext('2d');
const out3 = document.getElementById('out3'), tbl3 = document.getElementById('tbl3');
const st3 = { m0: 2, count: 3, more: true };

function chain3() {
  const out = [];
  let x = 0, m = st3.m0;
  while (out.length < st3.count && m <= st3.m0 + 40) {
    const a = m * m - st.n * st.n;
    const b = 2 * m * st.n;
    if (a > 0) {
      const k = out.length;                  // emitted index, so a skip cannot shift the steps
      const w = st3.more ? k + 1 : 1;        // x steps: 1,2,3 … or all 1
      const h = (a / b) * w;                 // keep this triangle's own shape
      out.push({ m, a, b, c: m * m + st.n * st.n, w, h, x0: x, x1: x + w });
      x += w;
    }
    m++;
  }
  return out;
}

function drawChain3(C) {
  const dpr = window.devicePixelRatio || 1;
  const W = cv3.clientWidth, H = Math.round(W * 0.46);
  cv3.width = W * dpr; cv3.height = H * dpr; cv3.style.height = H + 'px';
  ctx3.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx3.clearRect(0, 0, W, H);
  if (!C.length) return;

  const xMax = C[C.length - 1].x1, hMax = Math.max(...C.map(t => t.h));
  const padL = 64, padR = 44, padT = 44, padB = 62;
  const sc = Math.min((W - padL - padR) / Math.max(1, xMax), (H - padT - padB) / Math.max(0.2, hMax));
  const put = p => [padL + p[0] * sc, H - padB - p[1] * sc];   // +y up, flipped here

  // the x axis is b
  const o = put([0, 0]), e = put([xMax, 0]);
  ctx3.strokeStyle = '#2e2413'; ctx3.lineWidth = 1.4;
  ctx3.beginPath(); ctx3.moveTo(o[0], o[1]); ctx3.lineTo(e[0] + 18, e[1]); ctx3.stroke();
  for (let t = 0; t <= xMax; t++) {                            // one tick per x step
    const q = put([t, 0]);
    ctx3.beginPath(); ctx3.moveTo(q[0], q[1]); ctx3.lineTo(q[0], q[1] + 5); ctx3.stroke();
  }

  for (const t of C) {
    const p0 = put([t.x0, 0]), p1 = put([t.x1, 0]), p2 = put([t.x1, t.h]);
    ctx3.strokeStyle = '#2e2413'; ctx3.lineWidth = 1.6;
    ctx3.beginPath(); ctx3.moveTo(p0[0], p0[1]); ctx3.lineTo(p1[0], p1[1]); ctx3.lineTo(p2[0], p2[1]); ctx3.stroke();
    ctx3.strokeStyle = '#1f5fa8'; ctx3.lineWidth = 1.2;
    ctx3.beginPath(); ctx3.moveTo(p0[0], p0[1]); ctx3.lineTo(p2[0], p2[1]); ctx3.stroke();
  }

  // the apex chain: the stem the triangles describe
  ctx3.strokeStyle = '#c9a441'; ctx3.lineWidth = 2.6;
  ctx3.beginPath();
  C.forEach((t, i) => { const q = put([t.x1, t.h]); i ? ctx3.lineTo(q[0], q[1]) : ctx3.moveTo(q[0], q[1]); });
  ctx3.stroke();

  // label every apex with its integers — the figure rule
  ctx3.font = '12px ui-monospace,Menlo,monospace';
  for (const t of C) {
    const q = put([t.x1, t.h]);
    const txt = 'm=' + t.m + ' a=' + t.a + ' b=' + t.b;
    const w = ctx3.measureText(txt).width;
    const x = Math.min(Math.max(q[0] - w / 2, 4), W - w - 4);
    const y = Math.max(q[1] - 8, 16);
    ctx3.strokeStyle = '#fbf7ec'; ctx3.lineWidth = 3; ctx3.strokeText(txt, x, y);
    ctx3.fillStyle = '#2e2413'; ctx3.fillText(txt, x, y);
  }

  // legend, 15px as the figure rule requires
  ctx3.font = '15px Georgia,serif';
  const ly = H - 14; let lx = padL;
  const leg = (colour, txt) => {
    ctx3.fillStyle = colour; ctx3.fillRect(lx, ly - 11, 18, 3);
    ctx3.fillStyle = '#2e2413'; ctx3.fillText(txt, lx + 24, ly);
    lx += ctx3.measureText(txt).width + 54;
  };
  leg('#2e2413', 'base = b (x step)'); leg('#1f5fa8', 'hypotenuse c'); leg('#c9a441', 'apex chain');

  ctx3.fillStyle = '#7b6c4e'; ctx3.font = '12px ui-monospace,Menlo,monospace';
  ctx3.fillText('b →  (x step, one unit = one triangle width)', W - 400, H - padB + 30);
  ctx3.fillText('a ↑', 12, padT - 16);
  ctx3.font = '13px Georgia,serif'; ctx3.fillStyle = '#2e2413';
  ctx3.fillText('Fig. E3 · triangles chained along b, b on the x axis', padL, 18);
  ctx3.fillStyle = '#7b6c4e'; ctx3.font = '12px ui-monospace,Menlo,monospace';
  ctx3.fillText('x steps 0 → ' + xMax + ' · apex height max ' + hMax.toFixed(2), padL, 34);

  const rows = ['<tr><th>#</th><th>m</th><th>a</th><th>b</th><th>c</th><th>x from</th><th>x to</th><th>steps</th><th>height a/b·w</th></tr>'];
  C.forEach((t, i) => rows.push('<tr><td>' + (i + 1) + '</td><td>' + t.m + '</td><td>' + t.a + '</td><td>' + t.b +
    '</td><td>' + t.c + '</td><td>' + t.x0 + '</td><td>' + t.x1 + '</td><td>' + t.w +
    '</td><td>' + t.h.toFixed(3) + '</td></tr>'));
  rows.push('<tr><td colspan="5">total</td><td>0</td><td>' + xMax + '</td><td>' + xMax + '</td><td>—</td></tr>');
  tbl3.innerHTML = rows.join('');

  const first = C[0], last = C[C.length - 1];
  const widths = C.map(t => t.w).join(', ');
  out3.innerHTML = 'triangles <b>' + C.length + '</b> · widths <b>' + widths + '</b> x steps → total <b>' + xMax + '</b>\n' +
    'm ' + first.m + ' → ' + last.m + ' · apex height ' + first.h.toFixed(2) + ' → ' + last.h.toFixed(2) +
    ' · rise ' + (last.h / first.h).toFixed(2) + '× over ' + (last.x1 - first.x0) + ' steps\n' +
    'normalised: each b is drawn as its own x step, so the integers above are the family values, not the drawing widths';
}

// ---- Fig. S1: the n=1 stem, width fitted to the tight end ----------------
const cvs1 = document.getElementById('cvs1'), ctxs1 = cvs1.getContext('2d');
const outs1 = document.getElementById('outs1');
const st1 = { count: 6, frac: 0.6 };

function stem1() {
  const T = [];
  for (let i = 0; i < st1.count; i++) {
    const m = 2 + i;
    T.push({ m, a: m * m - 1, b: 2 * m, c: m * m + 1 });   // n = 1 family
  }
  const S = 2, h = 1;
  const nodes = [[0, 0]];
  for (let k = 0; k + 1 < T.length; k++)
    nodes.push([nodes[k][0] + S * (T[k].a + T[k + 1].a), nodes[k][1] - S * (T[k].b + T[k + 1].b)]);
  const spans = [];
  for (let k = 0; k + 1 < T.length; k++) {
    const p0 = nodes[k], p3 = nodes[k + 1];
    spans.push([p0, [p0[0] + h * T[k].a, p0[1] - h * T[k].b],
                [p3[0] - h * T[k + 1].a, p3[1] + h * T[k + 1].b], p3]);
  }
  return { T, nodes, spans };
}

function bez3(c, t) {
  const mt = 1 - t;
  return [mt * mt * mt * c[0][0] + 3 * mt * mt * t * c[1][0] + 3 * mt * t * t * c[2][0] + t * t * t * c[3][0],
          mt * mt * mt * c[0][1] + 3 * mt * mt * t * c[1][1] + 3 * mt * t * t * c[2][1] + t * t * t * c[3][1]];
}

function dbez3(c, t) {
  const mt = 1 - t;
  return [3 * (mt * mt * (c[1][0] - c[0][0]) + 2 * mt * t * (c[2][0] - c[1][0]) + t * t * (c[3][0] - c[2][0])),
          3 * (mt * mt * (c[1][1] - c[0][1]) + 2 * mt * t * (c[2][1] - c[1][1]) + t * t * (c[3][1] - c[2][1]))];
}

function kappaAt(c, t) {
  const v = dbez3(c, t);
  const mt = 1 - t;
  const w = [6 * (mt * (c[2][0] - 2 * c[1][0] + c[0][0]) + t * (c[3][0] - 2 * c[2][0] + c[1][0])),
             6 * (mt * (c[2][1] - 2 * c[1][1] + c[0][1]) + t * (c[3][1] - 2 * c[2][1] + c[1][1]))];
  const n2 = v[0] * v[0] + v[1] * v[1];
  if (!n2) return 0;
  return (v[0] * w[1] - v[1] * w[0]) / Math.pow(n2, 1.5);
}

function tightest(g) {
  let worst = 0, span = 0, at = 0;
  g.spans.forEach((c, k) => {
    for (let i = 0; i <= 240; i++) {
      const t = i / 240, kk = Math.abs(kappaAt(c, t));
      if (kk > worst) { worst = kk; span = k; at = t; }
    }
  });
  return { R: worst ? 1 / worst : Infinity, span, t: at };
}

function offsets(g, d) {
  const out = [];
  for (const c of g.spans) {
    for (let i = 0; i <= 32; i++) {
      const t = i / 32, p = bez3(c, t), v = dbez3(c, t);
      const L = Math.hypot(v[0], v[1]);
      if (!L) continue;
      const nx = -v[1] / L, ny = v[0] / L;
      out.push({ p, l: [p[0] + d * nx, p[1] + d * ny], r: [p[0] - d * nx, p[1] - d * ny] });
    }
  }
  return out;
}

function drawStem1() {
  const dpr = window.devicePixelRatio || 1;
  const W = cvs1.clientWidth, H = Math.round(W * 0.5);
  cvs1.width = W * dpr; cvs1.height = H * dpr; cvs1.style.height = H + 'px';
  ctxs1.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctxs1.clearRect(0, 0, W, H);

  const g = stem1();
  const tight = tightest(g);
  const d = st1.frac * tight.R;
  const off = offsets(g, d);

  // measured gap: every rail-to-rail pair, and the closest pair overall
  let gmin = Infinity, gmax = 0;
  for (const o of off) {
    const gap = Math.hypot(o.l[0] - o.r[0], o.l[1] - o.r[1]);
    gmin = Math.min(gmin, gap); gmax = Math.max(gmax, gap);
  }
  let closest = Infinity;
  for (const a of off) for (const b of off) {
    const q = Math.hypot(a.l[0] - b.r[0], a.l[1] - b.r[1]);
    if (q < closest) closest = q;
  }

  const all = off.flatMap(o => [o.p, o.l, o.r]);
  const xs = all.map(q => q[0]), ys = all.map(q => q[1]);
  const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
  const padL = 46, padR = 30, padT = 40, padB = 62;
  const sc = Math.min((W - padL - padR) / Math.max(1, x1 - x0), (H - padT - padB) / Math.max(1, y1 - y0));
  const put = q => [padL + (q[0] - x0) * sc, H - padB - (q[1] - y0) * sc];   // +y up, flipped here

  // measured gap ticks
  ctxs1.strokeStyle = '#d8ccae'; ctxs1.lineWidth = 1;
  off.forEach((o, i) => {
    if (i % 6) return;
    const a = put(o.l), b = put(o.r);
    ctxs1.beginPath(); ctxs1.moveTo(a[0], a[1]); ctxs1.lineTo(b[0], b[1]); ctxs1.stroke();
  });

  // the two rails
  for (const side of ['l', 'r']) {
    ctxs1.strokeStyle = '#1f5fa8'; ctxs1.lineWidth = 1.8;
    ctxs1.beginPath();
    off.forEach((o, i) => { const q = put(o[side]); i ? ctxs1.lineTo(q[0], q[1]) : ctxs1.moveTo(q[0], q[1]); });
    ctxs1.stroke();
  }

  // the centreline: the chain itself
  ctxs1.strokeStyle = '#2e2413'; ctxs1.lineWidth = 2.6; ctxs1.lineJoin = 'round';
  ctxs1.beginPath();
  off.forEach((o, i) => { const q = put(o.p); i ? ctxs1.lineTo(q[0], q[1]) : ctxs1.moveTo(q[0], q[1]); });
  ctxs1.stroke();

  // tightest point on the centreline
  const tc = g.spans[tight.span], tp = put(bez3(tc, tight.t));
  ctxs1.fillStyle = '#a23b2a'; ctxs1.beginPath(); ctxs1.arc(tp[0], tp[1], 4.5, 0, 7); ctxs1.fill();
  ctxs1.font = '12px ui-monospace,Menlo,monospace'; ctxs1.fillStyle = '#a23b2a';
  ctxs1.fillText('tightest: R_min ' + tight.R.toFixed(2) + ' (m=' + g.T[tight.span].m + ', 53.13° seed)', tp[0] + 8, tp[1] - 6);

  // title, axis, legend — inside the figure
  ctxs1.font = '13px Georgia,serif'; ctxs1.fillStyle = '#2e2413';
  ctxs1.fillText('Fig. S1 · n=1 stem · centreline with ±d rails, d = ' + d.toFixed(2), padL, 18);
  ctxs1.fillStyle = '#7b6c4e'; ctxs1.font = '12px ui-monospace,Menlo,monospace';
  ctxs1.fillText('d / R_min = ' + st1.frac.toFixed(2) + ' · gap measured ' + gmin.toFixed(2) + '–' + gmax.toFixed(2) + ' · 2d = ' + (2 * d).toFixed(2), padL, 34);
  ctxs1.fillText('x →', W - 60, H - padB + 34);
  ctxs1.fillText('y ↑', 12, padT - 6);

  ctxs1.font = '15px Georgia,serif';
  const ly = H - 14; let lx = padL;
  const leg = (colour, txt, width) => {
    ctxs1.fillStyle = colour; ctxs1.fillRect(lx, ly - 11, 18, width || 3);
    ctxs1.fillStyle = '#2e2413'; ctxs1.fillText(txt, lx + 24, ly);
    lx += ctxs1.measureText(txt).width + 54;
  };
  leg('#2e2413', 'centreline (chain)'); leg('#1f5fa8', '±d rails'); leg('#d8ccae', 'measured gap', 1);

  const legal = d < tight.R;
  outs1.innerHTML =
    'R_min <b>' + tight.R.toFixed(3) + '</b> at span ' + (tight.span + 1) + ' (m=' + g.T[tight.span].m + ', 53.13°) · ' +
    'd <b>' + d.toFixed(3) + '</b> = ' + st1.frac.toFixed(2) + ' R_min · ' +
    (legal ? '<span class="good">d &lt; R_min, margin ' + (tight.R - d).toFixed(3) + '</span>' : '<span class="bad">d ≥ R_min — the rail folds</span>') + '\n' +
    'rail-to-rail: paired <b>' + gmin.toFixed(4) + ' – ' + gmax.toFixed(4) + '</b> · closest pair <b>' + closest.toFixed(4) +
    '</b> · 2d = <b>' + (2 * d).toFixed(4) + '</b> · error ' + Math.abs(closest - 2 * d).toExponential(1) + '\n' +
    'verdict: <b>still a spine</b> — at constant width it reads as a ribbon: the section never tapers and nothing ends it, ' +
    'so the rails are a width laid on a spine, not a stem body. It becomes a stem only when a taper and a terminal are cut into this section.';
}

// ---- Fig. X: the two routes, drawn from the same triangle -----------------
function gcd(a, b) { a = Math.abs(a); b = Math.abs(b); while (b) { const t = a % b; a = b; b = t; } return a || 1; }

function frame(cv, pts, pad, aspect) {
  const dpr = window.devicePixelRatio || 1;
  const W = cv.clientWidth, H = Math.round(W * aspect);
  cv.width = W * dpr; cv.height = H * dpr; cv.style.height = H + 'px';
  const ctx = cv.getContext('2d');
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, W, H);
  const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]);
  let x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
  if (x1 - x0 < 1e-9) { x0 -= 1; x1 += 1; }
  if (y1 - y0 < 1e-9) { y0 -= 1; y1 += 1; }
  const sc = Math.min((W - 2 * pad) / (x1 - x0), (H - 2 * pad) / (y1 - y0));
  const ox = (W - (x1 - x0) * sc) / 2, oy = (H - (y1 - y0) * sc) / 2;
  return { ctx, W, H, sc, put: p => [ox + (p[0] - x0) * sc, H - oy - (p[1] - y0) * sc] };
}

// turn-exact: chord `chord`, one +36.87° turn per chord, exact numerators over 5^k
function spineChain(count, chord) {
  const pts = [], fr = [];
  let den = 1, D = [1, 0], px = 0, py = 0;
  for (let k = 0; k < count; k++) {
    const nd = [4 * D[0] - 3 * D[1], 3 * D[0] + 4 * D[1]], nden = den * 5;
    px = px * 5 + chord * nd[0];
    py = py * 5 + chord * nd[1];
    den = nden; D = nd;
    pts.push([px / den, py / den]); fr.push([px, py, den]);
  }
  return { pts, fr, den };
}

function chainNodes(count) {
  const T = [];
  for (let i = 0; i < count; i++) { const m = 2 + i; T.push({ m, a: m * m - 1, b: 2 * m }); }
  const nodes = [[0, 0]];
  for (let k = 0; k + 1 < T.length; k++)
    nodes.push([nodes[k][0] + 2 * (T[k].a + T[k + 1].a), nodes[k][1] - 2 * (T[k].b + T[k + 1].b)]);
  return { T, nodes };
}

function miterOffset(pts, d) {
  const out = [];
  for (let i = 0; i < pts.length; i++) {
    const p = pts[i];
    const a = pts[Math.max(0, i - 1)], b = pts[Math.min(pts.length - 1, i + 1)];
    let e0 = [p[0] - a[0], p[1] - a[1]], e1 = [b[0] - p[0], b[1] - p[1]];
    let l0 = Math.hypot(e0[0], e0[1]) || 1, l1 = Math.hypot(e1[0], e1[1]) || 1;
    e0 = [e0[0] / l0, e0[1] / l0]; e1 = [e1[0] / l1, e1[1] / l1];
    const n0 = [-e0[1], e0[0]], n1 = [-e1[1], e1[0]];
    let m = [n0[0] + n1[0], n0[1] + n1[1]];
    const l = Math.hypot(m[0], m[1]) || 1;
    m = [m[0] / l, m[1] / l];
    const k = d / Math.max(0.25, m[0] * n0[0] + m[1] * n0[1]);
    out.push([p[0] + k * m[0], p[1] + k * m[1]]);
  }
  return out;
}

function drawCompare() {
  // X1a — the triangle as an angle
  {
    const tri = [[0, 0], [8, 0], [8, 6]];
    const f = frame(document.getElementById('x1a'), tri, 46, 0.64);
    const { ctx, put } = f;
    ctx.strokeStyle = '#2e2413'; ctx.lineWidth = 2;
    ctx.beginPath(); tri.forEach((p, i) => { const q = put(p); i ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1]); }); ctx.stroke();
    const o = put([0, 0]);
    ctx.strokeStyle = '#a23b2a'; ctx.lineWidth = 1.6;
    ctx.beginPath(); ctx.arc(o[0], o[1], 46, -Math.atan2(6, 8), 0); ctx.stroke();
    ctx.fillStyle = '#a23b2a'; ctx.font = '13px ui-monospace,Menlo,monospace';
    ctx.fillText('36.87°', o[0] + 44, o[1] - 16);
    ctx.fillStyle = '#2e2413';
    ctx.fillText('8', (put([4, 0])[0]), put([4, 0])[1] + 18);
    ctx.fillText('6', put([8, 3])[0] + 8, put([8, 3])[1]);
    ctx.fillText('10', put([4, 3])[0] - 18, put([4, 3])[1] - 8);
    ctx.font = '12px ui-monospace,Menlo,monospace'; ctx.fillStyle = '#7b6c4e';
    ctx.fillText('cos = 4/5 · sin = 3/5', 12, f.H - 12);
  }

  // X1b — the same triangle as a vector
  {
    const f = frame(document.getElementById('x1b'), [[0, 0], [8, -6]], 56, 0.64);
    const { ctx, put } = f;
    const a = put([0, 0]), b = put([8, -6]);
    ctx.strokeStyle = '#1f5fa8'; ctx.lineWidth = 2.4;
    ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke();
    // arrow head
    const ang = Math.atan2(b[1] - a[1], b[0] - a[0]);
    ctx.beginPath(); ctx.moveTo(b[0], b[1]);
    ctx.lineTo(b[0] - 12 * Math.cos(ang - 0.4), b[1] - 12 * Math.sin(ang - 0.4));
    ctx.lineTo(b[0] - 12 * Math.cos(ang + 0.4), b[1] - 12 * Math.sin(ang + 0.4));
    ctx.closePath(); ctx.fillStyle = '#1f5fa8'; ctx.fill();
    ctx.fillStyle = '#2e2413'; ctx.beginPath(); ctx.arc(a[0], a[1], 4.5, 0, 7); ctx.fill();
    ctx.font = '13px ui-monospace,Menlo,monospace';
    ctx.fillText('T = (8, −6)', b[0] - 70, b[1] + 22);
    ctx.font = '12px ui-monospace,Menlo,monospace'; ctx.fillStyle = '#7b6c4e';
    ctx.fillText('add 2·(Tₖ + Tₖ₊₁) — no division', 12, f.H - 12);
  }

  // X2a — six chords, turn-exact
  {
    const s = spineChain(6, 5), pts = [[0, 0]].concat(s.pts);
    const f = frame(document.getElementById('x2a'), pts, 40, 0.64);
    const { ctx, put } = f;
    ctx.strokeStyle = '#2e2413'; ctx.lineWidth = 2; ctx.beginPath();
    pts.forEach((p, i) => { const q = put(p); i ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1]); }); ctx.stroke();
    ctx.fillStyle = '#fbf7ec'; ctx.strokeStyle = '#2e2413'; ctx.lineWidth = 1.8;
    for (const p of pts) { const q = put(p); ctx.beginPath(); ctx.arc(q[0], q[1], 4, 0, 7); ctx.fill(); ctx.stroke(); }
    ctx.fillStyle = '#7b6c4e'; ctx.font = '12px ui-monospace,Menlo,monospace';
    ctx.fillText('denominator 5⁶ = 15,625', 12, f.H - 12);
    ctx.fillStyle = '#2e2413';
    ctx.fillText('(4, 3)', put(pts[1])[0] + 8, put(pts[1])[1] - 6);
    document.getElementById('x2aNote').innerHTML =
      'Node 1 is (4, 3) exactly; node 2 is (27/5, 39/5); after six chords every point sits on a grid of 1/15,625.';
  }

  // X2b — six steps, ink-exact
  {
    const { nodes } = chainNodes(6), pts = nodes;
    const f = frame(document.getElementById('x2b'), pts, 40, 0.64);
    const { ctx, put } = f;
    ctx.strokeStyle = '#8a3b12'; ctx.lineWidth = 2; ctx.beginPath();
    pts.forEach((p, i) => { const q = put(p); i ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1]); }); ctx.stroke();
    ctx.fillStyle = '#fbf7ec'; ctx.strokeStyle = '#2e2413'; ctx.lineWidth = 1.8;
    for (const p of pts) { const q = put(p); ctx.beginPath(); ctx.arc(q[0], q[1], 4, 0, 7); ctx.fill(); ctx.stroke(); }
    ctx.fillStyle = '#7b6c4e'; ctx.font = '12px ui-monospace,Menlo,monospace';
    ctx.fillText('integers at scale 1', 12, f.H - 12);
    const last = pts[pts.length - 1];
    ctx.fillStyle = '#2e2413';
    ctx.fillText('(' + last[0] + ', ' + last[1] + ')', put(last)[0] - 78, put(last)[1] + 20);
    document.getElementById('x2bNote').innerHTML =
      'Nodes (' + pts.map(p => p[0] + ',' + p[1]).slice(0, 4).join(') (') + ') … — no scale needed, ever.';
  }

  // X3a — width on the polygon
  {
    const s = spineChain(5, 5), pts = [[0, 0]].concat(s.pts), d = 1.1;
    const L = miterOffset(pts, d), R = miterOffset(pts, -d);
    const f = frame(document.getElementById('x3a'), L.concat(R), 44, 0.64);
    const { ctx, put } = f;
    ctx.strokeStyle = '#1f5fa8'; ctx.lineWidth = 1.8;
    for (const side of [L, R]) {
      ctx.beginPath();
      side.forEach((p, i) => { const q = put(p); i ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1]); }); ctx.stroke();
    }
    ctx.strokeStyle = '#2e2413'; ctx.lineWidth = 1.4; ctx.beginPath();
    pts.forEach((p, i) => { const q = put(p); i ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1]); }); ctx.stroke();
    ctx.font = '15px Georgia,serif'; ctx.fillStyle = '#2e2413';
    ctx.fillText('polygon + miter rails', 12, f.H - 14);
    ctx.font = '12px ui-monospace,Menlo,monospace'; ctx.fillStyle = '#3f7d4e';
    ctx.fillText('rational: one known chord length', 12, f.H - 34);
  }

  // X3b — width on the curve
  {
    const { nodes } = chainNodes(5);
    const g = { spans: [] };
    const T = chainNodes(5).T;
    for (let k = 0; k + 1 < T.length; k++) {
      const p0 = nodes[k], p3 = nodes[k + 1];
      g.spans.push([p0, [p0[0] + T[k].a, p0[1] - T[k].b], [p3[0] - T[k + 1].a, p3[1] + T[k + 1].b], p3]);
    }
    const tight = tightest(g), d = 0.6 * tight.R, off = offsets(g, d);
    const f = frame(document.getElementById('x3b'), off.flatMap(o => [o.p, o.l, o.r]), 44, 0.64);
    const { ctx, put } = f;
    for (const side of ['l', 'r']) {
      ctx.strokeStyle = '#1f5fa8'; ctx.lineWidth = 1.8; ctx.beginPath();
      off.forEach((o, i) => { const q = put(o[side]); i ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1]); }); ctx.stroke();
    }
    ctx.strokeStyle = '#8a3b12'; ctx.lineWidth = 1.6; ctx.beginPath();
    off.forEach((o, i) => { const q = put(o.p); i ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1]); }); ctx.stroke();
    ctx.font = '15px Georgia,serif'; ctx.fillStyle = '#2e2413';
    ctx.fillText('curve + offset rails', 12, f.H - 14);
    ctx.font = '12px ui-monospace,Menlo,monospace'; ctx.fillStyle = '#a23b2a';
    ctx.fillText('floating point: √(x′² + y′²)', 12, f.H - 34);
  }
}

function update() {
  const d = build();
  if (!d) return;
  drawTri(tangents());
  drawChain3(chain3());
  drawStem1();
  drawCompare();
  const s = stats(d);
  draw(d, s);
  table(d);

  const pct = x => (100 * x).toFixed(1) + '%';
  out.innerHTML =
    'spans <b>' + s.spans + '</b> · nodes <b>' + s.nodes + '</b> · handles ' +
    (st.g2 ? 'per-node (G2)' : 'uniform h=' + st.h) + '\n' +
    'extent <b>' + Math.round(s.w).toLocaleString() + ' × ' + Math.round(s.ht).toLocaleString() + '</b>' +
    ' · largest coordinate <b>' + Math.round(s.maxAbs).toLocaleString() + '</b> (' + s.digits + ' digits)\n' +
    'control points: ' + (s.integer ? '<span class="good">integers</span>' : '<span class="bad">rational — scaled grid only</span>') + '\n' +
    'C1: <span class="good">exact</span> at all ' + Math.max(0, s.spans - 1) + ' joins' +
    ' · curvature jump: median <b>' + pct(s.med) + '</b>, max <b>' + pct(s.max) + '</b>';

  const perUnit = s.w / st.S;
  gridOut.innerHTML =
    'extent at S=' + st.S + ': <b>' + Math.round(s.w).toLocaleString() + ' × ' + Math.round(s.ht).toLocaleString() + '</b>\n' +
    'extent per unit step (S=1): <b>' + Math.round(perUnit).toLocaleString() + '</b> × ' + Math.round(s.ht / st.S).toLocaleString() + '\n' +
    'S for a 200,000-wide sheet: <b>' + Math.max(1, Math.round(200000 / Math.max(1, perUnit))) + '</b>' +
    ' · S for 1,000,000: <b>' + Math.max(1, Math.round(1000000 / Math.max(1, perUnit))) + '</b>';
}

function bind(id, key, fmt) {
  const el = document.getElementById(id), val = document.getElementById(id + 'V');
  el.addEventListener('input', () => {
    st[key] = Number(el.value);
    if (val) val.textContent = fmt ? fmt(st[key]) : st[key];
    update();
  });
}
bind('n', 'n'); bind('m0', 'm0'); bind('m1', 'm1'); bind('S', 'S'); bind('h', 'h');

const e3m = document.getElementById('e3m'), e3mV = document.getElementById('e3mV');
const e3k = document.getElementById('e3k'), e3kV = document.getElementById('e3kV');
e3m.addEventListener('input', () => { st3.m0 = Number(e3m.value); e3mV.textContent = st3.m0; update(); });
e3k.addEventListener('input', () => { st3.count = Number(e3k.value); e3kV.textContent = st3.count; update(); });
document.getElementById('e3step').addEventListener('click', e => {
  st3.more = !st3.more;
  e.target.textContent = 'x step: ' + (st3.more ? 'one more each' : 'equal');
  update();
});

const s1k = document.getElementById('s1k'), s1kV = document.getElementById('s1kV');
const s1d = document.getElementById('s1d'), s1dV = document.getElementById('s1dV');
s1k.addEventListener('input', () => { st1.count = Number(s1k.value); s1kV.textContent = st1.count; update(); });
s1d.addEventListener('input', () => { st1.frac = Number(s1d.value); s1dV.textContent = st1.frac.toFixed(2); update(); });

document.getElementById('g2').addEventListener('click', e => {
  st.g2 = !st.g2;
  e.target.textContent = 'handles: ' + (st.g2 ? 'per-node (G2)' : 'uniform');
  update();
});
document.getElementById('zoom').addEventListener('click', e => {
  st.zoom = !st.zoom;
  e.target.textContent = 'zoom: ' + (st.zoom ? 'first 4 spans' : 'whole chain');
  update();
});
document.getElementById('handles').addEventListener('click', e => {
  st.handles = !st.handles;
  e.target.textContent = 'handles: ' + (st.handles ? 'on' : 'off');
  update();
});
document.getElementById('reset').addEventListener('click', () => {
  Object.assign(st, { n: 2, m0: 5, m1: 12, S: 2, h: 1, g2: false, zoom: false, handles: true });
  for (const [id, key] of [['n', 'n'], ['m0', 'm0'], ['m1', 'm1'], ['S', 'S'], ['h', 'h']]) {
    document.getElementById(id).value = st[key];
    document.getElementById(id + 'V').textContent = st[key];
  }
  document.getElementById('g2').textContent = 'handles: uniform';
  Object.assign(st3, { m0: 2, count: 3, more: true });
  document.getElementById('e3m').value = st3.m0; document.getElementById('e3mV').textContent = st3.m0;
  document.getElementById('e3k').value = st3.count; document.getElementById('e3kV').textContent = st3.count;
  document.getElementById('e3step').textContent = 'x step: one more each';
  Object.assign(st1, { count: 6, frac: 0.6 });
  document.getElementById('s1k').value = st1.count; document.getElementById('s1kV').textContent = st1.count;
  document.getElementById('s1d').value = st1.frac; document.getElementById('s1dV').textContent = st1.frac.toFixed(2);
  document.getElementById('zoom').textContent = 'zoom: whole chain';
  document.getElementById('handles').textContent = 'handles: on';
  update();
});

window.addEventListener('resize', update);
update();
</script>
</body>
</html>
'''


def main():
    out = ROOT / "workbench" / "pythagorean-chain-editor.html"
    out.write_text(PAGE, encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
