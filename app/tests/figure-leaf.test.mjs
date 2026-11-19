// The central design is at least two curves: the leaf.
//
// The operator asked for this more than once (DESIGN-int §Central designs are
// at least two curves, 2026-11-17). A figure with pieces = 1 used to draw one
// curve in the middle. It now draws the curve and its mirror across the chord
// through its feet, so the two halves share both feet.

import { test } from "node:test";
import assert from "node:assert/strict";
import { figureFor } from "../src/lib/bordered.js";

const SIZE = 900;
const PAD = 0.04;

const leaf = {
  uid: "c-9999",
  name: "leaf-test",
  path: [
    [0, 0], [10, 20], [30, 40], [50, 40], [70, 20], [80, 0],
  ],
  pieces: 1,
  rotation: 0,
};

// The same transform svgFrom applies, so the test checks the 900 box and the
// four border edges in the coordinates a reader sees.
function toSvg(paths) {
  const all = paths.flat();
  const xs = all.map((p) => p[0]);
  const ys = all.map((p) => p[1]);
  const x0 = Math.min(...xs), x1 = Math.max(...xs);
  const y0 = Math.min(...ys), y1 = Math.max(...ys);
  const w = x1 - x0 || 1, h = y1 - y0 || 1;
  const inner = SIZE * (1 - 2 * PAD);
  const k = inner / Math.max(w, h);
  const ox = (SIZE - w * k) / 2 - x0 * k;
  const oy = (SIZE + h * k) / 2 + y0 * k;
  return paths.map((path) => path.map(([x, y]) => [x * k + ox, oy - y * k]));
}

test("the leaf is two curves with shared feet and a full border", () => {
  const figure = figureFor(leaf, {}, null);
  assert.equal(figure.centralCount, 2);

  const [below, above] = figure.paths.slice(0, 2);
  const feet = (line) => [line[0], line[line.length - 1]];
  const [b0, b1] = feet(below);
  const [a0, a1] = feet(above);
  const d0 = Math.hypot(b0[0] - a0[0], b0[1] - a0[1]);
  const d1 = Math.hypot(b1[0] - a1[0], b1[1] - a1[1]);
  console.log(`feet distances: ${d0.toExponential(3)} ${d1.toExponential(3)}`);
  assert.ok(d0 < 1e-6, `first feet ${d0}`);
  assert.ok(d1 < 1e-6, `last feet ${d1}`);

  for (const path of figure.paths) {
    for (const [x, y] of path) {
      assert.ok(Number.isFinite(x) && Number.isFinite(y), `not finite: ${x},${y}`);
    }
  }

  const svg = toSvg(figure.paths);
  const pad = SIZE * PAD;
  for (const path of svg) {
    for (const [x, y] of path) {
      assert.ok(x >= pad - 1e-6 && x <= SIZE - pad + 1e-6, `x ${x} outside the pad`);
      assert.ok(y >= pad - 1e-6 && y <= SIZE - pad + 1e-6, `y ${y} outside the pad`);
    }
  }

  const border = svg.slice(figure.centralCount);
  const near = (v, target) => Math.abs(v - target) <= 1;
  assert.ok(border.some((path) => path.some(([x]) => near(x, pad))), "left border edge");
  assert.ok(border.some((path) => path.some(([x]) => near(x, SIZE - pad))), "right border edge");
  assert.ok(border.some((path) => path.some(([, y]) => near(y, pad))), "top border edge");
  assert.ok(border.some((path) => path.some(([, y]) => near(y, SIZE - pad))), "bottom border edge");

  const central = svg.slice(0, figure.centralCount);
  const cxs = central.flat().map(([x]) => x);
  const cys = central.flat().map(([, y]) => y);
  assert.ok(Math.max(...cxs) - Math.min(...cxs) > 0, "central region empty in x");
  assert.ok(Math.max(...cys) - Math.min(...cys) > 0, "central region empty in y");
});

test("pieces 2 and 4 keep the old mirroring", () => {
  assert.equal(figureFor({ ...leaf, pieces: 2 }, {}, null).centralCount, 2);
  assert.equal(figureFor({ ...leaf, pieces: 4 }, {}, null).centralCount, 4);
});
