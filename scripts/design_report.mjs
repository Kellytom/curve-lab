// The small design decisions that are still open, one row per curve.
//
//   node scripts/design_report.mjs            # print the list
//   node scripts/design_report.mjs --write    # write state/DESIGN-TODO-int.md
//
// It reads the registry, the notes mirror, the figures index and the analysis,
// and it decides nothing: it sorts the curves by which small change would help
// most, so the next pass starts at the top instead of at the beginning.
//
// What counts as a "little thing":
//
//   corner   the two legs are near 90 degrees, so the curve can turn a corner
//            with a small miter; far from 90, the band should stop instead.
//   seam     the leaf's two halves cross at the waist: a notch or a pinch that
//            nobody chose. A tangent join or a declared gap fixes it.
//   offsets  the rails are off. The operator's point: a line becomes a form
//            once the rails are on.
//   band     the border is thick enough that the centre crowds it (a low
//            margin percent in the figures index).
//
// Curves are ranked by how many of those apply, then by crossings, because a
// curve with four problems and nine crossings is worth more attention than one
// with four and none.

import { existsSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const require = createRequire(import.meta.url);
const P = require(path.join(ROOT, "workbench", "plate_math.js"));

const registry = JSON.parse(readFileSync(path.join(ROOT, "workbench", "curve-registry.json"), "utf8")).curves;
const notes = JSON.parse(readFileSync(path.join(ROOT, "workbench", "curve-notes.json"), "utf8")).curves;
const noteByUid = Object.fromEntries(notes.map((note) => [note.uid, note]));
const index = JSON.parse(readFileSync(path.join(ROOT, "app", "public", "figures", "index.json"), "utf8")).curves;
const figByUid = Object.fromEntries(index.map((row) => [row.uid, row]));
const analysis = JSON.parse(readFileSync(path.join(ROOT, "workbench", "curve-analysis.json"), "utf8")).curves;
const metricByUid = Object.fromEntries(analysis.map((row) => [row.uid, row]));

const deg = (radians) => (radians * 180) / Math.PI;
const wrap180 = (angle) => ((angle % 180) + 180) % 180;

function pointsOf(record) {
  if (Array.isArray(record.path) && record.path.length > 8) return record.path;
  return P.spine(record.speedX, record.speedY, 160).map((s) => [s.x, s.y]);
}

function legGap(points) {
  const n = points.length;
  if (n < 6) return null;
  const a0 = Math.atan2(points[2][1] - points[0][1], points[2][0] - points[0][0]);
  const a1 = Math.atan2(points[n - 1][1] - points[n - 3][1], points[n - 1][0] - points[n - 3][0]);
  return wrap180(deg(a1 - a0));
}

// Does the mirror across the chord cross the curve anywhere except the feet?
function seamCrossings(points) {
  const [x0, y0] = points[0];
  const [x1, y1] = points[points.length - 1];
  const dx = x1 - x0, dy = y1 - y0;
  const l2 = dx * dx + dy * dy || 1;
  const mirrored = points.map(([x, y]) => {
    const t = ((x - x0) * dx + (y - y0) * dy) / l2;
    const px = x0 + t * dx, py = y0 + t * dy;
    return [2 * px - x, 2 * py - y];
  });
  const step = Math.max(1, Math.floor(points.length / 60));
  const A = points.filter((_, i) => i % step === 0);
  const B = mirrored.filter((_, i) => i % step === 0);
  let hits = 0;
  for (let i = 0; i < A.length - 1; i += 1) {
    for (let j = 0; j < B.length - 1; j += 1) {
      if (Math.abs(i - j) < 2) continue;             // the feet themselves
      const [ax, ay] = A[i], [bx, by] = A[i + 1];
      const [cx, cy] = B[j], [dx2, dy2] = B[j + 1];
      const den = (bx - ax) * (dy2 - cy) - (by - ay) * (dx2 - cx);
      if (!den) continue;
      const u = ((cx - ax) * (dy2 - cy) - (cy - ay) * (dx2 - cx)) / den;
      const v = ((cx - ax) * (by - ay) - (cy - ay) * (bx - ax)) / den;
      if (u > 0 && u < 1 && v > 0 && v < 1) hits += 1;
    }
  }
  return hits;
}

const rows = registry.map((record) => {
  const note = noteByUid[record.uid] || {};
  const metric = metricByUid[record.uid] || {};
  const figure = figByUid[record.uid] || {};
  const points = pointsOf(record);
  const gap = legGap(points);
  const seam = points.length ? seamCrossings(points) : 0;
  const corner = gap === null ? "unknown"
    : Math.abs(gap - 90) <= 20 ? "corner"
    : gap > 135 || gap < 45 ? "stop" : "miter";
  const tasks = [];
  if (corner === "miter") tasks.push(`corner ${gap.toFixed(0)}°`);
  if (corner === "stop") tasks.push(`stop ${gap.toFixed(0)}°`);
  if (seam > 0) tasks.push(`seam ${seam}`);
  if (!note.offsets) tasks.push("rails off");
  if ((figure.marginPercent ?? 0) >= 30) tasks.push(`band ${figure.marginPercent}%`);
  return {
    uid: record.uid,
    name: (note.name || record.name),
    family: record.family_id,
    gap: gap === null ? null : Math.round(gap),
    corner, seam,
    offsets: note.offsets ? 1 : 0,
    margin: figure.marginPercent ?? null,
    crossings: metric.crossings ?? 0,
    inflections: metric.inflections ?? 0,
    tasks,
    score: tasks.length,
  };
});

rows.sort((a, b) => b.score - a.score || b.crossings - a.crossings || a.name.localeCompare(b.name));

const byTask = {};
for (const row of rows) for (const task of row.tasks) {
  const key = task.split(" ")[0];
  byTask[key] = (byTask[key] || 0) + 1;
}

console.log(`${rows.length} curves · ${rows.filter((r) => r.score).length} with an open design task`);
console.log(Object.entries(byTask).map(([key, count]) => `${key} ${count}`).join(" · "));
for (const row of rows.slice(0, 8)) console.log(`  ${row.name} — ${row.tasks.join(", ")}`);

if (process.argv.includes("--write")) {
  const lines = [
    "# DESIGN-TODO-int — the little things, curve by curve",
    "",
    "Generated by `node scripts/design_report.mjs --write` from the registry, the",
    "notes, the figures index and the analysis. Do not edit by hand.",
    "",
    `**${rows.filter((row) => row.score).length} of ${rows.length}** curves have at least one open`,
    "design task. Ranked by how many apply, then by crossing pairs.",
    "",
    "| task | curves | what it means |",
    "|---|---|---|",
    `| stop | ${byTask.stop || 0} | the legs are far from 90°, so the band should end at the corner, not wrap |`,
    `| corner | ${byTask.corner || 0} | the legs suit a corner; rotate the motif to split it |`,
    `| seam | ${byTask.seam || 0} | the leaf's halves cross at the waist |`,
    `| rails | ${byTask.rails || 0} | offsets are off; a line becomes a form with the rails on |`,
    `| band | ${byTask.band || 0} | the border is thick enough to crowd the centre |`,
    "",
    "## The list",
    "",
    "| curve | legs | corner | seam | rails | band % | crossings | infl | tasks |",
    "|---|---|---|---|---|---|---|---|---|",
    ...rows.filter((row) => row.score).map((row) =>
      `| ${row.name} | ${row.gap ?? "?"}° | ${row.corner} | ${row.seam} | ${row.offsets ? "on" : "off"} | ${row.margin ?? "?"} | ${row.crossings} | ${row.inflections} | ${row.tasks.join(", ")} |`),
    "",
    "## Curves with nothing open",
    "",
    rows.filter((row) => !row.score).map((row) => row.name).join(" · ") || "none",
    "",
  ];
  writeFileSync(path.join(ROOT, "state", "DESIGN-TODO-int.md"), lines.join("\n"));
  console.log("wrote state/DESIGN-TODO-int.md");
}
