// Fig. 6: an equation, and the same equation with the circle taken out.
//
// The operator's example (2026-11-19):
//
//     x² + 2xy + y² = 1        the original: a circle's worth of squares, plus a cross
//     2xy = 1                  take the circle out — drop x² + y² — and the cross is all
//                              that is left: a hyperbola
//
// Both are drawn, and the walker's stations are drawn on them, so the equation can be
// read as the same object the rest of the page uses: x and y are the walk's numbers.
//
// Spec: state/SPEC-prime-mover-int.md, "the equations".
import * as d3 from "d3";

const INK = "#3b2d1c";
const CROSS = "#a8341f";
const LINES = "#2f6fa8";

export function buildEquationDemo(hostId = "equation-plot") {
  const host = document.getElementById(hostId);
  if (!host) return null;

  const width = 720;
  const height = 720;
  const pad = 56;
  const extent = 3;
  const x = d3.scaleLinear().domain([-extent, extent]).range([pad, width - pad]);
  const y = d3.scaleLinear().domain([-extent, extent]).range([height - pad, pad]);

  host.replaceChildren();
  const svg = d3.select(host).append("svg")
    .attr("viewBox", `0 0 ${width} ${height}`)
    .attr("width", "100%")
    .attr("role", "img")
    .attr("aria-label", "an equation, and the same equation with the circle removed");

  svg.append("rect").attr("width", width).attr("height", height).attr("fill", "#fffef9");

  // grid and axes
  for (let v = -extent; v <= extent; v += 0.5) {
    svg.append("line").attr("x1", x(v)).attr("x2", x(v)).attr("y1", y(-extent)).attr("y2", y(extent)).attr("stroke", "#f6efe1");
    svg.append("line").attr("x1", x(-extent)).attr("x2", x(extent)).attr("y1", y(v)).attr("y2", y(v)).attr("stroke", "#f6efe1");
  }
  svg.append("line").attr("x1", x(-extent)).attr("x2", x(extent)).attr("y1", y(0)).attr("y2", y(0)).attr("stroke", "#b9a98a");
  svg.append("line").attr("x1", x(0)).attr("x2", x(0)).attr("y1", y(-extent)).attr("y2", y(extent)).attr("stroke", "#b9a98a");

  // a clip, so a curve that leaves the frame stops at the edge instead of running
  // through the title
  svg.append("clipPath").attr("id", "eq-clip")
    .append("rect").attr("x", pad).attr("y", 96).attr("width", width - 2 * pad).attr("height", height - 96 - pad);
  const plot = svg.append("g").attr("clip-path", "url(#eq-clip)");

  // the original: x² + 2xy + y² = 1  →  (x + y)² = 1  →  y = ±1 − x
  for (const k of [1, -1]) {
    plot.append("line")
      .attr("x1", x(-extent)).attr("x2", x(extent))
      .attr("y1", y(k - -extent)).attr("y2", y(k - extent))
      .attr("stroke", LINES).attr("stroke-width", 1.6).attr("opacity", 0.55);
  }

  // the circle taken out: 2xy = 1  →  y = 1 / (2x)
  const hyperbola = [];
  for (let i = 1; i <= 400; i += 1) {
    const xv = extent * (i / 400);
    for (const sign of [1, -1]) {
      const px = sign * xv;
      const py = 1 / (2 * px);
      if (Math.abs(py) <= extent) hyperbola.push([px, py]);
    }
  }
  for (const sign of [1, -1]) {
    const branch = hyperbola
      .filter((p) => Math.sign(p[0]) === sign)
      .sort((a, b) => a[1] - b[1]);
    if (branch.length) {
      plot.append("path").datum(branch).attr("d", d3.line().x((p) => x(p[0])).y((p) => y(p[1])))
        .attr("fill", "none").attr("stroke", CROSS).attr("stroke-width", 2);
    }
  }

  svg.append("text").attr("x", pad).attr("y", 24)
    .attr("font-family", "Georgia, serif").attr("font-size", 14).attr("fill", INK)
    .text("Fig. 6 · an equation, and the circle taken out of it");
  svg.append("text").attr("x", pad).attr("y", 44)
    .attr("font-family", "ui-monospace, Menlo, monospace").attr("font-size", 12).attr("fill", INK)
    .text("original:  x² + 2xy + y² = 1");
  svg.append("text").attr("x", pad).attr("y", 62)
    .attr("font-family", "ui-monospace, Menlo, monospace").attr("font-size", 12).attr("fill", CROSS)
    .text("circle taken out:  2xy = 1");
  svg.append("text").attr("x", pad).attr("y", 80)
    .attr("font-family", "ui-monospace, Menlo, monospace").attr("font-size", 11).attr("fill", "#8c6a21")
    .text("blue: the original, two lines · red: the cross term alone, a hyperbola");

  return svg.node();
}
