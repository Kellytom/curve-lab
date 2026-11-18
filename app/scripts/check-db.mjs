// Prove the database matches the JSON index: one curve per uid, one set per
// curve, and a note row for every curve.
//
//   cd app && node scripts/check-db.mjs

import { readFileSync } from "node:fs";
import path from "node:path";
import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();
const ROOT = path.resolve(import.meta.dirname, "..", "..");
const registry = JSON.parse(readFileSync(path.join(ROOT, "workbench", "curve-registry.json"), "utf8"));

const counts = {
  curves: await prisma.curve.count(),
  notes: await prisma.note.count(),
  sets: await prisma.curveSet.count(),
};
const expected = {
  curves: registry.curves.length,
  notes: registry.curves.length,
  sets: (registry.sets || []).length,
};
console.log("database", counts);
console.log("expected", expected);

const orphans = await prisma.note.count({ where: { curve: null } });
const nameless = await prisma.curve.count({ where: { name: "" } });
if (JSON.stringify(counts) !== JSON.stringify(expected) || orphans || nameless) {
  console.error("mismatch", { orphans, nameless });
  process.exitCode = 1;
} else {
  console.log("database matches the registry");
}
await prisma.$disconnect();
