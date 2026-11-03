// Evolute → parallel involutes for several classical families.
//
// For any smooth curve C, the centres of curvature trace E = C + rho N.  Every
// parallel of C is an involute of E:
//
//     P_d(t) = E(t) - (s_E(t) + d0 + d) T_E(t)
//
// with T_E = E'/|E'| and d0 chosen so P_0 = C at the first sample.  The LAC
// also has an analytic evolute (another LAC, alpha_E = 2 - 1/alpha); the other
// families are computed by the same numerical construction.

const INK = "#2e2413";
const GOLD = "#c9a441";
const OFFSET_A = "#1f5fa8";
const OFFSET_B = "#b23a2b";
const MUTED = "#7b6c4e";
const GRID = "#e4dcc6";
const PAPER = "#fffdf7";
const N = 420;

const ALPHA = [
  { value: -1, label: "Euler / clothoid · α = −1", s0: 0.60, s1: 2.40 },
  { value: 0.5, label: "LAC · α = 0.5", s0: 0.45, s1: 2.20 },
  { value: 1, label: "Log spiral · α = 1", s0: 0.45, s1: 2.40 },
  { value: 2, label: "LAC · α = 2", s0: 0.50, s1: 2.00 },
  { value: 3, label: "LAC · α = 3", s0: 0.55, s1: 1.80 },
];

function theta(alpha, s) {
  if (Math.abs(alpha - 1) < 1e-12) return Math.log(s);
  return Math.pow(s, 1 - alpha) / (1 - alpha);
}

function lacPoints(alpha) {
  const opt = ALPHA.find((a) => a.value === alpha) || ALPHA[2];
  const ds = (opt.s1 - opt.s0) / N;
  const pts = [];
  let x = 0, y = 0;
  for (let i = 0; i <= N; i++) {
    const s = opt.s0 + i * ds;
    if (i > 0) {
      const sm = opt.s0 + (i - 0.5) * ds;
      const th = theta(alpha, sm);
      x += ds * Math.cos(th);
      y += ds * Math.sin(th);
    }
    pts.push([x, y]);
  }
  return pts;
}

function sampleRange(fn, t0, t1, n = N) {
  const out = [];
  for (let i = 0; i <= n; i++) out.push(fn(t0 + (t1 - t0) * i / n));
  return out;
}

const TAU = 2 * Math.PI;

