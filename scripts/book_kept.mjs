// The kept set as a print manifest: exactly the curves on /plates, with their files.
//
// The kept rule is imported from app/src/lib/provenance.js — the same `isKept` the
// plates page uses, so the manifest and the page cannot drift. The order is the
// plates order (stars, variants beside their parent).
//
//   node scripts/book_kept.mjs
//
// Writes book/kept.json. The PNG/SVG paths are the print render's; a missing file
// is listed, not hidden.

import { existsSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { isKept, MIN_STARS, provenanceFor } from "../app/src/lib/provenance.js";
import { orderPlates } from "../app/src/lib/plate-order.js";

const ROOT = path.resolve(import.meta.dirname, "..");
const registry = JSON.parse(readFileSync(path.join(ROOT, "workbench", "curve-registry.json"), "utf8")).curves;
const exported = JSON.parse(readFileSync(path.join(ROOT, "data", "curves.json"), "utf8")).rows;

// The export carries the saved note as an object; the plates page passes its text.
const byUid = new Map(registry.map((record) => [record.uid, { ...record }]));
for (const row of exported) {
  const base = byUid.get(row.uid) || {};
  byUid.set(row.uid, {
    ...base,
    ...row,
    stars: row.stars ?? row.note?.importance ?? 0,
    note: row.note?.note || "",
    params: base.params ?? row.note?.params ?? row.params,
  });
}

const kept = orderPlates([...byUid.values()].filter((curve) => isKept(curve, byUid)), "stars");
const rows = kept.map((curve) => {
  const { uid } = curve;
  const files = {
    printPng: `book/print/${uid}-3000-grey-300dpi.png`,
    printSvg: `book/print/${uid}.svg`,
    webPng: `app/public/plates-web/${uid}-1600-grey.png`,
    figurePng: `app/public/figures/${uid}.png`,
  };
  const present = Object.fromEntries(
    Object.entries(files).map(([key, file]) => [key, existsSync(path.join(ROOT, file))]));
  return {
    uid,
    name: curve.name,
    stars: curve.stars ?? 0,
    family: curve.family_id || curve.family || "",
    provenance: provenanceFor(curve, byUid),
    files,
    present,
  };
});

const missing = rows.flatMap((row) =>
  Object.entries(row.present).filter(([, there]) => !there).map(([key]) => `${row.uid}:${key}`));

const manifest = {
  format: "curve-lab kept set 1",
  generated: new Date().toISOString(),
  rule: `kept when rated ${MIN_STARS} or more, or a variant of a kept parent`,
  count: rows.length,
  missing,
  rows,
};
writeFileSync(path.join(ROOT, "book", "kept.json"), `${JSON.stringify(manifest, null, 1)}\n`);
console.log(`${rows.length} kept curves, ${missing.length} missing files${missing.length ? `: ${missing.slice(0, 8).join(", ")}` : ""}`);
console.log("wrote book/kept.json");
