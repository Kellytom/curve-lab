// Write the visible record from SQLite, or check that it is current.
//
//   PATH="$HOME/node24/bin:$PATH" node scripts/export-data.mjs                 # write data/
//   PATH="$HOME/node24/bin:$PATH" node scripts/export-data.mjs --table jobs    # write one file
//   PATH="$HOME/node24/bin:$PATH" node scripts/export-data.mjs --check         # refresh, then verify
//
// One file per table under `data/`, one object per row, plus `data/schema.json`
// and `data/manifest.json`. `data/README.md` explains every field in words.
// The save endpoints and the bulk writers call the same exporter, so a write
// to the database is also a write to the visible record.
//
// `--check` refreshes first and verifies second: the failure mode it can still
// catch is a save that lands inside the verify itself, not a copy that was old
// before the check started. Whoever writes the database refreshes the copy.

import { exportAll, exportTable, check } from "../app/src/lib/data-export.js";

const args = process.argv.slice(2);
const wantCheck = args.includes("--check");
const wantQuiet = args.includes("--quiet");
const tableIndex = args.indexOf("--table");
const table = tableIndex >= 0 ? args[tableIndex + 1] : null;

if (table && wantCheck) {
  console.error("--table writes one file; --check verifies the whole record. Pick one.");
  process.exitCode = 1;
} else if (table) {
  const { name, count } = await exportTable(table);
  console.log(`${name.padEnd(16)} ${String(count).padStart(5)} rows`);
} else if (wantCheck) {
  const refreshed = await exportAll();
  if (!wantQuiet) {
    for (const { name, count } of refreshed) {
      console.log(`${name.padEnd(16)} ${String(count).padStart(5)} rows`);
    }
  }
  const problems = await check();
  if (problems.length) {
    for (const problem of problems) console.error(problem);
    process.exitCode = 1;
  } else if (!wantQuiet) {
    console.log("data export refreshed and current");
  }
} else {
  const written = await exportAll();
  for (const { name, count } of written) console.log(`${name.padEnd(16)} ${String(count).padStart(5)} rows`);
  console.log("wrote data/, data/schema.json and data/manifest.json");
}
