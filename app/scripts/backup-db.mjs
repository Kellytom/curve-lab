// A consistent snapshot of the database, with rotation and an integrity check.
//
//   cd app && node scripts/backup-db.mjs
//
// `VACUUM INTO` writes a complete copy without stopping the app, and the copy is
// checked with `PRAGMA integrity_check`. The last 20 snapshots are kept in
// state/backups/db (gitignored). Run by `npm run dev` and `npm run build`, and
// by the migration before it writes.

import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, readdirSync, statSync, unlinkSync } from "node:fs";
import path from "node:path";

const ROOT = path.resolve(import.meta.dirname, "..", "..");
const DB = path.join(ROOT, "app", "prisma", "dev.db");
const DIR = path.join(ROOT, "state", "backups", "db");
const KEEP = 20;

if (!existsSync(DB)) {
  console.log("no database yet: nothing to back up");
  process.exit(0);
}

mkdirSync(DIR, { recursive: true });
const stamp = new Date().toISOString().replace(/[:.]/g, "-");
const target = path.join(DIR, `dev-${stamp}.db`);

execFileSync("sqlite3", [DB, `.backup '${target}'`], { stdio: "pipe" });
const check = execFileSync("sqlite3", [target, "PRAGMA integrity_check;"], { encoding: "utf8" }).trim();
if (check !== "ok") {
  console.error(`backup failed its integrity check: ${check}`);
  process.exit(1);
}

const files = readdirSync(DIR).filter((name) => /^dev-.*\.db$/.test(name)).sort();
for (const old of files.slice(0, Math.max(0, files.length - KEEP))) {
  unlinkSync(path.join(DIR, old));
}
console.log(`backup ${path.relative(ROOT, target)} · ${(statSync(target).size / 1024).toFixed(0)} KB · integrity ok`);
