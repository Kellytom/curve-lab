// The lattice mobile: a spirograph whose every station is an integer point.
//
// Two arms, each walking the integer points of its own circle, added station by
// station. Every station is the sum of two integer points, so every station is
// an integer point — no rounding anywhere — and a station can be cut and given a
// branch without moving off the lattice.
//
// The measured cost, stated on the page too: the integer points on a circle are
// not evenly spaced in angle, so the pen speeds up and slows down where they
// crowd, and the figures are coarser than a drawn spirograph. That is the price
// of exact stations.
import * as d3 from "d3";

const SIZE = 640;
const RADII = [5, 13, 25, 65, 325, 1105];

function circlePoints(radius) {
  const points = [];
  const r2 = radius * radius;
  for (let x = -radius; x <= radius; x += 1) {
    const y2 = r2 - x * x;
    const y = Math.round(Math.sqrt(Math.max(0, y2)));
    if (y * y !== y2) continue;
    points.push([x, y]);
    if (y) points.push([x, -y]);
  }
  points.sort((p, q) => Math.atan2(p[1], p[0]) - Math.atan2(q[1], q[0]));
  return points;
}

const cache = new Map();
function circle(radius) {
  if (!cache.has(radius)) cache.set(radius, circlePoints(radius));
  return cache.get(radius);
}

const gcd = (a, b) => (b ? gcd(b, a % b) : Math.abs(a));

const lcm = (a, b) => (a * b) / gcd(a, b);

function mobile(radiusA, radiusB, p, q) {
  const a = circle(radiusA);
  const b = circle(radiusB);
  // the figure closes when both arms return to their starting point
  const periodA = a.length / gcd(a.length, q);
  const periodB = b.length / gcd(b.length, p);
  const period = lcm(periodA, periodB);
  const steps = Math.min(540, period);
  const points = [];
  for (let k = 0; k < steps; k += 1) {
    const pa = a[(k * q) % a.length];
    const pb = b[(k * p) % b.length];
    points.push([pa[0] + pb[0], pa[1] + pb[1]]);
  }
  return { points, period, capped: steps < period };
}

function crossings(points) {
  const seen = new Set();
  const n = points.length;
  for (let i = 0; i < n - 1; i += 1) {
    const [ax, ay] = points[i];
    const [bx, by] = points[i + 1];
    for (let j = i + 2; j < n - 1; j += 1) {
      const [cx, cy] = points[j];
      const [dx, dy] = points[j + 1];
      if (i === 0 && j === n - 2 && points[0][0] === points[n - 1][0]
        && points[0][1] === points[n - 1][1]) continue;
      const den = (bx - ax) * (dy - cy) - (by - ay) * (dx - cx);
      if (!den) continue;
      const s = ((cx - ax) * (dy - cy) - (cy - ay) * (dx - cx)) / den;
      const w = ((cx - ax) * (by - ay) - (cy - ay) * (bx - ax)) / den;
      if (s > 0 && s < 1 && w > 0 && w < 1) {
        seen.add(`${(ax + (bx - ax) * s).toFixed(3)},${(ay + (by - ay) * s).toFixed(3)}`);
      }
    }
  }
  return seen.size;
}

// A branch is an exact lattice vector: the perpendicular of the incoming
// segment, reduced to primitive integers, taken six units long. Nothing here is
// rounded, so the branch endpoint is an integer point as well.
function branchVector(points, index) {
  const [x0, y0] = points[index];
  const [x1, y1] = points[(index + 1) % points.length];
  let dx = x1 - x0;
  let dy = y1 - y0;
  const g = gcd(dx, dy) || 1;
  dx /= g;
  dy /= g;
  return [-dy * 6, dx * 6];
}

