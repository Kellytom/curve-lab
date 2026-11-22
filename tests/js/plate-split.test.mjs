import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import P from "../../workbench/plate_math.js";

// The operator, 2026-11-22: "break the band at each sharp turn", and "but only for display
// purposes. keep it internally as an equation we can send back and forth to inkscape".
// So the break is computed from the curvature at render time; the record keeps its speed
// rows untouched, and the run's rail never reaches the fold limit.

const registry = JSON.parse(readFileSync(new URL("../../workbench/curve-registry.json", import.meta.url)));
const curveOf = (uid) => registry.curves.find((row) => row.uid === uid);

const optionsFor = (curve, widthPercent, strength = 1.3) => ({
  name: curve.name,
  speedX: curve.speedX,
  speedY: curve.speedY,
  width: { percent: widthPercent },
  character: { plus: strength, minus: strength, profile: "bow" },
});

test("a sharp curve is drawn as runs, with a gap at each turn", () => {
  // c-0046 (wave-1of14-3) has two cusps; at 4 % a single band folds, so the pen lifts.
  const split = P.splitGroup(optionsFor(curveOf("c-0046"), 4));
  assert.ok(split, "the sharp curve must produce runs, not a refusal");
  assert.ok(split.segments.length >= 2, `expected several runs, got ${split.segments.length}`);
  for (let i = 1; i < split.segments.length; i += 1) {
    assert.ok(split.segments[i].from > split.segments[i - 1].to,
      "consecutive runs must be separated by a real gap");
  }
});

test("every drawn run stays under the fold limit at the asked width", () => {
  const curve = curveOf("c-0046");
  const split = P.splitGroup(optionsFor(curve, 4));
  for (const segment of split.segments) {
    const kappa = P.curvatureProfile(curve.speedX, curve.speedY,
      segment.t.map((t) => ({ t })));
    segment.t.forEach((t, i) => {
      const gap = Math.hypot(segment.rails[0][i][0] - segment.spine[i][0],
        segment.rails[0][i][1] - segment.spine[i][1]);
      assert.ok(gap * kappa[i] <= 0.9 + 1e-6,
        `t = ${t}: gap ${gap} x curvature ${kappa[i]} folds`);
    });
  }
});

test("a curve that can carry the width is one continuous run", () => {
  // c-0001 at 1 % fits everywhere, so the band is not broken: one run, no lift.
  const split = P.splitGroup(optionsFor(curveOf("c-0001"), 1));
  assert.equal(split.segments.length, 1);
  assert.ok(split.segments[0].from < 0.01 && split.segments[0].to > 0.99);
});

test("the break is display only: the equation is not touched", () => {
  const curve = curveOf("c-0046");
  const before = JSON.stringify(curve);
  P.splitGroup(optionsFor(curve, 4));
  assert.equal(JSON.stringify(curve), before, "splitGroup must not edit the record");
  assert.ok(Array.isArray(curve.speedX) && Array.isArray(curve.speedY));
  assert.equal(curve.path, undefined, "a row curve stays a row curve");
});
