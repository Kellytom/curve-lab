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

  test(`${uid}: the band keeps the asked width, and a fold is marked as a crossing`, () => {
    const group = groupAt(uid, 6);
    // The law changed on 2026-11-23 (operator: remove the inside cap and the roundSpikes
    // bevel, let each rail cross itself at a tight turn, dot the crossing, hide the loop).
    // There is no cut any more: the rail is the asked offset at every station, so the band is
    // the ask; where the ask folds, the rail crosses itself, and the plate marks and hides it.
    assert.ok(group.paths.length >= 3, "a rated band must keep both rails");
    assert.ok(Math.abs(group.width - 6) < 0.6, `drew ${group.width} %, asked 6 %`);
    assert.ok(Number.isFinite(group.fold) && group.fold >= 0);
    const crossings = group.paths.slice(1, 3)
      .reduce((count, rail) => count + P.railHoles(rail).crossings.length, 0);
    if (group.fold > 0.9) {
      // a fold is a loop: it must cross itself somewhere, or the plate would hide nothing
      assert.ok(crossings > 0, `fold ${group.fold.toFixed(2)} with no crossing to mark`);
    }
    assert.equal(group.buckles, group.fold > 0.9 + 1e-9, "buckles must state the measured fold");
  });
}

test("c-0001 at the operator's preset keeps a band and marks its crossings", () => {
  // The 2026-11-21 fault was a band cut to 1.28 x the fold limit at the loop. The guard is
  // withdrawn (2026-11-23), so the check is now the new law's: the band exists, it is the
  // asked 1 %, and the rail's crossings are found so the plate can dot them.
  const group = groupAt("c-0001", 1, 2.5, 0.1);
  assert.ok(group.width > 0, "the band must exist");
  assert.ok(Math.abs(group.width - 1) < 0.2, `drew ${group.width} %, asked 1 %`);
  assert.ok(group.paths.length >= 3);
  const crossings = group.paths.slice(1, 3)
    .reduce((count, rail) => count + P.railHoles(rail).crossings.length, 0);
  assert.ok(crossings > 0, "c-0001 crosses itself at the preset; the plate must dot it");
  assert.ok(Number.isFinite(group.fold), "the fold is measured, not hidden");
});
