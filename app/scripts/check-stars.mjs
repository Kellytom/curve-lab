// The finder's stars, checked in a real browser.
//
//   node app/scripts/check-stars.mjs
//
// Guards the fault of 2026-11-19: clicking a star threw (a name used outside
// its scope), so the click never wrote the list and never saved, while the page
// showed the same curve twice. The check stars one curve, waits for the save,
// un-stars it, and requires the server to be back where it started. It also
// refuses a page with two cards for one curve.
//
// The Astro server must be up on :4321.

import { chromium } from "playwright-core";
import { createRequire } from "node:module";

const BASE = process.env.CURVE_LAB_URL || "http://127.0.0.1:4321";
const EXE = process.env.CHROME_PATH || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const require = createRequire(import.meta.url);

async function starCount() {
  const { PrismaClient } = require("@prisma/client");
  const prisma = new PrismaClient();
  try {
    return await prisma.star.count();
  } finally {
    await prisma.$disconnect();
  }
}

const before = await starCount();

const browser = await chromium.launch({ executablePath: EXE });
const page = await browser.newPage({ viewport: { width: 1200, height: 900 } });
const errors = [];
page.on("pageerror", (error) => errors.push(String(error)));

await page.goto(`${BASE}/finder/`, { waitUntil: "domcontentloaded" });
await page.waitForTimeout(800);
await page.evaluate(() => localStorage.removeItem("finder-stars"));
await page.reload({ waitUntil: "domcontentloaded" });
await page.waitForTimeout(800);

const shape = await page.evaluate(() => {
  const ids = [...document.querySelectorAll("button.star")].map((button) => button.dataset.id);
  return { cards: ids.length, duplicates: ids.length - new Set(ids).size };
});

const picked = await page.evaluate(() => {
  const button = [...document.querySelectorAll("button.star")].find((b) => b.textContent.trim() === "☆");
  button.click();
  return button.dataset.id;
});
await page.waitForTimeout(1200);
const starred = await page.evaluate((id) => ({
  on: document.querySelector(`button.star[data-id="${id}"]`).textContent.trim() === "★",
  stored: JSON.parse(localStorage.getItem("finder-stars") || "[]").length,
}), picked);

await page.evaluate((id) => document.querySelector(`button.star[data-id="${id}"]`).click(), picked);
await page.waitForTimeout(1200);
await browser.close();

const after = await starCount();
const failures = [];
if (shape.duplicates) failures.push(`the page draws ${shape.duplicates} duplicate card(s)`);
if (!starred.on) failures.push("the star did not turn on");
if (starred.stored < 1) failures.push("the click wrote nothing to the browser's list");
if (after !== before) failures.push(`the server has ${after} stars, not the ${before} it started with`);
if (errors.length) failures.push(`page errors: ${errors.join(" | ")}`);

if (failures.length) {
  console.error(failures.map((line) => `FAIL ${line}`).join("\n"));
  process.exit(1);
}
console.log(`ok — ${shape.cards} cards, no duplicates; starred and unstarred ${picked}; ${before} stars on the server before and after`);
