// Print-size PNGs for the book, from the same figure the page draws.
//
//   node scripts/book_export.mjs              # the 90 A plates at 3000 px
//   node scripts/book_export.mjs --b          # also the 90 -B plates
//   node scripts/book_export.mjs --only c-0001
//
// White ground, no text, tight to the marks, 300 dpi. The plate names and their
// settings come from workbench/frames.json, which scripts/frames_build.mjs
// writes; the figure comes from app/src/lib/bordered.js, so the book and the
// screen cannot disagree.
//
// Output: book/illus/<name>.png and book/illus.json (the manifest).

import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright-core";
import { figureFor, svgForFigure } from "../app/src/lib/bordered.js";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const SIZE = 3000;
const DPI = 300;
const OUT = path.join(ROOT, "book", "illus");
mkdirSync(OUT, { recursive: true });

const WITH_B = process.argv.includes("--b");
const FORCE = process.argv.includes("--force");
const onlyAt = process.argv.indexOf("--only");
const ONLY = onlyAt >= 0 ? new Set(process.argv.slice(onlyAt + 1).flatMap((v) => v.split(","))) : null;

const registry = JSON.parse(readFileSync(path.join(ROOT, "workbench", "curve-registry.json"), "utf8")).curves;
const byUid = Object.fromEntries(registry.map((record) => [record.uid, record]));
const notes = JSON.parse(readFileSync(path.join(ROOT, "workbench", "curve-notes.json"), "utf8")).curves;
const noteByUid = Object.fromEntries(notes.map((note) => [note.uid, note]));
const frames = JSON.parse(readFileSync(path.join(ROOT, "workbench", "frames.json"), "utf8"));

const recordOf = (uid) => {
  const note = noteByUid[uid] || {};
  const base = { ...byUid[uid], ...note };
  return base;
};

const rows = [];
const browser = await chromium.launch({
  executablePath: process.env.CHROME_PATH || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
});
const page = await browser.newPage({ viewport: { width: SIZE, height: SIZE }, deviceScaleFactor: 1 });

for (const plate of frames.curves) {
  if (ONLY && !ONLY.has(plate.uid)) continue;
  const variants = WITH_B ? ["A", "B"] : ["A"];
  for (const variant of variants) {
    const name = variant === "B" ? `${plate.illus}-B` : plate.illus;
    const file = path.join(OUT, `${name}.png`);
    if (existsSync(file) && !FORCE) {
      rows.push({ name, uid: plate.uid, variant, file: path.relative(ROOT, file), skipped: true });
      continue;
    }
    const record = recordOf(plate.uid);
    if (variant === "B") record.offsets = 1;
    const border = record.border_uid ? byUid[record.border_uid] : null;
    const figure = figureFor(record, { [record.name]: record }, border);
    const svg = svgForFigure(figure, name);
    await page.setContent(
      `<html><body style="margin:0;background:#fff">${svg.replace(
        `<svg xmlns="http://www.w3.org/2000/svg"`,
        `<svg xmlns="http://www.w3.org/2000/svg" width="${SIZE}" height="${SIZE}"`,
      )}</body></html>`,
      { waitUntil: "load" },
    );
    await page.screenshot({ path: file, clip: { x: 0, y: 0, width: SIZE, height: SIZE } });
    rows.push({
      name, uid: plate.uid, variant,
      frame: plate.frame, offsets: variant === "B" ? 1 : (record.offsets ? 1 : 0),
      perSide: figure.perSide, border: record.border_uid || null,
      file: path.relative(ROOT, file),
    });
    console.log(`${name} · ${SIZE}px · ${variant}`);
  }
}

await browser.close();

// 300 dpi, so LibreOffice inserts the plate at ~254 mm rather than 790 mm.
const written = rows.filter((row) => !row.skipped);
if (written.length) {
  execFileSync("sips", ["-s", "dpiWidth", String(DPI), "-s", "dpiHeight", String(DPI),
    ...written.map((row) => path.join(ROOT, row.file))], { stdio: "pipe" });
}

const manifestFile = path.join(ROOT, "book", "illus.json");
writeFileSync(manifestFile, JSON.stringify({
  format: "curve-lab.illus/1",
  note: "the frames as print plates: white ground, no text, tight to the marks, 300 dpi",
  pixels: SIZE,
  dpi: DPI,
  plates: rows,
}, null, 1) + "\n");

console.log(`\n${written.length} plates written, ${rows.length} in the manifest, ${DPI} dpi`);
