// One bordered PNG for every curve in the registry, 600 px, plus the measured
// border margin for each. The index page is the Astro route at /figures/.
//
//   node scripts/curve_pngs.mjs
//
// SVG is an intermediate and goes to build/figures-svg (gitignored). The PNGs
// and index.json land in app/public/figures.

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { chromium } from "playwright-core";

const { figureFor, svgForFigure } = await import("../app/src/lib/bordered.js");

const ROOT = path.resolve(import.meta.dirname, "..");
const PNG_DIR = path.join(ROOT, "app", "public", "figures");
const SVG_DIR = path.join(ROOT, "build", "figures-svg");
mkdirSync(PNG_DIR, { recursive: true });
mkdirSync(SVG_DIR, { recursive: true });

const registry = JSON.parse(readFileSync(path.join(ROOT, "workbench", "curve-registry.json"), "utf8")).curves;
const items = registry.map((record) => {
  const figure = figureFor(record, { [record.name]: record });
  const svgFile = path.join(SVG_DIR, `${record.uid}.svg`);
  writeFileSync(svgFile, svgForFigure(figure, `${record.uid}: ${record.name}`));
  return {
    record,
    svgFile,
    meta: {
      uid: record.uid,
      name: record.name,
      family: record.family_id,
      perSide: figure.perSide,
      marginPercent: figure.margin,
      failed: figure.failed,
      reason: figure.reason || null,
      tooWide: figure.tooWide || false,
    },
  };
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

const page = await browser.newPage({ viewport: { width: 600, height: 600 } });
for (const item of items) {
  await page.setContent(
    `<style>html,body{margin:0;background:#fff}svg{display:block;width:600px;height:600px}</style>` +
    readFileSync(item.svgFile, "utf8"),
    { waitUntil: "load" });
  await page.screenshot({ path: path.join(PNG_DIR, `${item.record.uid}.png`), type: "png" });
}
await browser.close();

writeFileSync(path.join(PNG_DIR, "index.json"),
  JSON.stringify({ format: "curve-lab.figures/1", curves: items.map((item) => item.meta) }, null, 1) + "\n");
console.log(`${items.length} bordered PNGs, with index.json`);
