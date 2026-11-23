// Render one saved curve's plate and figure, after the save has already answered.
//
//   node scripts/render_saved_curve.mjs <uid>
//
// The cut desk's save used to wait for these two renders inside the request: the plate at
// 1600 px and the figure both take seconds, up to 180 s each, so the button said "cutting…"
// for minutes and the operator reported, twice, that there was no way to save the cut curves
// (2026-11-23). The record is written before this runs; a failed render is logged, not lost.
// The dev server reloads when the files land, which is harmless: the page is already showing
// the saved banner. One run at a time: two saves rendering at once would each merge the
// figure index from a stale read (scripts/lib/render-lock.mjs).

import { execFile } from "node:child_process";
import { appendFileSync, mkdirSync } from "node:fs";
import path from "node:path";
import { promisify } from "node:util";
import { withLock } from "./lib/render-lock.mjs";

const run = promisify(execFile);
const ROOT = path.resolve(import.meta.dirname, "..");
const uid = process.argv[2];
if (!uid) {
  console.error("usage: node scripts/render_saved_curve.mjs <uid>");
  process.exit(2);
}

const LOG = path.join(ROOT, "state", "jobs", "render-saved.log");
mkdirSync(path.dirname(LOG), { recursive: true });
const note = (line) => {
  try { appendFileSync(LOG, `${new Date().toISOString()} ${uid} ${line}\n`); } catch { /* no log */ }
};

// The dev server exports CURVE_LAB_ROOT=.. relative to app/; a child run from the repo root
// would resolve one directory too high. Strip it for both scripts.
const cleanEnv = { ...process.env };
delete cleanEnv.CURVE_LAB_ROOT;

// One render at a time: the plate and figure indexes are merged, not replaced, so two saves
// rendering at once would each read the old list and the second would drop the first's entry.
try {
  await withLock(path.join(ROOT, "state", "jobs", "render.lock"), async () => {
    for (const script of ["print_plates.mjs", "curve_pngs.mjs"]) {
      try {
        await run(process.execPath, [path.join(ROOT, "scripts", script), "--only", uid],
          { cwd: ROOT, timeout: 240000, env: cleanEnv });
        note(`${script} ok`);
      } catch (error) {
        note(`${script} failed: ${String(error.message || error).slice(0, 300)}`);
      }
    }
  });
} catch (error) {
  note(`lock failed: ${String(error.message || error).slice(0, 300)}`);
}
