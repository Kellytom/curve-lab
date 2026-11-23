// Every curve on the study pages is a database row, with a status.
//
//   node scripts/check_page_curves.mjs
//
// The operator, 2026-11-23: "make sure even the temporary or in progress curves are in the
// database labeled as such, such as /extra-curves/, and 'Tschirnhausen and variations' in
// workbench/side-tests.html, also in all the glue curves and /class-v/."
//
// A curve in the collection is a Curve row; a page-only curve is a Study row naming its page.
// An unknown status is a fault too, because a label nobody can read is not a label.

import { readFileSync } from "node:fs";
import path from "node:path";

const ROOT = path.resolve(import.meta.dirname, "..");
process.env.DATABASE_URL ||= `file:${path.join(ROOT, "app", "prisma", "dev.db")}`;
const { prisma } = await import("../app/src/lib/db.js");

const CURVE_STATUS = new Set(["kept", "in-progress", "temporary", "proposed"]);
const STUDY_STATUS = new Set(["proposed", "in-progress", "temporary"]);

const curves = await prisma.curve.findMany({ select: { uid: true, name: true, status: true } });
const studies = await prisma.study.findMany({ select: { uid: true, name: true, page: true, status: true } });
const curveByUid = new Map(curves.map((row) => [row.uid, row]));
const studyByUid = new Map(studies.map((row) => [row.uid, row]));

const bad = [];
const needCurve = (uid, where) => {
  if (!curveByUid.has(uid)) bad.push(`${where}: ${uid} has no Curve row`);
};
const needStudy = (uid, page, where) => {
  const row = studyByUid.get(uid);
  if (!row) bad.push(`${where}: ${uid} has no Study row`);
  else if (row.page !== page) bad.push(`${where}: ${row.uid} is filed under ${row.page}, not ${page}`);
};

for (const row of curves) {
  if (!CURVE_STATUS.has(row.status)) bad.push(`curve ${row.uid}: status ${JSON.stringify(row.status)}`);
}
for (const row of studies) {
  if (!STUDY_STATUS.has(row.status)) bad.push(`study ${row.uid}: status ${JSON.stringify(row.status)}`);
}

// side-tests.html: every section that names a uid must be in the collection; the Tschirnhausen
// sheet is six study pieces, not collection curves.
const sideTests = readFileSync(path.join(ROOT, "workbench", "side-tests.html"), "utf8");
for (const match of sideTests.matchAll(/<section class="curve"><h2>([^<]+)<\/h2>/g)) {
  const heading = match[1];
  const uid = heading.match(/\bc-\d{4}[a-z]*\b/)?.[0];
  if (uid) needCurve(uid, "side-tests.html");
  else if (/^Tschirnhausen and variations/.test(heading)) {
    for (const piece of ["whole", "loop", "plus", "minus", "plus-t2", "plus-mirror"]) {
      needStudy(`study-tschirnhausen-${piece}`, "workbench/side-tests.html", "side-tests.html");
    }
  } else bad.push(`side-tests.html: "${heading}" names no uid and no study sheet`);
}

// extra-curves.json: the added family is in the collection; the proposals are studies.
const gaps = JSON.parse(readFileSync(path.join(ROOT, "app", "src", "data", "extra-curves.json"), "utf8"));
for (const row of gaps.addedOnRequest || []) {
  needCurve(row.uid, "/extra-curves/ (added on request)");
  if (curveByUid.get(row.uid)?.status !== "in-progress") {
    bad.push(`/extra-curves/: ${row.uid} is ${curveByUid.get(row.uid)?.status}, not in-progress`);
  }
}
for (const row of gaps.missingNamed || []) {
  needStudy(`study-${row.key}`, "/extra-curves/", "/extra-curves/ (proposed)");
}

// class-v.astro draws one collection curve.
const classV = readFileSync(path.join(ROOT, "app", "src", "pages", "class-v.astro"), "utf8");
for (const uid of new Set(classV.match(/\bc-\d{4}[a-z]*\b/g) || [])) needCurve(uid, "/class-v/");

// /glue/ stores no curve: the connector is computed from two typed slopes, so there is no row
// to check. Say so rather than pretending it was covered.
if (!/c-\d{4}/.test(readFileSync(path.join(ROOT, "app", "src", "pages", "glue.astro"), "utf8"))) {
  console.log("page curves: /glue/ has no stored curve (computed live), nothing to label");
}

for (const line of bad) console.log(`page curves: ${line}`);
if (bad.length) {
  console.log(`page curves: ${bad.length} problem(s)`);
  await prisma.$disconnect();
  process.exit(1);
}
console.log(`page curves: ok (${curves.length} curves, ${studies.length} studies, every status known)`);
await prisma.$disconnect();
