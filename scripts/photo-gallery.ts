/**
 * photo-gallery.ts — a contact sheet for judging the reductions, from the manifest.
 *
 *   node scripts/photo-gallery.ts            # build ~/Pictures/photo-reduced/gallery.html
 *   node scripts/photo-gallery.ts --open-path  # print the path only
 *
 * Finder is fine for moving files and bad for the question this work actually asks:
 * "is this copy good enough, and how much did it save?" So the manifest becomes one
 * page: a thumbnail per file, the bytes before and after, the ratio, and a click that
 * opens the full-size copy. No install, no library to import, nothing locked in.
 *
 * Thumbnails are cached in _thumbs/, named by the file's path hash, so a rebuild
 * after a new album costs only the new files.
 */

import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import path from "node:path";

const ROOT = path.join(homedir(), "Pictures", "photo-reduced");
const MANIFEST = path.join(ROOT, "manifest.jsonl");
const THUMBS = path.join(ROOT, "_thumbs");
const OUT = path.join(ROOT, "gallery.html");
const THUMB_PX = 360;

type Row = {
  asset_id: string;
  album: string;
  filename: string;
  original_bytes: number;
  reduced_bytes: number;
  ratio: number;
  out_path: string;
  width: number | null;
  height: number | null;
  status: string;
  engine: string | null;
  quality: number | null;
};

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
  .filter((r) => r.out_path && r.reduced_bytes > 0 && !r.status.startsWith("skipped-video"));

mkdirSync(THUMBS, { recursive: true });

let made = 0;
let cached = 0;
function thumb(row: Row): string | null {
  const full = path.join(ROOT, row.out_path);
  if (!existsSync(full)) return null;
  const key = createHash("sha1").update(row.out_path).digest("hex").slice(0, 16);
  const out = path.join(THUMBS, `${key}.jpg`);
  if (existsSync(out) && statSync(out).mtimeMs >= statSync(full).mtimeMs) {
    cached += 1;
    return `_thumbs/${key}.jpg`;
  }
  try {
    execFileSync("sips", ["-Z", String(THUMB_PX), "-s", "format", "jpeg", "-s", "formatOptions", "70", full, "--out", out], {
      stdio: "ignore",
    });
    made += 1;
    return `_thumbs/${key}.jpg`;
  } catch {
    return null;
  }
}

const byAlbum = new Map<string, { row: Row; thumb: string | null }[]>();
for (const row of rows) {
  const list = byAlbum.get(row.album) ?? [];
  list.push({ row, thumb: thumb(row) });
  byAlbum.set(row.album, list);
}

const mb = (n: number) => (n / 1e6).toFixed(2);
const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");

const totalIn = rows.reduce((n, r) => n + r.original_bytes, 0);
const totalOut = rows.reduce((n, r) => n + r.reduced_bytes, 0);

const sections = [...byAlbum.entries()]
  .sort((a, b) => b[1].reduce((n, x) => n + x.row.original_bytes, 0) - a[1].reduce((n, x) => n + x.row.original_bytes, 0))
  .map(([album, items]) => {
    const inBytes = items.reduce((n, x) => n + x.row.original_bytes, 0);
    const outBytes = items.reduce((n, x) => n + x.row.reduced_bytes, 0);
    const cards = items
      .sort((a, b) => b.row.original_bytes - a.row.original_bytes)
      .map(({ row, thumb: t }) => {
        const pct = Math.round(100 * row.reduced_bytes / row.original_bytes);
        const dims = row.width && row.height ? `${row.width}×${row.height}` : "";
        return `<figure>
  <a href="${encodeURI(row.out_path)}" target="_blank"><img loading="lazy" src="${t ?? ""}" alt="${esc(row.filename)}"></a>
  <figcaption>
    <b>${esc(row.filename)}</b>
    <span>${mb(row.original_bytes)} → ${mb(row.reduced_bytes)} MB · <em>${pct}%</em></span>
    <span class="dim">${dims} · ${row.engine ?? ""}${row.quality ? " q" + row.quality : ""}</span>
  </figcaption>
</figure>`;
      })
      .join("\n");
    return `<section>
  <h2>${esc(album)} <small>${items.length} files · ${mb(inBytes)} → ${mb(outBytes)} MB · ${Math.round(100 * outBytes / inBytes)}%</small></h2>
  <div class="grid">${cards}</div>
</section>`;
  })
  .join("\n");

const html = `<!doctype html>
<meta charset="utf-8">
<title>photo-reduced — contact sheet</title>
<style>
  body{font:14px -apple-system,system-ui,sans-serif;margin:0;padding:1.5rem 2rem 4rem;color:#111;background:#fafafa}
  h1{margin:0 0 .2rem;font-size:1.4rem}
  .sum{color:#555;margin:0 0 1.5rem}
  h2{font-size:1rem;margin:2rem 0 .6rem;border-bottom:1px solid #ddd;padding-bottom:.3rem}
  h2 small{font-weight:400;color:#666;margin-left:.5rem}
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:.9rem}
  figure{margin:0;background:#fff;border:1px solid #e3e3e3;border-radius:6px;overflow:hidden}
  figure img{display:block;width:100%;height:170px;object-fit:contain;background:#f0f0f0}
  figcaption{padding:.4rem .5rem;display:flex;flex-direction:column;gap:.1rem}
  figcaption b{font-weight:600;font-size:12px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  figcaption span{font-size:11px;color:#555}
  .dim{color:#888}
  em{font-style:normal;font-weight:600;color:#1f7a4d}
  nav{position:sticky;top:0;background:#fafafa;padding:.4rem 0;border-bottom:1px solid #eee;margin-bottom:.5rem;font-size:12px}
  nav a{margin-right:.8rem;color:#123a63}
</style>
<h1>photo-reduced — contact sheet</h1>
<p class="sum">${rows.length} files · ${mb(totalIn)} MB in → ${mb(totalOut)} MB out · <b>${Math.round(100 * (1 - totalOut / (totalIn || 1)))}% smaller</b> · click a picture for the full copy</p>
<nav>${[...byAlbum.keys()].map((a) => `<a href="#${encodeURIComponent(a)}">${esc(a)}</a>`).join(" ")}</nav>
${sections}
`;

writeFileSync(OUT, html);
console.log(`wrote ${OUT}`);
console.log(`${rows.length} files, ${byAlbum.size} albums; thumbnails ${made} made, ${cached} cached`);
