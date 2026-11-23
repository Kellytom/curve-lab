// Set one curve's pngIgnored flag, then make git follow it.
//
//   node scripts/set_png_flag.mjs <uid> keep     # this PNG is part of the record
//   node scripts/set_png_flag.mjs <uid> ignore   # derived: stays out of git
//
// The flag is on Curve and Study (app/prisma/schema.prisma). Flipping it is not enough on its
// own: `git rm --cached` or `git add -f` must follow, which is what curve_pngs_git.mjs does.
// This names the one curve so the operator does not have to open SQLite for a single picture
// (operator, 2026-11-23: "put a flag in the database for every curve ... and then make sure
// they are").

import { execFileSync } from "node:child_process";
import path from "node:path";

const ROOT = path.resolve(import.meta.dirname, "..");
const [uid, choice] = process.argv.slice(2);

if (!uid || !["keep", "ignore"].includes(choice)) {
  console.error("usage: node scripts/set_png_flag.mjs <uid> keep|ignore");
  process.exit(2);
}

process.env.DATABASE_URL ||= `file:${path.join(ROOT, "app", "prisma", "dev.db")}`;
const { prisma } = await import("../app/src/lib/db.js");

const pngIgnored = choice === "ignore";
const curve = await prisma.curve.findUnique({ where: { uid } });
const study = curve ? null : await prisma.study.findUnique({ where: { uid } });
if (!curve && !study) {
  console.error(`no Curve or Study row has uid ${uid}`);
  await prisma.$disconnect();
  process.exit(1);
}
if (curve) await prisma.curve.update({ where: { uid }, data: { pngIgnored } });
else await prisma.study.update({ where: { uid }, data: { pngIgnored } });
console.log(`${uid}: pngIgnored = ${pngIgnored} (${curve ? "curve" : "study"})`);

// The index change is part of the same act, never a later forgotten step.
execFileSync(process.execPath, [path.join(ROOT, "scripts", "curve_pngs_git.mjs"), "--write"],
  { cwd: ROOT, stdio: "inherit" });
await prisma.$disconnect();