function render() {
  const host = document.getElementById("lm-plot");
  if (!host) return;
  const radiusA = Number(document.getElementById("lm-radius-a").value);
  const radiusB = Number(document.getElementById("lm-radius-b").value);
  const p = Number(document.getElementById("lm-ratio-p").value);
  const q = Number(document.getElementById("lm-ratio-q").value);
  const { points, period, capped } = mobile(radiusA, radiusB, p, q);
  const cuts = new Set(
    (document.getElementById("lm-plot").dataset.cuts || "")
      .split(",").filter(Boolean).map(Number),
  );

  host.innerHTML = "";
  const svg = d3.select(host).append("svg")
    .attr("viewBox", `0 0 ${SIZE} ${SIZE}`)
    .attr("width", "100%")
    .attr("role", "img");
  svg.append("rect").attr("width", SIZE).attr("height", SIZE).attr("fill", "#fffdf7");

  const xs = points.map((d) => d[0]);
  const ys = points.map((d) => d[1]);
  const pad = 30;
  const reach = Math.max(
    Math.max(...xs) - Math.min(...xs),
    Math.max(...ys) - Math.min(...ys),
    1,
  );
  const x = d3.scaleLinear()
    .domain([Math.min(...xs) - reach * 0.05, Math.max(...xs) + reach * 0.05])
    .range([pad, SIZE - pad]);
  const y = d3.scaleLinear()
    .domain([Math.min(...ys) - reach * 0.05, Math.max(...ys) + reach * 0.05])
    .range([SIZE - pad, pad]);

  // lattice grid, one line per integer, hidden when it would be a grey wash
  const pixel = Math.abs(x(1) - x(0));
  if (pixel >= 14) {
    const gx = d3.range(Math.floor(x.domain()[0]), Math.ceil(x.domain()[1]));
    const gy = d3.range(Math.floor(y.domain()[0]), Math.ceil(y.domain()[1]));
    svg.append("g").selectAll("line").data(gx).join("line")
      .attr("x1", (v) => x(v)).attr("x2", (v) => x(v))
      .attr("y1", pad).attr("y2", SIZE - pad)
      .attr("stroke", "#eee5d2").attr("stroke-width", 0.6);
    svg.append("g").selectAll("line").data(gy).join("line")
      .attr("y1", (v) => y(v)).attr("y2", (v) => y(v))
      .attr("x1", pad).attr("x2", SIZE - pad)
      .attr("stroke", "#eee5d2").attr("stroke-width", 0.6);
  }

  const line = d3.line().x((d) => x(d[0])).y((d) => y(d[1]));
  svg.append("path").attr("d", line([...points, points[0]]))
    .attr("fill", "none").attr("stroke", "#6f4a2a").attr("stroke-width", 1.6)
    .attr("stroke-linejoin", "round");

  const spacingPixels = Math.abs(x(1) - x(0));
  const every = points.length > 40 ? Math.ceil(points.length / 24) : 1;

  svg.append("g").selectAll("circle")
    .data(points).join("circle")
    .attr("cx", (d) => x(d[0])).attr("cy", (d) => y(d[1]))
    .attr("r", (d, i) => (cuts.has(i) ? 4.6 : 2.6))
    .attr("fill", (d, i) => (cuts.has(i) ? "#a8341f" : "#c9761f"))
    .attr("stroke", (d, i) => (cuts.has(i) ? "#fff8e7" : "none"))
    .attr("stroke-width", 1.2)
    .style("cursor", "pointer")
    .on("click", (event, d) => {
      const index = points.findIndex((row) => row === d);
      const next = new Set(cuts);
      if (next.has(index)) next.delete(index); else next.add(index);
      document.getElementById("lm-plot").dataset.cuts = [...next].join(",");
      render();
    });

  if (spacingPixels >= 16) {
    svg.append("g").selectAll("text")
      .data(points.filter((_, i) => i % every === 0))
      .join("text")
      .attr("x", (d) => x(d[0]) + 6).attr("y", (d) => y(d[1]) - 6)
      .attr("font-family", "ui-monospace, Menlo, monospace").attr("font-size", 10)
      .attr("fill", "#8c5a1a")
      .text((d) => `${d[0]}, ${d[1]}`);
  }

  // branches: exact lattice stubs at the cut stations
  for (const index of cuts) {
    if (index >= points.length) continue;
    const [bx, by] = branchVector(points, index);
    const [x0, y0] = points[index];
    svg.append("line")
      .attr("x1", x(x0)).attr("y1", y(y0))
      .attr("x2", x(x0 + bx)).attr("y2", y(y0 + by))
      .attr("stroke", "#a8341f").attr("stroke-width", 2)
      .attr("stroke-dasharray", "5 4");
    svg.append("circle")
      .attr("cx", x(x0 + bx)).attr("cy", y(y0 + by)).attr("r", 3.4)
      .attr("fill", "#a8341f");
  }

  const hud = document.getElementById("lm-hud");
  if (hud) {
    // the figure closes by construction: at `period` steps both arms have
    // returned to their first point, so the last step lands on the first station
    const closed = !capped;
    hud.textContent =
      `stations ${points.length} · distinct ${new Set(points.map((d) => d.join(","))).size}`
      + ` · crossings ${crossings(points)} · ${closed ? `closed in ${period} steps` : `open, period ${period} capped at ${points.length}`}`
      + ` · grid 1 (every station an integer point) · cuts ${cuts.size}`;
  }

  (document.getElementById("lm-readout") || {}).textContent =
    `${circle(radiusA).length} + ${circle(radiusB).length} circle points · ratio ${p}/${q}`;
}

for (const id of ["lm-radius-a", "lm-radius-b", "lm-ratio-p", "lm-ratio-q"]) {
  const control = document.getElementById(id);
  if (control) control.addEventListener("change", render);
}
document.getElementById("lm-clear")?.addEventListener("click", () => {
  document.getElementById("lm-plot").dataset.cuts = "";
  render();
});
for (const id of ["lm-radius-a", "lm-radius-b"]) {
  const select = document.getElementById(id);
  if (select) select.innerHTML = RADII.map((r) => `<option value="${r}">${r}</option>`).join("");
}
if (document.getElementById("lm-radius-a")) document.getElementById("lm-radius-a").value = "65";
if (document.getElementById("lm-radius-b")) document.getElementById("lm-radius-b").value = "325";
render();
