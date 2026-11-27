/**
 * The closed ring's guard — the `closed: true` branch of the shared contract.
 *
 * Run: node --test tests/js/quintic-closed.test.ts
 */
import { test, describe } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const DATA = JSON.parse(readFileSync(path.join(ROOT, "workbench", "quintic-closed.json"), "utf8"));
const ring = DATA.curves[0];

describe("closed ring", () => {
  test("it is one closed curve with a winding", () => {
    assert.equal(DATA.count, 1);
    assert.equal(ring.closed, true);
    assert.ok(["ccw", "cw"].includes(ring.winding));
  });

  test("four spans, four joins", () => {
    assert.equal(ring.spans.length, 4);
    assert.equal(ring.joins.length, 4);
  });

  test("it closes: the last span ends where the first starts", () => {
    assert.deepEqual(ring.spans[3].points[5], ring.spans[0].points[0]);
  });

  test("every join meets in position and tangent", () => {
    for (const j of ring.joins) {
      assert.ok(j.residual.position < 1e-9, `${j.uid} gap ${j.residual.position}`);
      assert.ok(j.residual.tangentDegrees < 1e-6, `${j.uid} angle ${j.residual.tangentDegrees}`);
    }
  });

  test("the four rotations make the joins G3", () => {
    for (const j of ring.joins) assert.equal(j.continuity, "G3");
  });

  test("it is a circle of radius 60 to better than one grid unit", () => {
    assert.ok(ring.fitError < 1, `radial error ${ring.fitError}`);
  });

  test("every span is six integer points", () => {
    for (const s of ring.spans) {
      assert.equal(s.points.length, 6);
      assert.ok(s.points.every((p: number[]) => Number.isInteger(p[0]) && Number.isInteger(p[1])));
      assert.equal(s.weights, null);
    }
  });
});
