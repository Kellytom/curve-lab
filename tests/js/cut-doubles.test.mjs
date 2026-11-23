import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { cuspsOf, cutAt, arcsAt, doublesOf, turnPoints } from "../../app/src/lib/cut-doubles.js";
import { turn as plateTurn } from "../../scripts/lib/plate-frame.mjs";

// The operator, 2026-11-23: "many of them i want to cut at the big blue dot." The big blue dot
// is the cusp the plate already marks; a cut there keeps the long arc and drops the lobe the
// cusp closes.

const registry = JSON.parse(readFileSync(new URL("../../workbench/curve-registry.json", import.meta.url)));

test("the doubles are found from their names and stored points", () => {
  const doubles = doublesOf(registry.curves);
  assert.ok(doubles.length >= 50, `${doubles.length} doubles found`);
  assert.ok(doubles.every((curve) => /^double-/i.test(curve.name)));
});

test("c-0288 has cusps, on the source stations", () => {
  const record = registry.curves.find((curve) => curve.uid === "c-0288");
  const cusps = cuspsOf(record.path);
  assert.ok(cusps.length > 0, "the plate draws blue dots here, so the desk must find them");
  for (const cusp of cusps) {
    assert.ok(cusp.angle > 165);
    assert.ok(cusp.index > 0 && cusp.index < record.path.length - 1);
  }
});

test("a cut at a cusp keeps the long arc and drops the lobe", () => {
  const record = registry.curves.find((curve) => curve.uid === "c-0288");
  const cusp = cuspsOf(record.path)[0];
  const cut = cutAt(record.path, cusp.index, "long");
  assert.ok(cut.keptLength >= cut.droppedLength);
  // both arcs start or end at the cusp: that is the dot the operator picks
  const ends = [cut.points[0], cut.points[cut.points.length - 1]];
  assert.ok(ends.some((point) =>
    Math.hypot(point[0] - cut.cusp[0], point[1] - cut.cusp[1]) < 1e-9), "the cut does not meet the cusp");
  assert.ok(cut.points.length > 2);
});

test("short keeps the other side of the same dot", () => {
  const record = registry.curves.find((curve) => curve.uid === "c-0288");
  const cusp = cuspsOf(record.path)[0];
  const long = cutAt(record.path, cusp.index, "long");
  const short = cutAt(record.path, cusp.index, "short");
  assert.ok(short.keptLength <= long.keptLength);
  assert.ok(short.points.length > 2);
  assert.notDeepEqual(short.points, long.points);
});

test("the desk turns a curve exactly as its plate does", () => {
  // The operator saw c-0274 at 45 degrees off: the desk drew the stored points unturned.
  const sample = [[1, 0], [0, 1], [3, -2], [-4, 5]];
  for (const degrees of [0, 45, 90, 135, 180, -45, 225]) {
    assert.deepEqual(turnPoints(sample, degrees), plateTurn(sample, degrees),
      `${degrees} degrees differs from the plate's turn`);
  }
  // and the sign is the plate's: a 90 degree desk turn sends (1, 0) to (0, -1)
  const [x, y] = turnPoints([[1, 0]], 90)[0];
  assert.ok(Math.abs(x) < 1e-12 && Math.abs(y + 1) < 1e-12, `(1,0) turned to ${x},${y}`);
});

test("the two arcs of a cusp add up to the whole path", () => {
  const record = registry.curves.find((curve) => curve.uid === "c-0418");
  const cusp = cuspsOf(record.path)[0] || { index: Math.floor(record.path.length / 2) };
  const arcs = arcsAt(record.path, cusp.index);
  assert.ok(arcs.head.length + arcs.tail.length >= record.path.length);
  assert.ok(Math.abs((arcs.headLength + arcs.tailLength) - arcs.headLength - arcs.tailLength) < 1e-9);
});
