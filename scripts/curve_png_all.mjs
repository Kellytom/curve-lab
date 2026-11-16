// Capture every curve's figure from the page and CHECK it against the record.
//
//   node scripts/curve_png_all.mjs
//
// For each folder: load the record through the page, read what the page reports (grid, bend,
// crossings), compare it with the record's own numbers, screenshot #n-plot, and measure the
// ink in that PNG. A figure is "ok" only when the page's grid matches the record's and the
// image carries ink. Anything else is printed as a mismatch — the point of this script is to
// catch the case where a figure looks done and is not.

import { readdirSync, readFileSync, writeFileSync } from "node:fs";
import { chromium } from "playwright-core";

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

const rows = [];
for (const slug of readdirSync("curves").filter(name => !name.includes("."))) {
  const path = `curves/${slug}/curve.json`;
  const record = JSON.parse(readFileSync(path, "utf8"));
  await page.evaluate(item => window.phNthLoad(item), record);
  await page.waitForTimeout(650);
  const facts = await page.evaluate(() => {
    const text = document.getElementById("n-readout").textContent;
    const grid = (text.match(/grid 1\/([0-9,]+)/) || [])[1];
    const bend = (text.match(/bend ([0-9.]+)/) || [])[1];
    const crossings = (text.match(/crosses itself (\d+)/) || [])[1];
    const svg = document.getElementById("n-plot");
    return { grid: grid ? Number(grid.replace(/,/g, "")) : null, bend: bend ? Number(bend) : null,
             crossings: crossings ? Number(crossings) : null, viewBox: svg.getAttribute("viewBox") };
  });
  // A row the page cannot draw keeps its exact figure: capturing the page would overwrite a
  // correct picture with a blank one, which is the failure this script exists to catch.
  const pageCanDraw = record.figure && record.figure.page_agrees !== false;
  let png;
  if (pageCanDraw) {
    png = await (await page.$("#n-plot")).screenshot();
    writeFileSync(`curves/${slug}/figure.png`, png);
  } else {
    png = readFileSync(`curves/${slug}/figure.png`);
  }
  const ink = await page.evaluate(async b64 => {
    const image = new Image(); image.src = "data:image/png;base64," + b64; await image.decode();
    const canvas = document.createElement("canvas"); canvas.width = image.width; canvas.height = image.height;
    const context = canvas.getContext("2d"); context.drawImage(image, 0, 0);
    const { data } = context.getImageData(0, 0, canvas.width, canvas.height);
    let dark = 0, minX = 1e9, maxX = -1e9, minY = 1e9, maxY = -1e9;
    for (let y = 0; y < canvas.height; y++) for (let x = 0; x < canvas.width; x++) {
      const i = (y * canvas.width + x) * 4, g = (data[i] + data[i + 1] + data[i + 2]) / 3;
      if (g < 90) { dark++; minX = Math.min(minX, x); maxX = Math.max(maxX, x); minY = Math.min(minY, y); maxY = Math.max(maxY, y); }
    }
    return { dark, width: maxX - minX, height: maxY - minY, size: `${image.width}x${image.height}` };
  }, png.toString("base64"));
  const gridMatch = facts.grid === Number(record.grid);
  const bendMatch = record.bend === null || Math.abs((facts.bend || 0) - Number(record.bend)) < 0.01;
  const inked = ink.dark > 300 && ink.height > 20 && ink.width > 20;
  rows.push({ slug, recordGrid: record.grid, pageGrid: facts.grid, gridMatch,
              recordBend: record.bend, pageBend: facts.bend, bendMatch, ink, inked,
              exact: !pageCanDraw, bytes: png.length });
}

console.log("curve".padEnd(24), "grid record".padStart(12), "page".padStart(12), " agree", " bend", "ink px", "box", " verdict");
for (const row of rows) {
  const verdict = row.exact
    ? (row.inked ? "exact figure" : "BLANK")
    : (row.gridMatch && row.bendMatch && row.inked ? "ok" : "MISMATCH");
  console.log(row.slug.padEnd(24), String(row.recordGrid).padStart(12), String(row.pageGrid).padStart(12),
    String(row.gridMatch).padStart(6), String(row.bendMatch).padStart(5),
    String(row.ink.dark).padStart(6), `${row.ink.width}x${row.ink.height}`.padStart(9), verdict);
}
const bad = rows.filter(row => row.exact ? !row.inked : !(row.gridMatch && row.bendMatch && row.inked));
const fromPage = rows.filter(row => !row.exact).length;
console.log(`\n${rows.length} curves: ${fromPage} drawn by the page and agreeing with the record, ` +
            `${rows.length - fromPage} drawn exactly because the page cannot, ${bad.length} bad`);
await browser.close();
