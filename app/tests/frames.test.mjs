// The frame variants: swan takes the corner rule with a residual under 1°, a
// 135° curve stops, and C and D are different rows from A.

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { figureFor, svgForFigure } from "../src/lib/bordered.js";

const frames = JSON.parse(
  readFileSync(new URL("../../workbench/frames.json", import.meta.url), "utf8"),
);
const registry = JSON.parse(
  readFileSync(new URL("../../workbench/curve-registry.json", import.meta.url), "utf8"),
);
const byUid = new Map(registry.curves.map((curve) => [curve.uid, curve]));
const rows = frames.curves || [];
const swan = rows.filter((row) => row.name === "swan");
const svgFor = (row) => svgForFigure(
  figureFor({ ...byUid.get(row.uid), ...row }, {}, null),
  row.illus,
);

test("swan gets the corner rule with a residual under 1°", () => {
  const a = swan.find((row) => row.variant === "A");
  assert.ok(a, "swan is not in frames.json");
  assert.equal(a.cornerRule, "corner");
  assert.ok(a.cornerGap < 1, `swan cornerGap ${a.cornerGap}`);
});

test("a 135° curve stops", () => {
  const stop = rows.find(
    (row) => row.variant === "A" && row.cornerRule === "stop" && row.delta >= 130 && row.delta <= 140,
  );
  assert.ok(stop, "no 135° stop row in frames.json");
  const c = rows.find((row) => row.uid === stop.uid && row.variant === "C");
  assert.ok(c, "the stop curve needs a C row");
  assert.notEqual(svgFor(stop), svgFor(c), "the stop rule draws differently from A");
});

test("C differs from A and D differs from C", () => {
  const a = swan.find((row) => row.variant === "A");
  const c = swan.find((row) => row.variant === "C");
  const d = swan.find((row) => row.variant === "D");
  assert.ok(a && c && d, "swan needs A, C and D");
  assert.notEqual(a.note, c.note);
  assert.notEqual(c.note, d.note);
  assert.equal(d.seam, "gap");
  assert.notEqual(svgFor(a), svgFor(c), "C draws differently from A");
});
