// Every sandbox decision, as a readable file.
//
//   cd app && node scripts/export-sandbox.mjs
//
// Writes workbench/sandbox-curves.json: one object per row of the SandboxCurve table,
// with a header that says what each field means. The database is the store; this file
// is the visible copy, and the 5-minute sync pushes it.

import { writeFileSync, readFileSync } from "node:fs";
import path from "node:path";
import { PrismaClient } from "@prisma/client";

const ROOT = path.resolve(import.meta.dirname, "..", "..");
const OUT = path.join(ROOT, "workbench", "sandbox-curves.json");
const prisma = new PrismaClient();

const rows = await prisma.sandboxCurve.findMany({ orderBy: { name: "asc" } });
const curves = rows.map((row) => {
  let data = {};
  try { data = JSON.parse(row.data); } catch { data = { raw: row.data }; }
  return { name: row.name, ...data, savedAt: row.updatedAt.toISOString() };
});

writeFileSync(OUT, JSON.stringify({
  format: "curve-lab.sandbox-curves/1",
  written: new Date().toISOString(),
  about: "One object per SandboxCurve row. `name` is the key; `decision` is keep, later or reject; the rest is whatever the page that saved it wrote.",
  fields: {
    name: "the record's key, e.g. h-radius-3-4-quadratic",
    decision: "keep | later | reject (the hybrid desk)",
    crossedAt: "when the decision was made (ISO time)",
    savedAt: "when the row was last written (ISO time)",
  },
  count: curves.length,
  curves,
}, null, 1) + "\n");

console.log(`wrote ${path.relative(ROOT, OUT)}: ${curves.length} rows`);
await prisma.$disconnect();
