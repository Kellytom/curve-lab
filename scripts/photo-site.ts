/**
 * photo-site.ts — the static site: albums, pages, thumbnails, and a search index.
 *
 *   node scripts/photo-site.ts                # build from what photo-public has
 *   node scripts/photo-site.ts --thumbs-only  # just fill the thumbnail cache
 *
 * Reads ~/Pictures/photo-public/manifest.jsonl and writes a site **inside** that
 * folder, at `_site/`, so every link is relative and the whole thing can be zipped,
 * moved to a bucket, or opened from a USB stick with no server:
 *
 *   photo-public/
 *     _site/index.html            the album list
 *     _site/<album>.html          one album
 *     _site/index.json            what search and filtering read
 *     _thumbs/<hash>.png          240 px, for the grid
 *     <album>/<file>.png          the full public copy
 *
 * Page weight is the thing being designed. A 60-photo album at 90 KB a file would
 * be 5.4 MB; with 240 px thumbnails it is under 1 MB, and the full copy is only
 * fetched when someone clicks.
 */

import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import path from "node:path";

const ROOT = path.join(homedir(), "Pictures", "photo-public");
const MANIFEST = path.join(ROOT, "manifest.jsonl");
const SITE = path.join(ROOT, "_site");
const THUMBS = path.join(ROOT, "_thumbs");
const THUMB_PX = 240;

const argv = process.argv.slice(2);
const THUMBS_ONLY = argv.includes("--thumbs-only");

type Item = { src: string; out: string; bytes: number; colour: boolean };

if (!existsSync(MANIFEST)) {
  console.error(`no manifest at ${MANIFEST} — run photo-derivatives.ts first`);
  process.exit(2);
}

const items: Item[] = readFileSync(MANIFEST, "utf8")
  .split("\n")
  .filter(Boolean)
  .flatMap((line) => {
    try {
      return [JSON.parse(line) as Item];
    } catch {
      return [];
    }
  })
  .filter((it) => existsSync(path.join(ROOT, it.out)));

mkdirSync(SITE, { recursive: true });
mkdirSync(THUMBS, { recursive: true });

/* ---------- thumbnails ---------- */

let thumbMade = 0;
function thumbOf(item: Item): string {
  const key = createHash("sha1").update(item.out).digest("hex").slice(0, 16);
  const out = path.join(THUMBS, `${key}.png`);
  const full = path.join(ROOT, item.out);
  if (existsSync(out) && statSync(out).mtimeMs >= statSync(full).mtimeMs) return `../_thumbs/${key}.png`;
  try {
    execFileSync("sips", ["-Z", String(THUMB_PX), "-s", "format", "png", full, "--out", out], { stdio: "ignore" });
    execFileSync("pngquant", ["--colors", "16", "--speed", "11", "--force", "--output", out, out], { stdio: "ignore" });
    thumbMade += 1;
    return `../_thumbs/${key}.png`;
  } catch {
    return `../${item.out}`;
  }
}

/* ---------- group ---------- */

const byAlbum = new Map<string, Item[]>();
for (const item of items) {
  const album = item.out.split("/")[0] ?? "_";
  const list = byAlbum.get(album) ?? [];
  list.push(item);
  byAlbum.set(album, list);
}

const slug = (text: string) =>
  text.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "") || "album";

const kb = (n: number) => (n / 1024).toFixed(0);
const mb = (n: number) => (n / 1e6).toFixed(2);
const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");

const CSS = `
:root{--ink:#111;--dim:#666;--line:#e3e3e3;--bg:#fafafa}
*{box-sizing:border-box}
body{margin:0;padding:1.5rem 2rem 4rem;font:14px/1.45 -apple-system,system-ui,sans-serif;color:var(--ink);background:var(--bg)}
h1{font-size:1.35rem;margin:0 0 .2rem}
p.sub{color:var(--dim);margin:0 0 1.5rem}
nav{position:sticky;top:0;background:var(--bg);padding:.4rem 0 1rem;border-bottom:1px solid var(--line);margin-bottom:1rem}
a{color:#123a63}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:.9rem}
.albums{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:1rem}
figure{margin:0;background:#fff;border:1px solid var(--line);border-radius:6px;overflow:hidden}
figure img{display:block;width:100%;height:160px;object-fit:cover;background:#eee}
figcaption{padding:.35rem .5rem;font-size:12px;color:var(--dim);display:flex;justify-content:space-between;gap:.5rem}
figcaption b{color:var(--ink);font-weight:500;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.card{padding:.7rem .8rem;background:#fff;border:1px solid var(--line);border-radius:8px}
.card b{display:block;font-size:1rem;margin-bottom:.15rem}
.card span{color:var(--dim);font-size:12px}
`;

