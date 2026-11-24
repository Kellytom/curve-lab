// Open the gothic tuner in headless Chrome and prove the cut menu is live: the first paint
// names the default pair, changing the step redraws the arch and the readout, the select offers
// the steps, and a curve without a mirror says "one arm mirrored". No console error.
//
//   node scripts/check-gothic.mjs [base]

import fs from "node:fs";
import { chromium } from "playwright-core";

const BASE = process.argv[2] || "http://127.0.0.1:4321";
const candidates = [
  process.env.CHROME_PATH,
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  `${process.env.HOME}/.cache/puppeteer/chrome-headless-shell/mac-133.0.6943.98/chrome-headless-shell-mac-x64/chrome-headless-shell`,
].filter(Boolean);

let browser = null;
for (const executablePath of candidates) {
  if (!fs.existsSync(executablePath)) continue;
  try {
    browser = await chromium.launch({ executablePath, headless: true });
    break;
  } catch { browser = null; }
}
if (!browser) {
  console.error("no Chrome could be launched; set CHROME_PATH");
  process.exit(1);
}

const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
const problems = [];
const errors = [];
page.on("console", (message) => {
  if (message.type() === "error") errors.push(message.text());
});
page.on("pageerror", (error) => errors.push(String(error.message || error)));

const readout = () => page.$eval("#gothic-readout", (node) => node.textContent || "");
const figure = () => page.$eval("#gothic-preview", (node) => node.innerHTML);

try {
  await page.goto(`${BASE}/gothic/c-0008`, { waitUntil: "load", timeout: 20000 });
  await page.waitForSelector("#gothic-preview svg", { timeout: 8000 });

  const before = await readout();
  if (!/t = 9\/20 … 11\/20 \(step 1\/20\)/.test(before)) {
    problems.push(`the first paint does not name the default pair: ${before}`);
  }
  const svgBefore = await figure();

  const options = await page.$$eval("#gothic-q option", (nodes) => nodes.length);
  if (options !== 8) problems.push(`the menu offers ${options} steps, expected 8`);

  await page.selectOption("#gothic-q", "0.125");
  await page.waitForTimeout(250);
  const after = await readout();
  if (!/step 1\/8/.test(after)) problems.push(`the menu did not move the cut: ${after}`);
  if ((await figure()) === svgBefore) problems.push("the figure did not redraw when the cut moved");

  await page.goto(`${BASE}/gothic/c-0134`, { waitUntil: "load", timeout: 20000 });
  await page.waitForSelector("#gothic-preview svg", { timeout: 8000 });
  const oneArm = await page.$eval("#gothic-preview", (node) => node.closest(".gothic-lab")?.textContent || "");
  if (!/one arm mirrored/.test(oneArm)) problems.push("the non-mirrored parent does not say 'one arm mirrored'");
} catch (error) {
  problems.push(String(error.message || error));
}

if (errors.length) problems.push(`console errors: ${errors.slice(0, 3).join(" | ")}`);
await browser.close();

if (problems.length) {
  for (const problem of problems) console.error("gothic:", problem);
  process.exit(1);
}
console.log("gothic: ok — menu, redraw, one-arm notice, no console error");
