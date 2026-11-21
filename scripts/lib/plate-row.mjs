// The one place a plate's four character values are chosen.
//
// Order, everywhere: note → desk row → defaults (6 %, plus 2, minus 2, bow).
// This lives in a library, not inside print_plates.mjs, because it was a copy of the
// function that carried a duplicate `character:` key: the second key silently won and
// set plus and minus to 0, so every plate drew two parallel offsets no matter what the
// desk said. See state/REGRESSIONS-int.md.

export const DEFAULTS = { widthPercent: 6, plus: 2, minus: 2, profile: "bow" };

export function rowFor(record, context = {}) {
  const note = context.note || {};
  const desk = context.desk || {};
  const widthPercent = note.width_pct ?? note.widthPct ?? desk.widthPct ?? DEFAULTS.widthPercent;
  return {
    name: record.name,
    speedX: record.speedX || [],
    speedY: record.speedY || [],
    width: { percent: widthPercent },
    character: {
      plus: note.plus ?? desk.plus ?? DEFAULTS.plus,
      minus: note.minus ?? desk.minus ?? DEFAULTS.minus,
      profile: note.profile || desk.profile || DEFAULTS.profile,
    },
  };
}
