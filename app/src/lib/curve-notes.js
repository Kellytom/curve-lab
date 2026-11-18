// Names, importance, the turn and the pieces of a curve set, in SQLite through
// Prisma. A save is a transaction; a bad uid is refused before a row is written.

import { z } from "zod";
import { prisma } from "./db.js";

const Note = z.object({
  uid: z.string().regex(/^c-\d{4}$/, "uid must look like c-0001"),
  name: z.string().trim().min(1).max(80).optional(),
  importance: z.number().int().min(0).max(10).optional(),
  rotation: z.number().int().min(-360).max(360).optional(),
  pieces: z.union([z.literal(1), z.literal(2), z.literal(4)]).optional(),
  border_uid: z.string().regex(/^c-\d{4}$/, "border uid must look like c-0001").optional(),
});

const Payload = z.object({ curves: z.array(Note) });

export function toNote(row) {
  return {
    uid: row.uid,
    name: row.name || undefined,
    importance: row.importance,
    rotation: row.rotation,
    pieces: row.pieces,
    border_uid: row.borderUid || undefined,
    updated: row.updatedAt?.toISOString?.() || undefined,
  };
}

export function validateNotes(payload) {
  return Payload.parse(payload).curves;
}

export async function readNotes() {
  const rows = await prisma.note.findMany({ orderBy: { uid: "asc" } });
  return { curves: rows.map(toNote) };
}

export async function saveNotes(payload) {
  const incoming = validateNotes(payload);
  if (!incoming.length) {
    const error = new Error("nothing to save");
    error.status = 400;
    throw error;
  }
  await prisma.$transaction(incoming.map((note) => prisma.note.upsert({
    where: { uid: note.uid },
    create: {
      uid: note.uid,
      name: note.name ?? null,
      importance: note.importance ?? 0,
      rotation: note.rotation ?? 0,
      pieces: note.pieces ?? 1,
      borderUid: note.border_uid ?? null,
    },
    update: {
      ...(note.name !== undefined ? { name: note.name } : {}),
      ...(note.importance !== undefined ? { importance: note.importance } : {}),
      ...(note.rotation !== undefined ? { rotation: note.rotation } : {}),
      ...(note.pieces !== undefined ? { pieces: note.pieces } : {}),
      ...(note.border_uid !== undefined ? { borderUid: note.border_uid } : {}),
    },
  })));
  return { saved: incoming.length };
}
