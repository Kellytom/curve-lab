// The desk's rules for /tune: overwrite one row, save a new named version of one spine.
//
// The operator's need: "we might have 5 different versions from one spine, and that is
// good." So many rows per spine are allowed, but a name is a key — two rows may never
// share one, and a new version may not squat on a curve id. These tests fail if a save
// goes back to replacing the whole row, or if a collision is quietly suffixed.

import test from "node:test";
import assert from "node:assert/strict";
import { planSave, slugOf, valuesFrom } from "../src/lib/desk-tune.js";

const uids = new Set(["c-0001", "c-0002"]);
const row = (name, data) => ({ name, data: JSON.stringify(data) });
const values = (over = {}) => valuesFrom({ widthPct: 6, plus: 2, minus: 2, profile: "bow",
                                           degrees: 0, ...over });

const base = () => row("c-0001", {
  widthPct: 1.5, plus: 2, minus: 2, profile: "bow", transform: { degrees: 0 },
  curveName: "amper", construction: { kind: "piece", parent: "x" }, tune: true,
});

test("a name becomes a key that is safe in a URL", () => {
  assert.equal(slugOf("Amper 2"), "amper-2");
  assert.equal(slugOf("  Lace / 1of8  "), "lace-1of8");
  assert.equal(slugOf("!!!"), "");
});

test("overwrite keeps every field the tune does not own", () => {
  const plan = planSave({ rows: [base()], uids, mode: "overwrite", rowId: "c-0001",
                          spine: "c-0001", curveName: "amper", values: values({ plus: 5 }) });
  assert.equal(plan.ok, true);
  assert.equal(plan.created, false);
  assert.equal(plan.data.plus, 5);
  assert.equal(plan.data.widthPct, 6);
  assert.equal(plan.data.curveName, "amper", "the chosen name survives a value save");
  assert.deepEqual(plan.data.construction, { kind: "piece", parent: "x" },
    "the construction survives a value save");
  assert.equal(plan.data.spine, "c-0001");
});

test("a new version is a new row on the same spine", () => {
  const plan = planSave({ rows: [base()], uids, mode: "new", rowId: "c-0001", spine: "c-0001",
                          curveName: "Amper 2", values: values({ plus: 4 }) });
  assert.equal(plan.ok, true);
  assert.equal(plan.created, true);
  assert.equal(plan.name, "amper-2");
  assert.equal(plan.data.spine, "c-0001");
  assert.equal(plan.data.curveName, "Amper 2");
  assert.equal(plan.data.version, 2);
  assert.notEqual(plan.name, "c-0001", "a version never overwrites the base row");
});

test("five versions of one spine are all allowed", () => {
  const rows = [base(),
    row("amper-b", { spine: "c-0001", curveName: "amper b" }),
    row("amper-c", { spine: "c-0001", curveName: "amper c" }),
    row("amper-d", { spine: "c-0001", curveName: "amper d" })];
  const plan = planSave({ rows, uids, mode: "new", rowId: "c-0001", spine: "c-0001",
                          curveName: "amper e", values: values() });
  assert.equal(plan.ok, true);
  assert.equal(plan.name, "amper-e");
  assert.equal(plan.data.version, 5);
  // the base row predates the `spine` field; three named versions carry it explicitly
  assert.equal(rows.filter((item) => JSON.parse(item.data).spine === "c-0001").length, 3);
});

test("a name collision is refused and names the owner", () => {
  const rows = [base(), row("amper-2", { spine: "c-0001", curveName: "Amper 2" })];
  const byKey = planSave({ rows, uids, mode: "new", rowId: "c-0001", spine: "c-0001",
                           curveName: "amper 2", values: values() });
  assert.equal(byKey.ok, false);
  assert.equal(byKey.status, 409);
  assert.match(byKey.error, /already used by Amper 2/);

  const byChosen = planSave({ rows, uids, mode: "new", rowId: "c-0001", spine: "c-0001",
                              curveName: "AMPER 2", values: values() });
  assert.equal(byChosen.ok, false, "the chosen name is compared without case");
});

test("a new version may not take a curve id", () => {
  const plan = planSave({ rows: [base()], uids, mode: "new", rowId: "c-0001", spine: "c-0001",
                          curveName: "c-0002", values: values() });
  assert.equal(plan.ok, false);
  assert.equal(plan.status, 409);
  assert.match(plan.error, /already a curve id/);
});

test("a new version needs a name with a letter or a digit", () => {
  const empty = planSave({ rows: [base()], uids, mode: "new", rowId: "c-0001", spine: "c-0001",
                           curveName: "  ", values: values() });
  assert.equal(empty.ok, false);
  assert.equal(empty.status, 400);
  const symbols = planSave({ rows: [base()], uids, mode: "new", rowId: "c-0001",
                             spine: "c-0001", curveName: "!!!", values: values() });
  assert.equal(symbols.ok, false);
});

test("an overwrite may not rename onto another row", () => {
  const rows = [base(), row("amper-2", { spine: "c-0001", curveName: "Amper 2" })];
  const plan = planSave({ rows, uids, mode: "overwrite", rowId: "c-0001", spine: "c-0001",
                          curveName: "amper 2", values: values() });
  assert.equal(plan.ok, false);
  assert.equal(plan.status, 409);
});

test("a bad id and a missing version are refused before a write", () => {
  const bad = planSave({ rows: [base()], uids, mode: "overwrite", rowId: "nope",
                         spine: "nope", values: values() });
  assert.equal(bad.ok, false);
  assert.equal(bad.status, 400);
  const gone = planSave({ rows: [base()], uids, mode: "overwrite", rowId: "amper-9",
                          spine: "c-0001", values: values() });
  assert.equal(gone.ok, false);
  assert.equal(gone.status, 404);
});

test("values are clamped into the sliders' own ranges", () => {
  const out = valuesFrom({ widthPct: 99, plus: -99, minus: 3, profile: "nope", degrees: 999 });
  assert.equal(out.widthPct, 20);
  assert.equal(out.plus, -8);
  assert.equal(out.minus, 3);
  assert.equal(out.profile, "bow");
  assert.deepEqual(out.transform, { degrees: 360 });
});
