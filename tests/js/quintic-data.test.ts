/**
 * The shared contract, checked — `curve-lab.quintic/1`.
 *
 * These assertions are the agreement between the two workstreams:
 *
 *   - DeepSeek1 writes `workbench/quintic-guides.json` (scripts/quintic-guides.ts)
 *   - DeepSeek2's Inkscape extension reads spans and frames from the same shape
 *   - `format/quintic.schema.json` is the written form; this file is the runnable form
 *
 * Both sides run this. If it goes red, the data has drifted from the contract and
 * the fix belongs in the generator, not in a reader that "copes".
 *
 * Run: node --test tests/js/quintic-data.test.ts
 */
import { test, describe } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const DATA = path.join(ROOT, "workbench", "quintic-guides.json");
const SCHEMA = path.join(ROOT, "format", "quintic.schema.json");

const load = () => JSON.parse(readFileSync(DATA, "utf8"));

describe("quintic data contract", () => {
  test("the schema file exists and declares the same format id", () => {
    assert.ok(existsSync(SCHEMA), "format/quintic.schema.json is missing");
    const schema = JSON.parse(readFileSync(SCHEMA, "utf8"));
    assert.equal(schema.$id, "https://curve-lab/format/quintic/1");
  });

  test("the data declares its own format, degree and count", () => {
    const data = load();
    assert.equal(data.format, "curve-lab.quintic/1");
    assert.equal(data.degree, 5);
    assert.equal(data.count, data.curves.length);
    assert.equal(data.axes.y, "up", "the house rule: positive y points up");
    assert.equal(data.axes.x, "right");
  });

  test("every curve has a span list, a join list and a closed flag", () => {
    for (const c of load().curves) {
      assert.ok(Array.isArray(c.spans) && c.spans.length >= 1, `${c.uid} has no spans`);
      assert.ok(Array.isArray(c.joins), `${c.uid} has no joins array`);
      assert.equal(typeof c.closed, "boolean", `${c.uid} closed is not a boolean`);
      assert.ok(["math", "ornament"].includes(c.group), `${c.uid} has an unknown group`);
    }
  });

  test("uids are unique across curves and spans", () => {
    const data = load();
    const curveIds = new Set(data.curves.map((c: any) => c.uid));
    assert.equal(curveIds.size, data.curves.length, "duplicate curve uid");
    const spanIds = new Set(data.curves.flatMap((c: any) => c.spans.map((s: any) => s.uid)));
    assert.equal(spanIds.size, data.curves.reduce((n: number, c: any) => n + c.spans.length, 0), "duplicate span uid");
  });

  test("every span is one quintic with six integer points", () => {
    for (const c of load().curves) {
      for (const s of c.spans) {
        assert.equal(s.kind, "quintic", `${s.uid} is not a quintic`);
        assert.equal(s.points.length, 6, `${s.uid} has ${s.points.length} points`);
        for (const [x, y] of s.points) {
          assert.ok(Number.isInteger(x) && Number.isInteger(y), `${s.uid} has a non-integer point`);
        }
        assert.equal(s.weights, null, `${s.uid} carries weights, which the contract has not opened yet`);
      }
    }
  });

  test("the frame is measured from the points, never invented", () => {
    for (const c of load().curves) {
      for (const s of c.spans) {
        const p = s.points;
        assert.deepEqual(s.frame.start.p, p[0], `${s.uid} frame.start.p is not P0`);
        assert.deepEqual(s.frame.end.p, p[5], `${s.uid} frame.end.p is not P5`);
        assert.deepEqual(
          s.frame.start.tangent,
          [p[1][0] - p[0][0], p[1][1] - p[0][1]],
          `${s.uid} start tangent is not P1 - P0`,
        );
        assert.deepEqual(
          s.frame.end.tangent,
          [p[5][0] - p[4][0], p[5][1] - p[4][1]],
          `${s.uid} end tangent is not P5 - P4`,
        );
      }
    }
  });

  test("a closed curve ends where it starts; an open one does not have to", () => {
    for (const c of load().curves) {
      if (!c.closed) continue;
      const first = c.spans[0].points[0];
      const last = c.spans[c.spans.length - 1].points[5];
      assert.deepEqual(last, first, `${c.uid} is closed but does not meet itself`);
    }
  });

  test("both groups are present and each has 100 curves", () => {
    const data = load();
    const count = (g: string) => data.curves.filter((c: any) => c.group === g).length;
    assert.equal(count("math"), 100);
    assert.equal(count("ornament"), 100);
  });
});
