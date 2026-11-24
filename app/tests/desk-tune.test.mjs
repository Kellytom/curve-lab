// The desk's rules for /tune. A tuning row holds the four values; a new curve is a real
// record beside its parent, with its own uid: c-0002 -> c-0002a.
//
// The operator's need: choose the name for a new curve, and see it next to the old one on
// the plates page. These tests fail if a save goes back to replacing the row, if a variant
// loses its parent, or if a name collision is quietly suffixed.

import test from "node:test";
import assert from "node:assert/strict";
import { planOverwrite, planRename, planVariant, safeCurveName, valuesFrom, variantUid }
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

test("a trim keeps its rational bounds on the record", () => {
  const plan = planVariant({ curves, baseUid: "c-0002", name: "trimmed", values: values(),
    path: [[0, 0], [1, 0.2], [2, 0]], cut: { mode: "trim", from: "1/4", to: "3/4" } });
  assert.equal(plan.ok, true);
  assert.deepEqual(plan.record.params.cut,
    { of: "c-0002", ofName: plan.record.params.cut.ofName, mode: "trim",
      from: "1/4", to: "3/4", sampled: true });
  assert.equal(plan.record.conversion.algorithm, "trimmed at rational fractions of t");
  assert.match(plan.record.note, /t 1\/4 → 3\/4/);
});

test("a desk row that never became a record still holds its uid", () => {
  const plan = planVariant({ curves, baseUid: "c-0002", name: "spare", values: values(),
                             deskIds: ["c-0002b"] });
  assert.equal(plan.ok, true);
  assert.equal(plan.uid, "c-0002c");
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

test("a rename keeps the uid and its old name, and refuses a name already used", () => {
  const plan = planRename({ curves, uid: "c-0002a", name: "euler-hook-thin-two" });
  assert.equal(plan.ok, true);
  assert.equal(plan.uid, "c-0002a");
  assert.equal(plan.to, "euler-hook-thin-two");
  assert.ok(plan.aliases.includes("euler-hook-thin"), "the old name is kept as an alias");

  const clash = planRename({ curves, uid: "c-0002a", name: "euler-hook" });
  assert.equal(clash.ok, false);
  assert.equal(clash.status, 409);
  assert.match(clash.error, /c-0002/, "the owner is named");

  const same = planRename({ curves, uid: "c-0002a", name: "euler-hook-thin" });
  assert.equal(same.ok, false);
  assert.equal(same.status, 400);

  const missing = planRename({ curves, uid: "c-9999", name: "x" });
  assert.equal(missing.status, 404);

  const desk = planRename({ curves, uid: "c-0002a", name: "taken-on-desk",
                            deskNames: ["taken-on-desk"] });
  assert.equal(desk.ok, false, "a desk row's name is a name too");
  assert.equal(desk.status, 409);
});
