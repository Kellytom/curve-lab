// The registry as the pages read it: the JSON index, with the human edits from
// the database applied on top. The database is the record; the JSON is seed.
import { readFileSync } from "node:fs";
import path from "node:path";
import { prisma } from "./db.js";
import { repoRoot } from "./gallery.js";

export type Curve = {
  uid: string;
  name: string;
  lists: string[];
  aliases?: string[];
  candidate?: boolean;
  importance?: number;
  rotation?: number;
  pieces?: number;
  border_uid?: string;
  updated?: string;
  starred?: boolean;
  auto_named?: boolean;
  savedName?: string | null;
  [key: string]: any;
};

export type Registry = {
  curves: Curve[];
  sets?: any[];
  [key: string]: any;
};

export async function loadRegistry(base?: string): Promise<Registry> {
  const root = base || repoRoot();
  const registry: Registry = JSON.parse(readFileSync(path.join(root, "workbench", "curve-registry.json"), "utf8"));
  const [notes, curves] = await Promise.all([
    prisma.note.findMany(),
    prisma.curve.findMany({ select: { uid: true, candidate: true } }),
  ]);
  const byUid = new Map(notes.map((note: any) => [note.uid, note]));
  const candidateOf = new Map<string, boolean>(curves.map((curve: any) => [curve.uid, curve.candidate]));

  for (const record of registry.curves) {
    // A curve moved to the notes pool is a row in the database: the seed does
    // not know about it, so the database decides.
    if (candidateOf.has(record.uid)) record.candidate = candidateOf.get(record.uid);
    const note: any = byUid.get(record.uid);
    if (!note) continue;
    if (note.name && note.name !== record.name) {
      if (!Array.isArray(record.aliases)) record.aliases = [];
      if (!record.aliases.includes(record.name)) record.aliases.push(record.name);
      record.name = note.name;
      record.auto_named = false;
    }
    record.importance = note.importance ?? record.importance ?? 0;
    record.rotation = note.rotation ?? record.rotation ?? 0;
    record.pieces = note.pieces ?? record.pieces ?? 1;
    if (note.borderUid) record.border_uid = note.borderUid;
    record.updated = note.updatedAt ? note.updatedAt.toISOString() : undefined;
    record.savedName = note.name || null;
    // the note saved with the curve is the provenance the plates page prints
    if (note.note) record.note = note.note;
    if (note.perSide) record.perSide = note.perSide;
    if (note.borderTurn) record.borderTurn = note.borderTurn;
    if (note.offsets) record.offsets = note.offsets;
    if (note.widthPct) record.widthPct = note.widthPct;
    if (note.plus) record.plus = note.plus;
    if (note.minus) record.minus = note.minus;
    if (note.profile) record.profile = note.profile;
  }

  const records = new Map(registry.curves.map((record) => [record.uid, record]));
  for (const set of registry.sets || []) {
    const record = records.get(set.inner_uid);
    if (!record) continue;
    set.border_uid = record.border_uid || set.border_uid;
    set.rotation = record.rotation ?? set.rotation;
    set.pieces = record.pieces ?? set.pieces;
    set.importance = record.importance ?? set.importance;
  }
  return registry;
}
