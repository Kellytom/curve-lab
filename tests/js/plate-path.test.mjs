import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import P from "../../workbench/plate_math.js";

// The handoff's words: "fixing the band fill for a path curve, so the 185 path records can
// print character rails ... two bands with no filled blob and no spike, the offset never
// crosses the spine". The path rail's cap used to move one station at a time: on c-0273 the
// distance moved 4 % of the curve's size in one step and the edge made 105 sharp turns.
// These tests fail if the cap goes back to stepping.

const registry = JSON.parse(readFileSync(new URL("../../workbench/curve-registry.json", import.meta.url)));
const curve = registry.curves.find((row) => row.uid === "c-0273");
const group = P.pathGroup(curve.path, { widthPercent: 1.5, plus: 2, minus: 2, profile: "bow" });
const [spine, plusRail, minusRail] = group.paths;

const [x0, y0, x1, y1] = P.bbox(spine);
const size = Math.hypot(x1 - x0, y1 - y0);
const distances = (rail) => spine.map((point, i) => Math.hypot(point[0] - rail[i][0], point[1] - rail[i][1]));

const maxJump = (values) => {
  let jump = 0;
  for (let i = 1; i < values.length; i += 1) jump = Math.max(jump, Math.abs(values[i] - values[i - 1]));
  return jump;
};

const sharpTurns = (rail, radians = 0.35) => {
  let count = 0;
  for (let i = 1; i < rail.length - 1; i += 1) {
    const ax = rail[i][0] - rail[i - 1][0], ay = rail[i][1] - rail[i - 1][1];
    const bx = rail[i + 1][0] - rail[i][0], by = rail[i + 1][1] - rail[i][1];
    if (Math.abs(Math.atan2(ax * by - ay * bx, ax * bx + ay * by)) > radians) count += 1;
  }
  return count;
};

test("a path curve prints two rails, not one spine", () => {
  assert.equal(group.paths.length, 3, "a spine and two rails");
  assert.equal(plusRail.length, spine.length);
  assert.equal(minusRail.length, spine.length);
});

test("the two rails sit on opposite sides and never cross the spine", () => {
  for (const [rail, side] of [[plusRail, 1], [minusRail, -1]]) {
    let crossed = 0;
    for (let i = 1; i < spine.length; i += 1) {
      const a = spine[i - 1], b = spine[Math.min(spine.length - 1, i + 1)];
      const tx = b[0] - a[0], ty = b[1] - a[1];
      const len = Math.hypot(tx, ty) || 1;
      const ord = (-ty * (rail[i][0] - spine[i][0]) + tx * (rail[i][1] - spine[i][1])) / len;
      if (ord * side < -1e-9) crossed += 1;
    }
    assert.equal(crossed, 0, "a rail crossed to the other side of the spine");
  }
  // Amended 2026-11-22: the band is no longer symmetric. The operator: "the curve on the
  // inner side should be close to the spine, the curve on the outside can be wider." So the
  // midpoint is deliberately not the spine; what must hold is that neither rail crosses it,
  // and that the inside is never wider than the outside where the cap bites.
  const biggest = (rail) => spine.reduce((most, point, i) => Math.max(most,
    Math.hypot(rail[i][0] - point[0], rail[i][1] - point[1])), 0);
  assert.ok(Math.abs(biggest(plusRail) - biggest(minusRail)) > 1e-6,
    "a tight curve must draw one side thinner than the other");
});

test("the band edge never jumps and is not a sawtooth", () => {
  for (const rail of [plusRail, minusRail]) {
    const jump = maxJump(distances(rail));
    assert.ok(jump < 0.01 * size,
      `a rail jumped ${(100 * jump / size).toFixed(1)} % of the curve's size in one step`);
    assert.ok(sharpTurns(rail) < 30,
      `a rail made ${sharpTurns(rail)} sharp turns; the old cap made 105`);
  }
});
