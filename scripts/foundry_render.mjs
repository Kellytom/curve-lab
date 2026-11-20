// Render candidate curves with the collection's own figure code, so a new curve
// is seen through the same frame, fill and rails as a stored one.
//
//   node scripts/foundry_render.mjs candidates.json out-dir
//
// The input is a JSON array of {uid, name, path} records (path = [[x, y], ...]).
// Nothing is written to the registry or the database by this script.

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { chromium } from "playwright-core";

const { figureFor, svgForFigure } = await import("../app/src/lib/bordered.js");

const [input, outDir] = process.argv.slice(2);
if (!input || !outDir) {
  console.error("usage: node scripts/foundry_render.mjs candidates.json out-dir");
  process.exit(1);
}
mkdirSync(outDir, { recursive: true });
const records = JSON.parse(readFileSync(input, "utf8"));

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
const done = [];
for (const record of records) {
  const figure = figureFor(record, { [record.name]: record }, null);
  const svgFile = path.join(outDir, `${record.uid}.svg`);
  writeFileSync(svgFile, svgForFigure(figure, `${record.uid}: ${record.name}`));
  await page.setContent(
    `<style>html,body{margin:0;background:#fff}svg{display:block;width:600px;height:600px}</style>`
    + readFileSync(svgFile, "utf8"),
    { waitUntil: "load" });
  await page.screenshot({ path: path.join(outDir, `${record.uid}.png`), type: "png" });
  done.push({ uid: record.uid, name: record.name, failed: figure.failed, reason: figure.reason || null });
}
await browser.close();
console.log(JSON.stringify(done, null, 1));
