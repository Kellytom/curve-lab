/**
 * photo-reduce.ts — mirror the Photos album tree as reduced copies, one asset at a time.
 *
 *   node scripts/photo-reduce.ts --inventory          # read-only: albums, counts, video share
 *   node scripts/photo-reduce.ts --run --min-free-gb 5
 *   node scripts/photo-reduce.ts --run --album "Holiday 2019" --limit 20
 *
 * The spec is state/SPEC-photo-reduction-int.md; this file is the implementation of it.
 *
 * Rules, all of them from the spec and none negotiable:
 *   - the Photos library is never written to and never deleted from here;
 *   - one asset at a time, so a failure costs one photo;
 *   - the manifest is append-only and is the only state: resume skips ids already finished;
 *   - stop before free space falls under --min-free-gb (default 5);
 *   - never upscale: -Z is passed only when the long side is above the cap.
 *
 * Access: the shell cannot read *.photoslibrary (macOS TCC). The door used here is AppleScript
 * into Photos, which also pulls iCloud originals. `--inventory` says what is missing if it fails.
 */

import { execFileSync } from "node:child_process";
import { appendFileSync, existsSync, mkdirSync, readFileSync, readdirSync, rmSync, statSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { processOne, slug as slugOf } from "./lib/photo-process.ts";
import { homedir } from "node:os";
import { chmodSync } from "node:fs";
import path from "node:path";

/* ---------- options ---------- */

const argv = process.argv.slice(2);
const flag = (name: string, fallback?: string): string | undefined => {
  const i = argv.indexOf(name);
  return i >= 0 && argv[i + 1] && !argv[i + 1].startsWith("--") ? argv[i + 1] : fallback;
};
const has = (name: string) => argv.includes(name);

const OUT_ROOT = flag("--out", path.join(homedir(), "Pictures", "photo-reduced"))!;
const MANIFEST = path.join(OUT_ROOT, "manifest.jsonl");
const STAGING = path.join(OUT_ROOT, "_staging");
const MIN_FREE_GB = Number(flag("--min-free-gb", "5"));
const MAX_LONG_SIDE = Number(flag("--max-long-side", "3000"));
const QUALITY = Number(flag("--quality", "80"));
const ONLY_ALBUM = flag("--album");
const LIMIT = Number(flag("--limit", "0"));
const CHUNK = Math.max(1, Number(flag("--chunk", "20")));
const TRANSCODE_VIDEO = has("--video");
const ALL_LIBRARY = has("--all");
const HASH_INDEX = path.join(OUT_ROOT, "hashes.jsonl");
const ALBUM_CACHE = path.join(OUT_ROOT, "albums.json");
const REFRESH_ALBUMS = has("--refresh-albums");
const MODE = has("--from-plan") ? "plan" : has("--from-dir") ? "dir" : has("--run") || has("--all") ? "run" : has("--report") ? "report" : "inventory";
const FROM_DIR = flag("--from-dir");
const SHARD = flag("--shard");
const ROOT_STAGING = path.join(homedir(), "Pictures", "photo-inbox", "_unzipped");

type Album = { name: string; count: number };

/* ---------- Photos, through AppleScript ---------- */

function osa(script: string, timeoutMs = 60_000): string {
  try {
    return execFileSync("osascript", ["-e", script], {
      encoding: "utf8",
      timeout: timeoutMs,
      maxBuffer: 32 * 1024 * 1024,
    });
  } catch (error) {
    const e = error as { stderr?: string; signal?: string };
    if (e.signal === "SIGTERM") throw new Error("AppleScript timed out — a permission dialog is probably waiting");
    throw new Error((e.stderr || String(error)).trim());
  }
}

function checkAccess(): void {
  try {
    const name = osa('tell application "Photos" to get name', 15_000).trim();
    if (name !== "Photos") throw new Error(`Photos answered ${JSON.stringify(name)}`);
  } catch (error) {
    console.error("Cannot talk to Photos.\n");
    console.error(String((error as Error).message));
    console.error(
      [
        "",
        "Grant Automation for this process, then run again:",
        "  System Settings -> Privacy & Security -> Automation -> allow the app to control Photos",
        "  (or Full Disk Access for the app, which lets the shell read the library directly)",
        "",
        "The service daemon outlives quitting the app, so after granting a permission the daemon",
        "must be restarted, or the grant will not reach it.",
      ].join("\n"),
    );
    process.exit(2);
  }
}

/** The album list, cached: asking a 99k-item library costs minutes and times out. */
function listAlbums(): Album[] {
  if (!REFRESH_ALBUMS && existsSync(ALBUM_CACHE)) {
    try {
      const cached = JSON.parse(readFileSync(ALBUM_CACHE, "utf8")) as { albums: Album[] };
      if (Array.isArray(cached.albums) && cached.albums.length) {
        console.log(`${cached.albums.length} albums (cached; --refresh-albums to re-read)`);
        return cached.albums;
      }
    } catch {
      /* fall through to the live query */
    }
  }
  const albums = readAlbums();
  mkdirSync(OUT_ROOT, { recursive: true });
  writeFileSync(ALBUM_CACHE, `${JSON.stringify({ read_at: new Date().toISOString(), albums }, null, 1)}\n`);
  return albums;
}

function readAlbums(): Album[] {
  const script = `
    set out to ""
    tell application "Photos"
      repeat with a in (every album)
        set out to out & (name of a) & tab & (count of media items of a) & linefeed
      end repeat
    end tell
    return out`;
  return osa(script, 120_000)
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      const [name, count] = line.split("\t");
      return { name, count: Number(count) || 0 };
    });
}

