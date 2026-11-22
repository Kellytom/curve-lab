import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import P from "../../workbench/plate_math.js";
import { rowFor, symmetricStrength, TARGET_GAP_PERCENT } from "../../scripts/lib/plate-row.mjs";

// The operator, 2026-11-22: "half are too thin and half are too thick ... you should have
// algorithms to figure that out already and fix it before i even see it. right? check the
// thickness". The check: every plate's drawn gap, as a share of its own curve's size, must
// sit inside the band the operator called correct (c-0001a 1.9 %, c-0161 2.3 %).

const registry = JSON.parse(readFileSync(new URL("../../workbench/curve-registry.json", import.meta.url)));
const exported = JSON.parse(readFileSync(new URL("../../data/curves.json", import.meta.url)));
const noteOf = new Map((exported.rows || []).map((row) => [row.uid, row.note || {}]));
const deskFile = JSON.parse(readFileSync(new URL("../../data/sandbox-curves.json", import.meta.url)));
const deskOf = new Map((deskFile.rows || []).map((row) => [row.name, row]));

// the plate writer's own choice of segments
const partsOf = (record, row, strength, character) => {
  const targetGapPercent = row.width.source === "preset" ? TARGET_GAP_PERCENT : undefined;
  if (Array.isArray(record.path) && record.path.length > 2) {
    const opts = { widthPercent: row.width.percent, plus: strength, minus: strength, profile: row.character.profile, targetGapPercent };
    const split = P.splitPath(record.path, opts);
    if (split) return split.segments;
    const group = P.pathGroup(record.path, opts);
    return group ? [{ spine: group.paths[0], rails: group.paths.slice(1) }] : [];
  }
  const split = P.splitGroup({ ...row, character }, { targetGapPercent });
  if (split) return split.segments;
  const group = P.group({ ...row, character });
  return group.paths.length > 2 ? [{ spine: group.paths[0], rails: group.paths.slice(1) }] : [];
};

const gapOf = (record, row) => {
  const strength = symmetricStrength(row.character.plus, row.character.minus);
  const character = { ...row.character, plus: strength, minus: strength };
  const parts = partsOf(record, row, strength, character);
  const spine = parts.flatMap((part) => part.spine);
  if (!spine.length) return null;
  const xs = spine.map((p) => p[0]), ys = spine.map((p) => p[1]);
  const size = Math.hypot(Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys)) || 1;
  const gaps = [];
  for (const part of parts) {
    // measure the body of each run: the taper at a break is meant to be thin
    const from = Math.floor(part.spine.length * 0.15);
    const to = Math.ceil(part.spine.length * 0.85);
    for (const rail of part.rails.slice(0, 2)) {
      for (let i = from; i < to; i += 1) {
        if (rail[i]) gaps.push(Math.hypot(rail[i][0] - part.spine[i][0], rail[i][1] - part.spine[i][1]));
      }
    }
  }
  if (!gaps.length) return null;
  gaps.sort((a, b) => a - b);
  return { median: (gaps[Math.floor(gaps.length / 2)] / size) * 100, max: (gaps[gaps.length - 1] / size) * 100 };
};

test("every preset plate draws the target gap, not a thin one or a slab", () => {
  const offenders = [];
  for (const record of registry.curves) {
    const desk = deskOf.get(record.uid) || deskOf.get((record.aliases || [])[0]) || {};
    const row = rowFor(record, { note: noteOf.get(record.uid) || {}, desk });
    // a saved width is the operator's own choice and is not in this test
    const saved = Object.values(desk).length > 0 && desk.widthPct !== undefined;
    if (saved) continue;
    const gap = gapOf(record, row);
    if (!gap) { offenders.push(`${record.uid}: no band`); continue; }
    if (gap.median < 1.5 || gap.median > 2.6) {
      offenders.push(`${record.uid}: ${gap.median.toFixed(2)} %`);
    }
  }
  assert.deepEqual(offenders, [], `plates outside the target gap: ${offenders.slice(0, 12).join(", ")}`);
});

test("the target gap is the one the operator's good curves measure", () => {
  assert.ok(TARGET_GAP_PERCENT >= 1.5 && TARGET_GAP_PERCENT <= 2.5);
  for (const uid of ["c-0001a", "c-0161"]) {
    const record = registry.curves.find((row) => row.uid === uid);
    const desk = deskOf.get(uid) || {};
    const row = rowFor(record, { note: noteOf.get(uid) || {}, desk });
    const gap = gapOf(record, row);
    assert.ok(gap && Math.abs(gap.median - TARGET_GAP_PERCENT) < 0.6,
      `${uid} draws ${gap && gap.median.toFixed(2)} %, the target is ${TARGET_GAP_PERCENT} %`);
  }
});
