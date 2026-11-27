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
import { appendFileSync, existsSync, mkdirSync, readFileSync, readdirSync, rmSync, statSync } from "node:fs";
import { createHash } from "node:crypto";
import { homedir } from "node:os";
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
const MODE = has("--run") ? "run" : "inventory";

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

function listAlbums(): Album[] {
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

type Item = { id: string; filename: string; date: string };

/**
 * Export a range of one album in a single Apple event.
 * Resolving the album by name costs seconds, so one call per asset was 10×
 * slower than one call per chunk. Returns the ids and names in Photos' order.
 */
function exportChunk(album: string, from: number, to: number, target: string): Item[] {
  const script = `
    set out to ""
    tell application "Photos"
      set theAlbum to album ${JSON.stringify(album)}
      set theItems to media items ${from} thru ${to} of theAlbum
      repeat with m in theItems
        set out to out & (id of m as string) & tab & (filename of m as string) & tab & ((date of m) as string) & linefeed
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
      return { id, filename, date };
    });
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
  for (const line of readFileSync(MANIFEST, "utf8").split("\n")) {
    if (!line.trim()) continue;
    try {
      const row = JSON.parse(line) as Row;
      if (row.status && row.status !== "failed") done.add(row.asset_id);
    } catch {
      /* a torn last line from a crash is ignored, not a reason to stop */
    }
  }
  return done;
}

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

/* ---------- run ---------- */

function run(): void {
  checkAccess();
  mkdirSync(STAGING, { recursive: true });
  mkdirSync(OUT_ROOT, { recursive: true });
  const done = loadDone();
  const albums = listAlbums().filter((a) => !ONLY_ALBUM || a.name === ONLY_ALBUM);
  if (albums.length === 0) {
    console.error(ONLY_ALBUM ? `no album named ${JSON.stringify(ONLY_ALBUM)}` : "no albums");
    process.exit(2);
  }

  let processed = 0;
  let skipped = 0;
  let failed = 0;
  let before = 0;
  let after = 0;

  const IMAGE = [".heic", ".heif", ".jpg", ".jpeg", ".png", ".tif", ".tiff"];
  const VIDEO = [".mov", ".mp4", ".m4v"];

  /** Reduce one exported file, or record why not. Returns false on failure. */
  const handle = (album: string, item: Item, src: string, cleanUp: () => void): boolean => {
    const srcExt = path.extname(src).toLowerCase();
    const originalBytes = statSync(src).size;
    const albumDir = path.join(OUT_ROOT, album.replace(/[/:]/g, "-"));
    let outPath = path.join(albumDir, path.basename(src, path.extname(src)) + srcExt);
    let suffix = 2;
    while (existsSync(outPath)) {
      const stem = path.basename(outPath, path.extname(outPath));
      outPath = path.join(path.dirname(outPath), `${stem} (${suffix})${path.extname(outPath)}`);
      suffix += 1;
    }

    if (VIDEO.includes(srcExt)) {
      record({
        asset_id: item.id, album, filename: item.filename, kind: "video",
        original_bytes: originalBytes, reduced_bytes: originalBytes, ratio: 1, out_path: "",
        sha256: null, width: null, height: null, taken_at: item.date, quality: null,
        engine: null, status: "skipped-video", error: null, done_at: new Date().toISOString(),
      });
      skipped += 1;
      cleanUp();
      return true;
    }

    if (originalBytes < 400 * 1024) {
      mkdirSync(path.dirname(outPath), { recursive: true });
      execFileSync("cp", [src, outPath]);
      record({
        asset_id: item.id, album, filename: item.filename, kind: "photo",
        original_bytes: originalBytes, reduced_bytes: originalBytes, ratio: 1,
        out_path: path.relative(OUT_ROOT, outPath), sha256: sha256(outPath), width: null, height: null,
        taken_at: item.date, quality: null, engine: "copy", status: "skipped-small",
        error: null, done_at: new Date().toISOString(),
      });
      skipped += 1;
      cleanUp();
      return true;
    }

    try {
      let result = reduce(src, outPath);
      if (result.engine === "sips" && result.bytes > originalBytes / 2 && (result.quality ?? 100) > 70) {
        rmSync(outPath, { force: true });
        const again = path.join(path.dirname(src), "again" + srcExt);
        execFileSync("cp", [src, again]);
        const args = ["-s", "formatOptions", "70"];
        const dim = imageSize(again);
        if (dim && Math.max(dim.width, dim.height) > MAX_LONG_SIDE) args.push("-Z", String(MAX_LONG_SIDE));
        execFileSync("sips", [...args, again, "--out", outPath], { stdio: "ignore" });
        rmSync(again, { force: true });
        result = { engine: "sips", quality: 70, bytes: statSync(outPath).size };
      }

      // A reduction that inflates is not a reduction: keep the original bytes.
      if (result.bytes >= originalBytes) {
        rmSync(outPath, { force: true });
        mkdirSync(path.dirname(outPath), { recursive: true });
        execFileSync("cp", [src, outPath]);
        result = { engine: "copy", quality: null, bytes: statSync(outPath).size };
      }

      const dim = imageSize(outPath);
      const status =
        result.engine === "copy" ? "skipped-larger" : result.bytes <= originalBytes / 2 ? "reduced" : "over-target";
      record({
        asset_id: item.id, album, filename: item.filename, kind: "photo",
        original_bytes: originalBytes, reduced_bytes: result.bytes,
        ratio: +(result.bytes / originalBytes).toFixed(3),
        out_path: path.relative(OUT_ROOT, outPath), sha256: sha256(outPath),
        width: dim?.width ?? null, height: dim?.height ?? null, taken_at: item.date,
        quality: result.quality, engine: result.engine, status, error: null,
        done_at: new Date().toISOString(),
      });
      processed += 1;
      before += originalBytes;
      after += result.bytes;
      console.log(
        `  ${album} ${item.filename} ${(originalBytes / 1e6).toFixed(2)} -> ${(result.bytes / 1e6).toFixed(2)} MB ` +
          `(${(100 * result.bytes / originalBytes).toFixed(0)} %) ${status}`,
      );
      cleanUp();
      return true;
    } catch (error) {
      record({
        asset_id: item.id, album, filename: item.filename, kind: "photo",
        original_bytes: originalBytes, reduced_bytes: 0, ratio: 0,
        out_path: path.relative(OUT_ROOT, outPath), sha256: null, width: null, height: null,
        taken_at: item.date, quality: null, engine: null, status: "failed",
        error: (error as Error).message, done_at: new Date().toISOString(),
      });
      console.log(`  FAILED ${album} ${item.filename}: ${(error as Error).message}`);
      failed += 1;
      rmSync(outPath, { force: true });
      cleanUp();
      return false;
    }
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
        items = exportChunk(album.name, from, to, stage);
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

if (MODE === "run") run();
else inventory();
