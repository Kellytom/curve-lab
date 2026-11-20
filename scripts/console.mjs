// Print a page's console, page errors and failed requests, live.
//
//   node scripts/console.mjs http://127.0.0.1:4321/hybrids/ [seconds]
//
// A fresh headless Chrome loads the page and every message is echoed with a timestamp. This
// is the browser console I can see; yours (in your Chrome) I cannot — this is how to make the
// two the same.

import { chromium } from "playwright-core";

const [, , url, seconds = "3"] = process.argv;
if (!url) {
  console.error("usage: node scripts/console.mjs <url> [seconds]");
  process.exit(2);
}

const browser = await chromium.launch({
  executablePath: process.env.CHROME_PATH || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
});
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
const started = Date.now();
const stamp = () => `${String((Date.now() - started) / 1000).padStart(5)}s`;

page.on("console", (message) => console.log(`${stamp()}  ${message.type().padEnd(7)} ${message.text()}`));
page.on("pageerror", (error) => console.log(`${stamp()}  PAGEERR ${String(error)}`));
page.on("requestfailed", (request) =>
  console.log(`${stamp()}  REQFAIL ${request.url()} — ${request.failure()?.errorText}`));
page.on("response", (response) => {
  if (response.status() >= 400) console.log(`${stamp()}  HTTP ${response.status()} ${response.url()}`);
});

await page.goto(url, { waitUntil: "networkidle", timeout: 30000 });
await page.waitForTimeout(Number(seconds) * 1000);
console.log(`${stamp()}  done — ${await page.title()}`);
await browser.close();
