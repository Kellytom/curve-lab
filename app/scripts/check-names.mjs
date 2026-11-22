// The naming desk, checked in a real browser: every chosen curve has a name to
// save, and a saved name is still there after a reload.
//
//   node app/scripts/check-names.mjs
//
// The save is idempotent: it writes the name the curve already has, so running
// this never renames anything. Playwright launches its own browser; the Astro
// server must be up on :4321.

import { readFileSync } from "node:fs";
import { chromium } from "playwright-core";
import { gotoStable } from "./lib/navigate.mjs";
import { prisma } from "../src/lib/db.js";

const BASE = process.env.CURVE_LAB_URL || "http://127.0.0.1:4321";
const READ_ONLY = process.env.CURVE_LAB_READ_ONLY === "1";
const EXE = process.env.CHROME_PATH || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";

// The desk lists every registry curve the database has not set aside as a candidate.
// Count from the same two sources the page uses, not from a remembered number.
const registry = JSON.parse(
  readFileSync(new URL("../../workbench/curve-registry.json", import.meta.url), "utf8"));
const flags = await prisma.curve.findMany({ select: { uid: true, candidate: true } });
await prisma.$disconnect();
const candidateOf = new Map(flags.map((curve) => [curve.uid, curve.candidate]));
const expectedRows = registry.curves.filter(
  (curve) => !(candidateOf.has(curve.uid) ? candidateOf.get(curve.uid) : curve.candidate)).length;

const browser = await chromium.launch({ executablePath: EXE });
const page = await browser.newPage({ viewport: { width: 1200, height: 900 } });
const errors = [];
page.on("pageerror", (error) => errors.push(String(error)));

await gotoStable(page, `${BASE}/names/`, { waitUntil: "domcontentloaded" });
await page.waitForTimeout(800);
await page.evaluate(() => localStorage.removeItem("names-drafts"));
await page.reload({ waitUntil: "domcontentloaded" });
await page.waitForTimeout(800);

const desk = await page.evaluate(() => {
  const rows = [...document.querySelectorAll(".row")];
  return {
    rows: rows.length,
    unsaveable: rows.filter((row) => !row.querySelector(".preview").textContent.trim())
      .map((row) => row.querySelector(".now").textContent),
  };
});

// The first row: save the name it already has, then reload. In read-only mode
// nothing is written; the row is read and the page is reloaded to prove the name
// stays where it was.
const saved = await page.evaluate(async (readOnly) => {
  const row = document.querySelector(".row");
  const name = row.querySelector(".preview").textContent.replace(/^=\s*/, "");
  const now = row.querySelector(".now").textContent;
  if (!readOnly) {
    row.querySelector(".save").click();
    await new Promise((resolve) => setTimeout(resolve, 1200));
  }
  return { uid: row.dataset.uid, name, now, flag: readOnly ? "read-only" : row.querySelector(".flag").textContent };
}, READ_ONLY);

await page.reload({ waitUntil: "domcontentloaded" });
await page.waitForTimeout(1000);
const afterReload = await page.evaluate((uid) => {
  const row = document.querySelector(`.row[data-uid="${uid}"]`);
  return {
    now: row.querySelector(".now").textContent,
    preview: row.querySelector(".preview").textContent.trim(),
    draft: JSON.parse(localStorage.getItem("names-drafts") || "{}")[uid],
  };
}, saved.uid);

await browser.close();

const failures = [];
if (desk.rows !== expectedRows) failures.push(`expected ${expectedRows} chosen curves, the desk shows ${desk.rows}`);
if (desk.unsaveable.length) failures.push(`no name to save for: ${desk.unsaveable.join(", ")}`);
if (!READ_ONLY && !/saved/.test(saved.flag)) failures.push(`save said "${saved.flag}"`);
const expectedName = READ_ONLY ? saved.now : saved.name;
if (afterReload.now !== expectedName) failures.push(`after reload the name is "${afterReload.now}", not "${expectedName}"`);
if (afterReload.draft !== undefined) failures.push("the saved name is still a draft");
if (errors.length) failures.push(`page errors: ${errors.join(" | ")}`);

if (failures.length) {
  console.error(failures.map((line) => `FAIL ${line}`).join("\n"));
  process.exit(1);
}
console.log(`ok — ${desk.rows} rows, every one composes a name; ${saved.uid} ` + (READ_ONLY ? "read-only: no save was made" : `saved "${saved.name}" and it survived a reload`));
