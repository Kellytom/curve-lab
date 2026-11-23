// Keep the plate and figure PNGs in step with the database's pngIgnored flag.
//
//   node scripts/curve_pngs_git.mjs            # check: what disagrees with the flag
//   node scripts/curve_pngs_git.mjs --write    # untrack ignored PNGs, force-add kept ones
//
// Every curve (Curve) and every study-page curve (Study) carries `pngIgnored`: true means the
// render is derived and stays out of git, false means this one image is part of the record.
// The renders are `app/public/plates-web/<uid>-1600-grey.png` and `app/public/figures/<uid>.png`.
//
// A PNG with no row is also a fault: every curve on a page must be in the database.
// The operator, 2026-11-23: "put a flag in the database for every curve that indicates whether
// its png should be git ignored... and then make sure they are."

import { execFileSync } from "node:child_process";
import { existsSync, readdirSync } from "node:fs";
import path from "node:path";
const ROOT = path.resolve(import.meta.dirname, "..");
// run from the repo root: the default URL in db.js is relative to the process, so name it.
process.env.DATABASE_URL ||= `file:${path.join(ROOT, "app", "prisma", "dev.db")}`;
const { prisma } = await import("../app/src/lib/db.js");
const PLATES = path.join(ROOT, "app", "public", "plates-web");
const FIGURES = path.join(ROOT, "app", "public", "figures");
const write = process.argv.includes("--write");

const git = (...args) => {
  try {
    return execFileSync("git", args, { cwd: ROOT, encoding: "utf8" });
  } catch (error) {
    return String(error.stdout || "");
  }
};

const tracked = new Set(git("ls-files", "app/public/plates-web", "app/public/figures")
  .split("\n").filter(Boolean));

const owners = new Map();
for (const row of await prisma.curve.findMany({ select: { uid: true, name: true, pngIgnored: true, status: true } })) {
  owners.set(row.uid, { name: row.name, ignored: row.pngIgnored, kind: "curve", status: row.status });
}
for (const row of await prisma.study.findMany({ select: { uid: true, name: true, pngIgnored: true, status: true } })) {
  owners.set(row.uid, { name: row.name, ignored: row.pngIgnored, kind: "study", status: row.status });
}

const files = [];
if (existsSync(PLATES)) {
  for (const name of readdirSync(PLATES)) {
    if (!name.endsWith(".png")) continue;
    files.push({ rel: `app/public/plates-web/${name}`, uid: name.replace(/-1600-[a-z]+\.png$/, "") });
  }
}
if (existsSync(FIGURES)) {
  for (const name of readdirSync(FIGURES)) {
    if (!name.endsWith(".png")) continue;
    files.push({ rel: `app/public/figures/${name}`, uid: name.replace(/\.png$/, "") });
  }
}

const bad = [];
for (const file of files) {
  const owner = owners.get(file.uid);
  const isTracked = tracked.has(file.rel);
  if (!owner) {
    bad.push({ ...file, why: "no Curve or Study row owns this PNG", fix: "untrack" });
  } else if (owner.ignored && isTracked) {
    bad.push({ ...file, why: `tracked, but ${owner.kind} ${file.uid} (${owner.status}) ignores it`, fix: "untrack" });
  } else if (!owner.ignored && !isTracked) {
    bad.push({ ...file, why: `not tracked, but ${owner.kind} ${file.uid} keeps it`, fix: "add" });
  }
}

// A kept curve whose PNG has disappeared is also a disagreement worth naming.
for (const [uid, owner] of owners) {
  if (owner.ignored) continue;
  if (!files.some((file) => file.uid === uid)) {
    bad.push({ rel: `${uid}.png`, uid, why: `kept by ${owner.kind}, but no PNG exists`, fix: "render" });
  }
}

if (!bad.length) {
  const kept = [...owners.values()].filter((owner) => !owner.ignored).length;
  console.log(`pngs: ok (${files.length} files, ${owners.size} rows, ${kept} kept in git)`);
  await prisma.$disconnect();
  process.exit(0);
}

for (const row of bad) console.log(`pngs: ${row.rel}: ${row.why}`);
if (!write) {
  console.log(`pngs: ${bad.length} disagreements; run --write to follow the flag`);
  await prisma.$disconnect();
  process.exit(1);
}

const untrack = bad.filter((row) => row.fix === "untrack").map((row) => row.rel);
const add = bad.filter((row) => row.fix === "add").map((row) => row.rel);
if (untrack.length) git("rm", "--cached", "--quiet", "--", ...untrack);
if (add.length) git("add", "-f", "--", ...add);
console.log(`pngs: untracked ${untrack.length}, force-added ${add.length}`);
await prisma.$disconnect();
