// The prime mover page. Spec: state/SPEC-prime-mover-int.md · check: app/scripts/check-prime-mover-page.mjs
//
// Two drawings of the same driver and the tables of exact numbers behind them:
//
//   ring  — the i set on the unit circle. The first part is a circle, the second a
//           square, and they alternate around the ring. Nothing else is drawn.
//   wave  — x(i) and y(i) against i. Positions come from the exact counter and the
//           exact ratios; no rounded angle is ever used to place a point.
//
// On this page `i` is the driver's dial and nothing else. A step is written as its
// triple, (3, 4, 5), never as a complex step — one letter, one meaning. A complex
// step is refused because its length is not a ratio of whole numbers.

import { TRIPLES, gcd, ratio, iText, reduceTriple, driverRows } from "./prime-mover-driver.js";

const NS = "http://www.w3.org/2000/svg";
const POSITIVE = "#c9761f";   // second part of the i set, i > 0
const NEGATIVE = "#2f6fa8";   // first part of the i set, i < 0
const INK = "#3b2d1c";

const SAFE = Number.MAX_SAFE_INTEGER;

function currentTriple() {
  const name = document.getElementById("gd-triple")?.value || "3,4,5";
  return { name, ...(TRIPLES[name] || TRIPLES["3,4,5"]) };
}

function circlePoints(radius) {
  const points = [];
  const r2 = radius * radius;
  for (let x = -radius; x <= radius; x += 1) {
    const y2 = r2 - x * x;
    const y = Math.round(Math.sqrt(y2));
    if (y * y !== y2) continue;
    points.push([x, y]);
    if (y) points.push([x, -y]);
  }
  return points;
}

function stepsThatFit(hypotenuse, grid) {
  let power = 1;
  let steps = 0;
  while (power * hypotenuse <= grid) {
    power *= hypotenuse;
    steps += 1;
  }
  return steps;
}

function node(name, attrs) {
  const element = document.createElementNS(NS, name);
  for (const key of Object.keys(attrs)) element.setAttribute(key, attrs[key]);
  return element;
}

function text(content, attrs) {
  const element = node("text", attrs);
  element.textContent = content;
  return element;
}

// --- the ring: the i set ---------------------------------------------------
function drawRing(triple, rows) {
  const host = document.getElementById("gd-plot");
  if (!host) return;
  host.replaceChildren();

  const size = 720;
  const pad = 58;
  const centre = size / 2 + 20;   // clear of the figure title
  const radius = size / 2 - pad - 12;
  const at = (a, b, scale) => [centre + a * scale, centre - b * scale];
  const point = (row) => at(row.a / row.denominator, row.b / row.denominator, radius);

  host.appendChild(node("rect", { x: 0, y: 0, width: size, height: size, fill: "#fffef9" }));
  host.appendChild(text(`Fig. 1 · the i set · (${triple.legs[0]}, ${triple.legs[1]}, ${triple.hypotenuse}) · circle = first part, square = second part`, {
    x: 22, y: 26, "font-family": "Georgia, serif", "font-size": 14, fill: INK,
  }));
  host.appendChild(node("circle", {
    cx: centre, cy: centre, r: radius, fill: "none", stroke: "#c9a441",
    "stroke-width": 1.3, "stroke-dasharray": "6 5",
  }));
  host.appendChild(node("line", { x1: pad, y1: centre, x2: size - pad, y2: centre, stroke: "#ded0ae" }));
  host.appendChild(node("line", { x1: centre, y1: pad, x2: centre, y2: size - pad, stroke: "#ded0ae" }));

  const byK = new Map(rows.map((row) => [row.k, row]));
  const sequence = [];
  for (let k = 1; k <= triple.steps; k += 1) sequence.push(k, -k);
  const labelEvery = triple.steps > 6 ? 2 : 1;

  for (const k of sequence) {
    const row = byK.get(k);
    if (!row) continue;
    const warm = k > 0;
    const [x, y] = point(row);
    const mark = warm
      ? node("rect", { x: x - 5.5, y: y - 5.5, width: 11, height: 11, fill: POSITIVE,
        stroke: "#fffef9", "stroke-width": 1.4 })
      : node("circle", { cx: x, cy: y, r: 6, fill: NEGATIVE, stroke: "#fffef9", "stroke-width": 1.4 });

    // a station is clickable here too: it names its own row of the table
    mark.style.cursor = "pointer";
    mark.addEventListener("click", () => {
      const [rx, ry, den] = reduceTriple(row.a, row.b, row.denominator);
      const pick = document.getElementById("gd-drive-pick");
      if (pick) {
        pick.innerHTML = `i = ${iText(k, triple.steps)} · x = <b>${ratio(rx, den)}</b> · y = <b>${ratio(ry, den)}</b>`;
      }
    });
    host.appendChild(mark);

    if (Math.abs(k) % labelEvery !== 0) continue;
    const ux = row.a / row.denominator;
    const uy = row.b / row.denominator;
    host.appendChild(text(iText(k, triple.steps), {
      x: x + ux * (warm ? 24 : 36), y: y - uy * (warm ? 24 : 36) + 4,
      "font-family": "ui-monospace, Menlo, monospace", "font-size": 11,
      fill: warm ? "#8c5a1a" : "#245480", "text-anchor": "middle",
    }));
  }

  const [ox, oy] = at(1, 0, radius);
  host.appendChild(node("circle", { cx: ox, cy: oy, r: 6, fill: INK, stroke: "#fffef9", "stroke-width": 1.4 }));
  host.appendChild(text("i = 0", {
    x: ox + 12, y: oy + 20, "font-family": "ui-monospace, Menlo, monospace", "font-size": 11, fill: INK,
  }));

  const readout = document.getElementById("gd-readout");
  if (readout) {
    readout.innerHTML = `blue circle: the first part of the i set, i &lt; 0 &nbsp;·&nbsp; `
      + `orange square: the second part, i &gt; 0 &nbsp;·&nbsp; `
      + `step (${triple.legs[0]}, ${triple.legs[1]}, ${triple.hypotenuse}) · ${triple.steps} steps past a full turn`;
  }
}

