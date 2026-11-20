// Fig. 7: the geared spirograph — the toy, drawn from its own geometry.
//
// A small wheel of radius r rolls inside a ring of radius R, and a pen fixed at
// distance d from the wheel's centre draws the curve:
//
//     x = (R − r)cos t + d·cos((R − r)t / r)
//     y = (R − r)sin t − d·sin((R − r)t / r)
//
// The curve closes when (R − r)/r is rational, which it is for whole numbers. Drawn
// with a small wheel and a pen near its rim, it is the rosette the toy makes.
//
// **Sampled**: t is a real angle, so nothing here is an exact ratio. The figure says so.
//
// Spec: state/SPEC-prime-mover-int.md, "the geared spirograph".
import * as d3 from "d3";

const INK = "#6f4a2a";
const RING = "#c9a441";
const WHEEL = "#2f6fa8";
const TRACE = "#a8341f";

export function buildGearedSpirograph(hostId = "gear-plot") {
  const host = document.getElementById(hostId);
  if (!host) return null;

  const R = 6;    // ring radius
  const r = 2;    // wheel radius: R/r = 3, so three petals
  const d = 3.4;  // pen distance from the wheel's centre

  const steps = 1440;
  const points = [];
  for (let i = 0; i <= steps; i += 1) {
    const t = (i / steps) * 2 * Math.PI * (r / gcd(R, r)) * 3;   // enough turns to close
    const x = (R - r) * Math.cos(t) + d * Math.cos(((R - r) * t) / r);
    const y = (R - r) * Math.sin(t) - d * Math.sin(((R - r) * t) / r);
    points.push([x, y]);
  }

  const width = 720;
  const height = 720;
  const pad = 60;
  const reach = R + d + 1;   // the curve spans R + d, so frame it tight
  const x = d3.scaleLinear().domain([-reach, reach]).range([pad, width - pad]);
  const y = d3.scaleLinear().domain([-reach, reach]).range([height - pad, pad]);

  host.replaceChildren();
  const svg = d3.select(host).append("svg")
    .attr("viewBox", `0 0 ${width} ${height}`)
    .attr("width", "100%")
    .attr("role", "img")
    .attr("aria-label", "a geared spirograph: a small wheel rolling inside a ring");

  svg.append("rect").attr("width", width).attr("height", height).attr("fill", "#fffef9");

  // the x-y graph: grid lines at whole numbers, darker axes, ticks every 2
  const limit = Math.ceil(reach);
  for (let v = -limit; v <= limit; v += 1) {
    svg.append("line").attr("x1", x(v)).attr("x2", x(v)).attr("y1", y(-limit)).attr("y2", y(limit))
      .attr("stroke", v % 2 === 0 ? "#efe4c9" : "#f6efe1");
    svg.append("line").attr("x1", x(-limit)).attr("x2", x(limit)).attr("y1", y(v)).attr("y2", y(v))
      .attr("stroke", v % 2 === 0 ? "#efe4c9" : "#f6efe1");
    if (v % 2 === 0 && v !== 0) {
      svg.append("text").attr("x", x(v)).attr("y", y(0) + 14).attr("text-anchor", "middle")
        .attr("font-family", "ui-monospace, Menlo, monospace").attr("font-size", 9).attr("fill", "#a8977a").text(v);
      svg.append("text").attr("x", x(0) - 6).attr("y", y(v) + 3).attr("text-anchor", "end")
        .attr("font-family", "ui-monospace, Menlo, monospace").attr("font-size", 9).attr("fill", "#a8977a").text(v);
    }
  }
  svg.append("line").attr("x1", x(-limit)).attr("x2", x(limit)).attr("y1", y(0)).attr("y2", y(0)).attr("stroke", "#b9a98a");
  svg.append("line").attr("x1", x(0)).attr("x2", x(0)).attr("y1", y(-limit)).attr("y2", y(limit)).attr("stroke", "#b9a98a");
  svg.append("text").attr("x", x(limit) - 4).attr("y", y(0) + 14).attr("text-anchor", "end")
    .attr("font-family", "Georgia, serif").attr("font-size", 12).attr("fill", "#3b2d1c").text("x");
  svg.append("text").attr("x", x(0) + 6).attr("y", y(limit) + 12)
    .attr("font-family", "Georgia, serif").attr("font-size", 12).attr("fill", "#3b2d1c").text("y");

  // the integer stations, coloured by the part of the turn they came from
  const hits = points
    .map(([px, py], index) => ({ px, py, part: index / points.length < 0.5 ? "first" : "second" }))
    .filter(({ px, py }) => Math.abs(px - Math.round(px)) < 0.06 && Math.abs(py - Math.round(py)) < 0.06);
  for (const hit of hits) {
    svg.append("circle").attr("cx", x(hit.px)).attr("cy", y(hit.py)).attr("r", 4.5)
      .attr("fill", hit.part === "first" ? "#2f6fa8" : "#c9761f")
      .attr("stroke", "#fffef9").attr("stroke-width", 1);
  }

  // the ring, and the wheel at one pose
  svg.append("circle")
    .attr("cx", x(0)).attr("cy", y(0)).attr("r", x(R) - x(0))
    .attr("fill", "none").attr("stroke", RING).attr("stroke-width", 1.4).attr("stroke-dasharray", "6 5");

  const t0 = Math.PI / 6;
  const cx = (R - r) * Math.cos(t0);
  const cy = (R - r) * Math.sin(t0);
  svg.append("circle")
    .attr("cx", x(cx)).attr("cy", y(cy)).attr("r", x(r) - x(0))
    .attr("fill", "none").attr("stroke", WHEEL).attr("stroke-width", 1.6);
  const penX = cx + d * Math.cos(((R - r) * t0) / r);
  const penY = cy - d * Math.sin(((R - r) * t0) / r);
  svg.append("line")
    .attr("x1", x(cx)).attr("y1", y(cy)).attr("x2", x(penX)).attr("y2", y(penY))
    .attr("stroke", WHEEL).attr("stroke-width", 1.2);
  svg.append("circle").attr("cx", x(penX)).attr("cy", y(penY)).attr("r", 4).attr("fill", TRACE);

  const line = d3.line().x(([px]) => x(px)).y(([, py]) => y(py));
  svg.append("path").datum(points).attr("d", line)
    .attr("fill", "none").attr("stroke", INK).attr("stroke-width", 1.5);

  svg.append("text").attr("x", pad).attr("y", 24)
    .attr("font-family", "Georgia, serif").attr("font-size", 14).attr("fill", "#3b2d1c")
    .text(`Fig. 7 · the geared spirograph · ring ${R}, wheel ${r}, pen ${d} · ${R / r} petals`);
  svg.append("text").attr("x", pad).attr("y", 40)
    .attr("font-family", "ui-monospace, Menlo, monospace").attr("font-size", 11).attr("fill", "#8c6a21")
    .text(`a wheel in a ring · ${hits.length} integer stations · blue: first part, orange: second · sampled`);

  return svg.node();
}

function gcd(a, b) {
  return b ? gcd(b, a % b) : Math.abs(a);
}
