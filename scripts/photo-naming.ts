/**
 * photo-naming.ts — propose a name for every kept file, from the aliases we have.
 *
 *   node scripts/photo-naming.ts            # write naming-plan.csv and print a summary
 *
 * Read-only. It never renames anything; it prepares the decision the operator
 * said to make later ("we can go through and name exactly later").
 *
 * The rules it proposes by, in order:
 *   1. a real album beats `_by-year/YYYY` — an album is a name a person chose;
 *   2. among real albums, the shortest wins (the least screen-based, the most
 *      deliberate);
 *   3. the original filename wins when it says something human (`IMG_1234`,
 *      `stained-glass-window`) and is dropped when it is a UUID or a bare number —
 *      those come from the library, not from a person;
 *   4. the proposal is `<album-slug>-<original stem>` so the album is readable in
 *      the name itself, which is what makes a folder list legible.
 */

import { existsSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { homedir } from "node:os";

const ROOT = path.join(homedir(), "Pictures", "photo-reduced");
const MANIFEST = path.join(ROOT, "manifest.jsonl");
const ALIASES = path.join(ROOT, "aliases.jsonl");
const OUT = path.join(ROOT, "naming-plan.csv");

type Row = { out_path: string; album: string; filename: string; taken_at?: string; status: string };
type Alias = { p: string; a: string; n: string };

const rows: Row[] = readFileSync(MANIFEST, "utf8")
  .split("\n")
  .filter(Boolean)
  .flatMap((line) => {
    try {
      return [JSON.parse(line) as Row];
    } catch {
      return [];
    }
  });

const aliases = new Map<string, Set<string>>();
if (existsSync(ALIASES)) {
  for (const line of readFileSync(ALIASES, "utf8").split("\n")) {
    if (!line.trim()) continue;
    try {
      const a = JSON.parse(line) as Alias;
      const set = aliases.get(a.p) ?? new Set<string>();
      set.add(`${a.a}\u0000${a.n}`);
      aliases.set(a.p, set);
    } catch {
      /* torn line */
    }
  }
}

const slug = (text: string) =>
  text
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 40) || "unnamed";

/** A filename worth keeping: it has letters or a recognisable camera pattern. */
const humanName = (name: string): string | null => {
  const stem = path.basename(name, path.extname(name));
  if (/^[0-9a-f]{8}-[0-9a-f]{4}/i.test(stem)) return null; // a UUID
  if (/^[0-9]+$/.test(stem)) return null; // a bare number
  if (/^(img|dsc|pxl|mvimg|screenshot)[_-]?\d+/i.test(stem)) return stem; // a camera
  if (/[a-z]{3,}/i.test(stem)) return stem;
  return null;
};

const isYearBucket = (album: string) => album.startsWith("_by-year");

const seen = new Set<string>();
const plan: string[][] = [["kept_path", "current_name", "best_album", "original_name", "proposed_name", "aliases"]];

let renamed = 0;
let keptAsIs = 0;

for (const row of rows) {
  if (!row.out_path || seen.has(row.out_path)) continue;
  if (row.status === "duplicate" || row.status === "failed") continue;
  if (!existsSync(path.join(ROOT, row.out_path))) continue;
  seen.add(row.out_path);

  const names = [...(aliases.get(row.out_path) ?? new Set([`${row.album}\u0000${row.filename}`]))].map((s) => {
    const [album, name] = s.split("\u0000");
    return { album, name };
  });

  const real = names.filter((x) => !isYearBucket(x.album));
  const pool = real.length ? real : names;
  pool.sort((a, b) => a.album.length - b.album.length || a.album.localeCompare(b.album));
  const best = pool[0];

  const human = names.map((x) => humanName(x.name)).find((n) => n) ?? null;
  const ext = path.extname(row.out_path).toLowerCase();
  const currentName = path.basename(row.out_path);
  const proposed = `${slug(best.album)}-${human ?? path.basename(currentName, path.extname(currentName))}${ext}`;

  const same = proposed === currentName;
  if (same) keptAsIs += 1;
  else renamed += 1;

  plan.push([row.out_path, currentName, best.album, human ?? "", proposed, String(names.length)]);
}

writeFileSync(OUT, plan.map((line) => line.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(",")).join("\n") + "\n");

console.log(`${plan.length - 1} kept files`);
console.log(`  would keep their name: ${keptAsIs}`);
console.log(`  would be renamed:      ${renamed}`);
const multi = plan.slice(1).filter((line) => Number(line[5]) > 1).length;
console.log(`  with more than one alias: ${multi}`);
const examples = plan.slice(1).filter((line) => line[4] !== line[1]).slice(0, 8);
console.log("\nfirst changes:");
for (const line of examples) console.log(`  ${line[1]}\n    -> ${line[4]}   (album ${line[2]})`);
console.log(`\nwrote ${OUT} — nothing renamed`);