type Item = { id: string; filename: string; date: string; index: number };

/**
 * Export a range of one album in a single Apple event.
 * Resolving the album by name costs seconds, so one call per asset was 10×
 * slower than one call per chunk. Returns the ids and names in Photos' order.
 */
function libraryCount(): number {
  return Number(osa('tell application "Photos" to count (every media item)', 120_000).trim()) || 0;
}

function exportChunk(album: string | null, from: number, to: number, target: string): Item[] {
  const script = `
    set out to ""
    tell application "Photos"
      ${album === null ? "" : `set theAlbum to album ${JSON.stringify(album)}`}
      set theItems to media items ${from} thru ${to} ${album === null ? "" : "of theAlbum"}
      repeat with m in theItems
        set d to date of m
        set mo to (month of d as integer) as string
        if (count of mo) is 1 then set mo to "0" & mo
        set dy to (day of d as integer) as string
        if (count of dy) is 1 then set dy to "0" & dy
        set iso to ((year of d as integer) as string) & "-" & mo & "-" & dy
        set out to out & (id of m as string) & tab & (filename of m as string) & tab & iso & linefeed
      end repeat
      export theItems to POSIX file ${JSON.stringify(target)} with using originals
    end tell
    return out`;
  return osa(script, 900_000)
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      const [id, filename, date] = line.split("\t");
      return { id, filename, date, index: 0 };
    });
}

/** A folder-safe slug: "Hotels mexico" -> "hotels-mexico". */
function slug(text: string): string {
  return text
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 40) || "album";
}

/* ---------- manifest ---------- */

type Row = {
  asset_id: string;
  album: string;
  filename: string;
  kind: string;
  original_bytes: number;
  reduced_bytes: number;
  ratio: number;
  out_path: string;
  sha256: string | null;
  original_sha256?: string | null;
  width: number | null;
  height: number | null;
  taken_at: string;
  quality: number | null;
  engine: string | null;
  status: string;
  error: string | null;
  done_at: string;
};

