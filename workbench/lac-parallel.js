// LAC → evolute → parallel involutes.
//
// The log-aesthetic curve has curvature kappa(s) = s^-alpha, so its tangent
// angle is theta(s) = s^(1-alpha)/(1-alpha) for alpha != 1, and log(s) for
// alpha = 1.  The evolute is E = C + rho N, rho = s^alpha.  Every parallel of C
// is an involute of that one evolute:
//
//     P_d(s) = E(s) - (s_E(s) + d0 + d) T_E(s)
//
// with T_E = sign(alpha) N and d0 = sign(alpha) rho(s0).  The d = 0 member is C;
// d is the offset distance.  No normal step of C is needed after the evolute.
//
// The evolute of a LAC is another LAC ("auto-evolution"), with
// alpha_E = 2 - 1/alpha: alpha=-1 (Euler/clothoid) -> 3, alpha=1 (log spiral)
// -> 1, alpha=2 -> 3/2.

const INK = "#2e2413";
const GOLD = "#c9a441";
const OFFSET_A = "#1f5fa8";
const OFFSET_B = "#b23a2b";
const MUTED = "#7b6c4e";
const GRID = "#e4dcc6";
const PAPER = "#fffdf7";

const ALPHAS = [
  { value: -1, label: "Euler / clothoid · α = −1", s0: 0.60, s1: 2.40 },
  { value: 0.5, label: "LAC · α = 0.5", s0: 0.45, s1: 2.20 },
  { value: 1, label: "Log spiral · α = 1", s0: 0.45, s1: 2.40 },
  { value: 2, label: "LAC · α = 2", s0: 0.50, s1: 2.00 },
  { value: 3, label: "LAC · α = 3", s0: 0.55, s1: 1.80 },
];

const N = 420;

function theta(alpha, s) {
  if (Math.abs(alpha - 1) < 1e-12) return Math.log(s);
  return Math.pow(s, 1 - alpha) / (1 - alpha);
}

function sample(alpha, s0, s1) {
  const ds = (s1 - s0) / N;
  const C = [], E = [], T = [];
  let x = 0, y = 0;
  for (let i = 0; i <= N; i++) {
    const s = s0 + i * ds;
    if (i > 0) {
      const sm = s0 + (i - 0.5) * ds;
      const th = theta(alpha, sm);
      x += ds * Math.cos(th);
      y += ds * Math.sin(th);
    }
    const th = theta(alpha, s);
    const nx = -Math.sin(th), ny = Math.cos(th);
    const rho = Math.pow(s, alpha);
    C.push([x, y]);
    E.push([x + rho * nx, y + rho * ny]);
    T.push([Math.sign(alpha) * nx, Math.sign(alpha) * ny]);
  }
  return { C, E, T, alpha, s0, s1 };
}

function offset(C, T, d) {
  return C.map((p, i) => [p[0] - d * T[i][0], p[1] - d * T[i][1]]);
}

function bbox(points) {
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
  for (const [x, y] of points) {
    x0 = Math.min(x0, x);
    y0 = Math.min(y0, y);
    x1 = Math.max(x1, x);
    y1 = Math.max(y1, y);
  }
  return [x0, y0, x1, y1];
}

