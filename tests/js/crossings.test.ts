import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { crossingPairs, type Point } from "../../app/src/lib/crossings.ts";

// The TypeScript twin of curve_lab/crossings.py: the grid counter must give exactly the brute
// force answer, and a triple point is three pairs, not one place.

const brute = (points: Point[]): number => {
  const meet = (i: number, j: number): boolean => {
    const [ax, ay] = points[i];
    const [bx, by] = points[i + 1];
    const [cx, cy] = points[j];
    const [dx, dy] = points[j + 1];
    const denominator = (bx - ax) * (dy - cy) - (by - ay) * (dx - cx);
    if (Math.abs(denominator) < 1e-12) return false;
    const s = ((cx - ax) * (dy - cy) - (cy - ay) * (dx - cx)) / denominator;
    const u = ((cx - ax) * (by - ay) - (cy - ay) * (bx - ax)) / denominator;
    return s > 0 && s < 1 && u > 0 && u < 1;
  };
  let count = 0;
  for (let i = 0; i < points.length - 3; i += 1) {
    for (let j = i + 2; j < points.length - 1; j += 1) {
      if (meet(i, j)) count += 1;
    }
  }
  return count;
};

// a small deterministic walk, enough to exercise the grid and the strict test
const walk = (seed: number, n = 30): Point[] => {
  let state = seed;
  const random = (): number => {
    state = (state * 1664525 + 1013904223) % 4294967296;
    return state / 4294967296;
  };
  const points: Point[] = [[0, 0]];
  for (let i = 1; i < n; i += 1) points.push([random(), random()]);
  return points;
};

test("random polylines: the grid counter equals the brute force", () => {
  for (let seed = 1; seed <= 50; seed += 1) {
    const points = walk(seed);
    assert.equal(crossingPairs(points), brute(points), `seed ${seed}`);
  }
});

test("a figure eight has one crossing pair", () => {
  const eight: Point[] = [[-1, -1], [1, 1], [1, -1], [-1, 1]];
  // the two diagonals cross once, strictly inside both segments
  assert.equal(crossingPairs(eight), 1);
});

test("a triple point is three pairs", () => {
  const triple: Point[] = [[-1, 0], [1, 0], [1, 1], [-1, -1], [-1, 2], [1, -2]];
  assert.equal(crossingPairs(triple), 3);
});

test("the stored path records agree with the Python counter's pinned numbers", () => {
  const registry = JSON.parse(readFileSync(new URL("../../workbench/curve-registry.json", import.meta.url), "utf8"));
  const pinned: Record<string, number> = { "c-0273": 0, "c-0288": 0, "c-0274": 0 };
  for (const [uid, expected] of Object.entries(pinned)) {
    const record = registry.curves.find((curve: { uid: string }) => curve.uid === uid);
    assert.ok(record?.path?.length > 2, `${uid} has no stored path`);
    const points: Point[] = record.path.map(([x, y]: [number, number]) => [x, y]);
    assert.equal(crossingPairs(points), expected, `${uid}`);
  }
});
