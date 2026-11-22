// The review desk: the cards, the bulk bar, and the refusals. No write is made by this check:
// the empty selection sends nothing, and the rating of 11 is refused by the endpoint.
//
//   node app/scripts/check-review.mjs [base]

import fs from "node:fs";
import { chromium } from "playwright-core";
import { gotoStable } from "./lib/navigate.mjs";

const BASE = process.env.CURVE_LAB_URL || process.argv[2] || "http://127.0.0.1:4321";
const candidates = [
  process.env.CHROME_PATH,
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
].filter(Boolean);

let browser = null;
for (const executablePath of candidates) {
  if (!fs.existsSync(executablePath)) continue;
  try { browser = await chromium.launch({ executablePath, headless: true }); break; }
  catch { browser = null; }
}
if (!browser) {
  console.error("no Chrome could be launched; set CHROME_PATH");
  process.exit(1);
}
const page = await browser.newPage({ viewport: { width: 1280, height: 1000 } });
const problems = [];

try {
  await gotoStable(page, `${BASE}/review/?scope=unrated`, { waitUntil: "networkidle" });
  await page.waitForSelector(".review-card", { timeout: 8000 });
  const cards = await page.$$eval(".review-card", (nodes) => nodes.length);
  if (!cards) problems.push("the unrated scope has no cards");

  const buttons = await page.$$eval("#review-bar button", (nodes) =>
    nodes.map((node) => node.textContent.trim().toLowerCase()));
  for (const need of ["approve 10", "stars 5", "stars 2", "demote 1", "clear"]) {
    if (!buttons.includes(need)) problems.push(`the bar is missing "${need}": ${buttons}`);
  }

  if ((await page.$eval("#review-count", (node) => node.textContent)).trim() !== "0 selected") {
    problems.push("the page does not start with nothing selected");
  }
  await page.click('#review-bar button[data-stars="2"]');
  await page.waitForTimeout(200);
  const empty = await page.$eval("#review-status", (node) => node.textContent);
  if (!/select a curve first/.test(empty)) problems.push(`no-selection message: ${empty}`);

  const before = await page.$eval(".review-card", (node) => node.dataset.stars);
  await page.check(".review-card .pick");
  await page.fill("#review-stars", "11");
  await page.click("#review-apply");
  await page.waitForFunction(
    () => /not saved/.test(document.getElementById("review-status")?.textContent || ""),
    { timeout: 15000 },
  );
  const after = await page.$eval(".review-card", (node) => node.dataset.stars);
  if (after !== before) problems.push(`a refused rating changed the card: ${before} -> ${after}`);

  console.log(problems.length ? `FAIL\n- ${problems.join("\n- ")}`
    : "review desk: cards, bulk bar, and both refusals");
} finally {
  await browser.close();
}
process.exit(problems.length ? 1 : 0);
