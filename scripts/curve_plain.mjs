// A plain PNG of every curve: the spine alone, no border, no rails. For the
// naming desk, where the question is "which curve is this".
//
//   node scripts/curve_plain.mjs
//
// Writes app/public/curves/<uid>.png at 400 px. The SVG intermediate goes to
// build/plain-svg (gitignored).

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { chromium } from "playwright-core";

const { plainSvgForRecord } = await import("../app/src/lib/bordered.js");

const ROOT = path.resolve(import.meta.dirname, "..");
const PNG_DIR = path.join(ROOT, "app", "public", "curves");
const SVG_DIR = path.join(ROOT, "build", "plain-svg");
mkdirSync(PNG_DIR, { recursive: true });
mkdirSync(SVG_DIR, { recursive: true });

const registry = JSON.parse(readFileSync(path.join(ROOT, "workbench", "curve-registry.json"), "utf8")).curves;
const svgFiles = registry.map((record) => {
  const file = path.join(SVG_DIR, `${record.uid}.svg`);
  writeFileSync(file, plainSvgForRecord(record));
  return file;
});

const candidates = [
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/Applications/Chromium.app/Contents/MacOS/Chromium",
];
let browser = null;
for (const executablePath of candidates) {
  try { browser = await chromium.launch({ executablePath, headless: true }); break; } catch { /* next */ }
}
if (!browser) browser = await chromium.launch({ headless: true });

const page = await browser.newPage({ viewport: { width: 400, height: 400 } });
for (let i = 0; i < registry.length; i += 1) {
  const svg = readFileSync(svgFiles[i], "utf8");
  await page.setContent(
    `<style>html,body{margin:0;background:#fff}svg{display:block;width:400px;height:400px}</style>${svg}`,
    { waitUntil: "load" });
  await page.screenshot({ path: path.join(PNG_DIR, `${registry[i].uid}.png`), type: "png" });
}
await browser.close();
console.log(`${registry.length} plain PNGs in app/public/curves`);
