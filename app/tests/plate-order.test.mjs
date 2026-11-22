// The plates order. The operator: "once we add the ten stars, we will be able to rearrange
// all the curves and their variations." These tests pin the two orders.

import test from "node:test";
import assert from "node:assert/strict";
import { orderPlates, baseUidOf } from "../src/lib/plate-order.js";

const curve = (uid, stars, extra = {}) => ({ uid, name: uid, stars, ...extra });
const variant = (uid, stars, parent) => curve(uid, stars, { params: { variantOf: parent } });

test("a variant knows its base", () => {
  assert.equal(baseUidOf(variant("c-0001a", 0, "c-0001")), "c-0001");
  assert.equal(baseUidOf(curve("c-0002", 3)), "c-0002");
});

test("the star order puts the best family first and keeps its variant beside it", () => {
  const rows = [curve("c-0002", 3), variant("c-0001a", 0, "c-0001"), curve("c-0001", 5),
                curve("c-0003", 4), variant("c-0001b", 2, "c-0001")];
  assert.deepEqual(orderPlates(rows).map((row) => row.uid),
    ["c-0001", "c-0001a", "c-0001b", "c-0003", "c-0002"]);
});

test("a variant never lifts the family above its own rating", () => {
  const rows = [variant("c-0001a", 9, "c-0001"), curve("c-0001", 2), curve("c-0002", 8)];
  // c-0001a is rated 9, so the family's rank is 9; it still groups under c-0001.
  assert.deepEqual(orderPlates(rows).map((row) => row.uid), ["c-0001", "c-0001a", "c-0002"]);
});

test("the uid order is the plain fallback", () => {
  const rows = [curve("c-0002", 3), curve("c-0001", 5), curve("c-0001a", 0, { params: { variantOf: "c-0001" } })];
  assert.deepEqual(orderPlates(rows, "uid").map((row) => row.uid), ["c-0001", "c-0001a", "c-0002"]);
});
