// Draws the glue sandbox. The maths lives in app/src/lib/glue.js; this file only reads the
// controls, draws, and says what the numbers are.
import {
  parseSlope, fracText, controls, cubicPoints, crossings, slopeAt,
} from "../lib/glue.js";

const el = (id) => document.getElementById(id);

function draw() {
  const host = el("glue-preview");
  const readout = el("g-readout");
  const s0 = parseSlope(el("g-slope0").value);
  const s1 = parseSlope(el("g-slope1").value);
  if (!s0 || !s1) {
    readout.textContent = "both slopes must be fractions such as 3/4 or -7/24";
    return;
  }
  const gap = Number(el("g-gap").value);
  const h0 = Number(el("g-h0").value) / 100;
  const h1 = Number(el("g-h1").value) / 100;
  el("g-gap-out").textContent = gap.toFixed(2);
  el("g-h0-out").textContent = `${el("g-h0").value} %`;
  el("g-h1-out").textContent = `${el("g-h1").value} %`;

  // the two end points, one gap apart along x
  const p0 = { x: 0, y: 0 };
  const p3 = { x: gap, y: 0 };
  const ctrl = controls(p0, p3, s0, s1, h0, h1);
  const curve = cubicPoints(ctrl);
  const loops = crossings(curve);

  // the neighbouring legs, to show what is being joined
  const leg = (p, slope, sign, length = 0.45 * gap) => {
    const v = { x: slope.d, y: slope.n };
    const len = Math.hypot(v.x, v.y) || 1;
    return [{ x: p.x - sign * (length * v.x) / len, y: p.y - sign * (length * v.y) / len }, p];
  };
  const incoming = leg(p0, s0, 1);
  const outgoing = leg(p3, s1, -1);

  const all = [...curve, ...incoming, ...outgoing];
  const xs = all.map((p) => p.x), ys = all.map((p) => p.y);
  const x0 = Math.min(...xs), x1 = Math.max(...xs);
  const y0 = Math.min(...ys), y1 = Math.max(...ys);
  const w = 640, h = 420, margin = 30;
  const k = Math.min((w - 2 * margin) / (x1 - x0 || 1), (h - 2 * margin) / (y1 - y0 || 1));
  const ox = (w - (x1 - x0) * k) / 2, oy = (h - (y1 - y0) * k) / 2;
  const put = (p) => [ox + (p.x - x0) * k, h - (oy + (p.y - y0) * k)];
  const path = (pts, colour, width, dash = "") => '<path d="M ' +
    pts.map((p) => put(p).map((v) => v.toFixed(1)).join(" ")).join(" L ") +
    `" fill="none" stroke="${colour}" stroke-width="${width}"${dash ? ` stroke-dasharray="${dash}"` : ""} ` +
    'stroke-linecap="round" stroke-linejoin="round"/>';
  const dots = [p0, p3].map((p) => {
    const [x, y] = put(p);
    return `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="4" fill="#b03a2e"/>`;
  }).join("");

  host.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}">
    <rect width="${w}" height="${h}" fill="#fff"/>
    ${path(incoming, "#9a9a9a", 1.6, "7 5")}
    ${path(outgoing, "#9a9a9a", 1.6, "7 5")}
    ${path(curve, "#2b2b2b", 2.2)}
    ${dots}
    <text x="12" y="20" font-family="ui-monospace, Menlo, monospace" font-size="12" fill="#8a7a62">
      glued ${fracText(s0)} to ${fracText(s1)} · gap ${gap.toFixed(2)} · handles ${h0.toFixed(2)} / ${h1.toFixed(2)}</text>
    <text x="12" y="${h - 10}" font-family="ui-monospace, Menlo, monospace" font-size="12" fill="#5a4a36">
      ${loops.length ? `${loops.length} self-crossing(s)` : "no self-crossing"} · control points from exact directions</text>
  </svg>`;

  const drawnSlope = (t) => {
    const value = slopeAt(ctrl, t);
    return Number.isFinite(value) ? value : "∞";
  };
  readout.innerHTML =
    `start slope ${fracText(s0)} (drawn ${typeof drawnSlope(0) === "number" ? drawnSlope(0).toFixed(6) : "∞"}) · ` +
    `end slope ${fracText(s1)} (drawn ${typeof drawnSlope(1) === "number" ? drawnSlope(1).toFixed(6) : "∞"})<br>` +
    `control points: (${ctrl.map((p) => `${p.x.toFixed(4)}, ${p.y.toFixed(4)}`).join(") (")})<br>` +
    `${loops.length ? `crosses itself at ${loops.map((p) => `${p.x.toFixed(2)}, ${p.y.toFixed(2)}`).join(" · ")}` : "does not cross itself at these handles"}`;
}

function mount() {
  for (const id of ["g-slope0", "g-slope1", "g-gap", "g-h0", "g-h1"]) {
    el(id)?.addEventListener("input", draw);
  }
  draw();
}

if (typeof document !== "undefined") {
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mount);
  else mount();
}
