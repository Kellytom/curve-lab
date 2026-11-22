import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import P from "../../workbench/plate_math.js";
import { rowFor, symmetricStrength, TARGET_GAP_PERCENT } from "../../scripts/lib/plate-row.mjs";

// The operator, 2026-11-22: "half are too thin and half are too thick ... check the
// thickness", then the correction: "it breaks too many places. just keep the side curves
// with tight thin, but as thick as reasonable until they start to buckle, and i will
// manually adjust." So: one continuous band, never thicker than the measured target, as
// thin as the fold guard requires, and the tuner is told when it was cut.

const registry = JSON.parse(readFileSync(new URL("../../workbench/curve-registry.json", import.meta.url)));
const exported = JSON.parse(readFileSync(new URL("../../data/curves.json", import.meta.url)));
const noteOf = new Map((exported.rows || []).map((row) => [row.uid, row.note || {}]));
const deskFile = JSON.parse(readFileSync(new URL("../../data/sandbox-curves.json", import.meta.url)));
const deskOf = new Map((deskFile.rows || []).map((row) => [row.name, row]));

const measure = (record, row) => {
  const strength = symmetricStrength(row.character.plus, row.character.minus);
  const character = { ...row.character, plus: strength, minus: strength };
  let paths;
  let group;
  if (Array.isArray(record.path) && record.path.length > 2) {
    group = P.pathGroup(record.path, {
      widthPercent: row.width.percent, plus: strength, minus: strength, profile: row.character.profile,
    });
    paths = group ? group.paths : [];
  } else {
    group = P.group({ ...row, character });
    paths = group.paths;
  }
  if (paths.length < 3) return { gap: 0, group, spineOnly: true };
  const spine = paths[0];
  const xs = spine.map((p) => p[0]), ys = spine.map((p) => p[1]);
  const size = Math.hypot(Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys)) || 1;
  const gaps = [];
  for (const rail of paths.slice(1, 3)) {
    spine.forEach((p, i) => gaps.push(Math.hypot(rail[i][0] - p[0], rail[i][1] - p[1])));
  }
  gaps.sort((a, b) => a - b);
  return { gap: (gaps[Math.floor(gaps.length / 2)] / size) * 100, group, spineOnly: false };
};

test("no preset plate is a slab: the gap never exceeds the 2 % target", () => {
  const slabs = [];
  for (const record of registry.curves) {
    const desk = deskOf.get(record.uid) || deskOf.get((record.aliases || [])[0]) || {};
    const row = rowFor(record, { note: noteOf.get(record.uid) || {}, desk });
    if (row.width.source !== "preset") continue;
    const { gap } = measure(record, row);
    if (gap > TARGET_GAP_PERCENT + 0.4) slabs.push(`${record.uid}: ${gap.toFixed(2)} %`);
  }
  assert.deepEqual(slabs, [], `plates above the target: ${slabs.slice(0, 10).join(", ")}`);
});

test("a band that would buckle is cut, never folded", () => {
  for (const uid of ["c-0001", "c-0046", "c-0065"]) {
    const record = registry.curves.find((row) => row.uid === uid);
    const row = rowFor(record, { note: noteOf.get(uid) || {}, desk: deskOf.get(uid) || {} });
    const { group, spineOnly } = measure(record, row);
    if (spineOnly) continue;
    assert.ok(group.fold === undefined || group.fold <= 0.9 + 1e-9,
      `${uid} folds: ${group.fold}`);
    if (group.width < row.width.percent) {
      assert.equal(group.buckles, true, `${uid} was cut but does not say so`);
      assert.ok(group.buckleNote && group.buckleNote.includes("buckle"));
    }
  }
});

test("the target gap is the one the operator's good curves measure", () => {
  assert.ok(TARGET_GAP_PERCENT >= 1.5 && TARGET_GAP_PERCENT <= 2.5);
  for (const uid of ["c-0001a", "c-0161"]) {
    const record = registry.curves.find((row) => row.uid === uid);
    const row = rowFor(record, { note: noteOf.get(uid) || {}, desk: deskOf.get(uid) || {} });
    const { gap } = measure(record, row);
    assert.ok(gap > 0 && Math.abs(gap - TARGET_GAP_PERCENT) < 0.7,
      `${uid} draws ${gap.toFixed(2)} %, the target is ${TARGET_GAP_PERCENT} %`);
  }
});