const FAMILIES = [
  { key: "lac", label: "LAC · α", param: { name: "α", type: "select", values: ALPHA.map((a) => [String(a.value), a.label]), value: "1" },
    points: (p) => lacPoints(Number(p)), source: "LAC spines · S35–S65 · check-spirals.py", status: "done elsewhere + here",
    evolute: "LAC α_E = 2 − 1/α" },
  { key: "cycloid", label: "cycloid", points: () => sampleRange((t) => [t - Math.sin(t), 1 - Math.cos(t)], 0.15, Math.PI - 0.15),
    source: "stem-library S69", status: "finished here", evolute: "a congruent cycloid" },
  { key: "epicycloid", label: "epicycloid · k", param: { name: "k", type: "select", values: [["1", "k=1 · cardioid"], ["2", "k=2 · nephroid"], ["3", "k=3"], ["4", "k=4"], ["5", "k=5"]], value: "2" },
    points: (p) => { const k = Number(p); const end = k === 1 ? TAU : TAU / k; return sampleRange((t) => [(k + 1) * Math.cos(t) - Math.cos((k + 1) * t), (k + 1) * Math.sin(t) - Math.sin((k + 1) * t)], 0.1, end - 0.1); },
    source: "generators · epicycloids", status: "finished here", evolute: "same roulette family" },
  { key: "hypocycloid", label: "hypocycloid · k", param: { name: "k", type: "select", values: [["3", "k=3 · deltoid"], ["4", "k=4 · astroid"]], value: "4" },
    points: (p) => { const k = Number(p); return sampleRange((t) => [(k - 1) * Math.cos(t) + Math.cos((k - 1) * t), (k - 1) * Math.sin(t) - Math.sin((k - 1) * t)], 0.1, TAU / k - 0.1); },
    source: "generators · S12–S19", status: "finished here", evolute: "same roulette family" },
  { key: "ellipse", label: "ellipse → astroid", param: { name: "b", type: "select", values: [["0.35", "b = 0.35"], ["0.62", "b = 0.62"], ["0.82", "b = 0.82"]], value: "0.62" },
    points: (p) => { const b = Number(p); return sampleRange((t) => [Math.cos(t), b * Math.sin(t)], 0, TAU); },
    source: "astroid S17 · ellipse new here", status: "finished here", evolute: "the astroid" },
  { key: "astroid", label: "astroid", points: () => sampleRange((t) => [Math.cos(t) ** 3, Math.sin(t) ** 3], 0.05, Math.PI / 2 - 0.05),
    source: "stem-library S17", status: "finished here", evolute: "an astroid (scaled)" },
  { key: "circle-involute", label: "circle involute", points: () => sampleRange((t) => [Math.cos(t) + t * Math.sin(t), Math.sin(t) - t * Math.cos(t)], 0.15, 2.5 * Math.PI),
    source: "stem-library S68", status: "finished here", evolute: "the circle" },
  { key: "catenary", label: "catenary → tractrix", points: () => sampleRange((t) => [t, Math.cosh(t)], -1.5, 1.5),
    source: "stem-library S66 · tractrix new here", status: "finished here", evolute: "the tractrix" },
  { key: "parabola", label: "parabola → semicubical", points: () => sampleRange((t) => [t, t * t], -1.5, 1.5),
    source: "new here", status: "finished here", evolute: "the semicubical parabola" },
  { key: "semicubical", label: "semicubical (Neile)", points: () => sampleRange((t) => [t * t, t * t * t], 0.05, 1.25),
    source: "new here · evolute of the parabola", status: "finished here", evolute: "a cusped curve (computed)" },
  { key: "ph", label: "PH cubic · u = 1, v = t", points: () => sampleRange((t) => [t - t * t * t / 3, t * t], 0, 1.2),
    source: "generators S01–S04 · hodograph.py · sample here", status: "exact normal offset here", evolute: "the evolute of this PH cubic" },
];

function evoluteData(C) {
  const n = C.length - 1;
  const N = [], E = [], Rho = [];
  for (let i = 0; i <= n; i++) {
    const a = C[Math.max(0, i - 1)];
    const b = C[i];
    const c = C[Math.min(n, i + 1)];
    let dx = c[0] - a[0], dy = c[1] - a[1];
    let ddx = c[0] - 2 * b[0] + a[0];
    let ddy = c[1] - 2 * b[1] + a[1];
    if (n >= 2 && i === 0) {
      dx = C[2][0] - C[0][0]; dy = C[2][1] - C[0][1];
      ddx = C[2][0] - 2 * C[1][0] + C[0][0];
      ddy = C[2][1] - 2 * C[1][1] + C[0][1];
    } else if (n >= 2 && i === n) {
      dx = C[n][0] - C[n - 2][0]; dy = C[n][1] - C[n - 2][1];
      ddx = C[n][0] - 2 * C[n - 1][0] + C[n - 2][0];
      ddy = C[n][1] - 2 * C[n - 1][1] + C[n - 2][1];
    }
    const l = Math.hypot(dx, dy) || 1e-12;
    const tx = dx / l, ty = dy / l;
    const den = Math.pow(dx * dx + dy * dy, 1.5) || 1e-12;
    const kappa = 4 * (dx * ddy - dy * ddx) / den;
    const rho = Math.abs(kappa) > 1e-12 ? 1 / kappa : 0;
    const nx = -ty, ny = tx;
    N.push([nx, ny]);
    Rho.push(rho);
    E.push([b[0] + rho * nx, b[1] + rho * ny]);
  }
  return { E, N, Rho };
}

function offset(C, N, d) {
  return C.map((p, i) => [p[0] + d * N[i][0], p[1] + d * N[i][1]]);
}

function bbox(points) {
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
  for (const [x, y] of points) {
    x0 = Math.min(x0, x); y0 = Math.min(y0, y);
    x1 = Math.max(x1, x); y1 = Math.max(y1, y);
  }
  return [x0, y0, x1, y1];
}

