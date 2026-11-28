/**
 * photo-derivatives.ts — the public tier the website serves.
 *
 *   node scripts/photo-derivatives.ts --limit 20        # a sample, to judge quality
 *   node scripts/photo-derivatives.ts                   # everything, resumable
 *   node scripts/photo-derivatives.ts --force           # rebuild existing files
 *
 * Two tiers, measured 2026-11-28 on twelve real files (average 222 KB each):
 *
 *   colour, today            332 KB avg   -> 18.3 GB for 54k
 *   grey 1600 q75            190 KB avg   -> 10.5 GB
 *   grey 1200 q65 (default)  111 KB avg   ->  6.1 GB   <- fits one 10 GB free tier
 *   grey 1000 HEIC q55        45 KB avg   ->  2.5 GB   (smallest, worst compatibility)
 *
 * So the public site is greyscale at 1200 px and 6 GB, which one free bucket holds.
 * Colour is kept in three places where it is the reference rather than decoration:
 *
 *   1. a file in `keep-colour.txt`, one glob per line (`Grid art/*`, `*glass*`);
 *   2. the archive tree itself, untouched;
 *   3. the Internet Archive deposit of that tree.
 *
 * Output goes to ~/Pictures/photo-public, a separate tree, so the archive is never
 * rewritten by a change of mind about size or colour.
 */

import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, statSync, appendFileSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import path from "node:path";

const ROOT = path.join(homedir(), "Pictures", "photo-reduced");
const MANIFEST = path.join(ROOT, "manifest.jsonl");
const OUT = path.join(homedir(), "Pictures", "photo-public");
const OUT_MANIFEST = path.join(OUT, "manifest.jsonl");
const KEEP_COLOUR = path.join(ROOT, "keep-colour.txt");
const INDEX = path.join(OUT, "index.html");
const GREY_PROFILE =
  "/System/Library/ColorSync/Profiles/Generic Gray Gamma 2.2 Profile.icc";

const argv = process.argv.slice(2);
const flag = (name: string, fallback?: string): string | undefined => {
  const i = argv.indexOf(name);
  return i >= 0 && argv[i + 1] && !argv[i + 1].startsWith("--") ? argv[i + 1] : fallback;
};
const has = (name: string) => argv.includes(name);

const LONG_SIDE = Number(flag("--long-side", "1200"));
const GREY_QUALITY = Number(flag("--grey-quality", "65"));
const COLOUR_QUALITY = Number(flag("--colour-quality", "75"));
const LIMIT = Number(flag("--limit", "0"));
const ONLY_ALBUM = flag("--album");
const FORCE = has("--force");
const MIN_FREE_GB = Number(flag("--min-free-gb", "5"));

/* ---------- the colour exceptions ---------- */

/** Glob lines; `*` matches anything, case-insensitive, tested against album and source path. */
function loadKeepColour(): RegExp[] {
  if (!existsSync(KEEP_COLOUR)) return [];
  return readFileSync(KEEP_COLOUR, "utf8")
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line && !line.startsWith("#"))
    .map((glob) => new RegExp(`^${glob.replace(/[.+^${}()|[\]\\]/g, "\\$&").replace(/\*/g, ".*")}$`, "i"));
}

/* ---------- the work ---------- */

type Row = { album: string; out_path: string; filename: string; status: string; reduced_bytes: number };
type Done = { src: string; out: string; bytes: number; colour: boolean };

const keepColour = loadKeepColour();
const rows: Row[] = readFileSync(MANIFEST, "utf8")
  .split("\n")
  .filter(Boolean)
  .flatMap((line) => {
    try {
      return [JSON.parse(line) as Row];
    } catch {
      return [];
    }
  })
  .filter((r) => r.out_path && r.status !== "duplicate" && r.status !== "failed" && !r.status.startsWith("skipped-video"));

const already = new Set<string>();
if (existsSync(OUT_MANIFEST)) {
  for (const line of readFileSync(OUT_MANIFEST, "utf8").split("\n")) {
    if (!line.trim()) continue;
    try {
      already.add((JSON.parse(line) as Done).src);
    } catch {
      /* torn line */
    }
  }
}

const freeGb = (): number => {
  const out = execFileSync("df", ["-k", homedir()], { encoding: "utf8" }).trim().split("\n").pop()!;
  return Number(out.split(/\s+/)[3]) / 1024 / 1024;
};

