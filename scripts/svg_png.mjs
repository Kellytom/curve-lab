// Rasterise an SVG file to a PNG, at a width, on flat paper.
//
//   node scripts/svg_png.mjs in.svg out.png [width]
//
// Used by scripts/curve_svg.py: the curve is computed in exact fractions there, so the
// picture does not depend on the page's double-precision evaluation.

import { readFileSync, writeFileSync } from "node:fs";
import { chromium } from "playwright-core";

const [, , svgPath, outPath, widthArg] = process.argv;
if (!svgPath || !outPath) {
  console.error("usage: node scripts/svg_png.mjs <in.svg> <out.png> [width]");
  process.exit(1);
}
const width = Math.min(1000, Math.max(400, Number(widthArg) || 900));
const svg = readFileSync(svgPath, "utf8");
const match = svg.match(/viewBox="0 0 (\d+(?:\.\d+)?) (\d+(?:\.\d+)?)"/);
const aspect = match ? Number(match[2]) / Number(match[1]) : 0.62;
const height = Math.round(width * aspect);

const candidates = [process.env.CHROME_PATH,
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"].filter(Boolean);
let browser = null;
for (const executablePath of candidates) {
  try { browser = await chromium.launch({ executablePath, headless: true }); break; } catch { /* next */ }
}
if (!browser) browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
await page.setContent(`<html><body style="margin:0;background:#fbf7ec">${
  svg.replace(/width="[^"]*"/, `width="${width}"`).replace(/height="[^"]*"/, `height="${height}"`)
}</body></html>`);
await page.waitForTimeout(150);
const png = await page.screenshot({ clip: { x: 0, y: 0, width, height } });
writeFileSync(outPath, png);
console.log(`${outPath} ${png.length} bytes ${width}x${height}`);
await browser.close();