function loadDone(): Set<string> {
  const done = new Set<string>();
  if (!existsSync(MANIFEST)) return done;
  const KEPT = new Set(["reduced", "over-target", "skipped-small", "skipped-larger", "duplicate"]);
  for (const line of readFileSync(MANIFEST, "utf8").split("\n")) {
    if (!line.trim()) continue;
    try {
      const row = JSON.parse(line) as Row;
      if (!KEPT.has(row.status)) continue;
      // A row is only done if the file it names is really there. A row from a
      // failed attempt must not block its own retry.
      if (row.out_path && !existsSync(path.join(OUT_ROOT, row.out_path))) continue;
      done.add(row.asset_id);
    } catch {
      /* a torn last line from a crash is ignored, not a reason to stop */
    }
  }
  return done;
}

const isVideoName = (file: string) => [".mov", ".mp4", ".m4v"].includes(path.extname(file).toLowerCase());

function record(row: Row): void {
  mkdirSync(path.dirname(MANIFEST), { recursive: true });
  appendFileSync(MANIFEST, `${JSON.stringify(row)}\n`);
}

/* ---------- files and images ---------- */

const freeGb = (): number => {
  const out = execFileSync("df", ["-k", homedir()], { encoding: "utf8" }).trim().split("\n").pop()!;
  return (Number(out.split(/\s+/)[3]) / 1024 / 1024);
};

const sha256 = (file: string): string => createHash("sha256").update(readFileSync(file)).digest("hex");

function imageSize(file: string): { width: number; height: number } | null {
  try {
    const out = execFileSync("sips", ["-g", "pixelWidth", "-g", "pixelHeight", file], { encoding: "utf8" });
    const w = /pixelWidth:\s*(\d+)/.exec(out);
    const h = /pixelHeight:\s*(\d+)/.exec(out);
    return w && h ? { width: Number(w[1]), height: Number(h[1]) } : null;
  } catch {
    return null;
  }
}

type Reduced = { engine: string; quality: number | null; bytes: number };

/** Reduce one file into `out`, never upscaling. Returns the engine used. */
function reduce(src: string, out: string): Reduced {
  const ext = path.extname(src).toLowerCase();
  const size = imageSize(src);
  mkdirSync(path.dirname(out), { recursive: true });

  if (ext === ".png") {
    execFileSync("pngquant", ["--quality", "70-95", "--speed", "1", "--force", "--output", out, src], { stdio: "ignore" });
    try {
      execFileSync("oxipng", ["-o", "2", "--strip", "safe", "--quiet", out], { stdio: "ignore" });
    } catch {
      /* oxipng is lossless and optional: a failure leaves the pngquant result */
    }
    return { engine: "pngquant", quality: null, bytes: statSync(out).size };
  }

  const longSide = size ? Math.max(size.width, size.height) : 0;
  const args = ["-s", "formatOptions", String(QUALITY)];
  if (longSide > MAX_LONG_SIDE) args.push("-Z", String(MAX_LONG_SIDE));
  execFileSync("sips", [...args, src, "--out", out], { stdio: "ignore" });
  return { engine: "sips", quality: QUALITY, bytes: statSync(out).size };
}

/* ---------- inventory ---------- */

function inventory(): void {
  checkAccess();
  const albums = listAlbums();
  const total = albums.reduce((n, a) => n + a.count, 0);
  console.log(`${albums.length} albums, ${total} media items`);
  console.log(`free space: ${freeGb().toFixed(1)} GiB (stop at ${MIN_FREE_GB} GiB)`);
  for (const a of albums) console.log(`  ${String(a.count).padStart(6)}  ${a.name}`);
  console.log("\nThe video share is not in this listing; it comes from the first exported batch.");
}


/* ---------- report ---------- */

