import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import P from "../../workbench/plate_math.js";

// c-0416 (cruciform) stored its four branches end to end in one `path`, with a jump of 0.56 of
// the curve's size between them. Drawn as one polyline, every jump became a chord and the
// figure read as fragments. The rule now lives in `branchesOf` and every drawing asks it first:
// one group per branch, never a line across a jump.

const registry = JSON.parse(readFileSync(new URL("../../workbench/curve-registry.json", import.meta.url)));
const byUid = new Map(registry.curves.map((row) => [row.uid, row]));

const sizeOf = (points) => {
  const xs = points.map((p) => p[0]), ys = points.map((p) => p[1]);
  return Math.hypot(Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys)) || 1;
};

const longestStep = (points) => {
  let worst = 0;
  for (let i = 1; i < points.length; i += 1) {
    worst = Math.max(worst, Math.hypot(points[i][0] - points[i - 1][0], points[i][1] - points[i - 1][1]));
  }
  return worst;
};

test("c-0416 is four branches, and no branch carries the jump between them", () => {
  const record = byUid.get("c-0416");
  const branches = P.branchesOf(record);
  assert.equal(branches.length, 4, `split into ${branches.length} branches, not 4`);
  const size = sizeOf(record.path);
  for (const branch of branches) {
    assert.ok(branch.length > 2);
    assert.ok(longestStep(branch) < 0.25 * size,
      `a branch still carries a step of ${(longestStep(branch) / size).toFixed(2)} of the size`);
  }
});

test("a record with stored branches uses them, and a single path stays one branch", () => {
  assert.equal(P.branchesOf(byUid.get("c-0402")).length, 2);
  assert.equal(P.branchesOf(byUid.get("c-0418")).length, 1);
  assert.equal(P.branchesOf(byUid.get("c-0273")).length, 1);
});

test("the splatted path and the branch list agree on the geometry", () => {
  const record = byUid.get("c-0416");
  const branches = P.branchesOf(record);
  const key = (point) => `${point[0].toFixed(6)},${point[1].toFixed(6)}`;
  const fromPath = new Set(record.path.map(key));
  for (const branch of branches) {
    for (const point of branch) assert.ok(fromPath.has(key(point)), "a branch point is not the stored one");
  }
});
