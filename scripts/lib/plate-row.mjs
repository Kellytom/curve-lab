// The one place a plate's four character values are chosen.
//
// Order, everywhere: note → desk row → preset.
// This lives in a library, not inside print_plates.mjs, because it was a copy of the
// function that carried a duplicate `character:` key: the second key silently won and
// set plus and minus to 0, so every plate drew two parallel offsets no matter what the
// desk said. See state/REGRESSIONS-int.md.
import P from "../../workbench/plate_math.js";

// The preset is a **measured gap**, not a fixed width. The operator, 2026-11-22: "half are
// too thin and half are too thick ... check the thickness", then "reduce the width to 1% on
// the ones i have not edited". So the preset solves the width that puts the drawn gap at
// 1 % of the curve's own size; a curve with a saved width keeps its own number.
export const TARGET_GAP_PERCENT = 1;
export const DEFAULTS = { plus: 2.5, minus: 0.1, profile: "bow" };

// The median of the bow factor over the curve, so a solved base width lands at the target
// gap whatever the profile and strength are.
const medianFactor = (profile, strength) => {
  const values = [];
  for (let i = 0; i <= 200; i += 1) {
    values.push(1 + strength * P.profileAt(profile, i / 200));
  }
  values.sort((a, b) => a - b);
  return values[100] || 1;
};

export function presetWidthPercent(character) {
  const strength = (Math.abs(Number(character.plus) || 0) + Math.abs(Number(character.minus) || 0)) / 2;
  return Math.round((TARGET_GAP_PERCENT / medianFactor(character.profile, strength)) * 100) / 100;
}

// The operator, 2026-11-21: "the offset curves should look the same on both sides of the
// curve, not thin on the right and wide on the left." The two sides take one strength, the
// average of the saved pair; the profile is zero at both ends, so the start and end gaps are
// the base and the ends balance.
export const symmetricStrength = (plus, minus) =>
  (Math.abs(Number(plus) || 0) + Math.abs(Number(minus) || 0)) / 2;

// A zero in a note is the placeholder the 2026-11 note migration wrote, not a choice: every
// plate then drew a 0 % parallel band. The note wins only when it holds a real value; a zero
// falls through to the desk row, then the default. A deliberate zero belongs in the desk row.
const choose = (noteValue, deskValue, defaultValue) => {
  if (noteValue !== undefined && noteValue !== null && Number(noteValue) !== 0) return noteValue;
  if (deskValue !== undefined && deskValue !== null) return deskValue;
  return defaultValue;
};

export function rowFor(record, context = {}) {
  const note = context.note || {};
  const desk = context.desk || {};
  const plus = choose(note.plus, desk.plus, DEFAULTS.plus);
  const minus = choose(note.minus, desk.minus, DEFAULTS.minus);
  const profile = note.profile || desk.profile || DEFAULTS.profile;
  // Every curve takes the preset when it has no saved width, stored paths included. The
  // operator, 2026-11-21: "i didnt ask for spines only. i asked for clean curves like the
  // first two." (The path rails' fold at a tight loop is a geometry problem, not a reason to
  // drop the band.)
  const preset = presetWidthPercent({ plus, minus, profile });
  const noteWidth = note.width_pct ?? note.widthPct;
  const widthPercent = choose(noteWidth, desk.widthPct, preset);
  // Who set the width. The plate only normalises a preset curve to the target gap; a saved
  // width is the operator's own number and is used as asked.
  const widthSource = (noteWidth !== undefined && noteWidth !== null && Number(noteWidth) !== 0)
    ? "note"
    : (desk.widthPct !== undefined && desk.widthPct !== null ? "desk" : "preset");
  return {
    name: record.name,
    speedX: record.speedX || [],
    speedY: record.speedY || [],
    width: { percent: widthPercent, source: widthSource },
    character: { plus, minus, profile },
  };
}
