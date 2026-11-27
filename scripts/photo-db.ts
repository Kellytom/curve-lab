/**
 * photo-db.ts — read the Photos library database and write a work plan.
 *
 *   node scripts/photo-db.ts                 # copy the db, write plan.jsonl, print a summary
 *   node scripts/photo-db.ts --no-copy       # reuse the copy already in the temp folder
 *
 * Why the database and not AppleScript, measured 2026-11-27:
 *   - `count of albums` through Photos times out at AppleScript's 120 s limit on
 *     this library, and `every media item` times out too;
 *   - `every album` returned 272, while the database holds 8,557;
 *   - 56,341 of 118,612 assets are in **no album**, so an album-by-album export
 *     would silently miss half the library.
 *
 * The plan is one line per asset:
 *   { asset, src, album, date, kind, bytes }
 * where `src` is the file inside `originals/` and `album` is the largest album
 * that contains it, or `_by-year/YYYY` when it is in none.
 *
 * Requires Full Disk Access for the process that runs it. The library is never
 * written: the database is copied to the temp folder and the originals are only
 * read.
 */

import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, writeFileSync } from "node:fs";
import { homedir, tmpdir } from "node:os";
import path from "node:path";

const LIBRARY = path.join(homedir(), "Pictures", "Photos Library.photoslibrary");
const DB = path.join(LIBRARY, "database", "Photos.sqlite");
const COPY = path.join(tmpdir(), "photos-plan.sqlite");
const OUT = path.join(homedir(), "Pictures", "photo-reduced", "plan.jsonl");

const args = process.argv.slice(2);
if (!args.includes("--no-copy") || !existsSync(COPY)) {
  if (!existsSync(DB)) {
    console.error(`no database at ${DB} — is Full Disk Access granted?`);
    process.exit(2);
  }
  console.log("copying the database…");
  execFileSync("cp", [DB, COPY]);
}

const sql = (query: string): string =>
  execFileSync("sqlite3", ["-separator", "\t", COPY, query], { encoding: "utf8", maxBuffer: 1 << 30 });

/** The album an asset belongs to: the one holding the most assets, else by year. */
const query = `
  with membership as (
    select j.Z_3ASSETS as asset, j.Z_27ALBUMS as album,
           count(*) over (partition by j.Z_27ALBUMS) as album_size
    from Z_27ASSETS j
  ),
  best as (
    select asset, album,
           row_number() over (partition by asset order by album_size desc, album asc) as rn
    from membership
  )
  select
    z.Z_PK,
    z.ZDIRECTORY,
    coalesce(z.ZFILENAME, aa.ZORIGINALFILENAME, ''),
    coalesce(strftime('%Y', z.ZDATECREATED + 978307200, 'unixepoch'), 'unknown'),
    coalesce(strftime('%Y-%m-%d', z.ZDATECREATED + 978307200, 'unixepoch'), '1900-01-01'),
    z.ZKIND,
    coalesce(aa.ZORIGINALFILESIZE, 0),
    coalesce(a.ZTITLE, '')
  from ZASSET z
  left join ZADDITIONALASSETATTRIBUTES aa on aa.ZASSET = z.Z_PK
  left join best b on b.asset = z.Z_PK and b.rn = 1
  left join ZGENERICALBUM a on a.Z_PK = b.album
  where coalesce(z.ZTRASHEDSTATE, 0) = 0
  order by 8, 5;
`;

const rows = sql(query).split("\n").filter(Boolean);
console.log(`${rows.length} assets in the database`);

type PlanRow = { asset: number; src: string; album: string; date: string; kind: string; bytes: number };

const plan: PlanRow[] = [];
let missing = 0;
let unalbumed = 0;
let totalBytes = 0;
let videos = 0;
let videoBytes = 0;

for (const line of rows) {
  const [pk, directory, filename, year, date, kind, bytes, album] = line.split("\t");
  if (!filename) continue;
  const src = path.join(LIBRARY, "originals", directory ?? "", filename);
  const row: PlanRow = {
    asset: Number(pk),
    src: path.relative(path.join(homedir(), "Pictures"), src),
    album: album || `_by-year/${year || "unknown"}`,
    date,
    kind: Number(kind) === 1 ? "video" : "photo",
    bytes: Number(bytes) || 0,
  };
  if (!album) unalbumed += 1;
  if (row.kind === "video") {
    videos += 1;
    videoBytes += row.bytes;
  }
  totalBytes += row.bytes;
  if (!existsSync(src)) {
    missing += 1;
    continue;
  }
  plan.push(row);
}

mkdirSync(path.dirname(OUT), { recursive: true });
writeFileSync(OUT, plan.map((row) => JSON.stringify(row)).join("\n") + "\n");

const gb = (n: number) => (n / 1e9).toFixed(1);
const albums = new Map<string, number>();
for (const row of plan) albums.set(row.album, (albums.get(row.album) ?? 0) + 1);

console.log(`plan: ${plan.length} readable assets, ${albums.size} destinations`);
console.log(`bytes by the size column: ${gb(totalBytes)} GB`);
console.log(`videos: ${videos} (${gb(videoBytes)} GB)`);
console.log(`in no album: ${unalbumed} -> _by-year/YYYY`);
console.log(`missing from originals/: ${missing} (cloud-only or evicted)`);
console.log(`largest destinations:`);
[...albums.entries()]
  .sort((a, b) => b[1] - a[1])
  .slice(0, 10)
  .forEach(([name, n]) => console.log(`  ${String(n).padStart(6)}  ${name}`));
console.log(`\nwrote ${OUT}`);
