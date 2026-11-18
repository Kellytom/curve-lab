import assert from "node:assert/strict";
import test from "node:test";
import { validateFinderStars } from "../src/lib/finder-stars.js";

test("a malformed payload is refused before the database sees it", () => {
  assert.throws(() => validateFinderStars({ curves: [{ name: "" }] }));
  assert.throws(() => validateFinderStars({ nope: [] }));
});

test("the same curve twice is merged, not refused", () => {
  const stars = validateFinderStars({
    curves: [{ name: "loop t=1/2,3/4" }, { name: "loop t=1/2,3/4", note: "x" }, { name: "cross 2/5-4/5" }],
  });
  assert.equal(stars.length, 2);
  assert.equal(stars[0].note, "x");
});

test("a note and a spec survive validation", () => {
  const [star] = validateFinderStars({ curves: [{ name: "a", note: "keep", spec: { d: "1" } }] });
  assert.equal(star.note, "keep");
  assert.deepEqual(star.spec, { d: "1" });
});
