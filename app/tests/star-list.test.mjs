import assert from "node:assert/strict";
import test from "node:test";
import { dedupeStars, starKey } from "../src/lib/star-list.js";

test("a curve starred twice by id is one star", () => {
  const list = [{ id: "septic-1", name: "loop" }, { id: "septic-1", name: "loop" }];
  assert.equal(dedupeStars(list).length, 1);
});

test("an old name and a new id for the same curve collapse, and the id is kept", () => {
  const nameToId = { "loop t=1/2,3/4": "septic-65ba9eb9" };
  const list = [{ name: "loop t=1/2,3/4" }, { id: "septic-65ba9eb9", name: "loop t=1/2,3/4 (renamed)" }];
  const out = dedupeStars(list, nameToId);
  assert.equal(out.length, 1);
  assert.equal(out[0].id, "septic-65ba9eb9");
});

test("a name that no longer maps keeps its own star instead of vanishing", () => {
  const list = [{ name: "a curve from an older finder run" }];
  const out = dedupeStars(list, {});
  assert.equal(out.length, 1);
  assert.equal(starKey(out[0], {}), "name:a curve from an older finder run");
});

test("different curves stay different, in the order they were starred", () => {
  const list = [{ id: "a" }, { id: "b" }, { name: "c" }];
  assert.deepEqual(dedupeStars(list).map((star) => star.id || star.name), ["a", "b", "c"]);
});

test("an entry with neither id nor name is dropped", () => {
  assert.deepEqual(dedupeStars([{}, null, { id: "a" }]).map((star) => star.id), ["a"]);
});
