// Names, importance, the turn and the pieces of a curve set, in SQLite through
// Prisma. A save is a transaction; a bad uid is refused before a row is written.

import { copyFileSync, existsSync, writeFileSync } from "node:fs";
import path from "node:path";
import { z } from "zod";
import { prisma } from "./db.js";
import { repoRoot } from "./gallery.js";

const Note = z.object({
  uid: z.string().regex(/^c-\d{4}$/, "uid must look like c-0001"),
  name: z.string().trim().min(1).max(80).optional(),
  importance: z.number().int().min(0).max(10).optional(),
  rotation: z.number().int().min(-360).max(360).optional(),
  pieces: z.union([z.literal(1), z.literal(2), z.literal(4)]).optional(),
  border_uid: z.string().regex(/^c-\d{4}$/, "border uid must look like c-0001").optional(),
  perSide: z.number().int().min(3).max(40).optional(),
  borderTurn: z.union([z.literal(0), z.literal(90)]).optional(),
  offsets: z.number().int().min(0).max(1).optional(),
  widthPct: z.number().int().min(0).max(20).optional(),
  plus: z.number().int().min(0).max(5).optional(),
  minus: z.number().int().min(0).max(5).optional(),
  profile: z.enum(["bow", "s", "taper"]).optional(),
  // "move to notes": the curve leaves the naming desk and joins the pool on
  // /finder-candidates. Reversible with false.
  candidate: z.boolean().optional(),
});

const Payload = z.object({ curves: z.array(Note) });

export function toNote(row: any): any {
  return {
    uid: row.uid,
    name: row.name || undefined,
    importance: row.importance,
    rotation: row.rotation,
    pieces: row.pieces,
    border_uid: row.borderUid || undefined,
    perSide: row.perSide || undefined,
    borderTurn: row.borderTurn || undefined,
    offsets: row.offsets || undefined,
    widthPct: row.widthPct || undefined,
    plus: row.plus || undefined,
    minus: row.minus || undefined,
    profile: row.profile || undefined,
    updated: row.updatedAt?.toISOString?.() || undefined,
  };
}

export function validateNotes(payload: any): any[] {
  return Payload.parse(payload).curves;
}

export async function readNotes(): Promise<{ curves: any[] }> {
  const rows = await prisma.note.findMany({ orderBy: { uid: "asc" } });
  return { curves: rows.map(toNote) };
}

export async function saveNotes(payload: any): Promise<{ saved: number }> {
  const incoming = validateNotes(payload);
  if (!incoming.length) {
    const error = new Error("nothing to save");
    (error as any).status = 400;
    throw error;
  }
  // The candidate flag is a property of the curve row, not of its note: the
  // note holds what a person edits about the name, the curve row holds what
  // decides which page shows it.
  const moves = incoming.filter((note) => note.candidate !== undefined);
  await prisma.$transaction([
    ...incoming.map((note) => prisma.note.upsert({
      where: { uid: note.uid },
      create: {
        uid: note.uid,
        name: note.name ?? null,
        importance: note.importance ?? 0,
        rotation: note.rotation ?? 0,
        pieces: note.pieces ?? 1,
        borderUid: note.border_uid ?? null,
        perSide: note.perSide ?? 0,
        borderTurn: note.borderTurn ?? 0,
        offsets: note.offsets ?? 0,
        widthPct: note.widthPct ?? 0,
        plus: note.plus ?? 0,
        minus: note.minus ?? 0,
        profile: note.profile ?? null,
      },
      update: {
        ...(note.name !== undefined ? { name: note.name } : {}),
        ...(note.importance !== undefined ? { importance: note.importance } : {}),
        ...(note.rotation !== undefined ? { rotation: note.rotation } : {}),
        ...(note.pieces !== undefined ? { pieces: note.pieces } : {}),
        ...(note.border_uid !== undefined ? { borderUid: note.border_uid } : {}),
        ...(note.perSide !== undefined ? { perSide: note.perSide } : {}),
        ...(note.borderTurn !== undefined ? { borderTurn: note.borderTurn } : {}),
        ...(note.offsets !== undefined ? { offsets: note.offsets } : {}),
        ...(note.widthPct !== undefined ? { widthPct: note.widthPct } : {}),
        ...(note.plus !== undefined ? { plus: note.plus } : {}),
        ...(note.minus !== undefined ? { minus: note.minus } : {}),
        ...(note.profile !== undefined ? { profile: note.profile } : {}),
      },
    })),
    ...moves.map((note) => prisma.curve.update({
      where: { uid: note.uid },
      data: { candidate: note.candidate },
    })),
  ]);
  // The readable mirror: if the database and its snapshots are both lost, the
  // names are still in a file a person can open. The candidate flag rides with
  // them, so a rebuild knows which curves the operator set aside.
  const [rows, curves] = await Promise.all([
    prisma.note.findMany({ orderBy: { uid: "asc" } }),
    prisma.curve.findMany({ select: { uid: true, candidate: true } }),
  ]);
  const candidateOf = new Map(curves.map((curve: any) => [curve.uid, curve.candidate]));
  const dir = path.join(repoRoot(), "workbench");
  const file = path.join(dir, "curve-notes.json");
  if (existsSync(file)) copyFileSync(file, path.join(dir, "curve-notes.backup.json"));
  const exported = rows.map((row: any) => ({
    ...toNote(row),
    ...(candidateOf.get(row.uid) ? { candidate: true } : {}),
  }));
  writeFileSync(file, JSON.stringify({ format: "curve-lab.curve-notes/1", curves: exported }, null, 1) + "\n");
  return { saved: incoming.length };
}