/** Per-album summary of what is on disk, and the same table as index.html. */
function report(): void {
  const rows: Row[] = !existsSync(MANIFEST)
    ? []
    : readFileSync(MANIFEST, "utf8")
        .split("\n")
        .filter(Boolean)
        .flatMap((line) => {
          try {
            return [JSON.parse(line) as Row];
          } catch {
            return [];
          }
        });

  const byAlbum = new Map<string, { rows: number; in: number; out: number; small: number; video: number }>();
  for (const r of rows) {
    const a = byAlbum.get(r.album) ?? { rows: 0, in: 0, out: 0, small: 0, video: 0 };
    a.rows += 1;
    a.in += r.original_bytes;
    a.out += r.reduced_bytes || r.original_bytes;
    if (r.status === "skipped-small" || r.status === "skipped-larger") a.small += 1;
    if (r.status === "skipped-video") a.video += 1;
    byAlbum.set(r.album, a);
  }

  const mb = (n: number) => (n / 1e6).toFixed(1);
  const lines: string[] = [];
  lines.push(`album                         files      in MB    out MB   saved   small  video`);
  for (const [album, a] of [...byAlbum.entries()].sort((x, y) => y[1].in - x[1].in)) {
    const pct = a.in ? (100 * (1 - a.out / a.in)).toFixed(0) : "0";
    lines.push(
      `${album.slice(0, 26).padEnd(26)} ${String(a.rows).padStart(7)} ${mb(a.in).padStart(10)} ${mb(a.out).padStart(9)} ` +
        `${(pct + "%").padStart(6)} ${String(a.small).padStart(6)} ${String(a.video).padStart(6)}`,
    );
  }
  const tin = [...byAlbum.values()].reduce((n, a) => n + a.in, 0);
  const tout = [...byAlbum.values()].reduce((n, a) => n + a.out, 0);
  lines.push(`${"total".padEnd(26)} ${String(rows.length).padStart(7)} ${mb(tin).padStart(10)} ${mb(tout).padStart(9)} ${((tin ? 100 * (1 - tout / tin) : 0).toFixed(0) + "%").padStart(6)}`);
  lines.push(`free space now: ${freeGb().toFixed(1)} GiB`);
  console.log(lines.join("\n"));

  // the same table, for double-clicking in Finder
  const html = [
    "<!doctype html><meta charset=utf-8><title>photo-reduced</title>",
    "<style>body{font:14px -apple-system,system-ui,sans-serif;margin:2rem;color:#111}",
    "table{border-collapse:collapse}td,th{padding:.3rem .8rem;border-bottom:1px solid #ddd;text-align:right}",
    "td:first-child,th:first-child{text-align:left}code{background:#f3f3f3;padding:.1rem .3rem}</style>",
    `<h1>photo-reduced</h1><p>${rows.length} rows, ${mb(tin)} MB in, ${mb(tout)} MB out` +
      ` — ${tin ? (100 * (1 - tout / tin)).toFixed(0) : 0} % smaller. Free: ${freeGb().toFixed(1)} GiB.</p>`,
    "<p>Open the album folders in this directory. The record is <code>manifest.jsonl</code>.</p>",
    "<table><tr><th>album</th><th>files</th><th>in MB</th><th>out MB</th><th>saved</th><th>small</th><th>video</th></tr>",
    ...[...byAlbum.entries()].map(([album, a]) => {
      const pct = a.in ? (100 * (1 - a.out / a.in)).toFixed(0) : "0";
      return `<tr><td>${album}</td><td>${a.rows}</td><td>${mb(a.in)}</td><td>${mb(a.out)}</td><td>${pct} %</td><td>${a.small}</td><td>${a.video}</td></tr>`;
    }),
    "</table>",
  ].join("\n");
  writeFileSync(path.join(OUT_ROOT, "index.html"), html);
  console.log(`\nwrote ${path.join(OUT_ROOT, "index.html")}`);
}

/* ---------- run ---------- */

