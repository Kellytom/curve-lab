import test from "node:test";
import assert from "node:assert/strict";
import { arch, archPath, apexAngle, sides, sizeOf } from "../../app/src/lib/class-v.js";

// Class V: half a Tschirnhausen, trimmed, mirrored and joined at the tip. The fault this pins:
// the two halves were concatenated foot-to-apex twice, so the stroke jumped across the arch and
// the side curves drew long chords through the opening.

test("the arch is one stroke with no jump", () => {
  const built = arch({ trim: 0.1, to: 2.4, joinAt: "tip" });
  const spine = archPath(built);
  const size = sizeOf(built).width;
  for (let i = 1; i < spine.length; i += 1) {
    const step = Math.hypot(spine[i].x - spine[i - 1].x, spine[i].y - spine[i - 1].y);
    assert.ok(step < 0.05 * size, `a jump of ${step.toFixed(2)} at station ${i}`);
  }
  // the stroke starts at one foot and ends at the other, both near the bottom
  assert.ok(Math.abs(spine[0].y - spine.at(-1).y) < 1e-9, "the feet must sit at the same height");
  assert.ok(spine[0].x * spine.at(-1).x < 0, "the feet must sit on opposite sides");
});

test("the side curves follow the arch and never jump", () => {
  const built = arch({ trim: 0.1, to: 2.4, joinAt: "tip" });
  const spine = archPath(built);
  const band = sides(spine, 2);
  const size = sizeOf(built).width;
  for (const line of [band.left, band.right]) {
    for (let i = 1; i < line.length; i += 1) {
      const step = Math.hypot(line[i].x - line[i - 1].x, line[i].y - line[i - 1].y);
      assert.ok(step < 0.05 * size, `a rail jump of ${step.toFixed(2)} at station ${i}`);
    }
  }
});

test("the apex angle is a number and the trim moves it", () => {
  const a = apexAngle(arch({ trim: 0.05, to: 2.4, joinAt: "tip" }));
  const b = apexAngle(arch({ trim: 0.2, to: 2.4, joinAt: "tip" }));
  assert.ok(a > 0 && a < 180, `apex ${a}`);
  assert.ok(Math.abs(a - b) > 1, "a different trim must give a different point");
});