function path(ctx, points, put) {
  ctx.beginPath();
  points.forEach((p, i) => {
    const [x, y] = put(p);
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();
}

function draw() {
  const canvas = document.getElementById("curveCanvas");
  const alphaSel = document.getElementById("alpha");
  const dRange = document.getElementById("d");
  const dOut = document.getElementById("dval");
  const alpha = Number(alphaSel.value);
  const opt = ALPHAS.find((a) => a.value === alpha);
  const data = sample(alpha, opt.s0, opt.s1);

  const baseBox = bbox(data.C);
  const size = Math.max(baseBox[2] - baseBox[0], baseBox[3] - baseBox[1], 1e-9);
  const dMax = 0.24 * size;
  const d = dMax * Number(dRange.value) / 100;
  dOut.textContent = `± ${d.toFixed(3)}`;

  const plus = offset(data.C, data.T, d);
  const minus = offset(data.C, data.T, -d);
  const all = [...data.C, ...data.E, ...plus, ...minus];
  const [x0, y0, x1, y1] = bbox(all);

  const dpr = window.devicePixelRatio || 1;
  const W = canvas.clientWidth;
  const H = canvas.clientHeight;
  canvas.width = Math.round(W * dpr);
  canvas.height = Math.round(H * dpr);
  const ctx = canvas.getContext("2d");
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, W, H);

  ctx.fillStyle = PAPER;
  ctx.fillRect(0, 0, W, H);

  const pad = 32;
  const k = Math.min((W - 2 * pad) / (x1 - x0 || 1),
                     (H - 2 * pad) / (y1 - y0 || 1));
  const ox = (W - (x1 - x0) * k) / 2;
  const oy = (H - (y1 - y0) * k) / 2;
  const put = ([x, y]) => [ox + (x - x0) * k, H - (oy + (y - y0) * k)];

  // a light grid in page space
  ctx.strokeStyle = GRID;
  ctx.lineWidth = 1;
  for (let i = 1; i < 8; i++) {
    const gx = x0 + (x1 - x0) * i / 8;
    const a = put([gx, y0]), b = put([gx, y1]);
    ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke();
    const gy = y0 + (y1 - y0) * i / 8;
    const c = put([x0, gy]), e = put([x1, gy]);
    ctx.beginPath(); ctx.moveTo(c[0], c[1]); ctx.lineTo(e[0], e[1]); ctx.stroke();
  }

  // evolute: the shared structural anchor
  ctx.setLineDash([7, 5]);
  ctx.strokeStyle = GOLD;
  ctx.lineWidth = 1.4;
  path(ctx, data.E, put);
  ctx.setLineDash([]);

  // the two offsets
  ctx.strokeStyle = OFFSET_A;
  ctx.lineWidth = 1.6;
  path(ctx, plus, put);
  ctx.strokeStyle = OFFSET_B;
  path(ctx, minus, put);

  // the LAC base
  ctx.strokeStyle = INK;
  ctx.lineWidth = 2.6;
  path(ctx, data.C, put);

  // end labels
  const label = (points, colour, text) => {
    const [x, y] = put(points[points.length - 1]);
    ctx.fillStyle = colour;
    ctx.font = "11px ui-monospace, Menlo, monospace";
    ctx.fillText(text, x + 6, y - 5);
  };
  label(data.C, INK, "LAC base");
  label(plus, OFFSET_A, `d = +${d.toFixed(2)}`);
  label(minus, OFFSET_B, `d = −${d.toFixed(2)}`);
  label(data.E, GOLD, "evolute");

  const aE = 2 - 1 / alpha;
  document.getElementById("note").textContent =
    `α = ${alpha} · evolute LAC α_E = ${Number.isFinite(aE) ? aE.toFixed(3) : "—"} · ` +
    `${N} samples · ${d === 0 ? "the base alone" : "three members of one involute family"}`;
}

function main() {
  const alphaSel = document.getElementById("alpha");
  ALPHAS.forEach((a) => {
    const opt = document.createElement("option");
    opt.value = String(a.value);
    opt.textContent = a.label;
    if (a.value === 1) opt.selected = true;
    alphaSel.appendChild(opt);
  });
  const params = new URLSearchParams(window.location.search);
  const aParam = Number(params.get("alpha"));
  if (Number.isFinite(aParam) && ALPHAS.some((a) => a.value === aParam)) {
    alphaSel.value = String(aParam);
  }
  const dParam = Number(params.get("d"));
  if (Number.isFinite(dParam) && params.has("d")) {
    document.getElementById("d").value = String(Math.max(0, Math.min(100, dParam)));
  }
  alphaSel.addEventListener("change", draw);
  document.getElementById("d").addEventListener("input", draw);
  window.addEventListener("resize", draw);
  draw();
}

window.addEventListener("DOMContentLoaded", main);