mkdirSync(OUT, { recursive: true });

let made = 0;
let skipped = 0;
let failed = 0;
let bytesIn = 0;
let bytesOut = 0;
let colourCount = 0;

for (const row of rows) {
  if (ONLY_ALBUM && row.album !== ONLY_ALBUM) continue;
  if (LIMIT && made >= LIMIT) break;
  if (freeGb() <= MIN_FREE_GB) {
    console.log(`STOP: free space at the ${MIN_FREE_GB} GiB floor`);
    break;
  }
  if (!FORCE && already.has(row.out_path)) {
    skipped += 1;
    continue;
  }

  const src = path.join(ROOT, row.out_path);
  if (!existsSync(src)) {
    failed += 1;
    continue;
  }

  const colour = keepColour.some((re) => re.test(row.out_path) || re.test(row.album));
  const stem = path.basename(row.out_path, path.extname(row.out_path));
  const outPath = path.join(OUT, row.album.replace(/[/:]/g, "-"), `${stem}.jpg`);
  mkdirSync(path.dirname(outPath), { recursive: true });

  const args = ["-Z", String(LONG_SIDE), "-s", "format", "jpeg", "-s", "formatOptions", String(colour ? COLOUR_QUALITY : GREY_QUALITY)];
  if (!colour) args.push("--matchTo", GREY_PROFILE);
  args.push(src, "--out", outPath);

  try {
    execFileSync("sips", args, { stdio: "ignore" });
    const size = statSync(outPath).size;
    const inSize = statSync(src).size;
    bytesIn += inSize;
    bytesOut += size;
    made += 1;
    if (colour) colourCount += 1;
    appendFileSync(
      OUT_MANIFEST,
      `${JSON.stringify({ src: row.out_path, out: path.relative(OUT, outPath), bytes: size, colour })}\n`,
    );
    if (made % 200 === 0) {
      console.log(
        `  ${made} done · ${(bytesIn / 1e9).toFixed(2)} GB in -> ${(bytesOut / 1e9).toFixed(2)} GB out ` +
          `(${Math.round(100 * (bytesOut / (bytesIn || 1)))} %) · free ${freeGb().toFixed(1)} GiB`,
      );
    }
  } catch (error) {
    failed += 1;
    console.log(`  FAILED ${row.out_path}: ${(error as Error).message.slice(0, 80)}`);
  }
}

/* ---------- the page, so the sample can be judged ---------- */

const items = existsSync(OUT_MANIFEST)
  ? readFileSync(OUT_MANIFEST, "utf8")
      .split("\n")
      .filter(Boolean)
      .flatMap((line) => {
        try {
          return [JSON.parse(line) as Done];
        } catch {
          return [];
        }
      })
  : [];

if (items.length) {
  const grid = items
    .slice(-400)
    .map(
      (it) =>
        `<figure><a href="${encodeURI(it.out)}" target="_blank"><img loading="lazy" src="${encodeURI(it.out)}" alt=""></a>` +
        `<figcaption>${it.colour ? "colour" : "grey"} · ${(it.bytes / 1024).toFixed(0)} KB</figcaption></figure>`,
    )
    .join("\n");
  writeFileSync(
    INDEX,
    `<!doctype html><meta charset=utf-8><title>photo-public</title>
<style>body{font:13px -apple-system,system-ui,sans-serif;margin:1.5rem;background:#fafafa}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:.6rem}
figure{margin:0;background:#fff;border:1px solid #e3e3e3;border-radius:6px;overflow:hidden}
img{display:block;width:100%;height:150px;object-fit:contain;background:#eee}
figcaption{padding:.25rem .4rem;color:#666}</style>
<h1>photo-public — the site tier</h1>
<p>${items.length} files · ${(bytesOut / 1e9).toFixed(2)} GB this run · grey ${LONG_SIDE} px q${GREY_QUALITY}, colour exceptions q${COLOUR_QUALITY}</p>
<div class="grid">${grid}</div>
`,
  );
}

console.log(`\n${made} written, ${skipped} already done, ${failed} failed`);
console.log(
  `${(bytesIn / 1e9).toFixed(2)} GB in -> ${(bytesOut / 1e9).toFixed(2)} GB out ` +
    `(${Math.round(100 * (bytesOut / (bytesIn || 1)))} %), ${colourCount} kept in colour`,
);
console.log(`into ${OUT}`);
