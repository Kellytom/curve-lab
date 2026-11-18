// Put a snapshot back. The current database is copied aside first, so a restore
// is itself undoable.
//
//   cd app && node scripts/restore-db.mjs                # the newest snapshot
//   cd app && node scripts/restore-db.mjs dev-2026-....db # a named one

import { copyFileSync, existsSync, readdirSync, statSync } from "node:fs";
import path from "node:path";

const ROOT = path.resolve(import.meta.dirname, "..", "..");
const DB = path.join(ROOT, "app", "prisma", "dev.db");
const DIR = path.join(ROOT, "state", "backups", "db");

const wanted = process.argv[2];
const files = existsSync(DIR) ? readdirSync(DIR).filter((n) => /^dev-.*\.db$/.test(n)).sort() : [];
const choice = wanted || files.at(-1);
if (!choice) {
  console.error("no snapshot found");
  process.exit(1);
}
const source = path.join(DIR, path.basename(choice));
if (!existsSync(source)) {
  console.error(`no such snapshot: ${choice}`);
  process.exit(1);
}

if (existsSync(DB)) {
  const aside = `${DB}.before-restore-${Date.now()}`;
  copyFileSync(DB, aside);
  console.log(`current database kept at ${path.relative(ROOT, aside)}`);
}
copyFileSync(source, DB);
console.log(`restored ${path.relative(ROOT, source)} · ${(statSync(DB).size / 1024).toFixed(0)} KB`);
