// The trim desk: rational fractions of t reach the cut, and the preview follows the form.
//
//   node scripts/check-trim.mjs
//
// The maths is app/src/lib/trim-curve.js (node-tested); this proves the page's form posts the
// fractions it shows and the cut piece is drawn for the range asked for.

import { chromium } from "playwright-core";

const BASE = process.env.CURVE_LAB_URL || "http://127.0.0.1:4321";
const EXE = process.env.CHROME_PATH || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";

const browser = await chromium.launch({ executablePath: EXE, headless: true });
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
const errors: string[] = [];
page.on("pageerror", (error: Error) => errors.push(error.message));

await page.goto(`${BASE}/trim/c-0274`, { waitUntil: "networkidle" });
const caption = page.locator(".trim-half figcaption");
const first = await caption.innerText();
if (!first.includes("t 1/4 → 3/4")) throw new Error(`default cut: ${first}`);

await page.fill('input[name="from"]', "1/3");
await page.fill('input[name="to"]', "2/3");
await Promise.all([
  page.waitForLoadState("networkidle"),
  page.locator('.trim-form button[type="submit"]').first().click(),
]);
const url = new URL(page.url());
if (url.searchParams.get("from") !== "1/3" || url.searchParams.get("to") !== "2/3") {
  throw new Error(`the preview did not carry the fractions: ${page.url()}`);
}
const second = await caption.innerText();
if (!second.includes("t 1/3 → 2/3")) throw new Error(`after the preview: ${second}`);

// a bad fraction is refused with a message, not a broken picture
await page.fill('input[name="from"]', "0.3");
await Promise.all([
  page.waitForLoadState("networkidle"),
  page.locator('.trim-form button[type="submit"]').first().click(),
]);
const bad = await page.locator(".trim-bad").innerText().catch(() => "");
if (!/whole-number fraction/.test(bad)) throw new Error(`a decimal was not refused: ${bad}`);

if (errors.length) throw new Error(`page errors: ${errors.join(" · ")}`);
console.log(`trim: ok — 1/4 → 3/4, then 1/3 → 2/3 drawn; a decimal is refused`);
await browser.close();
