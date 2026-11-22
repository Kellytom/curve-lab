import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import P from "../../workbench/plate_math.js";

// The operator's words: "try different lower values for the percentage... the width jumps
// all around." The fold guard used to halve the width in powers of two, so raising the
// slider could narrow the band: on c-0002, 2.2 % became 1.15 % at the next step. These
// tests fail if the guard goes back to stepping.

const registry = JSON.parse(readFileSync(new URL("../../workbench/curve-registry.json", import.meta.url)));

const groupAt = (uid, widthPercent, plus = 2, minus = 2) => {
  const curve = registry.curves.find((row) => row.uid === uid);
  return P.group({
    name: curve.name, speedX: curve.speedX, speedY: curve.speedY,
    width: { percent: widthPercent }, character: { plus, minus, profile: "bow" },
  });
};

for (const uid of ["c-0001", "c-0002"]) {
  test(`${uid}: raising the width never narrows the band`, () => {
    let previous = 0;
    for (let step = 0.5; step <= 8.001; step += 0.1) {
      const width = Math.round(step * 10) / 10;
      const used = groupAt(uid, width).width;
      assert.ok(used >= previous - 1e-9,
        `width ${width} % drew ${used} %, narrower than the step below (${previous} %)`);
      previous = used;
    }
  });

  test(`${uid}: the band folds nowhere, and the outside keeps the asked width`, () => {
    const curve = registry.curves.find((row) => row.uid === uid);
    const group = groupAt(uid, 6);
    // the inside is cut at a tight turn; the outside moves away from the centre of curvature
    // and keeps the full ask. Nothing on either rail may fold.
    const samples = P.spine(curve.speedX, curve.speedY, 700).map((s) => [s.x, s.y]);
    const [x0, y0, x1, y1] = P.bbox(samples);
    const size = Math.hypot(x1 - x0, y1 - y0);
    assert.ok(Number.isFinite(group.fold) && group.fold <= 0.9 + 1e-6,
      `the drawn band folds: ${group.fold}`);
    assert.ok(group.paths.length >= 3, "a rated band must keep both rails");
    const outside = Math.max(group.widthPlus, group.widthMinus);
    assert.ok(outside > group.width, "the outside rail must be wider than the cut inside");
    assert.ok(outside > 3.5, `the outside rail is ${outside.toFixed(2)} %, the ask was 6 %`);
  });
}

test("c-0001 at the operator's preset keeps a band and does not fold at the loop", () => {
  // The measured fault: at 1 % / plus 2.5 / minus 0.1 the widest rail reached 1.28 x the
  // fold limit, because the guard capped the base width and then added the bow. The band
  // must still exist and nothing on it may fold.
  const group = groupAt("c-0001", 1, 2.5, 0.1);
  assert.ok(group.width > 0, "the band must exist");
  assert.ok(Number.isFinite(group.fold) && group.fold <= 0.9 + 1e-6,
    `the drawn band folds: ${group.fold}`);
  assert.ok(group.paths.length >= 3);
});
