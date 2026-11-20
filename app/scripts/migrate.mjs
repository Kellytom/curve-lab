// Copy the JSON registry into the database, once, and prove the counts.
//
//   cd app && node scripts/migrate.mjs
//
// The JSON stays as the read-only index that seeds the database. After this
// runs, names, importance, rotation and pieces are edited in the database.

import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { PrismaClient } from "@prisma/client";

execFileSync("node", [path.join(import.meta.dirname, "backup-db.mjs")], { stdio: "inherit" });
const prisma = new PrismaClient();
const ROOT = path.resolve(import.meta.dirname, "..", "..");
const workbench = (name) => path.join(ROOT, "workbench", name);

const registry = JSON.parse(readFileSync(workbench("curve-registry.json"), "utf8"));
let notes = { curves: [] };
try { notes = JSON.parse(readFileSync(workbench("curve-notes.json"), "utf8")); } catch { /* none yet */ }
const starNames = new Set(
  (JSON.parse(readFileSync(workbench("finder-stars.json"), "utf8")).curves || []).map((s) => s.name),
);

const byUid = new Map(notes.curves.filter((n) => n.uid).map((n) => [n.uid, n]));

if (await prisma.curve.count() === 0) {
await prisma.$transaction(async (tx) => {
  for (const record of registry.curves) {
    await tx.curve.upsert({
      where: { uid: record.uid },
      create: {
        uid: record.uid,
        name: record.name,
        family: record.family_id || null,
        lists: JSON.stringify(record.lists || []),
        aliases: JSON.stringify(record.aliases || []),
        starred: Boolean(record.starred) || [record.name, ...(record.aliases || [])].some((n) => starNames.has(n)),
        candidate: Boolean(record.candidate),
      },
      update: {
        name: record.name,
        family: record.family_id || null,
        lists: JSON.stringify(record.lists || []),
        aliases: JSON.stringify(record.aliases || []),
        starred: Boolean(record.starred) || [record.name, ...(record.aliases || [])].some((n) => starNames.has(n)),
        candidate: Boolean(record.candidate),
      },
    });

    const note = byUid.get(record.uid) || {};
    await tx.note.upsert({
      where: { uid: record.uid },
      create: {
        uid: record.uid,
        name: note.name ?? null,
        importance: note.importance ?? record.importance ?? 0,
        rotation: note.rotation ?? 0,
        pieces: note.pieces ?? 1,
        borderUid: note.border_uid ?? null,
      },
      update: {
        name: note.name ?? null,
        importance: note.importance ?? record.importance ?? 0,
        rotation: note.rotation ?? 0,
        pieces: note.pieces ?? 1,
        borderUid: note.border_uid ?? null,
      },
    });
  }

  for (const set of registry.sets || []) {
    await tx.curveSet.upsert({
      where: { uid: set.uid },
      create: {
        uid: set.uid, name: set.name, innerUid: set.inner_uid,
        borderUid: set.border_uid, rotation: set.rotation,
        pieces: set.pieces, perSide: set.per_side, importance: set.importance,
      },
      update: {
        name: set.name, borderUid: set.border_uid, rotation: set.rotation,
        pieces: set.pieces, perSide: set.per_side, importance: set.importance,
      },
    });
  }
});
}

// Stars, users and plate stars are small edited stores; the JSON is their seed.
const starFile = workbench("finder-stars.json");
if (existsSync(starFile)) {
  for (const star of JSON.parse(readFileSync(starFile, "utf8")).curves || []) {
    await prisma.star.upsert({
      where: { name: star.name },
      create: { name: star.name, note: star.note ?? null, spec: star.spec ? JSON.stringify(star.spec) : null },
      update: { note: star.note ?? null, spec: star.spec ? JSON.stringify(star.spec) : null },
    });
  }
}
const userFile = path.join(ROOT, "app", "data", "users.json");
if (existsSync(userFile)) {
  for (const user of JSON.parse(readFileSync(userFile, "utf8")).users || []) {
    await prisma.user.upsert({
      where: { id: user.id },
      create: { id: user.id, name: user.name, email: user.email || null, role: user.role || "viewer", notes: user.notes || null },
      update: { name: user.name, email: user.email || null, role: user.role || "viewer", notes: user.notes || null },
    });
  }
}
const plateFile = workbench("starred.json");
if (existsSync(plateFile)) {
  for (const plate of JSON.parse(readFileSync(plateFile, "utf8")).plates || []) {
    await prisma.plateStar.upsert({
      where: { id: plate.id },
      create: { id: plate.id, note: plate.note ?? null },
      update: { note: plate.note ?? null },
    });
  }
}

const counts = {
  curves: await prisma.curve.count(),
  notes: await prisma.note.count(),
  sets: await prisma.curveSet.count(),
};
console.log("database", counts, "registry", {
  curves: registry.curves.length, sets: (registry.sets || []).length,
});
if (counts.curves !== registry.curves.length) {
  console.error("curve count does not match");
  process.exitCode = 1;
}
// The visible record: a seed writes every table's copy, since the database
// went from empty to full.
if (process.env.CURVE_LAB_SKIP_EXPORT !== "1") {
  const { execFileSync } = await import("node:child_process");
  const nodeBin = process.env.NODE24 || "node";
  try {
    execFileSync(nodeBin, ["scripts/export-data.mjs"], { cwd: path.resolve(import.meta.dirname, "..", ".."), stdio: "inherit" });
  } catch (error) {
    console.error(`warning: the data export failed, run scripts/export-data.mjs: ${error.message}`);
  }
}
await prisma.$disconnect();
