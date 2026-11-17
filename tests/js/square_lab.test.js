// The square/frame geometry the interactive page uses.
// Run: node --test tests/js
const { test } = require("node:test");
const assert = require("node:assert/strict");
const L = require("../../workbench/square_lab.js");

const ARCH = L.CURVES["arch-345"].points;
const S = L.CURVES["s-345"].points;

test("the leg bisects the corner", () => {
  assert.ok(Math.abs(L.legAt(ARCH, 0) - 53.130102) < 1e-6);
  const stretched = L.stretchToLeg(ARCH, 45);
  assert.ok(Math.abs(L.legAt(stretched, 0) - 45) < 1e-9);
  // the ends do not move
  assert.deepEqual(stretched[0], [0, 0]);
  assert.deepEqual(stretched[3], [10, 0]);
});

test("an arch at 45° turns the corner continuously", () => {
  const curves = L.assemble(ARCH, 300, 45);
  assert.equal(curves.length, 4);
  assert.deepEqual(L.distinctKinks(L.ringKinks(curves)), [0]);
});

test("an S at 45° turns the corner at a right angle", () => {
  const curves = L.assemble(S, 300, 45);
  assert.deepEqual(L.distinctKinks(L.ringKinks(curves)), [90]);
});

test("an unstretched arch leaves a 16° kink", () => {
  const curves = L.assemble(ARCH, 300, L.legAt(ARCH, 0));
  assert.deepEqual(L.distinctKinks(L.ringKinks(curves)), [16]);
});

test("a frame has perSide copies on each side, each one chord long", () => {
  const curves = L.frame(ARCH, 3, 45, false, 900);
  assert.equal(curves.length, 12);
  const side170 = curves.filter((c) => c.name === "south");
  assert.equal(side170.length, 3);
  side170.forEach((curve) => {
    const first = curve.points[0];
    const last = curve.points[3];
    assert.ok(Math.abs(Math.hypot(last[0] - first[0], last[1] - first[1]) - 300) < 1e-9);
  });
});

test("the frame's joins are 0° at corners, 90° inside a side", () => {
  assert.deepEqual(L.distinctKinks(L.ringKinks(L.frame(ARCH, 3, 45, false, 900))), [0, 90]);
  assert.deepEqual(L.distinctKinks(L.ringKinks(L.frame(ARCH, 3, 45, true, 900))), [0]);
});

test("the stroke never falls below one point", () => {
  assert.equal(L.strokeFor(72), 1);          // 1 inch
  assert.equal(L.strokeFor(144), 1);         // 2 inches
  assert.ok(Math.abs(L.strokeFor(288) - 1.008) < 1e-9);  // 4 inches
});
