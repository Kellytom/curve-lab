// The hub's window stills: one screenshot per app page, saved to app/public/hub/.
//
// The hub used to open four live iframes at once, so it rendered four heavy pages before it
// appeared. The still opens at once and the real page loads when its window is reached; this
// script refreshes the stills so they do not drift from the pages.
//
//   node scripts/hub_shots.mjs            # needs the app on 127.0.0.1:4321
//   HUB_BASE=http://127.0.0.1:4321 node scripts/hub_shots.mjs
//
// Playwright launches the Chrome already on the machine, like scripts/shot.mjs.

import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright-core";
import { buildHub } from "../app/src/lib/pages.js";

const ROOT = path.resolve(import.meta.dirname, "..");
const OUT = path.join(ROOT, "app", "public", "hub");
const BASE = process.env.HUB_BASE || "http://127.0.0.1:4321";
const WIDTH = 1200;
const HEIGHT = 800;

fs.mkdirSync(OUT, { recursive: true });

const candidates = [
  process.env.CHROME_PATH,
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
].filter(Boolean);
let browser = null;
for (const executablePath of candidates) {
  if (!fs.existsSync(executablePath)) continue;
  browser = await chromium.launch({ executablePath, headless: true });
  break;
}
if (!browser) {
  console.error("no Chrome found; set CHROME_PATH");
  process.exit(1);
}

const page = await browser.newPage({ viewport: { width: WIDTH, height: HEIGHT }, deviceScaleFactor: 1 });
const hub = buildHub();
for (const entry of hub.app) {
  const file = path.join(OUT, `${entry.key}.png`);
  await page.goto(`${BASE}${entry.src}`, { waitUntil: "load", timeout: 60000 });
  // let the first paint and the fonts settle: a still taken mid-render is a wrong picture
  await page.waitForTimeout(400);
  await page.screenshot({ path: file });
  const bytes = fs.statSync(file).size;
  console.log(`${entry.src.padEnd(18)} -> ${path.relative(ROOT, file)} ${Math.round(bytes / 1024)} KB`);
}
await browser.close();
