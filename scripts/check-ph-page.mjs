// Check the generated gallery in a real browser: the six readouts, the save
// buttons, and no page errors.
//
//   node scripts/check-ph-page.mjs
//   node scripts/check-ph-page.mjs http://127.0.0.1:8003/workbench/ph-quintic-gallery.html
//
// Needs the headless Chrome shell on CDP port 9223 (the same one the other
// browser checks use). Exits 1 on any mismatch.

import { chromium } from "playwright-core";

const url = process.argv[2] || "http://127.0.0.1:8003/workbench/ph-quintic-gallery.html";
const expected = {
  "q7-readout": "bend 1.15",
  "q8-readout": "bend 5.58",
  "q9-readout": "bend 2.00",
  "q10-readout": "bend 1.91",
  "q11-readout": "bend 2.04",
  "q13-exact": "arc",
  "q14-readout": "bend 1.997",
};

const browser = await chromium.connectOverCDP("http://127.0.0.1:9223");
const page = await browser.contexts()[0].newPage();
const errors = [];
page.on("pageerror", error => errors.push(error.message));

await page.setViewportSize({ width: 1200, height: 1000 });
await page.goto(`${url}?v=${Date.now()}`, { waitUntil: "load" });

const failures = [];
for (const [id, prefix] of Object.entries(expected)) {
  const text = await page.evaluate(id => {
    const element = document.getElementById(id);
    return element ? element.textContent : null;
  }, id);
  if (text === null) failures.push(`${id}: missing`);
  else if (!text.startsWith(prefix)) failures.push(`${id}: "${text}" does not start with "${prefix}"`);
}

const saveButtons = await page.locator(".save-curve").count();
if (saveButtons !== 6) failures.push(`save buttons: ${saveButtons}, expected 6`);

// the septic sandbox: its numbers must match the Python metrics module
const sandboxUrl = url.replace("ph-quintic-gallery.html", "ph-septic-sandbox.html");
await page.goto(`${sandboxUrl}?v=${Date.now()}`, { waitUntil: "load" });
const septic = await page.evaluate(() => document.getElementById("b-readout").textContent);
if (!septic.startsWith("bend 1.850 | pitch 700 | inflection 0.494 | closest 1.461")) {
  failures.push(`septic readout: "${septic}"`);
}

if (errors.length) failures.push(`page errors: ${errors.join(" | ")}`);

await page.close();
await browser.close().catch(() => {});

if (failures.length) {
  console.error("FAIL");
  for (const failure of failures) console.error("  " + failure);
  process.exit(1);
}
console.log(`OK  ${Object.keys(expected).length} readouts, ${saveButtons} save buttons, no page errors`);
