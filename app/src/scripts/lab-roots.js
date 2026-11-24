// The root lab: build a curve from a mirrored root pair and a stack at 1/2,
// draw it live, and say in words what makes it what it is.
//
// The maths is the same as scripts/root_search.py, in JS because the page must
// recompute on every input change: v(t) from the roots, u(t) = 1 - 2t + 2t^2,
// integrate both for the drawing.
//
// The note under the curve is generated from the numbers of the curve on screen,
// never typed per case.

const STEPS = 220;

// (t - r) products, ascending powers, cleared to integers.

function integrate(row) {
  const out = [0];
  row.forEach((c, i) => out.push(c / (i + 1)));
  return out;
}

function evaluate(row, t) {
  let value = 0;
  for (let i = row.length - 1; i >= 0; i -= 1) value = value * t + row[i];
  return value;
}

function curvePoints(u, v, steps = STEPS) {
  // u and v are PH *speed* components, not velocities: the curve is the
  // integral of (u² - v², 2uv). Treating u,v as dx/dt draws a different curve.
  const uu = multiply(u, u);
  const vv = multiply(v, v);
  const uv = multiply(u, v);
  const n = Math.max(uu.length, vv.length);
  const pad = (row) => [...row, ...new Array(Math.max(0, n - row.length)).fill(0)];
  const speedsX = pad(uu).map((c, i) => c - pad(vv)[i]);
  const speedsY = pad(uv).map((c) => 2 * c);
  const x = integrate(speedsX);
  const y = integrate(speedsY);
  const points = [];
  for (let i = 0; i <= steps; i += 1) {
    const t = i / steps;
    points.push([evaluate(x, t), evaluate(y, t)]);
  }
  return points;
}

export function crossings(points) {
  // Counts segment pairs, not places: rank with the clustered router
  // (scripts/ph_crossings.py), which this must agree with at page sampling.
  let hits = 0;
  for (let i = 0; i < points.length - 2; i += 1) {
    const [ax, ay] = points[i];
    const [bx, by] = points[i + 1];
    for (let j = i + 2; j < points.length - 1; j += 1) {
      const [cx, cy] = points[j];
      const [dx, dy] = points[j + 1];
      const den = (bx - ax) * (dy - cy) - (by - ay) * (dx - cx);
      if (Math.abs(den) < 1e-12) continue;
      const s = ((cx - ax) * (dy - cy) - (cy - ay) * (dx - cx)) / den;
      const w = ((cx - ax) * (by - ay) - (cy - ay) * (bx - ax)) / den;
      if (s > 0 && s < 1 && w > 0 && w < 1) hits += 1;
    }
  }
  return hits;
}

function inflections(points) {
  // sign changes of the cross product of consecutive chords
  let count = 0;
  let last = 0;
  for (let i = 1; i < points.length - 1; i += 1) {
    const [x0, y0] = points[i - 1];
    const [x1, y1] = points[i];
    const [x2, y2] = points[i + 1];
    const cross = (x1 - x0) * (y2 - y1) - (y1 - y0) * (x2 - x1);
    if (Math.abs(cross) < 1e-9 * (1 + Math.hypot(x1 - x0, y1 - y0))) continue;
    const sign = Math.sign(cross);
    if (last && sign !== last) count += 1;
    last = sign;
  }
  return count;
}

function grace(points) {
  const xs = points.map((p) => p[0]);
  const ys = points.map((p) => p[1]);
  const cx = (Math.min(...xs) + Math.max(...xs)) / 2;
  const cy = (Math.min(...ys) + Math.max(...ys)) / 2;
  const size = Math.max(Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys)) || 1;
  let best = Infinity;
  for (let i = 0; i < points.length; i += 1) {
    const t = i / (points.length - 1);
    if (t < 0.08 || t > 0.92) continue;
    best = Math.min(best, Math.hypot(points[i][0] - cx, points[i][1] - cy));
  }
  return best === Infinity ? 9 : best / size;
}

// Integer polynomial product: (a0 + a1 t + ...)(b0 + b1 t + ...).
function multiply(a, b) {
  const out = new Array(a.length + b.length - 1).fill(0);
  a.forEach((ca, i) => b.forEach((cb, j) => { out[i + j] += ca * cb; }));
  return out;
}

export function build(p, q, mid, options = {}) {
  // The pair as integers: (q t - p)(q t - (q - p)); the stack as (2t - 1)^m; an optional
  // second mirrored pair for y. The x row is A + B(t² - t), which is symmetric about ½ for
  // every A and B, so both rows stay mirror-symmetric.
  // No floats and no denominator clearing, so a zero coefficient cannot break it.
  const { p2 = 0, q2 = 7, xA = 1, xB = 2 } = options;
  let v = multiply([-p, q], [-(q - p), q]);
  if (p2 > 0 && q2 > p2) v = multiply(v, multiply([-p2, q2], [-(q2 - p2), q2]));
  for (let i = 0; i < mid; i += 1) v = multiply(v, [-1, 2]);
  const u = [xA, -xB, xB];
  const points = curvePoints(u, v);
  return {
    u, v, points,
    crossings: crossings(points),
    inflections: inflections(points),
    grace: grace(points),
  };
}

