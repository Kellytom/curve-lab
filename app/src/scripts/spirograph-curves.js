// The spirograph, on stage II.
//
// Two vanes from ONE generator R = (24 + 7i)/25:
//
//   outer vane   a·R^k          turns 16.26° a station
//   inner vane   b·R^(m·k)      turns m times as fast, m whole
//   the curve    the sum of the two
//
// The ratio m must be a whole number, or the pattern never repeats. Every station is
// exact: R has length exactly one, and a, b, m are whole numbers.
//
// Drwan with D3: the sum in ink, the two vanes faintly in two tones, so the shape can
// be read back to the arms that made it. Spec: state/SPEC-stage-two-int.md.
import * as d3 from "d3";
import { fineWalk, walkFor, station } from "./prime-mover-driver.js";

const INK = "#6f4a2a";

function arm(power, amplitude, count, tripleName) {
  // both vanes come from the fine walk; the inner one steps `power` times as fast.
  const { hypotenuse } = walkFor(tripleName);
  const scale = amplitude / Number(hypotenuse);
  const walk = fineWalk(count * power, tripleName);
  return Array.from({ length: count }, (_, k) => {
    const point = station(walk[k * power]);
    return [point.x * scale, point.y * scale];
  });
}

// What the spirograph costs, before it costs it. Each vane is a BigInt rational whose
// denominator grows by the hypotenuse every step, so a thin triple with a large ratio
// builds numbers with thousands of digits and freezes the page.
export function spirographCost(ratio, tripleName = "7,24,25") {
  const { hypotenuse, turn } = walkFor(tripleName);
  const count = Math.min(111, 2 * Math.ceil(360 / turn));
  const digits = Math.log10(Number(hypotenuse));
  // the work is steps × the size of the numbers, and both grow with ratio and count
  return { count, cost: count * count * ratio * ratio * digits };
}

export function ratioData(ratio, outer = 10, inner = 4, tripleName = "7,24,25") {
  const count = spirographCost(ratio, tripleName).count;
  const a = arm(1, outer, count, tripleName);
  const b = arm(ratio, inner, count, tripleName);
  return {
    count,
    outer: a,
    inner: b,
    sum: a.map(([ax, ay], index) => [ax + b[index][0], ay + b[index][1]]),
  };
}

export function buildSpirograph(hostId = "sp-plot", ratio = 5, tripleName = "7,24,25") {
  const host = document.getElementById(hostId);
  if (!host) return null;

  const data = ratioData(ratio, 10, 4, tripleName);
  const width = 720;
  const height = 720;
  const pad = 42;
  // the frame follows the curve, with one scale on both axes
  const xs = data.sum.map(([px]) => px);
  const ys = data.sum.map(([, py]) => py);
  const midX = (Math.min(...xs) + Math.max(...xs)) / 2;
  const midY = (Math.min(...ys) + Math.max(...ys)) / 2;
  const half = Math.max(
    (Math.max(...xs) - Math.min(...xs)) / 2,
    (Math.max(...ys) - Math.min(...ys)) / 2,
  ) * 1.15;
  const x = d3.scaleLinear().domain([midX - half, midX + half]).range([pad, width - pad]);
  const y = d3.scaleLinear().domain([midY - half, midY + half]).range([height - pad, pad]);

  host.replaceChildren();
  const svg = d3.select(host).append("svg")
    .attr("viewBox", `0 0 ${width} ${height}`)
    .attr("width", "100%")
    .attr("role", "img")
    .attr("aria-label", `the spirograph at ratio ${ratio}`);

  svg.append("rect").attr("width", width).attr("height", height).attr("fill", "#fffef9");
  const line = d3.line()
    .x(([px]) => x(px))
    .y(([, py]) => y(py))
    .curve(d3.curveCatmullRom.alpha(0.5));

  // the sum: the spirograph itself
  svg.append("path").datum(data.sum).attr("d", line)
    .attr("fill", "none").attr("stroke", INK).attr("stroke-width", 1.6);

  // the calculated points, carrying the colours of the two source walks
  svg.selectAll("circle.station")
    .data(data.sum)
    .join("circle")
    .attr("class", "station")
    .attr("cx", ([px]) => x(px))
    .attr("cy", ([, py]) => y(py))
    .attr("r", 3.2)
    .attr("fill", (_, index) => (index % 2 === 0 ? "#c9761f" : "#2f6fa8"))
    .attr("stroke", "#fffef9")
    .attr("stroke-width", 0.8);

  svg.append("text")
    .attr("x", pad).attr("y", 24)
    .attr("font-family", "Georgia, serif").attr("font-size", 14).attr("fill", "#3b2d1c")
    .text(`Fig. 4 · the spirograph at ratio ${ratio} · ${data.count} stations`);
  svg.append("text")
    .attr("x", pad).attr("y", 40)
    .attr("font-family", "ui-monospace, Menlo, monospace").attr("font-size", 11).attr("fill", "#8c6a21")
    .text("a·walker(k) + b·walker(m·k) · the stations carry the two source colours");

  return svg.node();
}
