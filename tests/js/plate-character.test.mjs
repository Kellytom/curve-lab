import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import P from "../../workbench/plate_math.js";

// a real stored curve, so the rail has curvature to work with
const registry = JSON.parse(readFileSync(new URL("../../workbench/curve-registry.json", import.meta.url)));
const curve = registry.curves.find((row) => row.name === "curlicue");

// A character rail is not a parallel offset: its shape changes with plus, minus and the
// profile, at the same width. These tests fail if a plate ever falls back to a plain offset.

const base = () => ({
  name: curve.name,
  speedX: curve.speedX,
  speedY: curve.speedY,
  width: { percent: 6 },
  character: { plus: 2, minus: 2, profile: "bow" },
});

const railOf = (row) => {
  const group = P.group(row);
  assert.ok(group.paths.length >= 3, "spine and two rails expected");
  return group.paths[1];
};

test("plus changes the rail at the same width", () => {
  const a = base(); const b = base();
  b.character.plus = 6;
  assert.notDeepEqual(railOf(a), railOf(b));
});

test("minus changes the other side, not this one", () => {
  // The + rail is built from plus alone. The width, though, is the largest that clears the
  // fold on BOTH sides (register 51), so 1 % is used here: at the base 6 % the
  // guard binds and a larger minus narrows the whole band, which is the guard working, not
  // this rail reading minus.
  const a = { ...base(), width: { percent: 1 } };
  const b = { ...base(), width: { percent: 1 }, character: { ...base().character, minus: 6 } };
  assert.deepEqual(railOf(a), railOf(b), "the + rail's own law reads plus, not minus");
});

test("the profile changes the rail", () => {
  const a = base(); const b = base();
  b.character.profile = "s";
  assert.notDeepEqual(railOf(a), railOf(b));
});
