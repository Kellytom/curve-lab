import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { parseFraction, parseRange, trimRun, trimRecord } from "../../app/src/lib/trim-curve.ts";

// The operator, 2026-11-24: "cutting the legs off the curves using rational fractions of t".
// t = 0 is the first station, t = 1 the last; the cut is p/q, and the stations between the two
// cuts are kept. The legs are dropped, and the two cut points sit exactly at the fractions.

const registry = JSON.parse(readFileSync(new URL("../../workbench/curve-registry.json", import.meta.url)));

test("a fraction is whole numbers, inside 0 … 1, and a decimal is refused", () => {
  assert.equal(parseFraction("1/4").value, 0.25);
  assert.equal(parseFraction("1").value, 1, "a whole t of 1 is the last station");
  assert.throws(() => parseFraction("3"), /past the end/);
  assert.throws(() => parseFraction("0.25"), /whole-number fraction/);
  assert.throws(() => parseFraction("3/2"), /past the end/);
  assert.throws(() => parseFraction("1/0"), /zero/);
  assert.throws(() => parseFraction(""), /type a fraction/);
  assert.equal(parseFraction("2/4").text, "1/2", "a fraction is shown in lowest terms");
  assert.equal(parseFraction("5/10").text, "1/2");
  assert.equal(parseFraction("0").text, "0");
  assert.equal(parseFraction("3/5").text, "3/5", "a p-triple fraction is already lowest terms");
});

test("the range refuses a front cut at or past the back cut", () => {
  assert.deepEqual([parseRange("1/4", "3/4").from.value, parseRange("1/4", "3/4").to.value], [0.25, 0.75]);
  assert.throws(() => parseRange("3/4", "1/4"), /must come before/);
  assert.throws(() => parseRange("1/2", "1/2"), /must come before/);
});

test("a straight run keeps the middle and puts the ends exactly on the fractions", () => {
  const line = [[0, 0], [1, 0], [2, 0], [3, 0], [4, 0]];
  const trimmed = trimRun(line, parseFraction("1/4"), parseFraction("3/4"));
  assert.deepEqual(trimmed.kept[0], [1, 0], "the front cut is exactly at 1/4 of the span");
  assert.deepEqual(trimmed.kept.at(-1), [3, 0]);
  assert.equal(trimmed.kept.length, 3, "one interior station survives between the cuts");
  assert.deepEqual(trimmed.head[0], [0, 0], "the dropped front leg starts at the original first point");
  assert.deepEqual(trimmed.tail.at(-1), [4, 0]);
  assert.deepEqual(trimmed.head.at(-1), trimmed.kept[0], "the leg ends where the kept run starts");
});

test("every branch is trimmed by the same fractions", () => {
  const record = registry.curves.find((curve) => curve.uid === "c-0416");
  assert.ok(record.branches && record.branches.length === 4);
  const trimmed = trimRecord(record, parseFraction("1/5"), parseFraction("4/5"));
  assert.equal(trimmed.branches.length, 4);
  assert.equal(trimmed.marks.length, 8, "every branch's front and back cuts are marked");
  assert.deepEqual(trimmed.marks.slice(0, 2).map((mark) => mark.cut), ["from", "to"]);
  for (const branch of trimmed.branches) {
    assert.ok(branch.length > 2);
    assert.notDeepEqual(branch[0], branch.at(-1));
  }
  assert.ok(trimmed.path.length > trimmed.branches.length * 2);
});

test("a cut leaves nothing to keep when the range is empty of stations", () => {
  const pair = [[0, 0], [1, 1]];
  const trimmed = trimRun(pair, parseFraction("1/10"), parseFraction("2/10"));
  assert.equal(trimmed.kept.length, 2, "the two exact ends are still a drawable piece");
  assert.deepEqual(trimmed.kept[0], [0.1, 0.1]);
  assert.deepEqual(trimmed.kept.at(-1), [0.2, 0.2]);
});
