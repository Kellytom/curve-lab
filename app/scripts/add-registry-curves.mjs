// Upsert the registry's records into SQLite: curve, note and set rows.
//
//   cd app && node scripts/add-registry-curves.mjs
//
// migrate.mjs only seeds an empty database. This is the additive path: every
// registry record that has no row yet is created with its name, importance and
// starred flag, and a set row is created for it, so check-db stays equal.

import { readFileSync } from "node:fs";
import path from "node:path";
import { PrismaClient } from "@prisma/client";

const ROOT = path.resolve(import.meta.dirname, "..", "..");
const registry = JSON.parse(readFileSync(path.join(ROOT, "workbench", "curve-registry.json"), "utf8"));
const prisma = new PrismaClient();

let created = 0;
for (const record of registry.curves) {
  const existing = await prisma.curve.findUnique({ where: { uid: record.uid } });
  if (existing) continue;
  await prisma.$transaction([
    prisma.curve.create({
      data: {
        uid: record.uid,
        name: record.name,
        family: record.family_id || record.family || null,
        lists: JSON.stringify(record.lists || []),
        aliases: JSON.stringify(record.aliases || []),
        starred: Boolean(record.starred),
        candidate: Boolean(record.candidate),
      },
    }),
    prisma.note.create({
      data: {
        uid: record.uid,
        name: record.name,
        importance: Number(record.importance || 0),
        rotation: Number(record.rotation || 0),
        pieces: Number(record.pieces || 1),
        borderUid: record.borderUid || null,
        perSide: Number(record.perSide ?? 9),
        borderTurn: Number(record.borderTurn || 0),
        offsets: Number(record.offsets || 0),
        widthPct: Number(record.widthPct || 0),
        plus: Number(record.plus || 0),
        minus: Number(record.minus || 0),
        profile: record.profile || null,
        formula: record.formula ? JSON.stringify(record.formula) : null,
        params: record.params ? JSON.stringify(record.params) : null,
        grid: record.grid || null,
        stationRule: record.params?.stationRule || null,
        algorithm: record.conversion?.algorithm || record.kind || null,
        conversion: record.conversion ? JSON.stringify(record.conversion) : null,
      },
    }),
    prisma.curveSet.create({
      data: {
        uid: `set-${record.uid}`,
        name: record.name,
        innerUid: record.uid,
        borderUid: record.uid,
        rotation: 0,
        pieces: 1,
        perSide: 9,
        importance: Number(record.importance || 0),
      },
    }),
  ]);
  created += 1;
  console.log(`created ${record.uid} ${record.name}`);
}
console.log(`${created} created, registry has ${registry.curves.length}`);
await prisma.$disconnect();
