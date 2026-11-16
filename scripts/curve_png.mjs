// Render one curve record to a PNG, using the same drawing the page shows.
//
//   node scripts/curve_png.mjs curves/<slug>/curve.json curves/<slug>/figure.png [width]
//
// The page is opened in a throwaway browser, the record is loaded through the same
// window.phNthLoad the gallery uses, "loop only" and "focus the knot" are pressed, and
// the plot element is screenshotted. Nothing is re-implemented here: the picture is the
// page's own picture, so a figure cannot drift from what the operator sees.

import { readFileSync, writeFileSync } from "node:fs";
import { chromium } from "playwright-core";

const [, , recordPath, outPath, widthArg] = process.argv;
if (!recordPath || !outPath) {
  console.error("usage: node scripts/curve_png.mjs <record.json> <out.png> [width]");
  process.exit(1);
}
const record = JSON.parse(readFileSync(recordPath, "utf8"));
const width = Math.min(1000, Math.max(400, Number(widthArg) || 900));

const candidates = [
  process.env.CHROME_PATH,
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
].filter(Boolean);
let browser = null;
for (const executablePath of candidates) {
  try { browser = await chromium.launch({ executablePath, headless: true }); break; }
  catch { /* next */ }
}
if (!browser) browser = await chromium.launch({ headless: true });

const page = await browser.newPage({ viewport: { width: width + 160, height: 900 } });
await page.goto("http://127.0.0.1:8003/workbench/ph-nth-sandbox-exp.html", { waitUntil: "load" });
await page.waitForTimeout(600);
await page.evaluate(item => window.phNthLoad(item), record);
await page.waitForTimeout(400);
// the loop view: the middle of t, and the frame on the knot
await page.click("#n-loop-only").catch(() => {});
await page.waitForTimeout(300);
await page.click("#n-focus-knot-hud").catch(() => {});
await page.waitForTimeout(400);
const plot = await page.$("#n-plot");
const box = await plot.boundingBox();
const height = Math.round(width * box.height / box.width);
await page.setViewportSize({ width: width + 160, height: height + 200 });
await page.waitForTimeout(300);
const png = await (await page.$("#n-plot")).screenshot();
writeFileSync(outPath, png);
console.log(`${outPath} ${png.length} bytes ${width}x${height}`);
await browser.close();
