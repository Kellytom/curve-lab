// Copy the registry's plate turn into the database note, so the desk and the pages agree.
//
//   node app/scripts/sync-turns.mjs
//
// The plates read workbench/curve-registry.json; the tune desk reads Note.rotation. They had
// drifted (the registry at -90, the note still at 45), and the operator saw 45 on a page that
// reads the note.
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";

const require = createRequire(import.meta.url);
const { PrismaClient } = require("@prisma/client");
const ROOT = path.resolve(import.meta.dirname, "..", "..");
const registry = JSON.parse(readFileSync(path.join(ROOT, "workbench", "curve-registry.json"), "utf8"));
const prisma = new PrismaClient();

let changed = 0;
try {
  for (const record of registry.curves) {
    const transform = record.transform || { degrees: 0 };
    const degrees = Number(transform.degrees || 0);
    const note = await prisma.note.findUnique({ where: { uid: record.uid } });
    if (!note) continue;
    let current = null;
    try { current = note.transform ? JSON.parse(note.transform) : null; } catch { current = null; }
    if (current && Number(current.degrees) === degrees) continue;
    await prisma.note.update({
      where: { uid: record.uid },
      data: {
        rotation: degrees,
        transform: JSON.stringify({
          degrees,
          matrix: transform.matrix || [["1", "0"], ["0", "1"]],
          exact: transform.exact !== false,
        }),
      },
    });
    changed += 1;
  }
} finally {
  await prisma.$disconnect();
}
console.log(`${changed} note(s) turned to match the registry`);
