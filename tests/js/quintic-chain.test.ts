/**
 * The chain's own guard.
 *
 * `scripts/quintic-chain.ts` places spans by rigid motion, so G1 is exact by
 * construction. If a join ever reports a position or tangent residual, the
 * placement code is wrong, not the data. The first join is the classical
 * compound moulding — cyma reversa into cyma recta — and it is G3; that is a
 * measured fact, and this test keeps it measured.
 *
 * Run: node --test tests/js/quintic-chain.test.ts
 */
import { test, describe } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const CHAIN = JSON.parse(readFileSync(path.join(ROOT, "workbench", "quintic-chain.json"), "utf8"));

describe("quintic chain", () => {
  test("four spans, three joins", () => {
    assert.equal(CHAIN.chain.length, 4);
    assert.equal(CHAIN.joins.length, 3);
  });

  test("every join meets in position and tangent", () => {
    for (const j of CHAIN.joins) {
      assert.ok(j.residual.position < 1e-9, `${j.uid} has a position gap of ${j.residual.position}`);
      assert.ok(j.residual.tangentDegrees < 1e-6, `${j.uid} has a tangent gap of ${j.residual.tangentDegrees} degrees`);
    }
  });

  test("the cyma reversa into cyma recta join is G3", () => {
    const first = CHAIN.joins[0];
    assert.equal(first.continuity, "G3", "the compound moulding pair is no longer G3");
    assert.ok(first.relative.kappa < 0.01, `kappa jump ${first.relative.kappa}`);
    assert.ok(first.relative.rate < 0.05, `rate jump ${first.relative.rate}`);
  });

  test("the joins that are not G3 say so, with their number", () => {
    for (const j of CHAIN.joins.slice(1)) {
      assert.equal(j.continuity, "G1");
      assert.ok(j.relative.kappa > 0.01, `${j.uid} claims G1 but the curvature jump is ${j.relative.kappa}`);
    }
  });

  test("the placed spans keep six points each", () => {
    for (const s of CHAIN.chain) {
      assert.equal(s.points.length, 6);
      assert.ok(s.points.every((p: number[]) => p.length === 2 && p.every(Number.isFinite)));
    }
  });
});
