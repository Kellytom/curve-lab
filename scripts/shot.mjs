// Screenshot a page with Playwright. No daemon, no fixed port: the browser is
// launched for the shot and closed after it.
//
//   node scripts/shot.mjs <url> <out.png> [width] [height] [full|viewport]
//
// Playwright launches the Chrome already on the machine; nothing has to be
// running beforehand, which is what the old CDP-on-9223 version required.

import fs from "node:fs";
import { chromium } from "playwright-core";

const [, , url, out, w = "900", h = "1400", mode = "full"] = process.argv;
if (!url || !out) {
  console.error("usage: node scripts/shot.mjs <url> <out.png> [w] [h] [full|viewport]");
  process.exit(2);
}

const candidates = [
  process.env.CHROME_PATH,
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  `${process.env.HOME}/.cache/puppeteer/chrome-headless-shell/mac-133.0.6943.98/chrome-headless-shell-mac-x64/chrome-headless-shell`,
].filter(Boolean);

let browser = null;
let lastError = null;
for (const executablePath of candidates) {
  if (!fs.existsSync(executablePath)) continue;
  try {
    browser = await chromium.launch({ executablePath, headless: true });
    break;
  } catch (error) {
    lastError = error;
  }
}
if (!browser) {
  console.error("no Chrome could be launched:", lastError?.message ?? "none found");
  process.exit(1);
}

const page = await browser.newPage({
  viewport: { width: Number(w), height: Number(h) },
  deviceScaleFactor: 1,
});
await page.goto(url, { waitUntil: "load", timeout: 20000 });
await page.screenshot({ path: out, fullPage: mode === "full" });
const size = await page.evaluate(() => [
  document.documentElement.scrollWidth,
  document.documentElement.scrollHeight,
]);
console.log(out, `${size[0]}x${size[1]}`);
await browser.close();