function run(): void {
  checkAccess();
  mkdirSync(STAGING, { recursive: true });
  mkdirSync(OUT_ROOT, { recursive: true });
  const done = loadDone();
  let albums = ALL_LIBRARY
    ? [{ name: "__library__", count: libraryCount() }]
    : listAlbums().filter((a) => !ONLY_ALBUM || a.name === ONLY_ALBUM);
  if (SHARD) {
    const [mine, of] = SHARD.split("/").map(Number);
    albums = albums.filter((_, i) => i % of === mine - 1);
    console.log(`shard ${mine}/${of}: ${albums.length} albums`);
  }
  if (albums.length === 0) {
    console.error(ONLY_ALBUM ? `no album named ${JSON.stringify(ONLY_ALBUM)}` : "no albums");
    process.exit(2);
  }

  // Content hash -> the kept copy, so the same photo in two albums is stored once.
  const seenHashes = new Map<string, string>();
  for (const line of existsSync(MANIFEST) ? readFileSync(MANIFEST, "utf8").split("\n") : []) {
    if (!line.trim()) continue;
    try {
      const row = JSON.parse(line) as { sha256?: string; original_sha256?: string; out_path?: string; status?: string };
      const key = row.original_sha256 ?? row.sha256;
      if (key && row.out_path && row.status && row.status !== "duplicate"
          && row.status !== "failed" && existsSync(path.join(OUT_ROOT, row.out_path))) {
        seenHashes.set(key, row.out_path);
      }
    } catch {
      /* torn line */
    }
  }

  if (existsSync(HASH_INDEX)) {
    for (const line of readFileSync(HASH_INDEX, "utf8").split("\n")) {
      if (!line.trim()) continue;
      try {
        const rec = JSON.parse(line) as { h: string; p: string };
        if (rec.h && rec.p && existsSync(path.join(OUT_ROOT, rec.p))) seenHashes.set(rec.h, rec.p);
      } catch {
        /* torn line */
      }
    }
  }

  let processed = 0;
  let skipped = 0;
  let failed = 0;
  let before = 0;
  let after = 0;

  const IMAGE = [".heic", ".heif", ".jpg", ".jpeg", ".png", ".tif", ".tiff"];
  const VIDEO = [".mov", ".mp4", ".m4v"];

  /** Reduce one exported file, or record why not. Returns false on failure. */
  const handle = (albumIn: string, item: Item, src: string, cleanUp: () => void): boolean => {
    const album = albumIn === "__library__" ? `_by-year/${item.date.slice(0, 4)}` : albumIn;
    const albumDir = path.join(OUT_ROOT, album.replace(/[/:]/g, "-"));
    const stem = `${slugOf(album)}-${String(item.index).padStart(4, "0")}-${item.date}`;
    const result = processOne({
      src,
      outDir: albumDir,
      stem,
      maxLongSide: MAX_LONG_SIDE,
      quality: QUALITY,
      videoPreset: TRANSCODE_VIDEO ? "PresetHEVC1920x1080" : null,
      seen: seenHashes,
    });

    record({
      asset_id: item.id,
      album,
      filename: item.filename,
      kind: isVideoName(src) ? "video" : "photo",
      original_bytes: result.originalBytes,
      reduced_bytes: result.reducedBytes,
      ratio: result.ratio,
      out_path: result.outPath ? path.relative(OUT_ROOT, result.outPath) : "",
      sha256: result.sha256,
      original_sha256: result.originalSha256,
      width: result.width,
      height: result.height,
      taken_at: item.date,
      quality: result.quality,
      engine: result.engine,
      status: result.status,
      error: result.error,
      done_at: new Date().toISOString(),
    });

    if (result.status !== "failed" && result.status !== "duplicate" && result.outPath) {
      appendFileSync(HASH_INDEX, `${JSON.stringify({ h: result.originalSha256, p: path.relative(OUT_ROOT, result.outPath) })}\n`);
    }

    if (result.status === "failed") {
      failed += 1;
      console.log(`  FAILED ${album} ${item.filename}: ${result.error}`);
    } else if (result.status === "reduced" || result.status === "over-target") {
      processed += 1;
      before += result.originalBytes;
      after += result.reducedBytes;
      console.log(
        `  ${album} ${item.filename} ${(result.originalBytes / 1e6).toFixed(2)} -> ${(result.reducedBytes / 1e6).toFixed(2)} MB ` +
          `(${Math.round(100 * result.reducedBytes / result.originalBytes)} %) ${result.status}`,
      );
    } else {
      skipped += 1;
    }
    cleanUp();
    return result.status !== "failed";
  };

  outer: for (const album of albums) {
    for (let from = 1; from <= album.count; from += CHUNK) {
      if (LIMIT && processed + skipped + failed >= LIMIT) break outer;
      const free = freeGb();
      if (free <= MIN_FREE_GB) {
        console.log(`\nSTOP: free space ${free.toFixed(1)} GiB is at the ${MIN_FREE_GB} GiB floor`);
        break outer;
      }
      const to = Math.min(from + CHUNK - 1, album.count);
      const stage = path.join(STAGING, `chunk-${album.name.replace(/[/: ]/g, "_")}-${from}`);
      rmSync(stage, { recursive: true, force: true });
      mkdirSync(stage, { recursive: true });

      let items: Item[];
      try {
        items = exportChunk(album.name === "__library__" ? null : album.name, from, to, stage);
      } catch (error) {
        console.log(`  chunk failed ${album.name} ${from}-${to}: ${(error as Error).message}`);
        rmSync(stage, { recursive: true, force: true });
        failed += 1;
        continue;
      }

      const files = readdirSync(stage).filter((f) => !f.startsWith(".") && !f.toLowerCase().endsWith(".aae"));
      const byName = new Map<string, string>();
      for (const f of files) if (!byName.has(f.toLowerCase())) byName.set(f.toLowerCase(), path.join(stage, f));

      for (const item of items) {
        if (LIMIT && processed + skipped + failed >= LIMIT) break;
        if (done.has(item.id)) continue;
        const src = byName.get(item.filename.toLowerCase());
        if (!src) {
          record({
            asset_id: item.id, album: album.name, filename: item.filename, kind: "photo",
            original_bytes: 0, reduced_bytes: 0, ratio: 0, out_path: "", sha256: null,
            width: null, height: null, taken_at: item.date, quality: null, engine: null,
            status: "failed", error: "export produced no file for this item",
            done_at: new Date().toISOString(),
          });
          failed += 1;
          continue;
        }
        item.index = from + items.indexOf(item);
        handle(album.name, item, src, () => {});
      }
      rmSync(stage, { recursive: true, force: true });
    }
  }

  console.log(
    `\n${processed} reduced, ${skipped} skipped, ${failed} failed; ` +
      `${(before / 1e9).toFixed(2)} GB in, ${(after / 1e9).toFixed(2)} GB out, ` +
      `${(100 * (1 - after / (before || 1))).toFixed(0)} % smaller; free ${freeGb().toFixed(1)} GiB`,
  );
  console.log(`manifest: ${MANIFEST}`);
}