export function explain(result, p, q, mid, options = {}) {
  const { p2 = 0, q2 = 7, xA = 1, xB = 2 } = options;
  const symmetry = "both speed rows are mirror-symmetric about t = ½";
  const second = p2 > 0 && q2 > p2 ? `, plus the second pair ${p2}/${q2} and ${(q2 - p2)}/${q2}` : "";
  const shared = `the x row is ${xA} + ${xB}(t² − t), which is symmetric about ½ for any A and B`;
  const difference = `at ${p}/${q}${second} with ${mid} root${mid === 1 ? "" : "s"} at ½ it has ${result.crossings} crossing pair${result.crossings === 1 ? "" : "s"} and ${result.inflections} inflection${result.inflections === 1 ? "" : "s"}`;
  return `${difference}, and passes within ${(result.grace * 100).toFixed(1)}% of its own centre. It is different because the ${p2 > 0 && q2 > p2 ? "pairs" : "pair"} set where the curve turns back, and the stack at ½ sets how flat the middle is. Why it adds well: ${symmetry} (the roots come in pairs r and 1 − r), and ${shared}.`;
}

// --- the page wiring -------------------------------------------------------
// Guarded so the module imports cleanly in Node: the calibration test counts
// crossings on the same polyline the router counts.
if (typeof document !== "undefined") {
  const plot = document.getElementById("lab-plot");
  if (plot) {
  const controls = {
    p: document.getElementById("p"),
    q: document.getElementById("q"),
    mid: document.getElementById("mid"),
    p2: document.getElementById("p2"),
    q2: document.getElementById("q2"),
    xA: document.getElementById("x-a"),
    xB: document.getElementById("x-b"),
  };
  const outs = {
    p: document.getElementById("p-out"),
    q: document.getElementById("q-out"),
    mid: document.getElementById("mid-out"),
    p2: document.getElementById("p2-out"),
    q2: document.getElementById("q2-out"),
    xA: document.getElementById("x-a-out"),
    xB: document.getElementById("x-b-out"),
  };
  const facts = document.getElementById("lab-facts");
  const note = document.getElementById("lab-note");

  const draw = () => {
    const p = Math.max(1, Number(controls.p.value));
    const q = Math.max(p + 1, Number(controls.q.value));
    const mid = Number(controls.mid.value);
    const p2 = Math.max(0, Number(controls.p2.value));
    const q2 = Math.max(2, Number(controls.q2.value));
    const xA = Math.max(1, Number(controls.xA.value));
    const xB = Math.max(0, Number(controls.xB.value));
    outs.p.textContent = String(p);
    outs.q.textContent = String(q);
    outs.mid.textContent = String(mid);
    outs.p2.textContent = p2 === 0 ? "off" : String(p2);
    outs.q2.textContent = String(q2);
    outs.xA.textContent = String(xA);
    outs.xB.textContent = String(xB);

    const options = { p2, q2, xA, xB };
    const result = build(p, q, mid, options);
    const xs = result.points.map((point) => point[0]);
    const ys = result.points.map((point) => point[1]);
    const x0 = Math.min(...xs), x1 = Math.max(...xs);
    const y0 = Math.min(...ys), y1 = Math.max(...ys);
    const span = Math.max(x1 - x0, y1 - y0) || 1;
    const pad = 30;
    const k = (600 - 2 * pad) / span;
    const sx = (x) => pad + (x - x0) * k + ((600 - 2 * pad) - (x1 - x0) * k) / 2;
    const sy = (y) => 600 - pad - (y - y0) * k - ((600 - 2 * pad) - (y1 - y0) * k) / 2;
    const d = result.points.map(([x, y], i) => `${i ? "L" : "M"}${sx(x).toFixed(1)},${sy(y).toFixed(1)}`).join("");
    const zeroX = x0 <= 0 && x1 >= 0 ? sx(0) : null;
    const zeroY = y0 <= 0 && y1 >= 0 ? sy(0) : null;
    plot.innerHTML = `<rect width="600" height="600" fill="#fff"/>
      ${zeroY !== null ? `<line x1="${pad}" y1="${zeroY}" x2="${600 - pad}" y2="${zeroY}" stroke="#b9a98a"/>` : ""}
      ${zeroX !== null ? `<line x1="${zeroX}" y1="${pad}" x2="${zeroX}" y2="${600 - pad}" stroke="#b9a98a"/>` : ""}
      <path d="${d}" fill="none" stroke="#141414" stroke-width="2" stroke-linejoin="round"/>`;

    facts.textContent = `${result.crossings} crossing pairs · ${result.inflections} inflections · `
      + `grace ${(result.grace * 100).toFixed(1)}% · x row ${xA} + ${xB}(t² − t) · `
      + `pair 2 ${p2 === 0 ? "off" : `${p2}/${q2}`} · v = ${result.v.length - 1}th degree`;
    note.textContent = explain(result, p, q, mid, options);
  };

  [controls.p, controls.q, controls.mid, controls.p2, controls.q2, controls.xA, controls.xB]
    .forEach((control) => control.addEventListener("input", draw));
  document.querySelectorAll(".suggest button").forEach((button) => {
    button.addEventListener("click", () => {
      controls.p.value = button.dataset.p;
      controls.q.value = button.dataset.q;
      controls.mid.value = button.dataset.mid;
      controls.p2.value = "0";
      controls.q2.value = "7";
      controls.xA.value = "1";
      controls.xB.value = "2";
      draw();
    });
  });
  draw();
}
}
