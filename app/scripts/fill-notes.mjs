// Fill the empty database notes with the generated description from data/curves-readable.json.
//
//   PATH="$HOME/node24/bin:$PATH" node app/scripts/fill-notes.mjs
//
// Only a note that is empty is written: the operator's own notes are never replaced. The text
// says what the curve is, its speed pair or point count, its exact measurements, its turn and
// whether the outside rail has cut points.
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";

const require = createRequire(import.meta.url);
const { PrismaClient } = require("@prisma/client");
const ROOT = path.resolve(import.meta.dirname, "..", "..");
const readable = JSON.parse(readFileSync(path.join(ROOT, "data", "curves-readable.json"), "utf8"));
const prisma = new PrismaClient();

let filled = 0;
let kept = 0;
try {
  for (const curve of readable.curves) {
    const note = await prisma.note.findUnique({ where: { uid: curve.uid } });
    if (!note) continue;
    if (note.note && String(note.note).trim()) { kept += 1; continue; }
    await prisma.note.update({ where: { uid: curve.uid }, data: { note: curve.description } });
    filled += 1;
  }
} finally {
  await prisma.$disconnect();
}
console.log(`${filled} note(s) filled, ${kept} kept as written`);