/* ---------- a folder tree, e.g. a phone copied off a cable ---------- */

/** A Takeout or album download is a zip: unpack it beside itself, then reduce. */
function unpackIfZip(target: string): string {
  if (!target.toLowerCase().endsWith(".zip")) return target;
  const into = path.join(ROOT_STAGING, path.basename(target, path.extname(target)));
  mkdirSync(into, { recursive: true });
  // ditto refuses paths that escape the destination, unlike a hand-rolled unzip
  execFileSync("ditto", ["-x", "-k", target, into], { stdio: "ignore" });
  console.log(`unpacked ${path.basename(target)} -> ${into}`);
  return into;
}

function runFromDir(rootIn: string): void {
  const root = unpackIfZip(rootIn);
  const seen = new Map<string, string>();
  const done = loadDone();
  for (const line of existsSync(MANIFEST) ? readFileSync(MANIFEST, "utf8").split("\n") : []) {
    if (!line.trim()) continue;
    try {
      const row = JSON.parse(line) as Row;
      const key = row.original_sha256 ?? null;
      if (key && row.out_path && existsSync(path.join(OUT_ROOT, row.out_path)) && row.status !== "duplicate") {
        seen.set(key, row.out_path);
      }
    } catch {
      /* torn line */
    }
  }

  const files: { abs: string; rel: string }[] = [];
  const walk = (dir: string) => {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      if (entry.name.startsWith(".")) continue;
      const abs = path.join(dir, entry.name);
      if (entry.isDirectory()) walk(abs);
      else files.push({ abs, rel: path.relative(root, abs) });
    }
  };
  walk(root);
  files.sort((a, b) => a.rel.localeCompare(b.rel));
  console.log(`${files.length} files under ${root}`);

  if (existsSync(HASH_INDEX)) {
    for (const line of readFileSync(HASH_INDEX, "utf8").split("\n")) {
      if (!line.trim()) continue;
      try {
        const rec = JSON.parse(line) as { h: string; p: string };
        if (rec.h && rec.p && existsSync(path.join(OUT_ROOT, rec.p))) seenHashes.set(rec.h, rec.p);
      } catch {
        /* torn line */
      }
    }
  }

  let processed = 0;
  let skipped = 0;
  let failed = 0;
  let before = 0;
  let after = 0;
  const indexByAlbum = new Map<string, number>();

  for (const file of files) {
    if (LIMIT && processed + skipped + failed >= LIMIT) break;
    const free = freeGb();
    if (free <= MIN_FREE_GB) {
      console.log(`STOP: free space ${free.toFixed(1)} GiB is at the ${MIN_FREE_GB} GiB floor`);
      break;
    }
    const parts = file.rel.split(path.sep);
    const album = parts.length > 1 ? parts[0] : path.basename(root);
    const n = (indexByAlbum.get(album) ?? 0) + 1;
    indexByAlbum.set(album, n);
    const mtime = statSync(file.abs).mtime;
    const date = `${mtime.getFullYear()}-${String(mtime.getMonth() + 1).padStart(2, "0")}-${String(mtime.getDate()).padStart(2, "0")}`;
    const assetId = `dir:${createHash("sha1").update(file.rel).digest("hex").slice(0, 16)}`;
    if (done.has(assetId)) continue;

    const stem = `${slugOf(album)}-${String(n).padStart(4, "0")}-${date}`;
    const result = processOne({
      src: file.abs,
      outDir: path.join(OUT_ROOT, album.replace(/[/:]/g, "-")),
      stem,
      maxLongSide: MAX_LONG_SIDE,
      quality: QUALITY,
      videoPreset: TRANSCODE_VIDEO ? "PresetHEVC1920x1080" : null,
      seen,
    });

    record({
      asset_id: assetId,
      album,
      filename: path.basename(file.abs),
      kind: isVideoName(file.abs) ? "video" : "photo",
      original_bytes: result.originalBytes,
      reduced_bytes: result.reducedBytes,
      ratio: result.ratio,
      out_path: result.outPath ? path.relative(OUT_ROOT, result.outPath) : "",
      sha256: result.sha256,
      original_sha256: result.originalSha256,
      width: result.width,
      height: result.height,
      taken_at: date,
      quality: result.quality,
      engine: result.engine,
      status: result.status,
      error: result.error,
      done_at: new Date().toISOString(),
    });
    if (result.status === "reduced" || result.status === "over-target") {
      processed += 1;
      before += result.originalBytes;
      after += result.reducedBytes;
      console.log(`  ${album} ${path.basename(file.abs)} -> ${path.basename(result.outPath)} ${Math.round(100 * result.reducedBytes / result.originalBytes)} %`);
    } else if (result.status === "failed") failed += 1;
    else skipped += 1;
  }

  console.log(`\n${processed} reduced, ${skipped} skipped, ${failed} failed; ${(before / 1e9).toFixed(2)} GB in, ${(after / 1e9).toFixed(2)} GB out`);
}


