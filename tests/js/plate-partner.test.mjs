import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { partnersOf } from "../../scripts/lib/plate-partner.mjs";

// docs/SIDE-CURVES.md §1 and §5: a side curve is the same construction with one parameter
// shifted, not a parallel offset. For the stored families the shifted parameter is the
// scale about the origin; the operator, 2026-11-21: "c-0273 to whatever are wrong wrong
// wrong ... give the offset curves as they should be."

const path = [[1, 2], [-1, 0.5], [0.25, -0.75]];

test("the partners are the same path scaled about the origin", () => {
  const { right, left } = partnersOf(path, 0.04);
  path.forEach(([x, y], i) => {
    assert.ok(Math.abs(right[i][0] - x * 0.96) < 1e-12);
    assert.ok(Math.abs(right[i][1] - y * 0.96) < 1e-12);
    assert.ok(Math.abs(left[i][0] - x * 1.04) < 1e-12);
    assert.ok(Math.abs(left[i][1] - y * 1.04) < 1e-12);
  });
});

test("the origin stays fixed and the sides do not cross", () => {
  const pathWithOrigin = [[0, 0], [1, 1], [-1, 0.5]];
  const { right, left } = partnersOf(pathWithOrigin, 0.04);
  assert.deepEqual(right[0], [0, 0]);
  assert.deepEqual(left[0], [0, 0]);
  // along each ray from the origin the right is inside the left
  for (let i = 1; i < pathWithOrigin.length; i += 1) {
    const r = Math.hypot(...right[i]);
    const l = Math.hypot(...left[i]);
    assert.ok(r < l, "the right partner is inside the left");
  }
});

test("a real stored double scales cleanly at the plate's preset", () => {
  const registry = JSON.parse(readFileSync(new URL("../../workbench/curve-registry.json", import.meta.url)));
  const curve = registry.curves.find((row) => Array.isArray(row.path) && row.path.length > 2);
  assert.ok(curve, "a stored path is needed");
  const { right, left } = partnersOf(curve.path, 0.01);
  assert.equal(right.length, curve.path.length);
  assert.equal(left.length, curve.path.length);
  for (let i = 0; i < curve.path.length; i += 1) {
    const [x, y] = curve.path[i];
    assert.ok(Math.abs(right[i][0] - x * 0.99) < 1e-12);
    assert.ok(Math.abs(left[i][1] - y * 1.01) < 1e-12);
  }
});
