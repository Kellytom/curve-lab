// The one place a plate's four character values are chosen.
//
// Order, everywhere: note → desk row → defaults (1.5 %, plus 2, minus 2, bow).
// This lives in a library, not inside print_plates.mjs, because it was a copy of the
// function that carried a duplicate `character:` key: the second key silently won and
// set plus and minus to 0, so every plate drew two parallel offsets no matter what the
// desk said. See state/REGRESSIONS-int.md.

// The preset is the first two curves the operator tuned: c-0001 and c-0001a, at 1 % width,
// plus 2.5, minus 0.1. 6 % was the old guard's asked width; 1.5 % was the first correction;
// the operator's words, 2026-11-21: "6% is way too much, look at the first two curves i did
// for a better preset level."
export const DEFAULTS = { widthPercent: 1, plus: 2.5, minus: 0.1, profile: "bow" };

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
  // The zero placeholders are a row-record problem. A stored path (the doubles and the
  // flourishes) uses its zero note as the clean two-tone spine; the preset must not add a
  // band there (2026-11-21, the operator: "it looks to me like you went backwards with
  // c-0275 to 368").
  const storedPath = Array.isArray(record.path) && record.path.length > 2;
  const widthPercent = storedPath
    ? (note.width_pct ?? note.widthPct ?? desk.widthPct ?? 0)
    : choose(note.width_pct ?? note.widthPct, desk.widthPct, DEFAULTS.widthPercent);
  const plus = storedPath ? (note.plus ?? desk.plus ?? 0) : choose(note.plus, desk.plus, DEFAULTS.plus);
  const minus = storedPath ? (note.minus ?? desk.minus ?? 0) : choose(note.minus, desk.minus, DEFAULTS.minus);
  return {
    name: record.name,
    speedX: record.speedX || [],
    speedY: record.speedY || [],
    width: { percent: widthPercent },
    character: {
      plus,
      minus,
      profile: note.profile || desk.profile || DEFAULTS.profile,
    },
  };
}
