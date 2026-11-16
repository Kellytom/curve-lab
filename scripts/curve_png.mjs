// Capture figure 1: the primary curve's plot, exactly as the page draws it.
//
//   node scripts/curve_png.mjs curves/<slug>/curve.json curves/<slug>/figure.png
//
// The page is opened at a FIXED viewport, so the capture does not depend on any window the
// operator happens to have: a screenshot at a different width is a different image, which is
// what made two "page" pictures look different while both were faithful. The record is loaded
// through window.phNthLoad, the page is given time to settle, and the frame the page reports
// is printed next to the file it wrote, so the two can be compared line by line.

import { readFileSync, writeFileSync } from "node:fs";
import { chromium } from "playwright-core";

const [, , recordPath, outPath] = process.argv;
if (!recordPath || !outPath) {
  console.error("usage: node scripts/curve_png.mjs <record.json> <out.png>");
  process.exit(1);
}
const record = JSON.parse(readFileSync(recordPath, "utf8"));
const VIEWPORT = { width: 1280, height: 1000 };

const candidates = [process.env.CHROME_PATH,
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"].filter(Boolean);
let browser = null;
for (const executablePath of candidates) {
  try { browser = await chromium.launch({ executablePath, headless: true }); break; } catch { /* next */ }
}
if (!browser) browser = await chromium.launch({ headless: true });

const page = await browser.newPage({ viewport: VIEWPORT, deviceScaleFactor: 1 });
await page.goto("http://127.0.0.1:8003/workbench/ph-nth-sandbox-exp.html", { waitUntil: "load" });
await page.waitForTimeout(700);
await page.evaluate(item => window.phNthLoad(item), record);
await page.waitForTimeout(900);

const facts = await page.evaluate(() => {
  const svg = document.getElementById("n-plot");
  const frame = window.phNthFrame ? window.phNthFrame() : null;
  const spine = [...svg.querySelectorAll("path")]
    .find(p => (p.getAttribute("stroke") || "").toLowerCase() === "#2e2413");
  const d = spine ? spine.getAttribute("d") : "";
  const coords = (d.match(/-?\d+\.\d+,-?\d+\.\d+/g) || []);
  const xs = coords.map(c => Number(c.split(",")[0]));
  const ys = coords.map(c => Number(c.split(",")[1]));
  return {
    name: document.getElementById("n-curve-name").textContent,
    viewBox: svg.getAttribute("viewBox"),
    element: `${svg.clientWidth}x${svg.clientHeight}`,
    points: coords.length,
    pathBox: [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)].map(v => Math.round(v)),
    frame: frame ? { spanX: +(frame.maxX - frame.minX).toFixed(3), spanY: +(frame.maxY - frame.minY).toFixed(3) } : null,
    readout: document.getElementById("n-readout").textContent.slice(0, 70),
  };
});

const png = await (await page.$("#n-plot")).screenshot();
writeFileSync(outPath, png);
console.log(JSON.stringify(facts));
console.log(`${outPath} ${png.length} bytes`);
await browser.close();
