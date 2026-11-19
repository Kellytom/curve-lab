// Which chosen curves are actually the same drawing?
//
// The operator's rule (2026-11-19): a mirror is not necessarily a duplicate, and
// the same goes for a rotation or a flip. So:
//
//   duplicate = the same figure in the same orientation, only moved or scaled
//               (a reversed stroke counts: it draws the same marks)
//
// A mirror, a rotation or a flip is a different plate and is NOT reported. The
// first version of this script listed them and produced 500 meaningless pairs,
// because a coarse turning histogram cannot tell two smooth curves apart.
//
//   node scripts/dupe_audit.mjs            # print both lists
//   node scripts/dupe_audit.mjs --write    # also write state/DUPLICATES-int.md
//
// It marks uids; it deletes nothing.

import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const require = createRequire(import.meta.url);
const P = require(path.join(ROOT, "workbench", "plate_math.js"));

const SAMPLE = 64;
const DUPLICATE = Number(process.env.DUPE_THRESHOLD || 0.002);  // L2 on points normalised to an RMS radius of 1

function pointsOf(record) {
  if (Array.isArray(record.path) && record.path.length > 8) return record.path;
  if (Array.isArray(record.speedX) && record.speedX.some((v) => v !== 0)) {
    return P.spine(record.speedX, record.speedY, 240).map((s) => [s.x, s.y]);
  }
  return [];
}

// Resample by arc length, so two curves with different row speeds still land on
// the same stations: the comparison is of the drawing, not of the parameter.
function resample(points, count) {
  if (points.length < 2) return points;
  const lengths = [0];
  for (let i = 1; i < points.length; i += 1) {
    lengths.push(lengths[i - 1] + Math.hypot(points[i][0] - points[i - 1][0], points[i][1] - points[i - 1][1]));
  }
  const total = lengths[lengths.length - 1] || 1;
  const out = [];
  let at = 0;
  for (let k = 0; k < count; k += 1) {
    const want = (k / (count - 1)) * total;
    while (at < points.length - 2 && lengths[at + 1] < want) at += 1;
    const span = lengths[at + 1] - lengths[at] || 1;
    const f = Math.min(1, Math.max(0, (want - lengths[at]) / span));
    out.push([
      points[at][0] + (points[at + 1][0] - points[at][0]) * f,
      points[at][1] + (points[at + 1][1] - points[at][1]) * f,
    ]);
  }
  return out;
}

// Move to the centroid and scale so the RMS radius is 1: position and size gone.
function normalise(points) {
  const chosen = resample(points, SAMPLE);
  if (chosen.length < 8) return null;
  const cx = chosen.reduce((sum, p) => sum + p[0], 0) / chosen.length;
  const cy = chosen.reduce((sum, p) => sum + p[1], 0) / chosen.length;
  const centred = chosen.map(([x, y]) => [x - cx, y - cy]);
  const rms = Math.sqrt(centred.reduce((sum, [x, y]) => sum + x * x + y * y, 0) / centred.length) || 1;
  return centred.map(([x, y]) => [x / rms, y / rms]);
}

// The same figure walked the other way is the same marks on the page.
function pointDistance(a, b) {
  const direct = a.reduce((sum, [x, y], i) => sum + (x - b[i][0]) ** 2 + (y - b[i][1]) ** 2, 0);
  const reversed = a.reduce((sum, [x, y], i) => {
    const j = b.length - 1 - i;
    return sum + (x - b[j][0]) ** 2 + (y - b[j][1]) ** 2;
  }, 0);
  return Math.sqrt(Math.min(direct, reversed) / a.length);
}

const registry = JSON.parse(readFileSync(path.join(ROOT, "workbench", "curve-registry.json"), "utf8"));
const chosen = registry.curves.filter((record) => !record.candidate);
const curves = chosen.map((record) => {
  const points = pointsOf(record);
  return { record, points: normalise(points) };
}).filter((curve) => curve.points);

const duplicates = [];
for (let i = 0; i < curves.length; i += 1) {
  for (let j = i + 1; j < curves.length; j += 1) {
    const d = pointDistance(curves[i].points, curves[j].points);
    if (d < DUPLICATE) duplicates.push({ a: curves[i].record, b: curves[j].record, d });
  }
}
duplicates.sort((x, y) => x.d - y.d);

// One row per group: three curves that pairwise match are one group of three,
// not three groups.
const groups = [];
for (const pair of duplicates) {
  let group = groups.find((g) => g.uids.has(pair.a.uid) || g.uids.has(pair.b.uid));
  if (!group) {
    group = { uids: new Set(), members: [], worst: 0 };
    groups.push(group);
  }
  for (const record of [pair.a, pair.b]) {
    if (!group.uids.has(record.uid)) {
      group.uids.add(record.uid);
      group.members.push(record);
    }
  }
  group.worst = Math.max(group.worst, pair.d);
}

const line = (pair) => `worst ${pair.d.toFixed(4)} — ${pair.a.uid} ${pair.a.name}  |  ${pair.b.uid} ${pair.b.name}`;
console.log(`chosen ${chosen.length}, compared ${curves.length}`);
console.log(`threshold ${DUPLICATE}`);
console.log(`groups of the same drawing: ${groups.length}`);
for (const group of groups) {
  console.log(`  worst ${group.worst.toFixed(4)} — ${group.members.map((m) => `${m.uid} ${m.name}`).join("  |  ")}`);
}

if (process.argv.includes("--write")) {
  const lines = [
    "# DUPLICATES-int — the same drawing twice",
    "",
    "Generated by `node scripts/dupe_audit.mjs --write`. Do not edit by hand.",
    "",
    "The operator's rule: **a mirror, a rotation or a flip is a different plate, not",
    "a duplicate.** So only one case is reported: the same figure in the same",
    "orientation, only moved or scaled (a reversed stroke counts as the same marks).",
    "Symmetries are not searched for; they are allowed by definition.",
    "",
    `Duplicate threshold ${DUPLICATE} on points normalised to an RMS radius of 1;`,
    `${SAMPLE} stations, resampled by arc length.`,
    "",
    "## Duplicates — settle these",
    "",
    "| group | worst | uids | names |",
    "|---|---|---|---|",
    ...(groups.length
      ? groups.map((group, index) => `| ${index + 1} | ${group.worst.toFixed(4)} | ${group.members.map((m) => m.uid).join(", ")} | ${group.members.map((m) => m.name).join(" · ")} |`)
      : ["| 0 | — | none | none |"]),
    "",
    "Settle one by keeping either curve and moving the other to notes on `/names`",
    "(one click, with undo), then re-run this script.",
    "",
  ];
  writeFileSync(path.join(ROOT, "state", "DUPLICATES-int.md"), lines.join("\n"));
  console.log("wrote state/DUPLICATES-int.md");
}
