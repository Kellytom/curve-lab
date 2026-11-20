// Fig. 5: the integer spirograph. Two vanes, no fractions at all.
//
// The rule, in one line:
//
//     P(k) = A[k mod 12] + 2·B[(k·m) mod 12]
//
// where A and B are the twelve **integer points** of the circle x² + y² = 25², and m
// is the ratio. Both vanes are whole-number points, so the sum is a whole-number point:
// no denominators, no cancellation, nothing that can blow up. The price is the twelve
// stations — a lattice circle carries only so many — which is why the figure is a
// rosette of twelve corners rather than a smooth flower.
//
// Spec: state/SPEC-prime-mover-int.md, "the integer spirograph".
import * as d3 from "d3";

const INK = "#6f4a2a";
const WARM = "#c9761f";
const COOL = "#2f6fa8";

// the twelve integer points of radius 25, in order of angle
export function latticeCircle(radius = 25) {
  const points = [];
  for (let x = -radius; x <= radius; x += 1) {
    const y2 = radius * radius - x * x;
    const y = Math.round(Math.sqrt(y2));
    if (y * y !== y2) continue;
    points.push([x, y]);
    if (y) points.push([x, -y]);
  }
  points.sort((a, b) => Math.atan2(a[1], a[0]) - Math.atan2(b[1], b[0]));
  return points;
}

function pointsFor(ratio, radius = 25, inner = 2) {
  const circle = latticeCircle(radius);
  return circle.map((_, k) => {
    const [ax, ay] = circle[k % circle.length];
    const [bx, by] = circle[(k * ratio) % circle.length];
    return { k, ax, ay, bx: inner * bx, by: inner * by, x: ax + inner * bx, y: ay + inner * by };
  });
}

export function buildIntegerSpirograph(hostId = "int-spiro", ratio = 5) {
  const host = document.getElementById(hostId);
  if (!host) return null;

  const data = pointsFor(ratio);
  const width = 760;
  const height = 760;
  const pad = 54;
  const xs = data.map((p) => p.x);
  const ys = data.map((p) => p.y);
  const midX = (Math.min(...xs) + Math.max(...xs)) / 2;
  const midY = (Math.min(...ys) + Math.max(...ys)) / 2;
  const half = Math.max(
    (Math.max(...xs) - Math.min(...xs)) / 2,
    (Math.max(...ys) - Math.min(...ys)) / 2,
  ) * 1.12 || 1;

  const x = d3.scaleLinear().domain([midX - half, midX + half]).range([pad, width - pad]);
  const y = d3.scaleLinear().domain([midY - half, midY + half]).range([height - pad, pad]);

  host.replaceChildren();
  const svg = d3.select(host).append("svg")
    .attr("viewBox", `0 0 ${width} ${height}`)
    .attr("width", "100%")
    .attr("role", "img")
    .attr("aria-label", "the integer spirograph");

  svg.append("rect").attr("width", width).attr("height", height).attr("fill", "#fffef9");
  svg.append("line").attr("x1", x(midX - half)).attr("y1", y(0)).attr("x2", x(midX + half)).attr("y2", y(0)).attr("stroke", "#efe4c9");
  svg.append("line").attr("x1", x(0)).attr("y1", y(midY - half)).attr("x2", x(0)).attr("y2", y(midY + half)).attr("stroke", "#efe4c9");

  const line = d3.line().x(([px]) => x(px)).y(([, py]) => y(py)).curve(d3.curveCatmullRom.alpha(0.5));
  svg.append("path").datum(data.map((p) => [p.x, p.y])).attr("d", line)
    .attr("fill", "none").attr("stroke", INK).attr("stroke-width", 1.8);

  svg.selectAll("circle.station")
    .data(data)
    .join("circle")
    .attr("class", "station")
    .attr("cx", (p) => x(p.x))
    .attr("cy", (p) => y(p.y))
    .attr("r", 4)
    .attr("fill", (_, index) => (index % 2 === 0 ? WARM : COOL))
    .attr("stroke", "#fffef9")
    .attr("stroke-width", 0.9);

  svg.append("text").attr("x", pad).attr("y", 24)
    .attr("font-family", "Georgia, serif").attr("font-size", 14).attr("fill", "#3b2d1c")
    .text(`Fig. 5 · the integer spirograph at ratio ${ratio} · P(k) = A[k] + 2·B[${ratio}k]`);
  svg.append("text").attr("x", pad).attr("y", 40)
    .attr("font-family", "ui-monospace, Menlo, monospace").attr("font-size", 11).attr("fill", "#8c6a21")
    .text(`every station is a whole-number point · ${data.length} stations · no fractions, no growth`);

  return svg.node();
}
