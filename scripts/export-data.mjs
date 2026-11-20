// Write the visible record from SQLite, or check that it is current.
//
//   PATH="$HOME/node24/bin:$PATH" node scripts/export-data.mjs           # write data/
//   PATH="$HOME/node24/bin:$PATH" node scripts/export-data.mjs --check   # fail if stale
//
// One file per table under `data/`, one object per row, plus `data/schema.json`
// and `data/manifest.json`. `data/README.md` explains every field in words.
// The save endpoints call the same exporter, so a save is a save.

import { exportAll, check } from "../app/src/lib/data-export.js";

const wantCheck = process.argv.includes("--check");
const wantQuiet = process.argv.includes("--quiet");

if (wantCheck) {
  const problems = await check();
  if (problems.length) {
    for (const problem of problems) console.error(problem);
    process.exitCode = 1;
  } else if (!wantQuiet) {
    console.log("data export is current");
  }
} else {
  const written = await exportAll();
  for (const { name, count } of written) console.log(`${name.padEnd(16)} ${String(count).padStart(5)} rows`);
  console.log("wrote data/, data/schema.json and data/manifest.json");
}