// --- the wave: x(i) and y(i) ----------------------------------------------
function drawWave(triple, rows) {
  const host = document.getElementById("gd-drive-plot");
  if (!host) return;
  host.replaceChildren();

  const width = 900;
  const height = 560;
  const left = 78;
  const right = width - 28;
  const top = 58;
  const bottom = height - 70;
  const { steps } = triple;
  const xOf = (k) => left + ((k + steps) / (2 * steps)) * (right - left);
  const yOf = (value) => top + (1 - (value + 1) / 2) * (bottom - top);

  host.appendChild(node("rect", { x: 0, y: 0, width, height, fill: "#fffef9" }));
  host.appendChild(node("rect", { x: left, y: top, width: (right - left) / 2, height: bottom - top, fill: "#eef4fa" }));
  host.appendChild(node("rect", {
    x: left + (right - left) / 2, y: top, width: (right - left) / 2, height: bottom - top, fill: "#fdf3e6",
  }));
  host.appendChild(node("rect", { x: left, y: top, width: right - left, height: bottom - top, fill: "none", stroke: "#e6dcc6" }));
  host.appendChild(node("line", { x1: left, y1: yOf(0), x2: right, y2: yOf(0), stroke: "#b9a98a" }));

  for (let k = -steps; k <= steps; k += 1) {
    const x = xOf(k);
    host.appendChild(node("line", { x1: x, y1: bottom, x2: x, y2: bottom + 6, stroke: "#b9a98a" }));
    if (steps <= 6 && k % 2 !== 0) continue;
    if (steps > 6 && k % 2 !== 0) continue;
    host.appendChild(text(iText(k, steps), {
      x, y: bottom + 22, "font-family": "ui-monospace, Menlo, monospace", "font-size": 11,
      fill: "#8c6a21", "text-anchor": k === -steps ? "start" : (k === steps ? "end" : "middle"),
    }));
  }
  for (const value of [-1, -0.5, 0, 0.5, 1]) {
    const y = yOf(value);
    host.appendChild(node("line", { x1: left - 6, y1: y, x2: left, y2: y, stroke: "#b9a98a" }));
    host.appendChild(text(String(value), {
      x: left - 12, y: y + 4, "font-family": "ui-monospace, Menlo, monospace", "font-size": 11,
      fill: "#8c6a21", "text-anchor": "end",
    }));
  }

  host.appendChild(text(`Fig. 2 · x(i) and y(i) · step (${triple.legs[0]}, ${triple.legs[1]}, ${triple.hypotenuse})`, {
    x: left, y: 26, "font-family": "Georgia, serif", "font-size": 14, fill: INK,
  }));
  host.appendChild(text("every dot is an exact ratio of whole numbers; the pale curve is a pure sine of i", {
    x: left, y: 44, "font-family": "ui-monospace, Menlo, monospace", "font-size": 11, fill: "#8c6a21",
  }));

  const reference = (isCosine) => {
    const points = [];
    for (let step = -120; step <= 120; step += 1) {
      const i = step / 120;
      const radians = 2 * Math.PI * i;
      const value = isCosine ? Math.cos(radians) : Math.sin(radians);
      points.push(`${points.length ? "L" : "M"}${xOf(i * steps).toFixed(1)},${yOf(value).toFixed(1)}`);
    }
    return points.join(" ");
  };
  host.appendChild(node("path", { d: reference(true), fill: "none", stroke: "#efd5ae", "stroke-width": 1.4 }));
  host.appendChild(node("path", { d: reference(false), fill: "none", stroke: "#c3d7e8", "stroke-width": 1.4 }));

  const pick = document.getElementById("gd-drive-pick");
  for (const row of rows) {
    for (const key of ["a", "b"]) {
      const value = row[key] / row.denominator;
      const colour = key === "a" ? POSITIVE : NEGATIVE;
      const dot = node("circle", {
        cx: xOf(row.k), cy: yOf(value), r: row.k === 0 ? 4.6 : 3.6,
        fill: row.k === 0 ? INK : colour, stroke: "#fffef9", "stroke-width": 1,
      });
      dot.style.cursor = "pointer";
      dot.addEventListener("click", () => {
        const [rx, ry, den] = reduceTriple(row.a, row.b, row.denominator);
        if (pick) {
          pick.innerHTML = `i = ${iText(row.k, steps)} · x = <b>${ratio(rx, den)}</b> · y = <b>${ratio(ry, den)}</b>`;
        }
      });
      host.appendChild(dot);
    }
  }
}

