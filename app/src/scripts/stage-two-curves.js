// Stage II: the prime mover's x and y fed into a polynomial.
//
// The curve is exact at every station: X and Y are ratios of whole numbers, the
// coefficients are whole numbers, and the arithmetic is the rationals in
// prime-mover-driver.js. Only the line drawn between two stations is sampled, and
// the page says so.
//
// Spec: state/SPEC-stage-two-int.md · check: app/scripts/check-stage-two-page.mjs
import * as d3 from "d3";
import {
  TRIPLES, iText, walker, walkFor, quadrantPoints, rationalFloat,
  rational, add, multiply, subtract, cube, rationalText,
} from "./prime-mover-driver.js";

const NS = "http://www.w3.org/2000/svg";
const INK = "#3b2d1c";
const CURVE = "#6f4a2a";
const BASELINE = "#c9a441";

// Each preset is a polynomial of X and Y with whole-number coefficients.
const PRESETS = {
  circle: { label: "the circle", px: (X) => X, py: (X, Y) => Y },
  s: { label: "the S", px: (X) => X, py: (X, Y) => subtract(Y, cube(Y)) },
  loop: { label: "the loop", px: (X) => subtract(X, cube(X)), py: (X, Y) => Y },
  leaf: { label: "the leaf", px: (X, Y) => multiply(X, Y), py: (X, Y) => Y },
  crest: { label: "the crest", px: (X) => X, py: (X, Y) => multiply(X, Y) },
  // the cube: (X + Yi)³, which wraps the circle three times — a trefoil
  trefoil: {
    label: "the trefoil",
    px: (X, Y) => subtract(multiply(multiply(X, X), X), multiply(multiply(rational(3n), X), multiply(Y, Y))),
    py: (X, Y) => subtract(multiply(multiply(rational(3n), multiply(X, X)), Y), multiply(multiply(Y, Y), Y)),
  },
  // the same degree, folded on both axes at once
  fold: {
    label: "the cubic fold",
    px: (X, Y) => add(subtract(X, cube(X)), multiply(X, multiply(Y, Y))),
    py: (X, Y) => add(subtract(Y, cube(Y)), multiply(Y, multiply(X, X))),
  },
  knot: {
    label: "the knot",
    px: (X, Y) => add(X, multiply(X, multiply(Y, Y))),
    py: (X, Y) => add(Y, multiply(Y, multiply(X, X))),
  },
  horn: {
    label: "the horn",
    px: (X, Y) => add(X, multiply(X, Y)),
    py: (X, Y) => subtract(Y, multiply(X, X)),
  },
};

const text = rationalText;
// The drawing is the only place a value becomes a float. The data stays BigInt.
const toNumber = rationalFloat;


function currentPreset() {
  const name = document.getElementById("st-preset")?.value || "circle";
  return { name, ...(PRESETS[name] || PRESETS.circle) };
}

// The walk, taken on the unit circle. Two ranges:
//   full turn      k = 0 … n, so i = k/n runs 0 … +1
//   half turn      k = −n … +n, so i runs −1 … +1 (quadrants I and IV, mirrored)
function curvePoints(triple, preset) {
  const { hypotenuse, turn } = walkFor(triple.name);

  let walk;
  let steps;
  if (halfTurn) {
    walk = quadrantPoints(triple.name);
    steps = Math.max(1, ...walk.map((row) => Math.abs(row.k)));
  } else {
    const count = Math.ceil(360 / turn) + 1;
    // walker returns x, y and the denominator; the station also needs its index
    walk = Array.from({ length: count }, (_, k) => ({ k, ...walker(k, 1, triple.name) }));
    steps = walk.length - 1;
  }

  return walk.map((row) => {
    const X = rational(row.x, hypotenuse * row.d);
    const Y = rational(row.y, hypotenuse * row.d);
    return { k: row.k, steps, X, Y, px: preset.px(X, Y), py: preset.py(X, Y) };
  });
}

function node(name, attrs) {
  const element = document.createElementNS(NS, name);
  for (const key of Object.keys(attrs)) element.setAttribute(key, attrs[key]);
  return element;
}

function label(content, attrs) {
  const element = node("text", attrs);
  element.textContent = content;
  return element;
}

