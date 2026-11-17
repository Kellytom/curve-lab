// Check the saved-curve buttons survive the ways they were lost.
//
//   node scripts/check-saved.mjs
//
// Four things, each of which has happened:
//   1. a browser with no list is seeded from workbench/operator-list.json;
//   2. a damaged value is repaired from its backup, not replaced by nothing;
//   3. a save made after a damaged read does not overwrite the other curves;
//   4. a click on a restored button loads that curve.
//
// The page is `/workbench/ph-nth-sandbox.html`, the one with the B panel. The
// server must be up (`scripts/serve.py`).

import { readFileSync } from "node:fs";
import { chromium } from "playwright-core";

const tokenFile = process.env.HOME + "/.config/clothoid-lab/token";
const token = readFileSync(tokenFile, "utf8").trim();
const URL_PAGE = "http://127.0.0.1:8003/workbench/ph-nth-sandbox.html";
const candidates = [process.env.CHROME_PATH,
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"].filter(Boolean);
let browser = null;
for (const executablePath of candidates) {
  try { browser = await chromium.launch({ executablePath, headless: true }); break; } catch { /* next */ }
}
if (!browser) browser = await chromium.launch({ headless: true });

const results = [];
const check = (name, pass, detail) => {
  results.push({ name, pass, detail });
  console.log(`${pass ? "ok  " : "FAIL"}  ${name}${detail ? ` — ${detail}` : ""}`);
};

const context = await browser.newContext({ httpCredentials: { username: "operator", password: token } });
const page = await context.newPage();
const errors = [];
page.on("pageerror", error => errors.push(String(error)));

// 1. A browser that has never held a list gets the file's curves.
await page.goto(URL_PAGE, { waitUntil: "load" });
await page.waitForTimeout(1200);
const seeded = await page.evaluate(() => {
  const items = [...document.querySelectorAll("#n-saved .saved-item button:first-child")];
  return { count: items.length, stored: (() => {
    try { return JSON.parse(localStorage.getItem("ph-nth-curves") || "null"); } catch { return null; }
  })() };
});
check("a fresh browser is seeded from operator-list.json",
      Array.isArray(seeded.stored) && seeded.stored.length > 100,
      `${seeded.count} buttons, ${seeded.stored ? seeded.stored.length : 0} stored`);

// 2. A damaged value comes back from its backup.
await page.evaluate(() => {
  const items = JSON.parse(localStorage.getItem("ph-nth-curves"));
  localStorage.setItem("ph-nth-curves-backup", JSON.stringify(items));
  localStorage.setItem("ph-nth-curves", "{ this is not a list");
});
await page.reload({ waitUntil: "load" });
await page.waitForTimeout(900);
const repaired = await page.evaluate(() => {
  const status = (document.getElementById("n-paste-status") || {}).textContent || "";
  let stored = null;
  try { stored = JSON.parse(localStorage.getItem("ph-nth-curves") || "null"); } catch { stored = null; }
  return { status, count: Array.isArray(stored) ? stored.length : -1 };
});
check("a damaged list is repaired from its backup",
      repaired.count > 100, `${repaired.count} records; status: ${repaired.status.slice(0, 70)}`);

// 3. A save after a damaged read keeps the curves that are still there.
await page.evaluate(() => {
  localStorage.setItem("ph-nth-curves", "{\"broken\":");
  localStorage.setItem("ph-nth-curves-backup", JSON.stringify([{ name: "keep me", speedX: [1, 2, 1], speedY: [0, 1, 0] }]));
});
await page.reload({ waitUntil: "load" });
await page.waitForTimeout(800);
const afterSave = await page.evaluate(async () => {
  const button = document.getElementById("n-save-primary");
  const field = document.getElementById("n-name");
  if (field) field.value = "a new one";
  button.click();
  await new Promise(done => setTimeout(done, 300));
  try { return JSON.parse(localStorage.getItem("ph-nth-curves")); } catch { return null; }
});
check("a save does not wipe the list it could not read",
      Array.isArray(afterSave) && afterSave.some(item => item.name === "keep me"),
      Array.isArray(afterSave) ? `${afterSave.length} records kept` : "unreadable");

// 4. A restored button loads its curve.
await page.evaluate(() => localStorage.removeItem("ph-nth-curves"));
await page.reload({ waitUntil: "load" });
await page.waitForTimeout(1200);
const loaded = await page.evaluate(async () => {
  const button = [...document.querySelectorAll("#n-saved .saved-item button:first-child")]
    .find(candidate => candidate.textContent.includes("lace-1of8-3"));
  if (!button) return { clicked: false };
  button.click();
  await new Promise(done => setTimeout(done, 700));
  return { clicked: true, readout: document.getElementById("n-readout").textContent };
});
check("a restored button loads its curve",
      loaded.clicked && /grid 1\//.test(loaded.readout || ""),
      loaded.clicked ? loaded.readout.slice(0, 60) : "button missing");

// 5. A pair-shaped record (the "DK" save) loads too: it is the other shape the
// buttons hold, and renderSaved treats a pair differently from a single curve.
await page.evaluate(() => {
  localStorage.setItem("ph-nth-curves", JSON.stringify([{
    name: "pair check", category: "DK",
    primary: { speedX: [1, -2, 2, 0, 0, 0], speedY: [0, 3, -3, 1, 0, 0] },
    complementary: { speedX: [1, -2, 2, 0, 0, 0], speedY: [0, -3, 3, 1, 0, 0] },
  }]));
});
await page.reload({ waitUntil: "load" });
await page.waitForTimeout(900);
const pair = await page.evaluate(async () => {
  const button = [...document.querySelectorAll("#n-saved .saved-item button:first-child")]
    .find(candidate => candidate.textContent.includes("pair check"));
  if (!button) return { clicked: false };
  button.click();
  await new Promise(done => setTimeout(done, 700));
  return { clicked: true, readout: document.getElementById("n-readout").textContent };
});
check("a pair record loads from its button",
      pair.clicked && /grid|bend/.test(pair.readout || ""),
      pair.clicked ? pair.readout.slice(0, 60) : "button missing");

check("no page errors", errors.length === 0, errors.join(" | ").slice(0, 160));

await context.close();
await browser.close();
const bad = results.filter(result => !result.pass).length;
console.log(`\n${results.length} checks, ${bad} failed`);
process.exitCode = bad ? 1 : 0;
