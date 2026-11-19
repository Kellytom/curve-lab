import assert from "node:assert/strict";
import test from "node:test";
import { composeName, splitName } from "../src/lib/name-parts.js";

test("a construction with no variant is a name on its own", () => {
  assert.equal(composeName({ prefix: "amper", core: "", postfix: "" }), "amper");
  assert.equal(composeName({ prefix: "swan", core: "  ", postfix: "" }), "swan");
});

test("a variant with no middle keeps its postfix", () => {
  assert.equal(composeName({ prefix: "knot", core: "", postfix: "6" }), "knot-6");
  assert.equal(composeName({ prefix: "inflect", core: "", postfix: "2" }), "inflect-2");
});

test("three parts join with one dash, and stray dashes do not double", () => {
  assert.equal(composeName({ prefix: "lace", core: "1of8", postfix: "3" }), "lace-1of8-3");
  assert.equal(composeName({ prefix: "lace-", core: "1of8", postfix: "-3" }), "lace-1of8-3");
});

test("nothing at all composes to nothing, so Save can still refuse", () => {
  assert.equal(composeName({ prefix: "", core: "", postfix: "" }), "");
  assert.equal(composeName(), "");
});

test("splitting a stored name gives back the same name", () => {
  for (const [name, family] of [
    ["lace-1of8-3", "lace"],
    ["knot-6", "knot"],
    ["amper", "amper"],
    ["u-bowl", "u"],
    ["mobile-exact-1-1of2-1of5-1-2-5", "mobile-exact"],
  ]) {
    const parts = splitName(name, family);
    assert.equal(composeName(parts), name, `${name} did not round trip`);
  }
});

test("an old draft never hides a newer saved name", async () => {
  const { draftState } = await import("../src/lib/name-parts.js");
  const savedAt = Date.parse("2026-11-19T01:01:00Z");
  assert.deepEqual(draftState("45deg-t1of4", savedAt), { value: "45deg-t1of4", stale: true });
  assert.deepEqual(draftState({ value: "old", at: savedAt - 1000 }, savedAt).stale, true);
  assert.deepEqual(draftState({ value: "typed now", at: savedAt + 1000 }, savedAt), { value: "typed now", stale: false });
});

test("an empty draft is not a draft", async () => {
  const { draftState } = await import("../src/lib/name-parts.js");
  assert.equal(draftState("", 0).value, undefined);
  assert.equal(draftState({ value: "", at: Date.now() }, 0).value, undefined);
});
