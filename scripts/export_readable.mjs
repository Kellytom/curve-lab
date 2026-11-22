// One readable JSON of every curve: the equation in words, the measurements, the turn, the
// stars and a description. The registry holds the geometry; this file repeats it in a shape a
// person can read. Nothing here is a new source of truth — it is generated.
//
//   PATH="$HOME/node24/bin:$PATH" node scripts/export_readable.mjs
//
// Writes data/curves-readable.json. A stored path is not copied point by point (that would be
// megabytes); its point count and construction are given, and the points stay in the registry.
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import P from "../workbench/plate_math.js";

const ROOT = path.resolve(import.meta.dirname, "..");
const OUT = path.join(ROOT, "data", "curves-readable.json");
const registry = JSON.parse(readFileSync(path.join(ROOT, "workbench", "curve-registry.json"), "utf8"));
const exported = JSON.parse(readFileSync(path.join(ROOT, "data", "curves.json"), "utf8"));
const cutsFile = path.join(ROOT, "book", "print", "cuts.json");
const cuts = existsSync(cutsFile)
  ? new Map(JSON.parse(readFileSync(cutsFile, "utf8")).curves.map((c) => [c.uid, c.points.length]))
  : new Map();

const rowOf = new Map((exported.rows || []).map((row) => [row.uid, row]));
const degreeOf = (poly) => (Array.isArray(poly) ? poly.length - 1 : 0);

const fraction = (value, places = 3) =>
  Number.isFinite(Number(value)) ? Number(Number(value).toFixed(places)) : null;

// The generated description: what the curve is, how it was made, what it measures, and what a
// tuner needs to know. It is written here, never into the database note, so the operator's own
// notes stay theirs.
function describe(record, row, metric, turn) {
  const bits = [];
  const kind = record.path ? "a stored outline" : "an exact parametric curve";
  bits.push(`${record.name} (${record.uid}) is ${kind}` +
    (record.family ? ` from the ${record.family} family` : "") + ".");
  if (!record.path) {
    bits.push(`Its speed is u = ${JSON.stringify(record.speedX)} and v = ${JSON.stringify(record.speedY)}; ` +
      `the position is the integral of (u²−v², 2uv).`);
  } else {
    bits.push(`It is stored as ${record.path.length} points` +
      (record.definition ? `, made by the ${record.definition.family || record.definition.kind || "recorded"} construction` : "") +
      "; the exact points are in the registry.");
  }
  if (metric && metric.grid) {
    bits.push(`Measured exactly: grid 1/${metric.grid}, bend ${Number(metric.bend).toFixed(3)} ` +
      `(arc over chord), ${metric.inflections} inflection(s), ${metric.crossings} crossing pair(s).`);
  } else {
    bits.push("No exact measurement is recorded yet for this curve.");
  }
  if (turn) bits.push(`The plate turns it ${turn.degrees}°${turn.exact ? " exactly" : " (the 45° diagonal carries √2, so the turn is not exact)"}.`);
  if (cuts.get(record.uid)) bits.push(`The outside rail crosses itself ${cuts.get(record.uid)} time(s); each crossing is a future cut point.`);
  if (row && row.note && row.note.note) bits.push(`Note: ${row.note.note}`);
  return bits.join(" ");
}

const curves = registry.curves.map((record) => {
  const row = rowOf.get(record.uid) || {};
  const metric = row.metric || {};
  const note = row.note || {};
  let turn = null;
  try {
    turn = record.transform || (note.transform ? JSON.parse(note.transform) : null);
  } catch { turn = null; }
  const geometry = record.path
    ? { kind: "stored-path", points: record.path.length, start: record.path[0], end: record.path[record.path.length - 1],
        definition: record.definition || null }
    : { kind: "speed-rows", speedX: record.speedX, speedY: record.speedY,
        degree: Math.max(degreeOf(record.speedX), degreeOf(record.speedY)), step: record.step ?? 1 };
  return {
    uid: record.uid,
    name: record.name,
    aliases: record.aliases || [],
    family: record.family || record.family_id || null,
    source: record.source || null,
    stars: row.stars ?? null,
    geometry,
    formula: row.formula
      ? { plain: row.formula.plain, rational: row.formula.rational, parameter: row.formula.parameter }
      : null,
    measured: {
      grid: metric.grid ?? null,
      bend: fraction(metric.bend),
      arc: fraction(metric.arc),
      chord: fraction(metric.chord),
      inflections: metric.inflections ?? null,
      crossings: metric.crossings ?? null,
      meetingPoints: metric.meetingPoints ?? null,
      closestApproach: fraction(metric.closest),
      mirrorGap: fraction(metric.mirrorY),
      halfTurnGap: fraction(metric.halfTurn),
      bbox: metric.bboxW ? { w: fraction(metric.bboxW), h: fraction(metric.bboxH) } : null,
    },
    turn: turn ? { degrees: turn.degrees ?? 0, exact: turn.exact !== false } : { degrees: 0, exact: true },
    plate: {
      widthPercent: note.widthPct || null,
      plus: note.plus || null,
      minus: note.minus || null,
      profile: note.profile || null,
      cutPoints: cuts.get(record.uid) || 0,
    },
    note: note.note || null,
    description: describe(record, row, metric, turn),
    links: {
      tune: `/tune/${record.uid}`,
      plateSvg: `/api/print-plate/${record.uid}?format=svg`,
      tuneDesk: `/tune/${record.uid}`,
    },
  };
});

const out = {
  format: "curve-lab.curves-readable/1",
  note: "One object per curve: the equation in words, the exact measurements, the plate turn, " +
    "the stars and a generated description. The geometry of a speed-row curve is its speed " +
    "pair; a stored path is summarised and its points stay in the registry. The database note " +
    "is the operator's; the description here is generated and never written back.",
  source: {
    registry: "workbench/curve-registry.json",
    database: "data/curves.json",
    cutPoints: "book/print/cuts.json",
    exactCore: "curve_lab/measure.py",
  },
  count: curves.length,
  curves,
};
writeFileSync(OUT, `${JSON.stringify(out, null, 2)}\n`);
const bytes = readFileSync(OUT).length;
console.log(`${curves.length} curves -> ${path.relative(ROOT, OUT)} (${(bytes / 1024).toFixed(0)} KB)`);
