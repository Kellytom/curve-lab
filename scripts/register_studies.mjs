// Register the study-page curves and label the in-progress family.
//
//   node scripts/register_studies.mjs --write
//   node scripts/register_studies.mjs            # report only
//
// The operator, 2026-11-23: "make sure even the temporary or in progress curves are in the
// database labeled as such". A curve that lives on a study page only — a proposed classical
// curve, a Tschirnhausen variation — gets a Study row with its page and status. The curves that
// are already in the collection but are still proposals (the Tschirnhausen family on
// /extra-curves/ and /class-v/) get status "in-progress" on their Curve row.
//
// The list of proposals comes from app/src/data/extra-curves.json (generated); the variation
// names come from workbench/side-tests.html. Nothing here invents geometry.

import { readFileSync } from "node:fs";
import path from "node:path";
const ROOT = path.resolve(import.meta.dirname, "..");
// run from the repo root: the default URL in db.js is relative to the process, so name it.
process.env.DATABASE_URL ||= `file:${path.join(ROOT, "app", "prisma", "dev.db")}`;
const { prisma } = await import("../app/src/lib/db.js");
const write = process.argv.includes("--write");

const SIDE_TESTS = "workbench/side-tests.html";
const variations = [
  ["study-tschirnhausen-whole", "t = −12/5 → 12/5 · the whole curve"],
  ["study-tschirnhausen-loop", "the loop at the node"],
  ["study-tschirnhausen-plus", "the + arm, node → tip"],
  ["study-tschirnhausen-minus", "the − arm, tip → node"],
  ["study-tschirnhausen-plus-t2", "the + arm, trimmed at t = 2"],
  ["study-tschirnhausen-plus-mirror", "the + arm, mirrored"],
];

const gaps = JSON.parse(readFileSync(path.join(ROOT, "app/src/data/extra-curves.json"), "utf8"));
const proposals = (gaps.missingNamed || []).map((curve) => [
  `study-${curve.key}`,
  curve.key.replace(/-/g, " "),
]);

const wanted = [
  ...variations.map(([uid, name]) => ({ uid, name, page: SIDE_TESTS, status: "in-progress" })),
  ...proposals.map(([uid, name]) => ({ uid, name, page: "/extra-curves/", status: "proposed" })),
];

const known = new Set((await prisma.study.findMany()).map((row) => row.uid));
const missing = wanted.filter((row) => !known.has(row.uid));

// The Tschirnhausen family is in the collection but is still the proposal made real.
const family = ["c-0398", "c-0399", "c-0400", "c-0401"];
const curves = await prisma.curve.findMany({ where: { uid: { in: family } },
  select: { uid: true, status: true } });
const relabel = curves.filter((row) => row.status !== "in-progress");

if (!write) {
  console.log(`studies: ${wanted.length} wanted, ${missing.length} missing`);
  for (const row of missing) console.log(`  missing ${row.uid} · ${row.page} · ${row.status}`);
  console.log(`curves: ${relabel.length} of ${family.length} not yet in-progress`);
  process.exit(missing.length || relabel.length ? 1 : 0);
}

for (const row of missing) {
  await prisma.study.create({ data: { ...row, pngIgnored: true,
    note: row.page === SIDE_TESTS
      ? "a glue piece on the side-tests sheet; its slope is not rational at the node"
      : "a named classical curve proposed on the gaps page; no record yet" } });
}
for (const row of relabel) {
  await prisma.curve.update({ where: { uid: row.uid }, data: { status: "in-progress" } });
}
console.log(`studies: added ${missing.length}; curves: relabelled ${relabel.length}`);
await prisma.$disconnect();