function stroke(ctx, points, put) {
  ctx.beginPath();
  points.forEach((p, i) => {
    const [x, y] = put(p);
    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  });
  ctx.stroke();
}

function currentFamily() {
  return FAMILIES.find((f) => f.key === document.getElementById("family").value) || FAMILIES[0];
}

function paramValue(f) {
  const el = document.getElementById("param");
  if (!f.param || !el) return f.param ? f.param.value : null;
  return el.value;
}

function buildParam(f) {
  const wrap = document.getElementById("paramwrap");
  wrap.innerHTML = "";
  if (!f.param) return;
  const label = document.createElement("label");
  label.textContent = f.param.name;
  let input;
  if (f.param.type === "select") {
    input = document.createElement("select");
    input.id = "param";
    f.param.values.forEach(([value, text]) => {
      const o = document.createElement("option");
      o.value = value; o.textContent = text;
      if (value === f.param.value) o.selected = true;
      input.appendChild(o);
    });
  }
  input.addEventListener("change", draw);
  label.appendChild(input);
  wrap.appendChild(label);
}

function draw() {
  const f = currentFamily();
  const param = paramValue(f);
  const C = f.points(param);
  const data = evoluteData(C);

  const baseBox = bbox(C);
  const size = Math.max(baseBox[2] - baseBox[0], baseBox[3] - baseBox[1], 1e-9);
  const dMax = 0.20 * size;
  const d = dMax * Number(document.getElementById("d").value) / 100;
  document.getElementById("dval").textContent = `± ${d.toFixed(3)}`;

  const plus = offset(C, data.N, d);
  const minus = offset(C, data.N, -d);
  const core = [...C, ...plus, ...minus];
  const [cx0, cy0, cx1, cy1] = bbox(core);
  const padX = (cx1 - cx0) * 0.22, padY = (cy1 - cy0) * 0.22;
  const localE = data.E.filter((p) =>
    p[0] >= cx0 - padX && p[0] <= cx1 + padX &&
    p[1] >= cy0 - padY && p[1] <= cy1 + padY);
  const [x0, y0, x1, y1] = bbox([...core, ...localE]);

  const canvas = document.getElementById("curveCanvas");
  const dpr = window.devicePixelRatio || 1;
  const W = canvas.clientWidth, H = canvas.clientHeight;
  canvas.width = Math.round(W * dpr);
  canvas.height = Math.round(H * dpr);
  const ctx = canvas.getContext("2d");
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.fillStyle = PAPER; ctx.fillRect(0, 0, W, H);

  const pad = 30;
  const k = Math.min((W - 2 * pad) / (x1 - x0 || 1), (H - 2 * pad) / (y1 - y0 || 1));
  const ox = (W - (x1 - x0) * k) / 2, oy = (H - (y1 - y0) * k) / 2;
  const put = ([x, y]) => [ox + (x - x0) * k, H - (oy + (y - y0) * k)];

  ctx.strokeStyle = GRID; ctx.lineWidth = 1;
  for (let i = 1; i < 8; i++) {
    const gx = x0 + (x1 - x0) * i / 8, a = put([gx, y0]), b = put([gx, y1]);
    ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke();
    const gy = y0 + (y1 - y0) * i / 8, c = put([x0, gy]), e = put([x1, gy]);
    ctx.beginPath(); ctx.moveTo(c[0], c[1]); ctx.lineTo(e[0], e[1]); ctx.stroke();
  }

  ctx.setLineDash([7, 5]); ctx.strokeStyle = GOLD; ctx.lineWidth = 1.4;
  stroke(ctx, data.E, put); ctx.setLineDash([]);

  ctx.strokeStyle = OFFSET_A; ctx.lineWidth = 1.6; stroke(ctx, plus, put);
  ctx.strokeStyle = OFFSET_B; stroke(ctx, minus, put);
  ctx.strokeStyle = INK; ctx.lineWidth = 2.6; stroke(ctx, C, put);

  const label = (points, colour, text, frac = 0.5) => {
    const i = Math.max(0, Math.min(points.length - 1, Math.floor((points.length - 1) * frac)));
    const [x, y] = put(points[i]);
    ctx.fillStyle = colour;
    ctx.font = "11px ui-monospace, Menlo, monospace";
    const w = ctx.measureText(text).width;
    const lx = Math.min(Math.max(x + 6, 6), W - w - 6);
    const ly = Math.min(Math.max(y - 6, 14), H - 6);
    ctx.fillStyle = "rgba(255,253,247,0.86)";
    ctx.fillRect(lx - 3, ly - 10, w + 6, 13);
    ctx.fillStyle = colour;
    ctx.fillText(text, lx, ly);
  };
  label(C, INK, "base", 0.5);
  label(plus, OFFSET_A, `d = +${d.toFixed(2)}`, 0.32);
  label(minus, OFFSET_B, `d = −${d.toFixed(2)}`, 0.68);

  const inset = document.getElementById("evoluteCanvas");
  if (inset) {
    const iw = inset.clientWidth, ih = inset.clientHeight;
    inset.width = Math.round(iw * dpr);
    inset.height = Math.round(ih * dpr);
    const ictx = inset.getContext("2d");
    ictx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ictx.fillStyle = PAPER;
    ictx.fillRect(0, 0, iw, ih);
    const [ex0, ey0, ex1, ey1] = bbox(data.E);
    const ipad = 22;
    const ik = Math.min((iw - 2 * ipad) / (ex1 - ex0 || 1), (ih - 2 * ipad) / (ey1 - ey0 || 1));
    const iox = (iw - (ex1 - ex0) * ik) / 2, ioy = (ih - (ey1 - ey0) * ik) / 2;
    const iput = ([x, y]) => [iox + (x - ex0) * ik, ih - (ioy + (y - ey0) * ik)];
    ictx.strokeStyle = GRID;
    ictx.lineWidth = 1;
    for (let i = 1; i < 6; i++) {
      const gx = ex0 + (ex1 - ex0) * i / 6;
      const a = iput([gx, ey0]), b = iput([gx, ey1]);
      ictx.beginPath(); ictx.moveTo(a[0], a[1]); ictx.lineTo(b[0], b[1]); ictx.stroke();
      const gy = ey0 + (ey1 - ey0) * i / 6;
      const c = iput([ex0, gy]), e = iput([ex1, gy]);
      ictx.beginPath(); ictx.moveTo(c[0], c[1]); ictx.lineTo(e[0], e[1]); ictx.stroke();
    }
    ictx.setLineDash([7, 5]);
    ictx.strokeStyle = GOLD;
    ictx.lineWidth = 1.4;
    ictx.beginPath();
    data.E.forEach((p, i) => {
      const [x, y] = iput(p);
      if (i === 0) ictx.moveTo(x, y); else ictx.lineTo(x, y);
    });
    ictx.stroke();
    ictx.setLineDash([]);
    ictx.fillStyle = MUTED;
    ictx.font = "10px ui-monospace, Menlo, monospace";
    ictx.fillText("evolute E · full", 8, 16);
  }

  document.getElementById("note").textContent =
    `${f.label} · ${f.evolute} · ${d === 0 ? "the base alone" : "two-sided parallel"}`;
  document.getElementById("source").textContent = `${f.source} · ${f.status}`;
}

function main() {
  const familySel = document.getElementById("family");
  FAMILIES.forEach((f) => {
    const o = document.createElement("option");
    o.value = f.key; o.textContent = f.label;
    if (f.key === "lac") o.selected = true;
    familySel.appendChild(o);
  });

  const params = new URLSearchParams(window.location.search);
  const fParam = params.get("family");
  if (fParam && FAMILIES.some((f) => f.key === fParam)) familySel.value = fParam;
  const aParam = params.get("alpha");
  if (aParam) {
    const lac = FAMILIES[0];
    if (lac.param.values.some(([v]) => v === aParam)) lac.param.value = aParam;
  }
  const dParam = params.get("d");
  if (dParam && Number.isFinite(Number(dParam))) {
    document.getElementById("d").value = String(Math.max(0, Math.min(100, Number(dParam))));
  }

  const rebuild = () => { buildParam(currentFamily()); draw(); };
  familySel.addEventListener("change", rebuild);
  document.getElementById("d").addEventListener("input", draw);
  window.addEventListener("resize", draw);
  rebuild();
}

window.addEventListener("DOMContentLoaded", main);