/* ---------- an album page ---------- */

function albumPage(album: string, list: Item[]): { file: string; html: string; weight: number } {
  const sorted = [...list].sort((a, b) => b.bytes - a.bytes);
  let weight = 0;
  const figures = sorted
    .map((item) => {
      const t = thumbOf(item);
      const name = item.out.split("/").slice(1).join("/");
      weight += existsSync(path.join(ROOT, t.replace("../", ""))) ? statSync(path.join(ROOT, t.replace("../", ""))).size : 0;
      return `<figure><a href="../${encodeURI(item.out)}" target="_blank"><img loading="lazy" src="${encodeURI(t)}" alt="${esc(name)}"></a>
<figcaption><b>${esc(name)}</b><span>${kb(item.bytes)} KB${item.colour ? " · colour" : ""}</span></figcaption></figure>`;
    })
    .join("\n");

  const bytes = list.reduce((n, i) => n + i.bytes, 0);
  const file = `${slug(album)}.html`;
  const html = `<!doctype html><meta charset="utf-8"><title>${esc(album)}</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>${CSS}</style>
<p><a href="index.html">← all albums</a></p>
<h1>${esc(album)}</h1>
<p class="sub">${list.length} files · ${mb(bytes)} MB · click a picture for the full copy</p>
<div class="grid">${figures}</div>
`;
  return { file, html, weight };
}

/* ---------- build ---------- */

const pages: { file: string; html: string; weight: number }[] = [];
const index: { album: string; page: string; files: number; bytes: number }[] = [];

for (const [album, list] of [...byAlbum.entries()].sort((a, b) => b[1].length - a[1].length)) {
  const page = albumPage(album, list);
  pages.push(page);
  index.push({ album, page: page.file, files: list.length, bytes: list.reduce((n, i) => n + i.bytes, 0) });
}

writeFileSync(path.join(SITE, "index.json"), `${JSON.stringify({ albums: index, files: items.length }, null, 1)}\n`);

if (!THUMBS_ONLY) {
  for (const page of pages) writeFileSync(path.join(SITE, page.file), page.html);

  const cards = index
    .map((row) => {
      const cover = byAlbum.get(row.album)![0];
      const t = thumbOf(cover);
      return `<div class="card"><a href="${row.page}"><img loading="lazy" src="${encodeURI(t)}" alt="" style="width:100%;height:140px;object-fit:cover;border-radius:4px;margin-bottom:.5rem"></a>
<b><a href="${row.page}">${esc(row.album)}</a></b><span>${row.files} files · ${mb(row.bytes)} MB</span></div>`;
    })
    .join("\n");

  const totalBytes = items.reduce((n, i) => n + i.bytes, 0);
  writeFileSync(
    path.join(SITE, "index.html"),
    `<!doctype html><meta charset="utf-8"><title>photo archive</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>${CSS}</style>
<h1>Photo archive</h1>
<p class="sub">${items.length} files in ${index.length} albums · ${mb(totalBytes)} MB · static HTML, no server, no database</p>
<div class="albums">${cards}</div>
`,
  );
}

const heaviest = pages.map((p) => ({ file: p.file, weight: p.weight })).sort((a, b) => b.weight - a.weight)[0];
console.log(`${items.length} files, ${byAlbum.size} albums`);
console.log(`${THUMBS_ONLY ? "thumbnails only" : "pages written"} to ${SITE}`);
console.log(`thumbnails made this run: ${thumbMade}`);
if (heaviest) console.log(`heaviest album page images: ${mb(heaviest.weight)} MB (${heaviest.file})`);
