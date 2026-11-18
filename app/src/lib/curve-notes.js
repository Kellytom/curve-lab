// Naming and importance, kept beside the registry rather than inside it: the
// registry is rebuilt from the sources, and a rebuild must not lose a human's
// name or rating.
//
// A failed read is never a write; every save keeps the previous file; an empty
// list cannot replace a non-empty one.

import { copyFile, mkdir, readFile, rename, writeFile } from "node:fs/promises";
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { z } from "zod";

export const FORMAT = "curve-lab.curve-notes/1";

const Note = z.object({
  uid: z.string().regex(/^c-\d{4}$/, "uid must look like c-0001"),
  name: z.string().trim().min(1).max(80).optional(),
  importance: z.number().int().min(0).max(10).optional(),
}).passthrough();

const Payload = z.object({ curves: z.array(Note) });

export function notesPath(root) {
  return path.join(path.resolve(root), "workbench", "curve-notes.json");
}

export function readNotes(root) {
  const file = notesPath(root);
  if (!existsSync(file)) return { curves: [] };
  try {
    const data = JSON.parse(readFileSync(file, "utf8"));
    return Array.isArray(data.curves) ? { curves: data.curves } : { curves: [] };
  } catch {
    return { curves: [] };
  }
}

export async function saveNotes(payload, root) {
  const incoming = Payload.parse(payload).curves;
  const file = notesPath(root);
  const dir = path.dirname(file);
  await mkdir(dir, { recursive: true });
  const current = readNotes(root).curves;
  if (!incoming.length && current.length) {
    const error = new Error("refusing to empty the notes; send at least one curve");
    error.status = 409;
    throw error;
  }
  const byUid = new Map(current.map((note) => [note.uid, note]));
  for (const note of incoming) byUid.set(note.uid, { ...byUid.get(note.uid), ...note });
  if (existsSync(file)) {
    const backups = path.join(dir, "backups");
    await mkdir(backups, { recursive: true });
    const stamp = new Date().toISOString().replace(/[:.]/g, "-");
    await copyFile(file, path.join(backups, `curve-notes-${stamp}.json`));
  }
  const temp = `${file}.tmp`;
  await writeFile(temp, JSON.stringify({ format: FORMAT, curves: [...byUid.values()] }, null, 1) + "\n");
  await rename(temp, file);
  return { saved: byUid.size, path: file };
}
