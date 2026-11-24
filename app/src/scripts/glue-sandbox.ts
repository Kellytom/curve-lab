// Draws the glue sandbox. The maths lives in app/src/lib/glue.ts; this file only reads the
// controls, draws, and says what the numbers are.
import {
  parseSlope, fracText, controls, cubicPoints, rationalPoints, crossings, slopeAt,
  quinticControls, quinticPoints, endConditions, type Point,
} from "../lib/glue.ts";
import { fitSpanOffset } from "../lib/parallel-bezier.ts";

const el = (id: string): HTMLElement | null => document.getElementById(id);
const input = (id: string): HTMLInputElement => el(id) as HTMLInputElement;
const select = (id: string): HTMLSelectElement => el(id) as HTMLSelectElement;
const output = (id: string): HTMLOutputElement => el(id) as HTMLOutputElement;

function draw(): void {
  const host = el("glue-preview");
  const readout = el("g-readout");
  if (!host || !readout) return;
  const s0 = parseSlope(input("g-slope0").value);
  const s1 = parseSlope(input("g-slope1").value);
  if (!s0 || !s1) {
    readout.textContent = "both slopes must be fractions such as 3/4 or -7/24";
    return;
  }
  const gap = Number(input("g-gap").value);
  const h0 = Number(input("g-h0").value) / 100;
  const h1 = Number(input("g-h1").value) / 100;
  output("g-gap-out").textContent = gap.toFixed(2);
  output("g-h0-out").textContent = `${input("g-h0").value} %`;
  output("g-h1-out").textContent = `${input("g-h1").value} %`;

  // the two end points, one gap apart along x
  const p0 = { x: 0, y: 0 };
  const p5 = { x: gap, y: 0 };
  const kind = select("g-kind").value;
  const weight = Number(input("g-weight").value);
  const distance = Number(input("g-distance").value);
  output("g-weight-out").textContent = weight.toFixed(1);
  output("g-distance-out").textContent = distance.toFixed(2);
  input("g-weight-row").style.display = kind === "rational" ? "" : "none";
  input("g-distance-row").style.display = kind === "levien" ? "" : "none";
  input("g-g3-row").style.display = kind === "quintic" ? "" : "none";

  const ctrl = controls(p0, p5, s0, s1, h0, h1);
  if (!ctrl) {
    readout.textContent = "the slopes must be finite directions";
    return;
  }
  let curve = cubicPoints(ctrl);
  let offset: Point[][] | null = null;
  let fit: { spans: unknown[]; error_max: number; cusps: unknown[] } | null = null;
  let conditions: ReturnType<typeof endConditions> | null = null;
  if (kind === "rational") curve = rationalPoints(ctrl, [1, weight, weight, 1]);
  if (kind === "quintic") {
    const q = quinticControls(p0, p5, s0, s1, {
      h0, h1,
      kappa0: Number(input("g-k0").value) || 0,
      kappa1: Number(input("g-k1").value) || 0,
      dkappa0: Number(input("g-r0").value) || 0,
      dkappa1: Number(input("g-r1").value) || 0,
    });
    if (!q) {
      readout.textContent = "the quintic needs both handles above zero";
      return;
    }
    curve = quinticPoints(q);
    conditions = endConditions(q);
  }
  if (kind === "levien") {
    // the Levien port works in [x, y] tuples; the sandbox uses {x, y}
    const pt = (p: Point): [number, number] => [p.x, p.y];
    const back = (pair: [number, number]): Point => ({ x: pair[0], y: pair[1] });
    fit = fitSpanOffset({ p0: pt(ctrl[0]), c1: pt(ctrl[1]), c2: pt(ctrl[2]), p3: pt(ctrl[3]) },
      distance, 0.005);
    offset = (fit.spans as Array<{ p0: [number, number]; c1: [number, number];
      c2: [number, number]; p3: [number, number] }>).map((span) => cubicPoints([
      back(span.p0), back(span.c1), back(span.c2), back(span.p3),
    ]));
  }
  // the band: the connector's two side curves, at a width that is a share of the gap. The ends
  // are drawn with caps to the spine, so the ribbon can be seen joining the neighbours' bands.
  const bandOn = input("g-band").checked;
  const bandWidth = Number(input("g-band-w").value) / 100;
  input("g-band-row").style.display = bandOn ? "" : "none";
  output("g-band-out").textContent = `${(bandWidth * 100).toFixed(1)} %`;
  let sides: Point[][] | null = null;
  let bandFold = 0;
  if (bandOn) {
    const width = bandWidth * gap;
    const n = curve.length;
    const normals = curve.map((p, i) => {
      const a = curve[Math.max(0, i - 1)], b = curve[Math.min(n - 1, i + 1)];
      const tx = b.x - a.x, ty = b.y - a.y;
      const len = Math.hypot(tx, ty) || 1;
      return { x: -ty / len, y: tx / len };
    });
    const rail = (sign: number): Point[] => curve.map((p, i) => ({
      x: p.x + sign * width * normals[i].x,
      y: p.y + sign * width * normals[i].y,
    }));
    sides = [rail(1), rail(-1)];
    const curvature = curve.map((p, i) => {
      const a = curve[Math.max(0, i - 1)], b = curve[Math.min(n - 1, i + 1)];
      const v1 = { x: p.x - a.x, y: p.y - a.y };
      const v2 = { x: b.x - p.x, y: b.y - p.y };
      const l1 = Math.hypot(v1.x, v1.y) || 1, l2 = Math.hypot(v2.x, v2.y) || 1;
      const cross = (v1.x * v2.y - v1.y * v2.x) / (l1 * l2);
      const dot = (v1.x * v2.x + v1.y * v2.y) / (l1 * l2);
      const turn = Math.atan2(cross, dot);
      const step = 0.5 * (l1 + l2) || 1;
      return Math.abs(turn / step);
    });
    bandFold = Math.max(...curvature.map((k) => k * width));
  }
  const loops = crossings(curve);

  // the neighbouring legs, to show what is being joined
  const leg = (p: Point, slope: { d: number; n: number }, sign: number, length = 0.45 * gap) => {
    const v = { x: slope.d, y: slope.n };
    const len = Math.hypot(v.x, v.y) || 1;
    return [{ x: p.x - sign * (length * v.x) / len, y: p.y - sign * (length * v.y) / len }, p];
  };
  const incoming = leg(p0, s0, 1);
  const outgoing = leg(p5, s1, -1);

  const all = [...curve, ...(offset ? offset.flat() : []), ...(sides ? sides.flat() : []),
    ...incoming, ...outgoing];
  const xs = all.map((p) => p.x), ys = all.map((p) => p.y);
  const x0 = Math.min(...xs), x1 = Math.max(...xs);
  const y0 = Math.min(...ys), y1 = Math.max(...ys);
  const w = 640, h = 420, margin = 30;
  const k = Math.min((w - 2 * margin) / (x1 - x0 || 1), (h - 2 * margin) / (y1 - y0 || 1));
  const ox = (w - (x1 - x0) * k) / 2, oy = (h - (y1 - y0) * k) / 2;
  const put = (p: Point): [number, number] => [ox + (p.x - x0) * k, h - (oy + (p.y - y0) * k)];
  const path = (pts: Point[], colour: string, width: number, dash = ""): string => '<path d="M ' +
    pts.map((p) => put(p).map((v) => v.toFixed(1)).join(" ")).join(" L ") +
    `" fill="none" stroke="${colour}" stroke-width="${width}"${dash ? ` stroke-dasharray="${dash}"` : ""} ` +
    'stroke-linecap="round" stroke-linejoin="round"/>';
  const dots = [p0, p5].map((p) => {
    const [x, y] = put(p);
    return `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="4" fill="#b03a2e"/>`;
  }).join("");

  host.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}">
    <rect width="${w}" height="${h}" fill="#fff"/>
    ${path(incoming, "#9a9a9a", 1.6, "7 5")}
    ${path(outgoing, "#9a9a9a", 1.6, "7 5")}
    ${path(curve, "#2b2b2b", 2.2)}
    ${offset ? offset.map((line) => path(line, "#a06a2c", 1.4, "6 4")).join("") : ""}
    ${sides ? sides.map((line) => path(line, "#a06a2c", 1.3)).join("") : ""}
    ${sides ? path([sides[0][0], sides[1][0]], "#a06a2c", 1.3) + path([sides[0].at(-1)!, sides[1].at(-1)!], "#a06a2c", 1.3) : ""}
    ${dots}
    <text x="12" y="20" font-family="ui-monospace, Menlo, monospace" font-size="12" fill="#8a7a62">
      glued ${fracText(s0)} to ${fracText(s1)} · gap ${gap.toFixed(2)} · handles ${h0.toFixed(2)} / ${h1.toFixed(2)}</text>
    <text x="12" y="${h - 10}" font-family="ui-monospace, Menlo, monospace" font-size="12" fill="#5a4a36">
      ${loops.length ? `${loops.length} self-crossing(s)` : "no self-crossing"} · ${kind === "rational" ? `weights 1 / ${weight.toFixed(1)} / ${weight.toFixed(1)} / 1` : kind === "levien" ? `Levien fit: ${fit!.spans.length} span(s), worst ${fit!.error_max.toFixed(4)}` : kind === "quintic" ? "G3 at both ends — the six conditions are printed" : "control points from exact directions"}</text>
  </svg>`;

  const drawnSlope = (t: number): number | string => {
    const value = kind === "quintic" && conditions
      ? (t === 0 ? conditions.start.slope : conditions.end.slope)
      : slopeAt(ctrl, t);
    return Number.isFinite(value) ? value : "∞";
  };
  const conditionText = (conditions && kind === "quintic")
    ? `<br>start κ ${conditions.start.kappa.toFixed(6)} · dκ/ds ${conditions.start.rate.toFixed(6)}` +
      `<br>end κ ${conditions.end.kappa.toFixed(6)} · dκ/ds ${conditions.end.rate.toFixed(6)}`
    : "";
  readout.innerHTML =
    `start slope ${fracText(s0)} (drawn ${typeof drawnSlope(0) === "number" ? (drawnSlope(0) as number).toFixed(6) : "∞"}) · ` +
    `end slope ${fracText(s1)} (drawn ${typeof drawnSlope(1) === "number" ? (drawnSlope(1) as number).toFixed(6) : "∞"})` +
    conditionText + "<br>" +
    `control points: (${ctrl.map((p) => `${p.x.toFixed(4)}, ${p.y.toFixed(4)}`).join(") (")})<br>` +
    `${loops.length ? `crosses itself at ${loops.map((p) => `${p.x.toFixed(2)}, ${p.y.toFixed(2)}`).join(" · ")}` : "does not cross itself at these handles"}` +
    (kind === "levien" ? `<br>offset ${distance.toFixed(2)} fitted with ${fit!.spans.length} cubic span(s); worst miss ${fit!.error_max.toFixed(5)}; ${fit!.cusps.length} cusp range(s)` : "") +
    (bandOn ? `<br>band ±${(bandWidth * gap).toFixed(3)} (${(bandWidth * 100).toFixed(1)} % of the gap); ` +
      `fold ${bandFold.toFixed(2)} ${bandFold > 0.9 ? "— the band folds here; widen the gap or narrow it" : "— the band holds"}` : "");
}

function mount(): void {
  for (const id of ["g-slope0", "g-slope1", "g-gap", "g-h0", "g-h1", "g-kind", "g-weight",
    "g-distance", "g-band", "g-band-w", "g-k0", "g-k1", "g-r0", "g-r1"]) {
    el(id)?.addEventListener("input", draw);
    el(id)?.addEventListener("change", draw);
  }
  draw();
}

if (typeof document !== "undefined") {
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mount);
  else mount();
}
