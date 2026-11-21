// Why a curve is on the plates page. The operator, 2026-11-21: "put the curves with
// stars? just dont put the ones with 1 star." These tests pin the filter and the sentence.

import test from "node:test";
import assert from "node:assert/strict";
import { isKept, provenanceFor, starsLabel, starsOf, MIN_STARS } from "../src/lib/provenance.js";

const base = (over = {}) => ({
  uid: "c-0001", name: "amper", importance: 5, family: "amper", note: "", ...over,
});
const parent = base();
const variant = (over = {}) => base({
  uid: "c-0001a", name: "amper-thin", importance: 0,
  params: { variantOf: "c-0001" },
  note: "variant of c-0001 (amper) · width 1% · bow plus 2.5 minus 0.1 · turn 0", ...over,
});
const byUid = new Map([[parent.uid, parent], ["c-0001a", variant()]]);

test("two stars are kept, one star and no stars are not", () => {
  assert.equal(MIN_STARS, 2);
  assert.equal(isKept(base({ importance: 2 }), byUid), true);
  assert.equal(isKept(base({ importance: 1 }), byUid), false);
  assert.equal(isKept(base({ importance: 0 }), byUid), false);
});

test("a variant joins a kept parent, even with no stars of its own", () => {
  assert.equal(isKept(variant(), byUid), true);
  const weak = base({ uid: "c-0002", importance: 1 });
  const map = new Map([[weak.uid, weak], ["c-0002a", base({ uid: "c-0002a", importance: 0, params: { variantOf: "c-0002" } })]]);
  assert.equal(isKept(map.get("c-0002a"), map), false);
});

test("the sentence starts with the rating or the parent", () => {
  assert.match(provenanceFor(parent, byUid), /^Chosen at 5\/10/);
  assert.match(provenanceFor(variant(), byUid), /^Variant of c-0001 \(amper, 5\/10\)/);
});

test("a variant's note is not repeated and stays one line", () => {
  const sentence = provenanceFor(variant(), byUid);
  assert.equal((sentence.match(/variant of/gi) || []).length, 1, sentence);
  assert.ok(sentence.includes("width 1%"), sentence);
  const messy = provenanceFor(base({ note: "line one\n  line   two" }), byUid);
  assert.ok(!messy.includes("\n"), messy);
  assert.match(messy, /line one line two\.$/);
});

test("a note is the proof when there is one; the formula is the fallback", () => {
  assert.ok(provenanceFor(base({ note: "DW: the mirrored half" }), byUid).includes("DW: the mirrored half"));
  assert.ok(provenanceFor(base({ formula: { plain: "x = t^2, y = t^3" } }), byUid).includes("x = t^2, y = t^3"));
  const bare = provenanceFor(base({ family: "amper", name: "amper", source: "found" }), byUid);
  assert.ok(bare.includes("found in the finder"), bare);
  assert.ok(!bare.includes("amper family"), "a family equal to the name proves nothing");
});

test("every curve states its stars, or none", () => {
  assert.equal(starsLabel(5), "5/10");
  assert.equal(starsLabel(null), "none");
  assert.equal(starsOf({ stars: 4, importance: 0 }), 4, "the explicit star value wins");
  assert.equal(starsOf({ stars: null, importance: 9 }), 0, "none is not a stored rating");
});
