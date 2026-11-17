// Square and frame assemblies of one curve, for the interactive frame page.
//
// The rule is one line: the leg bisects the corner. Put the curve's chord on
// the edge, one copy per edge (or `perSide` copies end to end), and stretch the
// curve across its chord until its end tangent is half the corner angle. A
// square corner is 90°, so the leg is 45°.
//
// Everything is floats; the page measures in points (1/72 in), so a 1-point
// stroke is literally 1 unit and stays 1 point when the image is scaled.
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.SquareLab = factory();
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const at = (p, t) => {
    const m = 1 - t;
    return [
      m * m * m * p[0][0] + 3 * m * m * t * p[1][0] + 3 * m * t * t * p[2][0] + t * t * t * p[3][0],
      m * m * m * p[0][1] + 3 * m * m * t * p[1][1] + 3 * m * t * t * p[2][1] + t * t * t * p[3][1],
    ];
  };

  const derivative = (p, t) => {
    const m = 1 - t;
    return [
      3 * m * m * (p[1][0] - p[0][0]) + 6 * m * t * (p[2][0] - p[1][0]) + 3 * t * t * (p[3][0] - p[2][0]),
      3 * m * m * (p[1][1] - p[0][1]) + 6 * m * t * (p[2][1] - p[1][1]) + 3 * t * t * (p[3][1] - p[2][1]),
    ];
  };

  const legAt = (p, t) => {
    const [dx, dy] = derivative(p, t);
    return (Math.atan2(dy, dx) * 180) / Math.PI;
  };

  const chord = (p) => Math.hypot(p[3][0] - p[0][0], p[3][1] - p[0][1]);

  const scale = (p, k) => p.map(([x, y]) => [x * k, y * k]);
  const translate = (p, o) => p.map(([x, y]) => [x + o[0], y + o[1]]);
  const flipY = (p) => p.map(([x, y]) => [x, -y]);

  const rotate = (p, deg) => {
    const a = (deg * Math.PI) / 180;
    const c = Math.cos(a), s = Math.sin(a);
    return p.map(([x, y]) => [x * c - y * s, x * s + y * c]);
  };

  // Scale across the chord until the start leg is `deg` above it. The ends do
  // not move, so the side of the square stays exactly the side.
  const stretchToLeg = (p, deg) => {
    let shape = legAt(p, 0) < 0 ? flipY(p) : p;
    const [dx, dy] = derivative(shape, 0);
    if (Math.abs(dy) < 1e-12) throw new Error("the start tangent is parallel to the chord");
    const k = (Math.tan((deg * Math.PI) / 180) * dx) / dy;
    return shape.map(([x, y]) => [x, y * k]);
  };

  const edges = (side) => [
    ["south", [0, 0], 0],
    ["east", [side, 0], 90],
    ["north", [side, side], 180],
    ["west", [0, side], 270],
  ];

  const place = (p, deg, origin) => translate(rotate(p, deg), origin);

  const assemble = (p, side, legDeg) => {
    const length = chord(p);
    if (!(length > 0)) throw new Error("the chord has no length");
    const base = stretchToLeg(scale(p, side / length), legDeg);
    return edges(side).map(([name, origin, deg]) => {
      const points = place(base, deg, origin);
      return { name, copy: "", points,
               startLeg: legAt(base, 0) + deg, endLeg: legAt(base, 1) + deg,
               start: at(base, 0), end: at(base, 1) };
    });
  };

  const frame = (p, perSide, legDeg, alternate, side) => {
    if (perSide < 1) throw new Error("a frame needs at least one copy per side");
    const length = chord(p);
    const copyLength = side / perSide;
    const base = stretchToLeg(scale(p, copyLength / length), legDeg);
    const curves = [];
    edges(side).forEach(([name, origin, deg]) => {
      for (let copy = 0; copy < perSide; copy += 1) {
        const shape = alternate && copy % 2 ? flipY(base) : base;
        const points = place(translate(shape, [copy * copyLength, 0]), deg, origin);
        curves.push({ name, copy: `[${copy}]`, points,
                      startLeg: legAt(shape, 0) + deg,
                      endLeg: legAt(shape, 1) + deg });
      }
    });
    return curves;
  };

  const ringKinks = (curves) => curves.map((curve, i) => {
    const next = curves[(i + 1) % curves.length];
    let d = Math.abs(curve.endLeg - next.startLeg) % 180;
    if (d > 90) d = 180 - d;
    return { from: `${curve.name}${curve.copy}`, to: `${next.name}${next.copy}`, angle: d };
  });

  const distinctKinks = (kinks) =>
    [...new Set(kinks.map((k) => Math.round(k.angle)))].sort((a, b) => a - b);

  // The one point floor, in points. At 4 in (288 pt) a 0.35% line is 1.008 pt;
  // below that the floor holds it at 1 point however small the image gets.
  const strokeFor = (widthPt) => Math.max(1, 0.0035 * widthPt);

  const bbox = (curves) => {
    let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    curves.forEach((curve) => curve.points.forEach(([x, y]) => {
      if (x < x0) x0 = x; if (y < y0) y0 = y;
      if (x > x1) x1 = x; if (y > y1) y1 = y;
    }));
    return [x0, y0, x1, y1];
  };

  const sample = (points, n) => {
    const out = [];
    for (let i = 0; i <= n; i += 1) out.push(at(points, i / n));
    return out;
  };

  // Curves as the three named cubics the page offers.
  const CURVES = {
    "arch-345": { label: "arch 3-4-5", points: [[0, 0], [3, 4], [7, 4], [10, 0]] },
    "s-345": { label: "S 3-4-5", points: [[0, 0], [3, -4], [7, 4], [10, 0]] },
    "arch-5-12-13": { label: "arch 5-12-13", points: [[0, 0], [5, 12], [21, 12], [26, 0]] },
    "s-5-12-13": { label: "S 5-12-13", points: [[0, 0], [5, -12], [21, 12], [26, 0]] },
  };

  return { at, derivative, legAt, chord, stretchToLeg, rotate, translate,
           scale, assemble, frame, ringKinks, distinctKinks, bbox, sample,
           strokeFor, CURVES };
});
