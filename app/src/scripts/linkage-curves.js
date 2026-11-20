// Fig. 8: a three-link linkage whose coupler point traces a rosette.
//
// The mechanism: a crank that turns about A, a coupler, and a rocker that turns about
// D. Three moving links, one ground. A point P fixed to the coupler traces the curve.
//
// Interactive: drag the crank, or move the sliders. The trace follows the crank round,
// so the rosette appears as you turn it.
//
// **Sampled, not exact.** C is the intersection of two circles, which is irrational in
// general, so nothing here claims exactness — the only figure on the page that does not.
//
// Spec: state/SPEC-prime-mover-int.md, "the linkage".
import * as d3 from "d3";

const INK = "#3b2d1c";
const CRANK = "#c9761f";
const COUPLER = "#6f4a2a";
const ROCKER = "#2f6fa8";
const GROUND = "#b9a98a";
const TRACE = "#a8341f";

// Grashof crank-rocker: d + r1 < r2 + r3, so the crank turns fully.
// Grashof crank-rocker: shortest + longest <= the other two, so the crank turns fully.
//   2 + 5 <= 5 + 3   ->  AB = 2, ground = 5, coupler = 5, rocker = 3
const A = [0, 0];
const D = [5, 0];
const R1 = 2;   // crank AB, the shortest link
const R2 = 5;   // coupler BC
const R3 = 3;   // rocker CD

const state = { theta: 40, u: 1.5, v: 0.6 };

function intersection(p, r1, q, r2) {
  const dx = q[0] - p[0];
  const dy = q[1] - p[1];
  const d = Math.hypot(dx, dy);
  if (d > r1 + r2 || d < Math.abs(r1 - r2) || d === 0) return null;
  const a = (r1 * r1 - r2 * r2 + d * d) / (2 * d);
  const h2 = r1 * r1 - a * a;
  if (h2 < 0) return null;
  const h = Math.sqrt(h2);
  const xm = p[0] + (a * dx) / d;
  const ym = p[1] + (a * dy) / d;
  return [
    [xm + (h * -dy) / d, ym + (h * dx) / d],
    [xm - (h * -dy) / d, ym - (h * dx) / d],
  ];
}

function assembly(thetaDeg, branch = null) {
  const theta = (thetaDeg * Math.PI) / 180;
  const B = [A[0] + R1 * Math.cos(theta), A[1] + R1 * Math.sin(theta)];
  const options = intersection(B, R2, D, R3);
  if (!options) return null;
  let C = options[0];
  if (branch !== null) {
    C = Math.hypot(options[0][0] - branch[0], options[0][1] - branch[1])
      <= Math.hypot(options[1][0] - branch[0], options[1][1] - branch[1]) ? options[0] : options[1];
  }
  const ux = C[0] - B[0];
  const uy = C[1] - B[1];
  const length = Math.hypot(ux, uy) || 1;
  const P = [
    B[0] + state.u * ux - state.v * length * (uy / length),
    B[1] + state.u * uy + state.v * length * (ux / length),
  ];
  return { B, C, P };
}

