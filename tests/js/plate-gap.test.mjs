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

test("no preset plate is a slab: the gap never exceeds the 1 % target", () => {
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

test("a folded rail is reported, and its crossing is the cut point", () => {
  // Law change, 2026-11-23: the inside cap is withdrawn. A rail that would fold now folds,
  // and the fold is named instead of cut away; the crossing it makes is the cut point.
  for (const uid of ["c-0001", "c-0046", "c-0065"]) {
    const record = registry.curves.find((row) => row.uid === uid);
    const row = rowFor(record, { note: noteOf.get(uid) || {}, desk: deskOf.get(uid) || {} });
    const { group, spineOnly } = measure(record, row);
    if (spineOnly) continue;
    assert.ok(group.fold === undefined || Number.isFinite(group.fold), `${uid}: no fold measure`);
    if (group.fold > 0.9) {
      assert.equal(group.buckles, true, `${uid} folds but does not say so`);
      assert.ok(group.buckleNote && group.buckleNote.includes("crossing"),
        `${uid}: the note must name the crossing, not a cut`);
    }
    const rails = group.paths.slice(1, 3);
    const crossings = rails.reduce((count, rail) => count + P.railHoles(rail).crossings.length, 0);
    if (group.fold > 0.9) assert.ok(crossings > 0, `${uid}: a fold with no crossing`);
  }
});

test("a tight turn lets the inside rail cross itself, and the loop is a hidden span", () => {
  // The operator, 2026-11-23: "letting each rail cross itself at a tight turn, marking every
  // crossing with a red dot, hiding the small loop as an invisible span." c-0046 is the
  // measured case: its rail folds through itself at the two sharp turns.
  const record = registry.curves.find((row) => row.uid === "c-0046");
  const row = rowFor(record, { note: noteOf.get("c-0046") || {}, desk: deskOf.get("c-0046") || {} });
  const { group } = measure(record, row);
  assert.ok(group.fold > 0.9, `c-0046 should fold; fold ${group.fold}`);
  assert.equal(group.buckles, true);
  const rails = group.paths.slice(1, 3);
  const infos = rails.map((rail) => P.railHoles(rail));
  assert.ok(infos.every((info) => info.crossings.length > 0), "both rails cross themselves");
  assert.ok(infos.some((info) => info.spans.length > 0), "a loop must be found and hidden");
  for (const info of infos) {
    for (const span of info.spans) {
      assert.ok(span.from < span.to, "a span runs forward along the rail");
      assert.ok(span.length > 0, "a hidden span has a length");
    }
  }
});

test("the preset draws the 1 % target, a saved curve keeps its own width", () => {
  assert.equal(TARGET_GAP_PERCENT, 1);
  const record = registry.curves.find((row) => row.uid === "c-0161");
  const preset = rowFor(record, { note: noteOf.get("c-0161") || {}, desk: deskOf.get("c-0161") || {} });
  assert.equal(preset.width.source, "preset");
  const { gap } = measure(record, preset);
  assert.ok(gap > 0.8 && gap < 1.3, `c-0161 draws ${gap.toFixed(2)} %, the target is 1 %`);

  // the operator's own curves are untouched
  const saved = registry.curves.find((row) => row.uid === "c-0001a");
  const savedRow = rowFor(saved, { note: noteOf.get("c-0001a") || {}, desk: deskOf.get("c-0001a") || {} });
  assert.notEqual(savedRow.width.source, "preset", "a saved curve is not normalised");
  assert.equal(savedRow.width.percent, 1);
});
