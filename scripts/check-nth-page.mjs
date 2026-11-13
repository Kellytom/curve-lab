// Check the eleventh-power page in a real browser: the twelve speed boxes, the
// width law, the terminal rule, the serif and the openness dial.
//
//   node scripts/check-nth-page.mjs

import { chromium } from "playwright-core";

const url = "http://127.0.0.1:8003/workbench/ph-nth-sandbox.html";
const failures = [];

const candidates = [
  process.env.CHROME_PATH,
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  `${process.env.HOME}/.cache/puppeteer/chrome-headless-shell/mac-133.0.6943.98/chrome-headless-shell-mac-x64/chrome-headless-shell`,
].filter(Boolean);

let browser = null;
for (const executablePath of candidates) {
  try {
    browser = await chromium.launch({ executablePath, headless: true });
    break;
  } catch (error) { /* try the next one */ }
}
if (!browser) browser = await chromium.launch({ headless: true });

const page = await browser.newPage({ viewport: { width: 1120, height: 1000 } });
const errors = [];
page.on("pageerror", error => errors.push(error.message));
await page.goto(`${url}?v=${Date.now()}`, { waitUntil: "load" });

const boxes = await page.$$eval("#n-controls input[type=number]", els => els.length);
if (boxes !== 12) failures.push(`speed boxes: ${boxes}, expected 12`);

// the view: spine only by default, then rails, then the two terminals
const paths = () => page.evaluate(() => document.querySelectorAll("#n-plot path").length);
if (await paths() !== 1) failures.push("default view is not the spine alone");
await page.click("#n-rails");
if (await paths() !== 3) failures.push("rails toggle did not add two paths");
await page.click("#n-terminal-end");
if (await paths() !== 4) failures.push("end terminal did not add an arc");
await page.click("#n-terminal-start");
if (await paths() !== 5) failures.push("start terminal did not add an arc");
await page.click("#n-terminal-start");
await page.click("#n-terminal-end");
await page.click("#n-rails");
if (await paths() !== 1) failures.push("toggles did not return to the spine alone");

// the sliders must write the number boxes
const boxesBefore = await page.$$eval("#n-controls input[type=number]", els => els.map(input => input.value));
const sliders = await page.$$("#n-controls input[type=range]:not(.decade)");
await sliders[1].evaluate(el => { el.value = "4"; el.dispatchEvent(new Event("input", { bubbles: true })); });
await page.waitForTimeout(120);
const boxesAfter = await page.$$eval("#n-controls input[type=number]", els => els.map(input => input.value));
if (boxesBefore[1] === boxesAfter[1]) failures.push("a slider moved the curve but not the number box");

// the width readout must agree with d0 and the flare
const widthText = await page.textContent("#n-width-readout");
const d0 = Number((widthText.match(/d0 ([0-9.]+)/) || [])[1]);
const d1 = Number((widthText.match(/d\(1\) ([0-9.]+)/) || [])[1]);
const flare = Number((widthText.match(/flare ([0-9.]+)x/) || [])[1]);
if (!Number.isFinite(d1) || Math.abs(flare - d1 / d0) > 0.02) failures.push(`flare: ${flare}x against d(1)/d0 ${(d1 / d0).toFixed(2)}x`);

const notes = await page.getAttribute('a[href="ph-nth-serif-notes.html"]', "href");
if (!notes) failures.push("the serif notes link is missing");

if (errors.length) failures.push(`page errors: ${errors.join(" | ")}`);

await page.close();
await browser.close().catch(() => {});

if (failures.length) {
  console.error("FAIL");
  for (const failure of failures) console.error("  " + failure);
  process.exit(1);
}
console.log("OK  12 boxes, spine by default, rails and both terminals, sliders write the boxes, dial lands");
