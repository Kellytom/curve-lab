import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import P from "../../workbench/plate_math.js";
import { symmetricStrength } from "../../scripts/lib/plate-row.mjs";

// The operator, 2026-11-21: "the offset curves should look the same on both sides of the
// curve, not thin on the right and wide on the left ... they should start at different x and
// y ... if the difference at the end is 10x 10y, then move the starting position by 5 x and
// 5 y to balance." The two sides take the average strength; the profile is zero at both ends,
// so the start and end gaps are the base, not a scale about the origin.

const registry = JSON.parse(readFileSync(new URL("../../workbench/curve-registry.json", import.meta.url)));
const curve = registry.curves.find((row) => row.uid === "c-0001");

test("the two sides take the average of the saved plus and minus", () => {
  assert.equal(symmetricStrength(2.5, 0.1), 1.3);
  assert.equal(symmetricStrength(2, 2), 2);
  assert.equal(symmetricStrength(0, 0), 0);
});

test("the offset curves are equidistant from the spine, station for station", () => {
  const strength = symmetricStrength(2.5, 0.1);
  const group = P.group({
    name: curve.name, speedX: curve.speedX, speedY: curve.speedY,
    width: { percent: 1 }, character: { plus: strength, minus: strength, profile: "bow" },
  });
  const [spine, plusRail, minusRail] = group.paths;
  assert.ok(spine && plusRail && minusRail, "spine and two offset curves");
  for (let i = 0; i < spine.length; i += 1) {
    const plus = Math.hypot(plusRail[i][0] - spine[i][0], plusRail[i][1] - spine[i][1]);
    const minus = Math.hypot(minusRail[i][0] - spine[i][0], minusRail[i][1] - spine[i][1]);
    assert.ok(Math.abs(plus - minus) < 1e-9, `side gaps differ at station ${i}: ${plus} vs ${minus}`);
  }
});

test("the start and end gaps are the same, so the ends balance", () => {
  // The operator: "if the difference at the end is 10x 10y, then move the starting position by
  // 5 x and 5 y to balance." With the bow profile zero at both ends, the two sides start and
  // end at the base gap; the start and the end match, and the next session moves the curve's
  // starting point where they do not.
  const strength = symmetricStrength(2.5, 0.1);
  const group = P.group({
    name: curve.name, speedX: curve.speedX, speedY: curve.speedY,
    width: { percent: 1 }, character: { plus: strength, minus: strength, profile: "bow" },
  });
  const [spine, plusRail, minusRail] = group.paths;
  const gap = (rail, i) => Math.hypot(rail[i][0] - spine[i][0], rail[i][1] - spine[i][1]);
  const end = spine.length - 1;
  for (const [name, rail] of [["plus", plusRail], ["minus", minusRail]]) {
    assert.ok(Math.abs(gap(rail, 0) - gap(rail, end)) < 1e-6,
      `${name}: start gap ${gap(rail, 0)} vs end gap ${gap(rail, end)}`);
  }
  assert.ok(Math.abs(gap(plusRail, 0) - gap(minusRail, 0)) < 1e-9, "the two start gaps differ");
  assert.ok(Math.abs(gap(plusRail, end) - gap(minusRail, end)) < 1e-9, "the two end gaps differ");
});
