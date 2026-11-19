// Finder stars, in SQLite through Prisma. The JSON file is written afterwards
// as an export: the Python registry build reads it without a Node driver.
//
// A star is keyed by the curve's name; a rename keeps the star because the
// registry carries the old name as an alias.

import { copyFileSync, existsSync, mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";
import { z } from "zod";
import { prisma } from "./db.js";

const Star = z.object({
  name: z.string().min(1),
  note: z.string().optional(),
  spec: z.record(z.string()).optional(),
}).passthrough();

const Payload = z.object({ curves: z.array(Star) });

export function validateFinderStars(payload) {
  if (!payload || !Array.isArray(payload.curves)) throw new Error("expected { curves: [...] }");
  const parsed = Payload.parse(payload).curves;
  const byName = new Map();
  for (const star of parsed) {
    const existing = byName.get(star.name);
    byName.set(star.name, existing ? { ...existing, ...star } : star);
  }
  return [...byName.values()];
}

export async function readFinderStars() {
  const rows = await prisma.star.findMany({ orderBy: { name: "asc" } });
  return {
    source: "database",
    curves: rows.map((row) => ({
      name: row.name,
      ...(row.note ? { note: row.note } : {}),
      ...(row.spec ? { spec: JSON.parse(row.spec) } : {}),
    })),
  };
}

function exportJson(root, curves) {
  const dir = path.join(path.resolve(root), "workbench");
  mkdirSync(dir, { recursive: true });
  const file = path.join(dir, "finder-stars.json");
  if (existsSync(file)) copyFileSync(file, path.join(dir, "finder-stars.backup.json"));
  writeFileSync(file, JSON.stringify({ format: "curve-lab.finder-stars/1", curves }, null, 1) + "\n");
  return file;
}

export async function saveFinderStars(payload, root) {
  const curves = validateFinderStars(payload);
  if (!curves.length) {
    const current = await prisma.star.count();
    if (current) {
      const error = new Error("refusing to empty the star list");
      error.status = 409;
      throw error;
    }
  }
  // A save adds and updates. It never deletes a name the client did not send:
  // a browser with a partial list wiped four stars that way on 2026-11-19.
  // Removing a star is explicit, in `removed`.
  const removed = Array.isArray(payload?.removed) ? payload.removed : [];
  const operations = curves.map((star) => prisma.star.upsert({
    where: { name: star.name },
    create: {
      name: star.name,
      note: star.note ?? null,
      spec: star.spec ? JSON.stringify(star.spec) : null,
    },
    update: {
      note: star.note ?? null,
      spec: star.spec ? JSON.stringify(star.spec) : null,
    },
  }));
  await prisma.$transaction([
    ...(removed.length ? [prisma.star.deleteMany({ where: { name: { in: removed } } })] : []),
    ...operations,
  ]);
  const file = exportJson(root, curves.map((star) => ({
    name: star.name, ...(star.note ? { note: star.note } : {}),
    ...(star.spec ? { spec: star.spec } : {}),
  })));
  return { saved: curves.length, path: file };
}