// --- the tables -------------------------------------------------------------
function drawTables(triple, rows, driverGrid) {
  const testGrid = Number(document.getElementById("gd-grid").value);

  const driverBody = document.querySelector("#gd-drive tbody");
  if (driverBody) {
    driverBody.innerHTML = rows.map((row) => {
      const [rx, ry, den] = reduceTriple(row.a, row.b, row.denominator);
      return `<tr><td>${iText(row.k, triple.steps)}</td>`
        + `<td class="num">${ratio(rx, den)}</td>`
        + `<td class="num">${ratio(ry, den)}</td></tr>`;
    }).join("");
  }

  const stepsBody = document.querySelector("#gd-steps tbody");
  if (stepsBody) {
    stepsBody.innerHTML = [[3, 4, 5], [7, 24, 25], [44, 117, 125]]
      .map(([a, b, c]) => `<tr><td>(${a}, ${b}, ${c})</td><td class="num">${stepsThatFit(c, testGrid)}</td></tr>`)
      .join("");
  }

  const points = circlePoints(testGrid);
  const counts = new Map();
  for (const [x, y] of points) {
    const divisor = gcd(gcd(x, y), testGrid) || 1;
    const den = testGrid / divisor;
    counts.set(den, (counts.get(den) || 0) + 1);
  }
  const densityBody = document.querySelector("#gd-dens tbody");
  if (densityBody) {
    densityBody.innerHTML = [...counts.entries()].sort((a, b) => a[0] - b[0])
      .map(([den, count]) => `<tr><td>${den}</td><td class="num">${count}</td></tr>`)
      .join("");
  }

  const fits = rows.every((row) => {
    const [, , den] = reduceTriple(row.a, row.b, row.denominator);
    return den <= driverGrid && driverGrid % den === 0;
  });
  const safe = driverGrid <= SAFE;
  const guard = document.getElementById("gd-drive-guard");
  if (guard) {
    guard.innerHTML = `driver grid: <b>${triple.hypotenuse}<sup>${triple.steps}</sup> = `
      + `${driverGrid.toLocaleString("en-US")}</b> · every station divides it: <b>${fits ? "yes" : "NO"}</b>`
      + ` · inside the browser's exact range: <b>${safe ? "yes" : "NO"}</b>`;
  }
}

function drawAll() {
  const triple = currentTriple();
  const { rows, grid } = driverRows(triple);
  drawRing(triple, rows);
  drawWave(triple, rows);
  drawTables(triple, rows, grid);
}

for (const id of ["gd-triple", "gd-grid"]) {
  const control = document.getElementById(id);
  if (control) control.addEventListener("change", drawAll);
}
drawAll();
