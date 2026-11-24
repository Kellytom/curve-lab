import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { trace, symmetryGap } from "../../app/src/lib/coupler-curves.ts";
import { crossingPairs } from "../../app/src/lib/crossings.ts";

// The TypeScript twin of scripts/coupler_curves.py. The committed coupler-curves.json was
// written by the Python for the default integer grid; the pinned rows must reproduce it.

const committed = JSON.parse(readFileSync(new URL("../../workbench/coupler-curves.json", import.meta.url), "utf8")) as {
  curves: Array<{
    r2: number; r3: number; r4: number; d: number; a: number; b: number;
    crossings: number; mirror: number; points: Array<[number, number]>;
  }>;
};

test("the committed set is 20 rows, ranked by crossings then mirror", () => {
  const rows = committed.curves;
  assert.ok(rows.length > 0 && rows.length <= 20);
  for (let i = 1; i < rows.length; i += 1) {
    const a = rows[i - 1], b = rows[i];
    assert.ok(a.crossings > b.crossings
      || (a.crossings === b.crossings && a.mirror <= b.mirror), `rows ${i - 1} and ${i} are out of order`);
  }
});

test("the top three pinned traces reproduce the committed rows", () => {
  for (const expected of committed.curves.slice(0, 3)) {
    const points = trace(expected.r2, expected.r3, expected.r4, expected.d, expected.a, expected.b);
    assert.equal(points.length, expected.points.length, "the trace length");
    assert.equal(crossingPairs(points), expected.crossings, "the crossing pairs");
    assert.ok(Math.abs(symmetryGap(points) - expected.mirror) < 1e-9, "the mirror gap");
    for (const [index, key] of [[0, "first"], [points.length - 1, "last"]] as const) {
      const actual = points[index], wanted = expected.points[index];
      assert.ok(Math.abs(actual[0] - wanted[0]) < 1e-3 && Math.abs(actual[1] - wanted[1]) < 1e-3,
        `${key} point: ${actual} vs ${wanted}`);
    }
  }
});
