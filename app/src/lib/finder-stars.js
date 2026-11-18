// Starring curves in the finder, in plain Node so any server can call it.
//
// The page keeps its stars in localStorage and posts them here; the file is
// `workbench/finder-stars.json`, the same pattern as the book's `starred.json`.
// A failed read is never a write: the payload is validated before anything
// touches the disk, and the write is atomic (temp file, then rename).

import { copyFile, mkdir, readdir, rename, unlink, writeFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { z } from "zod";

const Star = z.object({
  name: z.string().min(1),
  note: z.string().optional(),
  spec: z.record(z.string()).optional(),
}).passthrough();

const Payload = z.object({
  format: z.string().optional(),
  curves: z.array(Star),
});

export function validateFinderStars(payload) {
  if (!payload || !Array.isArray(payload.curves)) {
    throw new Error("expected { curves: [...] }");
  }
  const parsed = Payload.parse(payload).curves;
  const seen = new Set();
  for (const star of parsed) {
    if (seen.has(star.name)) throw new Error(`duplicate curve: ${star.name}`);
    seen.add(star.name);
  }
  return parsed;
}

const KEEP_BACKUPS = 5;

export function fileHash(text) {
  return createHash("sha1").update(text).digest("hex").slice(0, 12);
}

async function rotateBackup(dir, target) {
  const backups = path.join(dir, "backups");
  await mkdir(backups, { recursive: true });
  const stamp = new Date().toISOString().replace(/[:.]/g, "-");
  await copyFile(target, path.join(backups, `finder-stars-${stamp}.json`));
  const files = (await readdir(backups)).filter((name) => name.startsWith("finder-stars-")).sort();
  for (const old of files.slice(0, Math.max(0, files.length - KEEP_BACKUPS))) {
    await unlink(path.join(backups, old));
  }
}

export async function saveFinderStars(payload, root) {
  const curves = validateFinderStars(payload);
  const dir = path.join(path.resolve(root), "workbench");
  await mkdir(dir, { recursive: true });
  const target = path.join(dir, "finder-stars.json");
  const backup = path.join(dir, "finder-stars.backup.json");
  const temp = `${target}.tmp`;
  // Keep the previous list before replacing it: the damage is noticed a session
  // later, and the register holds two cases where a save destroyed the old data.
  if (existsSync(target)) {
    // Two tabs must not silently overwrite each other: the caller may say which
    // version it read, and a mismatch is refused rather than merged.
    if (payload?.baseHash) {
      const current = fileHash(readFileSync(target, "utf8"));
      if (payload.baseHash !== current) {
        const error = new Error(`this list changed since it was read (${current}); reload and star again`);
        error.status = 409;
        throw error;
      }
    }
    await copyFile(target, backup);
    await rotateBackup(dir, target);
  }
  await writeFile(temp, JSON.stringify({ format: "curve-lab.finder-stars/1", curves }, null, 1) + "\n");
  await rename(temp, target);
  return { saved: curves.length, path: target, backup };
}

// A read that fails is not an empty list: repair from the backup, and say which
// source answered so the page can tell the operator.
export function readFinderStars(root) {
  const dir = path.join(path.resolve(root), "workbench");
  for (const [name, source] of [["finder-stars.json", "live"], ["finder-stars.backup.json", "backup"]]) {
    const file = path.join(dir, name);
    if (!existsSync(file)) continue;
    try {
      const data = JSON.parse(readFileSync(file, "utf8"));
      if (Array.isArray(data.curves)) return { curves: data.curves, source };
    } catch {
      // damaged: fall through to the backup
    }
  }
  return { curves: [], source: "none" };
}
