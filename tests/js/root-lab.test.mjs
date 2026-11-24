import test from "node:test";
import assert from "node:assert/strict";
import { build, explain } from "../../app/src/scripts/lab-roots.js";

// The lab's recipe: mirrored roots for y, an x row A + B(t² − t), and the PH integral of
// (u² − v², 2uv). Both rows are symmetric about t = ½, so the curve must be as well — that is
// the property the "sums stay proper" note rests on.

// v is anti-symmetric about t = ½ and u is symmetric, so u² − v² is symmetric and 2uv is
// anti-symmetric: the curve mirrors about the vertical line through x = x(1)/2 —
// x(t) + x(1−t) = x(1) and y(t) = y(1−t).
const mirrorWorst = (points) => {
  const last = points.length - 1;
  const [endX] = points[last];
  const xs = points.map((point) => point[0]);
  const ys = points.map((point) => point[1]);
  const size = Math.max(...xs) - Math.min(...xs) || Math.max(...ys) - Math.min(...ys) || 1;
  let worst = 0;
  for (let i = 0; i <= last; i += 1) {
    const [x0, y0] = points[i];
    const [x1, y1] = points[last - i];
    worst = Math.max(worst, Math.abs(x0 + x1 - endX), Math.abs(y0 - y1));
  }
  return worst / size;
};

test("the default curve is the known good one and is symmetric about its midpoint", () => {
  const result = build(1, 9, 3);
  assert.deepEqual(result.u, [1, -2, 2]);
  assert.equal(result.v.length - 1, 5, "pair plus three roots at ½ is degree 5");
  assert.ok(mirrorWorst(result.points) < 1e-8, `asymmetry ${mirrorWorst(result.points)}`);
  assert.ok(Number.isInteger(result.crossings) && result.crossings >= 0);
  assert.ok(Number.isInteger(result.inflections) && result.inflections >= 0);
});

test("a second pair adds two roots to y and nothing to x, and keeps the symmetry", () => {
  const one = build(1, 9, 3);
  const two = build(1, 9, 3, { p2: 2, q2: 7 });
  assert.deepEqual(two.u, one.u);
  assert.equal(two.v.length - one.v.length, 2);
  assert.ok(mirrorWorst(two.points) < 1e-8);
  assert.notDeepEqual(two.points, one.points);
});

test("the x row is A + B(t² − t) and B = 0 still leaves a symmetric curve", () => {
  const flat = build(1, 9, 3, { xA: 2, xB: 0 });
  assert.deepEqual(flat.u, [2, -0, 0]);
  assert.ok(mirrorWorst(flat.points) < 1e-8);
  const bent = build(1, 9, 3, { xA: 1, xB: 4 });
  assert.deepEqual(bent.u, [1, -4, 4]);
  assert.ok(mirrorWorst(bent.points) < 1e-8);
});

test("p2 = 0 is off, and a denominator at or below the numerator cannot add a real pair", () => {
  const off = build(1, 9, 3, { p2: 0 });
  assert.equal(off.v.length, build(1, 9, 3).v.length);
  const bad = build(1, 9, 3, { p2: 7, q2: 7 });
  assert.equal(bad.v.length, build(1, 9, 3).v.length);
});

test("the note names the axes it was built from, not a typed case", () => {
  const result = build(2, 5, 1, { p2: 3, q2: 10, xA: 2, xB: 3 });
  const note = explain(result, 2, 5, 1, { p2: 3, q2: 10, xA: 2, xB: 3 });
  assert.match(note, /2\/5/);
  assert.match(note, /3\/10/);
  assert.match(note, /2 \+ 3\(t² − t\)/);
  assert.match(note, new RegExp(`${result.crossings} crossing`));
});
