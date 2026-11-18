// One PNG for every curve in the registry, 600 px, plus a sheet to browse them.
//
//   node scripts/curve_pngs.mjs
//
// SVG is only an intermediate and goes to build/figures-svg (gitignored). The
// PNGs and the sheet land in app/public/figures, served at /figures/.

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { chromium } from "playwright-core";

const { svgForRecord } = await import("../app/src/lib/bordered.js");

const ROOT = path.resolve(import.meta.dirname, "..");
const PNG_DIR = path.join(ROOT, "app", "public", "figures");
const SVG_DIR = path.join(ROOT, "build", "figures-svg");
mkdirSync(PNG_DIR, { recursive: true });
mkdirSync(SVG_DIR, { recursive: true });

const registry = JSON.parse(readFileSync(path.join(ROOT, "workbench", "curve-registry.json"), "utf8")).curves;
const items = [];
for (const record of registry) {
  const svg = svgForRecord(record);
  const svgFile = path.join(SVG_DIR, `${record.uid}.svg`);
  writeFileSync(svgFile, svg);
  items.push({ record, svgFile });
}

const candidates = [
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/Applications/Chromium.app/Contents/MacOS/Chromium",
];
let browser = null;
for (const executablePath of candidates) {
  try { browser = await chromium.launch({ executablePath, headless: true }); break; } catch { /* next */ }
}
if (!browser) browser = await chromium.launch({ headless: true });

const page = await browser.newPage({ viewport: { width: 600, height: 600 } });
let made = 0;
for (const { record, svgFile } of items) {
  const svg = readFileSync(svgFile, "utf8");
  await page.setContent(
    `<style>html,body{margin:0;background:#fff}svg{display:block;width:600px;height:600px}</style>${svg}`,
    { waitUntil: "load" });
  await page.screenshot({ path: path.join(PNG_DIR, `${record.uid}.png`), type: "png" });
  made += 1;
}
await browser.close();

const sheet = `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Every curve</title>
<style>
body{font:13px/1.4 system-ui,sans-serif;margin:0;padding:18px;background:#faf8f2;color:#222}
h1{font-size:18px;margin:0 0 4px}p{color:#666;margin:0 0 16px}
.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
figure{margin:0;background:#fff;border:1px solid #ddd;padding:6px}
img{display:block;width:100%;height:auto}
figcaption{font-size:11px;color:#555;margin-top:4px;word-break:break-all}
</style></head><body>
<h1>Every curve</h1>
<p>${made} curves, one PNG each, cut from the same frame rule as the gallery.</p>
<div class="grid">
${items.map(({ record }) => `<figure><img src="${record.uid}.png" loading="lazy" alt="${record.name}"><figcaption>${record.uid} · ${record.name}<br>${record.family_id} · ${record.lists.join(", ")}</figcaption></figure>`).join("\n")}
</div></body></html>`;
writeFileSync(path.join(PNG_DIR, "index.html"), sheet);
console.log(`${made} PNGs in app/public/figures, and index.html`);
