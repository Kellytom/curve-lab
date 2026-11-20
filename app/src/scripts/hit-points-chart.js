// Fig. 4: the hit points on the 25 circle, drawn with D3 and zoomable.
//
// Every point is an exact ratio of whole numbers; the drawing converts to a number
// only to place a dot. Grid lines show the whole numbers; a dashed guide runs from
// each point to both axes, so a point's x and y are read straight off the grid.
// Zoom is geometric (D3's zoom transform), with dot size and stroke width divided
// by the scale so nothing turns into a blob.
//
// Spec: state/SPEC-prime-mover-int.md, "the hit points".
import * as d3 from "d3";
import { hitPoints, quadrantPoints, walkFor, station } from "./prime-mover-driver.js";

const INK = "#3b2d1c";
const WARM = "#c9761f";
const COOL = "#2f6fa8";
const GRID = "#eee5d2";
const GUIDE = "#e3c9a4";

export function buildHitChart(hostId = "hit-chart", count = 12, tripleName = "7,24,25", halfTurn = false) {
  const host = document.getElementById(hostId);
  if (!host) return null;

  // the station count follows the triple: enough to pass a full turn, or half of it
  const step = walkFor(tripleName).turn;
  const stations = halfTurn ? quadrantPoints(tripleName) : hitPoints(tripleName, Math.ceil(360 / step) + 1);
  const exact = stations;
  // every triple walks a circle of its own radius z; here they are all drawn on 25.
  // The conversion happens in the driver: this file never touches a BigInt.
  const hypotenuse = Number(walkFor(tripleName).hypotenuse);
  const rows = exact.map((point) => {
    const s = station(point);
    return { i: s.k, x: (s.x * 25) / hypotenuse, y: (s.y * 25) / hypotenuse };
  });

  // the table is fed from the same values as the chart, so they cannot disagree
  // The same twelve points as Gaussian integers: X + Yi, whole numbers, with the
  // radius that makes them whole. A Gaussian integer is a pair of whole numbers
  // tagged with i; nothing irrational enters, and nothing is rounded.
  // A square plot: equal scale on both axes, or the circle is drawn as an ellipse.
  const width = 760;
  const height = 760;
  const margin = { top: 28, right: 26, bottom: 44, left: 56 };
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;
  const radius = 28;   // a little wider than the circle, so the edge is visible

  const x = d3.scaleLinear().domain([-radius, radius]).range([0, innerWidth]);
  const y = d3.scaleLinear().domain([-radius, radius]).range([innerHeight, 0]);

  host.replaceChildren();
  const svg = d3.select(host).append("svg")
    .attr("viewBox", `0 0 ${width} ${height}`)
    .attr("width", "100%")
    .attr("role", "img")
    .attr("aria-label", "the hit points on the 25 circle, zoomable")
    .style("cursor", "grab");

  svg.append("rect").attr("width", width).attr("height", height).attr("fill", "#fffef9");

  const plot = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);
  plot.append("clipPath").attr("id", "hit-clip")
    .append("rect").attr("width", innerWidth).attr("height", innerHeight);
  const canvas = plot.append("g").attr("clip-path", "url(#hit-clip)");

  // the reference circle
  canvas.append("circle")
    .attr("cx", x(0)).attr("cy", y(0)).attr("r", x(25) - x(0))
    .attr("fill", "none").attr("stroke", "#c9a441").attr("stroke-width", 1.2)
    .attr("stroke-dasharray", "6 5");

  // dashed guides: every point down to x = 0 and across to y = 0
  for (const row of rows) {
    canvas.append("line")
      .attr("x1", x(row.x)).attr("x2", x(row.x))
      .attr("y1", y(row.y)).attr("y2", y(0))
      .attr("stroke", GUIDE).attr("stroke-width", 0.9).attr("stroke-dasharray", "3 3");
    canvas.append("line")
      .attr("x1", x(row.x)).attr("x2", x(0))
      .attr("y1", y(row.y)).attr("y2", y(row.y))
      .attr("stroke", GUIDE).attr("stroke-width", 0.9).attr("stroke-dasharray", "3 3");
  }

  // the points
  const dots = canvas.append("g").selectAll("circle").data(rows).join("circle")
    .attr("cx", (row) => x(row.x))
    .attr("cy", (row) => y(row.y))
    .attr("r", 4)
    .attr("fill", WARM)
    .attr("stroke", "#fffef9")
    .attr("stroke-width", 1);

  dots.append("title").text((row) => `i = ${row.i} · x = ${row.x} · y = ${row.y}`);

  // axes and grid, redrawn on zoom so the labels stay legible
  const xAxis = plot.append("g").attr("transform", `translate(0,${innerHeight})`);
  const yAxis = plot.append("g");
  const grid = plot.insert("g", ":first-child");

  const zoom = d3.zoom()
    .scaleExtent([0.6, 40])
    .on("zoom", (event) => {
      const { k, x: tx, y: ty } = event.transform;
      canvas.attr("transform", `translate(${tx},${ty}) scale(${k})`);
      // keep marks a constant size on screen
      dots.attr("r", 4 / k)
        .attr("stroke-width", 1 / k);
      canvas.selectAll("line").attr("stroke-width", (d, index, nodes) => (index < 2 ? 1.2 / k : 0.9 / k));
      canvas.select("circle").attr("stroke-width", 1.2 / k);
      if (k > 3) {
        canvas.selectAll("line").style("visibility", "visible");
      }
    });

  svg.call(zoom);

  function drawAxes() {
    const xTickValues = d3.range(-28, 29, 4);
    const yTickValues = d3.range(-28, 29, 4);

    xAxis.call(
      d3.axisBottom(x).tickValues(xTickValues).tickSizeOuter(0),
    ).call((selection) => selection.selectAll("text")
      .attr("font-family", "ui-monospace, Menlo, monospace")
      .attr("font-size", 10)
      .attr("fill", "#9b8a6b"));

    yAxis.call(
      d3.axisLeft(y).tickValues(yTickValues).tickSizeOuter(0),
    ).call((selection) => selection.selectAll("text")
      .attr("font-family", "ui-monospace, Menlo, monospace")
      .attr("font-size", 10)
      .attr("fill", "#9b8a6b"));

    grid.selectAll("*").remove();
    for (const value of xTickValues) {
      grid.append("line")
        .attr("x1", x(value)).attr("x2", x(value))
        .attr("y1", 0).attr("y2", innerHeight)
        .attr("stroke", GRID).attr("stroke-width", 0.8);
    }
    for (const value of yTickValues) {
      grid.append("line")
        .attr("x1", 0).attr("x2", innerWidth)
        .attr("y1", y(value)).attr("y2", y(value))
        .attr("stroke", GRID).attr("stroke-width", 0.8);
    }
  }
  drawAxes();

  // the axis lines themselves, which d3 draws but leaves unstyled here
  for (const axis of [xAxis, yAxis]) {
    axis.selectAll("path")
      .attr("stroke", "#6b5a3e").attr("stroke-width", 1.1).attr("fill", "none");
    axis.selectAll("line")
      .attr("stroke", "#6b5a3e").attr("stroke-width", 1.1);
  }

  // the two zero lines, a shade stronger than the grid
  plot.append("line")
    .attr("x1", 0).attr("x2", innerWidth).attr("y1", y(0)).attr("y2", y(0))
    .attr("stroke", "#b9a98a").attr("stroke-width", 1.2);
  plot.append("line")
    .attr("x1", x(0)).attr("x2", x(0)).attr("y1", 0).attr("y2", innerHeight)
    .attr("stroke", "#b9a98a").attr("stroke-width", 1.2);

  // axis names, at the end of each axis
  plot.append("text")
    .attr("x", innerWidth).attr("y", innerHeight + 36)
    .attr("text-anchor", "end")
    .attr("font-family", "Georgia, serif").attr("font-size", 14).attr("fill", INK)
    .text("x");
  plot.append("text")
    .attr("x", -40).attr("y", -6)
    .attr("font-family", "Georgia, serif").attr("font-size", 14).attr("fill", INK)
    .text("y");

  plot.append("text")
    .attr("x", 0).attr("y", -10)
    .attr("font-family", "Georgia, serif").attr("font-size", 14).attr("fill", INK)
    .text(`Fig. 4 · ${rows.length} hit points, ${step.toFixed(2)}° apart · `
      + `${halfTurn ? "quadrants I and IV" : "the full turn"} · scroll to zoom, drag to pan`);

  plot.append("text")
    .attr("x", 0).attr("y", 4)
    .attr("font-family", "ui-monospace, Menlo, monospace").attr("font-size", 11).attr("fill", COOL)
    .text(exact.every((point) => station(point).exact)
      ? "each hit point is a reduced ratio of whole numbers"
      : "exact ratios in the notes · dots drawn to 2⁻³⁰ (nine decimal places)");

  return svg.node();
}
