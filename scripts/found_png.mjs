// Capture figure 1 for every found curve: load it in the page, screenshot the primary plot.
//
//   node scripts/found_png.mjs            # all of found-curves.json
//   node scripts/found_png.mjs --only name
//
// One image per curve in workbench/figures/<slug>.png, the same picture the HUD shows, so a
// gallery cell never draws its own approximation.

import { mkdirSync, readFileSync, writeFileSync, existsSync } from "node:fs";
import { chromium } from "playwright-core";

const VIEWPORT = { width: 1280, height: 1000 };
const OUT = "workbench/figures";
mkdirSync(OUT, { recursive: true });
const slugify = name => name.replace(/[^a-z0-9]+/gi, "-").replace(/^-|-$/g, "").toLowerCase();

const document_ = JSON.parse(readFileSync("workbench/found-curves.json", "utf8"));
const only = process.argv.includes("--only") ? process.argv[process.argv.indexOf("--only") + 1] : null;
const curves = only ? document_.curves.filter(c => c.name === only) : document_.curves;

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

let made = 0, flat = 0;
for (const curve of curves) {
  const rows = new Map(curve.terms.map(t => [Number(t.power), [Number(t.x), Number(t.y)]]));
  const top = Math.max(...rows.keys());
  const speedX = Array.from({ length: top + 1 }, (_, k) => (rows.get(k) || [0, 0])[0]);
  const speedY = Array.from({ length: top + 1 }, (_, k) => (rows.get(k) || [0, 0])[1]);
  await page.evaluate(item => window.phNthLoad(item), { name: curve.name, step: 1, speedX, speedY });
  await page.waitForTimeout(260);
  const stats = await page.evaluate(() => {
    const d = document.querySelector("#n-plot path").getAttribute("d");
    const c = (d.match(/-?\d+\.\d+,-?\d+\.\d+/g) || []);
    const xs = c.map(v => Number(v.split(",")[0])), ys = c.map(v => Number(v.split(",")[1]));
    return { n: c.length, w: Math.max(...xs) - Math.min(...xs), h: Math.max(...ys) - Math.min(...ys) };
  });
  const png = await (await page.$("#n-plot")).screenshot();
  const path = `${OUT}/${slugify(curve.name)}.png`;
  writeFileSync(path, png);
  made++;
  if (stats.h < 20) flat++;
  if (made % 20 === 0) console.log(`${made}/${curves.length} … ${curve.name} ${stats.w.toFixed(0)}x${stats.h.toFixed(0)}`);
}
console.log(`${made} figures written, ${flat} of them flat (under 20 px tall)`);
await browser.close();
