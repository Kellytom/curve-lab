import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { analyse, stableCrossings, type CurveRecord } from "../../app/src/lib/curve-analysis.ts";

// The TypeScript analysis must reproduce the committed curve-analysis.json row for row on the
// records it is proved on here; the whole-file parity is `scripts/analyse_curves.ts --out`.

const registry = JSON.parse(readFileSync(new URL("../../workbench/curve-registry.json", import.meta.url), "utf8")) as {
  curves: CurveRecord[];
};
const committed = JSON.parse(readFileSync(new URL("../../workbench/curve-analysis.json", import.meta.url), "utf8")) as {
  curves: Array<Record<string, unknown>>;
};
const byUid = new Map(committed.curves.map((row) => [row.uid, row]));
const recordOf = (uid: string): CurveRecord => {
  const record = registry.curves.find((row) => row.uid === uid);
  assert.ok(record, `${uid} is not in the registry`);
  return record;
};

test("a rows curve, a path curve, a Tschirnhausen and a classical shape match the JSON", () => {
  for (const uid of ["c-0022", "c-0273", "c-0398", "c-0402", "c-0134", "c-0426"]) {
    const expected = byUid.get(uid);
    assert.ok(expected, `${uid} has no committed analysis row`);
    assert.deepEqual(analyse(recordOf(uid)), expected, uid);
  }
});

test("the crossing count is the stable pair count, not a place count", () => {
  const record = recordOf("c-0262");
  assert.ok(record.speedX?.length);
  const hits = stableCrossings(record.speedX, record.speedY ?? []);
  assert.equal(hits.length, 9, `c-0262 has ${hits.length} pairs, the calibration pins 9`);
});
