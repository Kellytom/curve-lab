// The root lab's controls reach the maths: a second pair and the x row change the curve.
//
//   node scripts/check-roots.mjs
//
// The page builds its curve in the browser (app/src/scripts/lab-roots.js); this moves the new
// controls and requires the facts line to follow, so a slider wired to nothing cannot pass.

import { chromium } from "playwright-core";

const BASE = process.env.CURVE_LAB_URL || "http://127.0.0.1:4321";
const EXE = process.env.CHROME_PATH || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";

const browser = await chromium.launch({ executablePath: EXE, headless: true });
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
const errors = [];
page.on("pageerror", (error) => errors.push(error.message));

await page.goto(`${BASE}/roots/`, { waitUntil: "networkidle" });
const facts = page.locator("#lab-facts");
const before = await facts.innerText();
if (!before.includes("pair 2 off")) throw new Error(`default facts: ${before}`);
if (!before.includes("x row 1 + 2(t² − t)")) throw new Error(`default facts: ${before}`);

const set = async (id, value) => {
  await page.locator(`#${id}`).evaluate((element, next) => {
    element.value = String(next);
    element.dispatchEvent(new Event("input", { bubbles: true }));
  }, value);
};

await set("p2", 5);
const withSecond = await facts.innerText();
if (!withSecond.includes("pair 2 5/7")) throw new Error(`after p2 = 5: ${withSecond}`);

await set("x-b", 4);
const withRow = await facts.innerText();
if (!withRow.includes("x row 1 + 4(t² − t)")) throw new Error(`after B = 4: ${withRow}`);

if (errors.length) throw new Error(`page errors: ${errors.join(" · ")}`);
console.log(`roots: ok — second pair and x row reach the curve (${before.slice(0, 40)}…)`);
await browser.close();