export function buildLinkage(hostId = "linkage-plot") {
  const host = document.getElementById(hostId);
  if (!host) return null;

  const width = 720;
  const height = 720;
  const pad = 70;
  const extent = 7;                 // the frame is ±7 units, one scale on both axes
  const x = d3.scaleLinear().domain([-extent, extent]).range([pad, width - pad]);
  const y = d3.scaleLinear().domain([-extent, extent]).range([height - pad, pad]);

  host.replaceChildren();
  const svg = d3.select(host).append("svg")
    .attr("viewBox", `0 0 ${width} ${height}`)
    .attr("width", "100%")
    .attr("role", "img")
    .attr("aria-label", "an interactive three-link mechanism tracing a rosette")
    .style("touch-action", "none");

  svg.append("rect").attr("width", width).attr("height", height).attr("fill", "#fffef9");
  // the x-y graph: a grid at whole numbers, axes, and ticks every unit on the axes
  for (let v = -extent; v <= extent; v += 1) {
    svg.append("line").attr("x1", x(v)).attr("x2", x(v)).attr("y1", y(-extent)).attr("y2", y(extent)).attr("stroke", "#f6efe1");
    svg.append("line").attr("x1", x(-extent)).attr("x2", x(extent)).attr("y1", y(v)).attr("y2", y(v)).attr("stroke", "#f6efe1");
  }
  svg.append("line").attr("x1", x(-extent)).attr("y1", y(0)).attr("x2", x(extent)).attr("y2", y(0)).attr("stroke", "#b9a98a");
  svg.append("line").attr("x1", x(0)).attr("y1", y(-extent)).attr("x2", x(0)).attr("y2", y(extent)).attr("stroke", "#b9a98a");
  for (let v = -extent; v <= extent; v += 2) {
    if (v === 0) continue;
    svg.append("text").attr("x", x(v)).attr("y", y(0) + 14).attr("text-anchor", "middle")
      .attr("font-family", "ui-monospace, Menlo, monospace").attr("font-size", 9).attr("fill", "#a8977a").text(v);
    svg.append("text").attr("x", x(0) - 6).attr("y", y(v) + 3).attr("text-anchor", "end")
      .attr("font-family", "ui-monospace, Menlo, monospace").attr("font-size", 9).attr("fill", "#a8977a").text(v);
  }
  svg.append("text").attr("x", x(extent) - 4).attr("y", y(0) + 14).attr("text-anchor", "end")
    .attr("font-family", "Georgia, serif").attr("font-size", 12).attr("fill", "#3b2d1c").text("x");
  svg.append("text").attr("x", x(0) + 6).attr("y", y(extent) + 12)
    .attr("font-family", "Georgia, serif").attr("font-size", 12).attr("fill", "#3b2d1c").text("y");

  // the integer stations of the trace, coloured by the part of the turn
  const hitLayer = svg.append("g");

  // The trace, built as the crank turns — and its mirror, which is the same
  // mechanism turned the other way. A coupler curve alone is one loop with a cusp;
  // the pair is the symmetric rosette.
  const traceData = [];
  const mirrorData = [];
  const trace = svg.append("path")
    .attr("fill", "none").attr("stroke", TRACE).attr("stroke-width", 1.6).attr("opacity", 0.9);
  const mirrorTrace = svg.append("path")
    .attr("fill", "none").attr("stroke", TRACE).attr("stroke-width", 1.6).attr("opacity", 0.55);

  const line = (colour, width2) => svg.append("line")
    .attr("stroke", colour).attr("stroke-width", width2).attr("stroke-linecap", "round");

  const ground = line(GROUND, 3).attr("stroke-dasharray", "6 4");
  const crank = line(CRANK, 4.5);
  const coupler = line(COUPLER, 4.5);
  const rocker = line(ROCKER, 4.5);
  const couplerArm = line(COUPLER, 2).attr("stroke-dasharray", "4 3");

  const makeJoint = (label, colour, radius) => {
    const circle = svg.append("circle").attr("r", radius).attr("fill", colour).attr("stroke", "#fffef9").attr("stroke-width", 1.2);
    const text = svg.append("text")
      .attr("font-family", "ui-monospace, Menlo, monospace").attr("font-size", 11).attr("fill", colour)
      .text(label);
    return { circle, text };
  };

  const jointA = makeJoint("A", INK, 4.5);
  const jointD = makeJoint("D", INK, 4.5);
  const jointB = makeJoint("B", CRANK, 5.5);
  const jointC = makeJoint("C", ROCKER, 4.5);
  const jointP = makeJoint("P", TRACE, 4.5);

  svg.append("text")
    .attr("x", pad).attr("y", 26)
    .attr("font-family", "Georgia, serif").attr("font-size", 14).attr("fill", INK)
    .text("Fig. 8 · a three-link mechanism · the coupler curve and its mirror make the rosette");
  svg.append("text")
    .attr("x", pad).attr("y", 42)
    .attr("font-family", "ui-monospace, Menlo, monospace").attr("font-size", 11).attr("fill", "#8c6a21")
    .text("drag the crank · blue: first part, orange: second · the mirror is the crank reversed · sampled");

  let lastC = null;
  const seenHits = new Set();

  function draw() {
    const pose = assembly(state.theta, lastC);
    if (!pose) return;
    lastC = pose.C;
    const { B, C, P } = pose;

    const set = (element, p, q) => element
      .attr("x1", x(p[0])).attr("y1", y(p[1]))
      .attr("x2", x(q[0])).attr("y2", y(q[1]));

    set(ground, A, D);
    set(crank, A, B);
    set(coupler, B, C);
    set(rocker, C, D);
    set(couplerArm, B, P);

    for (const [joint, p] of [[jointA, A], [jointD, D], [jointB, B], [jointC, C], [jointP, P]]) {
      joint.circle.attr("cx", x(p[0])).attr("cy", y(p[1]));
      joint.text.attr("x", x(p[0]) + 9).attr("y", y(p[1]) - 9);
    }

    // an integer station: the coupler point landing on a whole-number point
    const nearInteger = Math.abs(P[0] - Math.round(P[0])) < 0.02
      && Math.abs(P[1] - Math.round(P[1])) < 0.02;
    if (nearInteger) {
      const key = `${Math.round(P[0])},${Math.round(P[1])}`;
      if (!seenHits.has(key)) {
        seenHits.add(key);
        hitLayer.append("circle")
          .attr("cx", x(P[0])).attr("cy", y(P[1])).attr("r", 4.5)
          .attr("fill", state.theta < 180 ? "#2f6fa8" : "#c9761f")
          .attr("stroke", "#fffef9").attr("stroke-width", 1);
      }
    }

    traceData.push([x(P[0]), y(P[1])]);
    mirrorData.push([x(P[0]), y(2 * A[1] - P[1])]);   // reflected in the ground line
    if (traceData.length > 900) { traceData.shift(); mirrorData.shift(); }
    trace.attr("d", d3.line()(traceData));
    mirrorTrace.attr("d", d3.line()(mirrorData));
  }

  // dragging the crank: the pointer's angle from A sets it
  const svgNode = svg.node();
  let dragging = false;
  const toAngle = (event) => {
    const box = svgNode.getBoundingClientRect();
    const px = ((event.clientX - box.left) / box.width) * width;
    const py = ((event.clientY - box.top) / box.height) * height;
    return (Math.atan2(y.invert(py) - A[1], x.invert(px) - A[0]) * 180) / Math.PI;
  };
  svgNode.addEventListener("pointerdown", (event) => {
    dragging = true;
    svgNode.setPointerCapture(event.pointerId);
    state.theta = toAngle(event);
    draw();
  });
  svgNode.addEventListener("pointermove", (event) => {
    if (!dragging) return;
    state.theta = toAngle(event);
    draw();
  });
  svgNode.addEventListener("pointerup", () => { dragging = false; });

  const setFromControls = () => {
    const theta = Number(document.getElementById("lk-theta")?.value ?? state.theta);
    const u = Number(document.getElementById("lk-u")?.value ?? state.u * 100) / 100;
    const v = Number(document.getElementById("lk-v")?.value ?? state.v * 100) / 100;
    state.theta = theta;
    state.u = u;
    state.v = v;
    lastC = null;
    seenHits.clear();
    hitLayer.selectAll("*").remove();
    traceData.length = 0;
    mirrorData.length = 0;
    // one full turn of the crank, so the rosette is complete
    for (let a = 0; a <= 360; a += 2) {
      state.theta = a;
      draw();
    }
    state.theta = theta;
    draw();
  };
  for (const id of ["lk-theta", "lk-u", "lk-v"]) {
    document.getElementById(id)?.addEventListener("input", setFromControls);
  }

  setFromControls();
  return svg.node();
}