/* ---------- the database plan: every asset, albums and years ---------- */

function runFromPlan(): void {
  const PLAN = path.join(OUT_ROOT, "plan.jsonl");
  if (!existsSync(PLAN)) {
    console.error(`no plan at ${PLAN} — run scripts/photo-db.ts first`);
    process.exit(2);
  }
  const seen = new Map<string, string>();
  const done = loadDone();
  if (existsSync(HASH_INDEX)) {
    for (const line of readFileSync(HASH_INDEX, "utf8").split("\n")) {
      if (!line.trim()) continue;
      try {
        const rec = JSON.parse(line) as { h: string; p: string };
        if (rec.h && rec.p && existsSync(path.join(OUT_ROOT, rec.p))) seen.set(rec.h, rec.p);
      } catch {
        /* torn line */
      }
    }
  }

  const rows = readFileSync(PLAN, "utf8")
    .split("\n")
    .filter(Boolean)
    .map((line) => JSON.parse(line) as { asset: number; src: string; album: string; date: string; kind: string; bytes: number });

  let processed = 0;
  let skipped = 0;
  let failed = 0;
  let before = 0;
  let after = 0;
  const counters = new Map<string, number>();

  for (const row of rows) {
    if (LIMIT && processed + skipped + failed >= LIMIT) break;
    const free = freeGb();
    if (free <= MIN_FREE_GB) {
      console.log(`STOP: free space ${free.toFixed(1)} GiB is at the ${MIN_FREE_GB} GiB floor`);
      break;
    }
    const assetId = `db:${row.asset}`;
    if (done.has(assetId)) continue;

    const n = (counters.get(row.album) ?? 0) + 1;
    counters.set(row.album, n);
    const src = path.join(homedir(), "Pictures", row.src);
    if (!existsSync(src)) {
      skipped += 1;
      continue;
    }
    const result = processOne({
      src,
      outDir: path.join(OUT_ROOT, row.album.replace(/[/:]/g, "-")),
      stem: `${slugOf(row.album.split("/").pop() ?? row.album)}-${String(n).padStart(4, "0")}-${row.date}`,
      maxLongSide: MAX_LONG_SIDE,
      quality: QUALITY,
      videoPreset: TRANSCODE_VIDEO ? "PresetHEVC1920x1080" : null,
      seen,
    });

    record({
      asset_id: assetId,
      album: row.album,
      filename: path.basename(row.src),
      kind: result.engine === "avconvert" ? "video" : "photo",
      original_bytes: result.originalBytes,
      reduced_bytes: result.reducedBytes,
      ratio: result.ratio,
      out_path: result.outPath ? path.relative(OUT_ROOT, result.outPath) : "",
      sha256: result.sha256,
      original_sha256: result.originalSha256,
      width: result.width,
      height: result.height,
      taken_at: row.date,
      quality: result.quality,
      engine: result.engine,
      status: result.status,
      error: result.error,
      done_at: new Date().toISOString(),
    });

    if (result.status !== "failed" && result.status !== "duplicate" && result.outPath) {
      appendFileSync(HASH_INDEX, `${JSON.stringify({ h: result.originalSha256, p: path.relative(OUT_ROOT, result.outPath) })}\n`);
    }

    if (result.status === "reduced" || result.status === "over-target") {
      processed += 1;
      before += result.originalBytes;
      after += result.reducedBytes;
      if (processed % 25 === 0) {
        console.log(
          `  ${processed} done · ${(before / 1e9).toFixed(1)} GB in -> ${(after / 1e9).toFixed(1)} GB out ` +
            `(${Math.round(100 * after / (before || 1))} %) · free ${freeGb().toFixed(1)} GiB`,
        );
      }
    } else if (result.status === "failed") failed += 1;
    else skipped += 1;
  }

  console.log(
    `\n${processed} reduced, ${skipped} skipped, ${failed} failed; ` +
      `${(before / 1e9).toFixed(2)} GB in, ${(after / 1e9).toFixed(2)} GB out`,
  );
}

if (MODE === "plan") runFromPlan();
else if (MODE === "dir") runFromDir(FROM_DIR!);
else if (MODE === "run") run();
else if (MODE === "report") report();
else inventory();
