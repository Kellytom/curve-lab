// Copy the JSON registry into the database, once, and prove the counts.
//
//   cd app && node scripts/migrate.mjs
//
// The JSON stays as the read-only index that seeds the database. After this
// runs, names, importance, rotation and pieces are edited in the database.

import { readFileSync } from "node:fs";
import path from "node:path";
import { PrismaClient } from "@prisma/client";

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
await prisma.$disconnect();
