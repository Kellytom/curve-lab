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
// The view is chosen by the record's figure spec, so a figure can be adjusted by hand:
//   "view": "loop"   the middle of t (default)
//   "view": "knot"   frame the knot
//   "view": "whole"  the whole curve
//   "range": [from, to]   an explicit window of t
const spec = record.figure || {};
const view = spec.view || "loop";
if (Array.isArray(spec.range)) {
  await page.evaluate(([from, to]) => {
    for (const [id, value] of [["n-t-from", from], ["n-t-to", to]]) {
      const field = document.getElementById(id);
      if (field) { field.value = String(value); field.dispatchEvent(new Event("change", { bubbles: true })); }
    }
  }, spec.range);
  await page.waitForTimeout(400);
} else if (view === "loop") {
  await page.click("#n-loop-only").catch(() => {});
  await page.waitForTimeout(300);
} else if (view === "knot") {
  await page.click("#n-focus-knot-hud").catch(() => {});
  await page.waitForTimeout(300);
}
// manual adjustments, written by hand in curve.json when a figure needs them
const focus = spec.focus;
if (focus) {
  await page.fill("#n-focus-x", String(focus.x)).catch(() => {});
  await page.fill("#n-focus-y", String(focus.y)).catch(() => {});
  await page.click("#n-focus-here").catch(() => {});
  await page.waitForTimeout(300);
}
if (spec.zoom) {
  await page.fill("#n-zoom-number", String(spec.zoom)).catch(() => {});
  await page.waitForTimeout(300);
}
if (Array.isArray(spec.pan)) {
  await page.fill("#n-pan-x-number", String(spec.pan[0] || 0)).catch(() => {});
  await page.fill("#n-pan-y-number", String(spec.pan[1] || 0)).catch(() => {});
  await page.waitForTimeout(300);
}
const plot = await page.$("#n-plot");
const box = await plot.boundingBox();
const height = Math.round(width * box.height / box.width);
await page.setViewportSize({ width: width + 160, height: height + 200 });
await page.waitForTimeout(300);
const facts = await page.evaluate(() => {
  const f = window.phNthFrame();
  const d = document.querySelector("#n-plot path").getAttribute("d");
  return { span: +((f.maxX - f.minX)).toExponential(2),
           points: (new Set((d.match(/-?\d+\.\d+,-?\d+\.\d+/g) || []))).size,
           scale: window.phNthScale ? window.phNthScale() : null };
});
console.log("render facts:", JSON.stringify(facts));
const png = await (await page.$("#n-plot")).screenshot();
writeFileSync(outPath, png);
console.log(`${outPath} ${png.length} bytes ${width}x${height}`);
await browser.close();
