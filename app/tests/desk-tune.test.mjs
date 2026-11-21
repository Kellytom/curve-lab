// The desk's rules for /tune. A tuning row holds the four values; a new curve is a real
// record beside its parent, with its own uid: c-0002 -> c-0002a.
//
// The operator's need: choose the name for a new curve, and see it next to the old one on
// the plates page. These tests fail if a save goes back to replacing the row, if a variant
// loses its parent, or if a name collision is quietly suffixed.

import test from "node:test";
import assert from "node:assert/strict";
import { planOverwrite, planVariant, safeCurveName, valuesFrom, variantUid }
  from "../src/lib/desk-tune.js";

const uids = new Set(["c-0002", "c-0003"]);
const row = (name, data) => ({ name, data: JSON.stringify(data) });
const values = (over = {}) => valuesFrom({ widthPct: 6, plus: 2, minus: 2, profile: "bow",
                                           degrees: 0, ...over });
const curves = [
  { uid: "c-0002", name: "euler-hook", aliases: [], speedX: [1, 2], speedY: [3, 4],
    kind: "rows", transform: { degrees: 0 }, lists: ["found"] },
  { uid: "c-0002a", name: "euler-hook-thin", aliases: [], params: { variantOf: "c-0002" },
    speedX: [1, 2], speedY: [3, 4], kind: "rows", transform: { degrees: 0 } },
  { uid: "c-0003", name: "lace-1of8-3", aliases: ["lace"], speedX: [1], speedY: [1] },
];

test("a curve name is a path component", () => {
  assert.equal(safeCurveName("Euler Hook Thin"), "euler-hook-thin");
  assert.equal(safeCurveName("  lace / 1/8 "), "lace-1of8");
  assert.equal(safeCurveName("!!!"), "");
});

test("a variant takes the next letter on its spine", () => {
  assert.equal(variantUid("c-0002", new Set()), "c-0002a");
  assert.equal(variantUid("c-0002", new Set(["c-0002a"])), "c-0002b");
  assert.equal(variantUid("c-0002", new Set(["c-0002a", "c-0002b"])), "c-0002c");
});

test("save keeps every field the tune does not own", () => {
  const rows = [row("c-0002", { widthPct: 1.5, plus: 2, minus: 2, profile: "bow",
                                spine: "c-0002", curveName: "amper", construction: { kind: "piece" } })];
  const plan = planOverwrite({ rows, uids, rowId: "c-0002", spine: "c-0002",
                               values: values({ plus: 5 }) });
  assert.equal(plan.ok, true);
  assert.equal(plan.data.plus, 5);
  assert.equal(plan.data.widthPct, 6);
  assert.equal(plan.data.curveName, "amper");
  assert.deepEqual(plan.data.construction, { kind: "piece" });
});

test("a bad id is refused before a write", () => {
  const bad = planOverwrite({ rows: [], uids, rowId: "nope", spine: "nope", values: values() });
  assert.equal(bad.ok, false);
  assert.equal(bad.status, 400);
});

test("a new curve is a record beside its parent", () => {
  const plan = planVariant({ curves, baseUid: "c-0002", name: "Euler Hook Wide", values: values({ plus: 4 }) });
  assert.equal(plan.ok, true);
  assert.equal(plan.uid, "c-0002b");
  assert.equal(plan.name, "euler-hook-wide");
  assert.equal(plan.record.uid, "c-0002b");
  assert.equal(plan.record.params.variantOf, "c-0002");
  assert.equal(plan.record.params.parent, "c-0002");
  assert.equal(plan.record.plus, 4);
  assert.deepEqual(plan.record.speedX, [1, 2], "the geometry is copied from the spine");
  assert.ok(plan.record.lists.includes("variant"));
  assert.equal(plan.record.starred, false);
});

test("a variant of a variant lands in the original series", () => {
  const plan = planVariant({ curves, baseUid: "c-0002a", name: "thin two", values: values() });
  assert.equal(plan.ok, true);
  assert.equal(plan.uid, "c-0002b");
  assert.equal(plan.record.params.variantOf, "c-0002");
});

test("a name collision is refused and names the owner", () => {
  const plan = planVariant({ curves, baseUid: "c-0002", name: "Euler Hook Thin", values: values() });
  assert.equal(plan.ok, false);
  assert.equal(plan.status, 409);
  assert.match(plan.error, /already used by c-0002a \(euler-hook-thin\)/);
  const alias = planVariant({ curves, baseUid: "c-0002", name: "lace", values: values() });
  assert.equal(alias.ok, false);
  assert.equal(alias.status, 409, "an alias is a name too");
});

test("a new curve needs a name with a letter or a digit", () => {
  const empty = planVariant({ curves, baseUid: "c-0002", name: "  ", values: values() });
  assert.equal(empty.ok, false);
  assert.equal(empty.status, 400);
  const symbols = planVariant({ curves, baseUid: "c-0002", name: "!!!", values: values() });
  assert.equal(symbols.ok, false);
});

test("values are clamped into the sliders' own ranges", () => {
  const out = valuesFrom({ widthPct: 99, plus: -99, minus: 3, profile: "nope", degrees: 999 });
  assert.equal(out.widthPct, 20);
  assert.equal(out.plus, -8);
  assert.equal(out.minus, 3);
  assert.equal(out.profile, "bow");
  assert.deepEqual(out.transform, { degrees: 360 });
});
