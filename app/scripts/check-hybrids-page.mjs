// The hybrid desk: one card per candidate, a decision that survives a reload, and a
// save that does not disturb another card. Spec: state/SPEC-hybrids-int.md.
//
//   node app/scripts/check-hybrids-page.mjs

import { readFileSync } from "node:fs";
import path from "node:path";
import { chromium } from "playwright-core";

const ROOT = path.resolve(import.meta.dirname, "..", "..");
const BASE = process.env.CURVE_LAB_URL || "http://127.0.0.1:4321";
const EXE = process.env.CHROME_PATH || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const data = JSON.parse(readFileSync(path.join(ROOT, "workbench", "hybrids.json"), "utf8"));
const wanted = data.candidates.length;

const browser = await chromium.launch({ executablePath: EXE });
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
const errors = [];
page.on("pageerror", (error) => errors.push(String(error)));

let failed = 0;
const check = (ok, message) => {
  if (ok) console.log(`  ok   ${message}`);
  else { failed += 1; console.log(`  FAIL ${message}`); }
};

const response = await page.goto(`${BASE}/hybrids/`, { waitUntil: "domcontentloaded", timeout: 30000 });
check(response?.status() === 200, `page answers ${response?.status()}`);

const cards = await page.locator(".hybrid-card").count();
check(cards === wanted, `${cards} cards, expected ${wanted}`);

const images = await page.evaluate(() => [...document.querySelectorAll(".hybrid-card img")]
  .slice(0, 8).map((img) => ({ ok: img.complete && img.naturalWidth > 0, src: img.getAttribute("src") })));
check(images.every((image) => image.ok), "every sampled figure loads");

const decisions = await page.evaluate(() => [...document.querySelectorAll(".hybrid-card")]
  .slice(0, 2).map((card) => card.dataset.name));
for (const name of decisions) {
  await page.locator(`.hybrid-card[data-name="${name}"] [data-decision="keep"]`).click();
  await page.waitForTimeout(250);
}
check(true, `pressed keep on ${decisions.length} cards`);

await page.reload({ waitUntil: "domcontentloaded" });
await page.waitForTimeout(900);
const kept = await page.evaluate((names) => names.map((name) =>
  document.querySelector(`.hybrid-card[data-name="${name}"]`)?.dataset.decision || ""), decisions);
check(kept.every((value) => value === "keep"), `both decisions survive a reload (${kept.join(", ")})`);

// the stars are the naming desk's widget: click 7, reload, seven are on
const starCard = decisions[0];
await page.locator(`.hybrid-card[data-name="${starCard}"] .stars button[data-imp="7"]`).click();
await page.waitForTimeout(300);
await page.reload({ waitUntil: "domcontentloaded" });
await page.waitForTimeout(900);
const starsOn = await page.evaluate((name) =>
  document.querySelectorAll(`.hybrid-card[data-name="${name}"] .stars button.on`).length, starCard);
check(starsOn === 7, `stars survive a reload (${starsOn} on, expected 7)`);

// the name is typed and kept, like the naming desk
const nameCard = decisions[0];
await page.locator(`.hybrid-card[data-name="${nameCard}"] .hybrid-name`).fill("swan-hybrid-7");
await page.locator(`.hybrid-card[data-name="${nameCard}"] .hybrid-name`).blur();
await page.waitForTimeout(300);
await page.reload({ waitUntil: "domcontentloaded" });
await page.waitForTimeout(900);
const keptName = await page.evaluate((name) =>
  document.querySelector(`.hybrid-card[data-name="${name}"] .hybrid-name`)?.value || "", nameCard);
check(keptName === "swan-hybrid-7", `the typed name survives a reload ("${keptName}")`);

check(errors.length === 0, errors.length ? `page errors: ${errors.join(" | ")}` : "no page errors");

// a failed read must not become a write: with the decisions unreachable, a click saves nothing
const blocked = await browser.newPage({ viewport: { width: 1280, height: 900 } });
let posts = 0;
blocked.on("request", (request) => {
  if (request.method() === "POST" && request.url().includes("/api/sandbox-curves")) posts += 1;
});
await blocked.route("**/api/sandbox-curves", (route) =>
  route.request().method() === "GET"
    ? route.fulfill({ status: 500, body: "down" })
    : route.continue());
await blocked.goto(`${BASE}/hybrids/`, { waitUntil: "domcontentloaded", timeout: 30000 });
await blocked.waitForTimeout(900);
const warned = await blocked.evaluate(() => document.getElementById("hybrids-counts")?.textContent || "");
await blocked.locator(".hybrid-card .hybrid-actions button").first().click();
await blocked.waitForTimeout(300);
check(warned.includes("saving is off"), "a failed read turns saving off");
check(posts === 0, `no write after a failed read (${posts} POSTs)`);

await browser.close();
console.log(failed ? `FAILED ${failed}` : "ok /hybrids/ — cards, figures, decisions kept");
process.exit(failed ? 1 : 0);
