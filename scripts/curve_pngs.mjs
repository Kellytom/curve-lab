// One PNG for every curve in the registry, 600 px. The index is the Astro
// page at /figures/, so this script writes images only.
//
//   node scripts/curve_pngs.mjs                 # SVGs, PNGs, sheet
//
// SVG is an intermediate and goes to build/figures-svg (gitignored). The PNGs
// and the sheet land in app/public/figures, served at /figures/.

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

const svgFiles = registry.map((record) => {
    const file = path.join(SVG_DIR, `${record.uid}.svg`);
    writeFileSync(file, svgForRecord(record));
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

  const page = await browser.newPage({ viewport: { width: 600, height: 600 } });
  for (let i = 0; i < registry.length; i += 1) {
    const svg = readFileSync(svgFiles[i], "utf8");
    await page.setContent(
      `<style>html,body{margin:0;background:#fff}svg{display:block;width:600px;height:600px}</style>${svg}`,
      { waitUntil: "load" });
    await page.screenshot({ path: path.join(PNG_DIR, `${registry[i].uid}.png`), type: "png" });
  }
await browser.close();

console.log(`${registry.length} curves in the sheet", PNGs written"`);
