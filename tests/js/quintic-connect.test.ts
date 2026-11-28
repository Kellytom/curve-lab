/**
 * The solved chain's guard — G3 by construction, and measured anyway.
 *
 * `scripts/quintic-connect.ts` uses DeepSeek2's solver (`quinticControls` in
 * app/src/lib/glue.ts) and then re-measures every station and join from the six
 * control points. Two bugs in that solver were found while building this, and the
 * script works around both; this test keeps the chain honest either way.
 *
 *   1. `unitDirection` divides by the squared length instead of its root for any
 *      slope that is not a Pythagorean triple: slope 1 gives a vector of length
 *      0.707 and the curvature aimed for lands 2√2 too large. The script uses
 *      p-triple slopes only.
 *   2. `dkappa1` is taken along the reversed direction while `kappa1` is forward.
 *      Asking for −0.0001 at the end returned +0.0001. The script negates it.
 *
 * If either is fixed upstream, these tests still pass — the chain is what is
 * judged, not the workaround.
 *
 * Run: node --test tests/js/quintic-connect.test.ts
 */
import { test, describe } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const CHAIN = JSON.parse(readFileSync(path.join(ROOT, "workbench", "quintic-connect.json"), "utf8"));

describe("solved G3 chain", () => {
  test("three spans and two joins", () => {
    assert.equal(CHAIN.spans.length, 3);
    assert.equal(CHAIN.joins.length, 2);
  });

  test("every station is met: position, slope, curvature and its rate", () => {
    for (const s of CHAIN.stationErrors) {
      assert.ok(s.position < 1e-9, `station ${s.station} position ${s.position}`);
      assert.ok(s.slope < 1e-9, `station ${s.station} slope ${s.slope}`);
      assert.ok(s.kappa < 1e-9, `station ${s.station} kappa ${s.kappa}`);
      assert.ok(s.rate < 1e-9, `station ${s.station} rate ${s.rate}`);
    }
  });

  test("both joins are G3, with residuals at machine precision", () => {
    for (const j of CHAIN.joins) {
      assert.equal(j.continuity, "G3", `${j.uid} is ${j.continuity}`);
      assert.ok(j.residual.position < 1e-9, `${j.uid} position`);
      assert.ok(j.residual.tangentDegrees < 1e-9, `${j.uid} tangent`);
      assert.ok(j.residual.kappa < 1e-9, `${j.uid} kappa`);
      assert.ok(j.residual.rate < 1e-9, `${j.uid} rate`);
    }
  });

  test("the chain does not cross itself", () => {
    assert.equal(CHAIN.selfCrossings, 0);
  });

  test("every slope used is a Pythagorean direction, so the solver is exact", () => {
    for (const s of CHAIN.stations) {
      const x = s.slope.d;
      const y = s.slope.n;
      const root = Math.round(Math.sqrt(x * x + y * y));
      assert.equal(root * root, x * x + y * y, `slope ${y}/${x} is not a p-triple`);
    }
  });

  test("each span is six points", () => {
    for (const s of CHAIN.spans) {
      assert.equal(s.points.length, 6);
      assert.ok(s.points.every((p: number[]) => p.every(Number.isFinite)));
    }
  });
});
