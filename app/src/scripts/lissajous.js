// The Lissajous maker: x = T_m(t), y = T_n(t), t in [-1, 1].
//
// Chebyshev polynomials have whole coefficients, so every rational t gives a
// rational point and the grid is 1 — this is the integer form of the classical
// Lissajous figure. The page recomputes as the two degrees change.

const STEPS = 500;

export function chebyshev(n) {
  if (n === 0) return [1];
  let a = [1];
  let b = [0, 1];
  for (let k = 2; k <= n; k += 1) {
    const doubled = [0, ...b.map((c) => 2 * c)];
    const length = Math.max(doubled.length, a.length);
    const left = [...doubled, ...new Array(length - doubled.length).fill(0)];
    const right = [...a, ...new Array(length - a.length).fill(0)];
    const next = left.map((c, i) => c - right[i]);
    a = b;
    b = next;
  }
  return b;
}

function evaluate(row, t) {
  let value = 0;
  for (let i = row.length - 1; i >= 0; i -= 1) value = value * t + row[i];
  return value;
}

export function pointsFor(m, n, steps = STEPS) {
  const xRow = chebyshev(m);
  const yRow = chebyshev(n);
  const points = [];
  for (let k = 0; k <= steps; k += 1) {
    const t = -1 + (2 * k) / steps;
    points.push([evaluate(xRow, t), evaluate(yRow, t)]);
  }
  return { xRow, yRow, points };
}

export function crossings(points) {
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

// --- page wiring -----------------------------------------------------------
const svg = document.getElementById("liss-plot");
if (svg) {
  const mInput = document.getElementById("liss-m");
  const nInput = document.getElementById("liss-n");
  const readout = document.getElementById("liss-readout");
  const draw = () => {
    const m = Number(mInput.value);
    const n = Number(nInput.value);
    document.getElementById("liss-m-out").textContent = String(m);
    document.getElementById("liss-n-out").textContent = String(n);
    const { points, xRow, yRow } = pointsFor(m, n);
    const xs = points.map((p) => p[0]);
    const ys = points.map((p) => p[1]);
    const span = Math.max(Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys)) || 1;
    const pad = 22;
    const k = (360 - 2 * pad) / span;
    const cx = (Math.max(...xs) + Math.min(...xs)) / 2;
    const cy = (Math.max(...ys) + Math.min(...ys)) / 2;
    const sx = (x) => 180 + (x - cx) * k;
    const sy = (y) => 180 - (y - cy) * k;
    const d = points.map(([x, y], i) => `${i ? "L" : "M"}${sx(x).toFixed(1)},${sy(y).toFixed(1)}`).join("");
    svg.innerHTML = `<rect width="360" height="360" fill="#fff"/>
      <line x1="${pad}" y1="180" x2="${360 - pad}" y2="180" stroke="#b9a98a"/>
      <line x1="180" y1="${pad}" x2="180" y2="${360 - pad}" stroke="#b9a98a"/>
      <path d="${d}" fill="none" stroke="#141414" stroke-width="1.6" stroke-linejoin="round"/>`;
    const closed = m !== n;
    readout.textContent = `${crossings(points)} crossing pairs · x = T${m} = [${xRow.join(", ")}] · `
      + `y = T${n} = [${yRow.join(", ")}] · whole coefficients, grid 1 · `
      + (closed ? "closes at both ends (t = ±1)" : "degenerate: the same degree both ways");
  };
  [mInput, nInput].forEach((input) => input.addEventListener("input", draw));
  draw();
}
