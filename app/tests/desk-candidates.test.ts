// A variant posted from Inkscape is found by its parent link, not by its uid.
//
// The operator's need: a candidate made in Inkscape appears on the tune page it came from.
// A posted row is not a registry curve, so it is listed only when its `base_uid` names the
// spine, and it disappears from the list once it has been promoted to a record.

import test from "node:test";
import assert from "node:assert/strict";
import { candidatesFor, parseDeskRow } from "../src/lib/desk-candidates.ts";

const row = (name, data) => ({ name, data: JSON.stringify(data) });
const posted = (over = {}) => ({
  name: "c-0002b", curveName: "euler-hook-end-edited", base_uid: "c-0002",
  speedX: [2.2, -4.4, 6.6], speedY: [4.4, -22, 22],
  kind: "rows", variant: "inkscape", source: "inkscape-roundtrip",
  origin: "inkscape-roundtrip", candidate: true,
  transform: { degrees: 0, matrix: [[1, 0], [0, 1]], exact: true },
  savedAt: "2026-11-22T07:27:59.859Z", ...over,
});

test("a posted variant is found by its parent link", () => {
  const found = candidatesFor([row("c-0002b", posted())], "c-0002");
  assert.equal(found.length, 1);
  assert.equal(found[0].uid, "c-0002b");
  assert.equal(found[0].name, "euler-hook-end-edited");
  assert.equal(found[0].baseUid, "c-0002");
  assert.equal(found[0].origin, "inkscape-roundtrip");
  assert.deepEqual(found[0].rows.speedX, [2.2, -4.4, 6.6]);
  assert.deepEqual(found[0].transform, { degrees: 0, exact: true });
});

test("a row for another spine, or with no parent, is not this spine's candidate", () => {
  const rows = [
    row("c-0003b", posted({ base_uid: "c-0003" })),
    row("c-0002c", posted({ base_uid: undefined, name: "c-0002c" })),
    row("c-0002b", posted()),
  ];
  const found = candidatesFor(rows, "c-0002");
  assert.deepEqual(found.map((item) => item.uid), ["c-0002b"]);
});

test("a promoted candidate is listed once, as a curve", () => {
  const rows = [row("c-0002b", posted())];
  assert.equal(candidatesFor(rows, "c-0002", ["c-0002b"]).length, 0);
});

test("a row with no speed rows is not drawn as a candidate", () => {
  const rows = [row("c-0002b", posted({ speedX: [], speedY: [] })),
    row("c-0002c", posted({ name: "c-0002c", speedX: [1, 2], speedY: [3] }))];
  assert.equal(candidatesFor(rows, "c-0002").length, 0);
});

test("bad JSON is skipped, not thrown", () => {
  assert.deepEqual(parseDeskRow({ name: "x", data: "{oops" }), {});
  assert.equal(candidatesFor([{ name: "x", data: "{oops" }], "c-0002").length, 0);
});

test("the list is ordered by uid, and the chosen name falls back to the row key", () => {
  const rows = [
    row("c-0002c", posted({ name: "c-0002c", curveName: "" })),
    row("c-0002b", posted()),
  ];
  const found = candidatesFor(rows, "c-0002");
  assert.deepEqual(found.map((item) => item.uid), ["c-0002b", "c-0002c"]);
  assert.equal(found[1].name, "c-0002c");
});
