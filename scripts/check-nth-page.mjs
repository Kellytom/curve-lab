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

// the terminal rule: R = 2 d(1), read back from the page itself
const widthText = await page.textContent("#n-width-readout");
const d1 = Number((widthText.match(/d\(1\) ([0-9.]+)/) || [])[1]);
const terminal = Number((widthText.match(/terminal R ([0-9.]+)/) || [])[1]);
if (!Number.isFinite(d1) || !Number.isFinite(terminal) || Math.abs(terminal - 2 * d1) > 0.002) {
  failures.push(`terminal rule: R ${terminal} against 2 d(1) ${2 * d1}`);
}
const flare = Number((widthText.match(/flare ([0-9.]+)x/) || [])[1]);
const d0 = Number((widthText.match(/d0 ([0-9.]+)/) || [])[1]);
if (!Number.isFinite(flare) || Math.abs(flare - d1 / d0) > 0.02) {
  failures.push(`flare: ${flare}x against d(1)/d0 ${(d1 / d0).toFixed(2)}x`);
}

// the serif foot: two arcs and a base, and the toggle removes them
const before = await page.evaluate(() => document.querySelectorAll("#n-plot path").length);
await page.uncheck("#n-serif");
const after = await page.evaluate(() => document.querySelectorAll("#n-plot path").length);
if (after !== before - 2) failures.push(`serif toggle: ${before} -> ${after} paths`);
await page.check("#n-serif");

// the openness dial must land
const openness = async () => Number((await page.textContent("#n-readout")).match(/open ([0-9.]+)/)[1]);
await page.fill("#n-open-value", "0.30");
await page.click("#n-open");
await page.waitForTimeout(700);
const reached = await openness();
if (!Number.isFinite(reached) || Math.abs(reached - 0.30) > 0.01) {
  failures.push(`close-to 0.30 gave openness ${reached}`);
}

// the detail figure must keep its labels inside and apart
const detail = await page.evaluate(() => {
  const svg = document.getElementById("n-detail");
  const box = svg.getBoundingClientRect();
  const texts = [...svg.querySelectorAll("text")].map(t => {
    const r = t.getBoundingClientRect();
    return { text: t.textContent, x: r.left, y: r.top, w: r.width, h: r.height };
  });
  let overlaps = 0;
  for (let i = 0; i < texts.length; i++) {
    for (let j = i + 1; j < texts.length; j++) {
      const a = texts[i], c = texts[j];
      if (a.x < c.x + c.w && c.x < a.x + a.w && a.y < c.y + c.h && c.y < a.y + a.h) overlaps++;
    }
  }
  const outside = texts.filter(t => t.x < box.left - 1 || t.y < box.top - 1 ||
                                    t.x + t.w > box.right + 1 || t.y + t.h > box.bottom + 1);
  return { overlaps, outside: outside.length };
});
if (detail.overlaps) failures.push(`detail text overlaps: ${detail.overlaps}`);
if (detail.outside) failures.push(`detail text outside the box: ${detail.outside}`);
if (errors.length) failures.push(`page errors: ${errors.join(" | ")}`);

await page.close();
await browser.close().catch(() => {});

if (failures.length) {
  console.error("FAIL");
  for (const failure of failures) console.error("  " + failure);
  process.exit(1);
}
console.log("OK  12 boxes, width law, terminal R = 2 d(1), serif, dial, clean detail");