function drawCurve(triple, preset, points) {
  const host = document.getElementById("st-plot");
  if (!host) return;
  host.replaceChildren();

  const size = 720;
  const pad = 56;
  const centre = size / 2 + 18;

  // The frame follows the drawn points, not the origin: a shallow arc must fill the
  // figure, not sit at the bottom of a square chosen for the unit circle.
  const xs = points.map((point) => toNumber(point.px));
  const ys = points.map((point) => toNumber(point.py));
  const midX = (Math.min(...xs) + Math.max(...xs)) / 2;
  const midY = (Math.min(...ys) + Math.max(...ys)) / 2;
  // fit the drawn curve: the frame is the content plus a margin, nothing more
  const span = Math.max(
    (Math.max(...xs) - Math.min(...xs)) * 1.12,
    (Math.max(...ys) - Math.min(...ys)) * 1.12,
    1e-6,
  );
  // span is the full width of the content; half of it must reach the frame's edge
  const scale = (size / 2 - pad) / (span / 2);
  const px = (value) => size / 2 + (toNumber(value) - midX) * scale;
  const py = (value) => size / 2 - (toNumber(value) - midY) * scale;

  host.appendChild(node("rect", { x: 0, y: 0, width: size, height: size, fill: "#fffef9" }));
  host.appendChild(label(`Fig. 1 · ${preset.label} · step (${triple.legs[0]}, ${triple.legs[1]}, ${triple.hypotenuse})`, {
    x: 22, y: 26, "font-family": "Georgia, serif", "font-size": 14, fill: INK,
  }));
  host.appendChild(label("x → right · y → up · orange: second part · blue: first part", {
    x: 22, y: 44, "font-family": "ui-monospace, Menlo, monospace", "font-size": 11, fill: "#8c6a21",
  }));
  host.appendChild(label("stations exact · the line between them is an approximate cubic curve", {
    x: 22, y: 60, "font-family": "ui-monospace, Menlo, monospace", "font-size": 11, fill: "#8c6a21",
  }));

  // axes
  host.appendChild(node("line", { x1: pad, y1: centre, x2: size - pad, y2: centre, stroke: "#ded0ae" }));
  host.appendChild(node("line", { x1: centre, y1: pad, x2: centre, y2: size - pad, stroke: "#ded0ae" }));
  host.appendChild(label("x", { x: size - pad, y: centre + 18, "font-family": "ui-monospace, Menlo, monospace", "font-size": 12, fill: "#9b8a6b", "text-anchor": "end" }));
  host.appendChild(label("y", { x: centre + 10, y: pad + 4, "font-family": "ui-monospace, Menlo, monospace", "font-size": 12, fill: "#9b8a6b" }));

  // the baseline: the prime mover's own circle
  // the unit circle is a reference; draw it only when the frame can hold it whole
  const circleFits = span >= 2 * 1.02;
  if (circleFits) {
    host.appendChild(node("circle", {
      cx: px({ n: 0n, d: 1n }), cy: py({ n: 0n, d: 1n }), r: 1 * scale,
      fill: "none", stroke: BASELINE, "stroke-width": 1.2, "stroke-dasharray": "5 5", opacity: 0.8,
    }));
  }

  // the curve, through the exact stations
  const ordered = [...points].sort((a, b) => a.k - b.k);
  // a cubic Bézier chain through the exact stations: Catmull-Rom, so the line
  // between two stations is a curve and not a chord
  const line = d3.line()
    .x((point) => px(point.px))
    .y((point) => py(point.py))
    .curve(d3.curveCatmullRom.alpha(0.5));
  host.appendChild(node("path", {
    d: line(ordered), fill: "none", stroke: CURVE, "stroke-width": 2,
  }));

  const pick = document.getElementById("st-pick");
  for (const point of ordered) {
    // the colour rule of the prime mover, carried onto the curve point:
    // the second part (i > 0) orange, the first part (i < 0) blue
    const warm = point.k % 2 === 0;
    const dot = node("circle", {
      cx: px(point.px), cy: py(point.py),
      r: point.k === 0 ? 8 : 6.5,
      fill: point.k === 0 ? INK : (warm ? "#c9761f" : "#2f6fa8"),
      stroke: "#fffef9", "stroke-width": 1.4,
    });
    dot.style.cursor = "pointer";
    dot.addEventListener("click", () => {
      if (!pick) return;
      pick.innerHTML = `i = ${iText(point.k, point.steps)} · X = <b>${text(point.X)}</b>`
        + ` · Y = <b>${text(point.Y)}</b> · curve point <b>(${text(point.px)}, ${text(point.py)})</b>`;
    });
    host.appendChild(dot);
  }

  const body = document.querySelector("#st-table tbody");
  if (body) {
    body.innerHTML = ordered.map((point) => `<tr><td>${iText(point.k, point.steps)}</td>`
      + `<td class="num">${text(point.px)}</td>`
      + `<td class="num">${text(point.py)}</td></tr>`).join("");
  }

  const readout = document.getElementById("st-readout");
  if (readout) {
    const widest = points.reduce((best, point) => (
      Math.abs(toNumber(point.px)) + Math.abs(toNumber(point.py))
        > Math.abs(toNumber(best.px)) + Math.abs(toNumber(best.py)) ? point : best
    ), points[0]);
    readout.innerHTML = `${preset.label} on step (${triple.legs[0]}, ${triple.legs[1]}, ${triple.hypotenuse})`
      + ` · ${points.length} exact stations · furthest point <b>(${text(widest.px)}, ${text(widest.py)})</b>`
      + ` · the line between stations is sampled, the stations are not`;
  }
}

let chosenTriple = "7,24,25";
let halfTurn = false;

export function setCurveTriple(name, half = halfTurn) {
  chosenTriple = name;
  halfTurn = Boolean(half);
  drawAll();
}

function drawAll() {
  const triple = { name: chosenTriple, ...(TRIPLES[chosenTriple] || TRIPLES["7,24,25"]) };
  const preset = currentPreset();
  drawCurve(triple, preset, curvePoints(triple, preset));
}

const presetSelect = document.getElementById("st-preset");
if (presetSelect) presetSelect.addEventListener("change", drawAll);
if (document.getElementById("st-plot")) drawAll();
