import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { mirrorPair, parseFraction, parseRange, recommendTrim, trimRun, trimRecord, TRIM_PAIRS } from "../../app/src/lib/trim-curve.ts";

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

test("a preset's other end is (q − p)/q, ordered", () => {
  assert.deepEqual(mirrorPair("200/10001"), { from: "200/10001", to: "9801/10001" });
  assert.deepEqual(mirrorPair("1/4"), { from: "1/4", to: "3/4" });
  assert.deepEqual(mirrorPair("3/5"), { from: "2/5", to: "3/5" }, "the pair is ordered");
  assert.deepEqual(mirrorPair("1/17"), { from: "1/17", to: "16/17" });
  assert.deepEqual(mirrorPair("1/2"), { from: "1/2", to: "1/2" }, "half mirrors to itself");
});

test("a leg is the constant-curvature run at the end, and the suggestion clears it", () => {
  // a straight tail into a tight loop: the curvature is flat on the tail, then breaks
  const pts: [number, number][] = [];
  for (let i = 0; i <= 60; i += 1) pts.push([-1 + i * 0.01, 0]);
  for (let i = 0; i <= 120; i += 1) {
    const a = (i / 120) * Math.PI * 2;
    pts.push([0.2 * Math.cos(a), 0.2 * Math.sin(a)]);
  }
  const rec = recommendTrim(pts);
  assert.ok(rec, "a curve with a leg and a loop has a suggestion");
  const share = Math.max(rec.broke.front, rec.broke.back);
  assert.ok(share > 0.2, `the leg is most of the straight tail, got ${share}`);
  const [p, q] = rec.from.split("/").map(Number);
  assert.equal(rec.to, `${q - p}/${q}`, "the suggestion's other end is the mirror");
  assert.ok(p / q >= Math.max(0, share - 0.005), "the cut clears the measured leg");
  assert.ok(p / q <= share + 0.15, "and is not far past it");
});

test("every suggestion fraction has a p-triple hypotenuse for its denominator", () => {
  const hyp = new Set([5, 13, 17, 25, 29, 37, 41, 53, 61, 65, 73, 85, 89, 97, 101, 109, 113,
    125, 137, 149, 157, 169, 173, 181, 185, 193, 197, 10001]);
  for (const [, q] of TRIM_PAIRS) assert.ok(hyp.has(q), `${q} is not a hypotenuse`);
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
