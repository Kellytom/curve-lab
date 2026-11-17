// Check that rails draws, and that the complementary-curve controls exist.
//
//   node scripts/check-rails.mjs
//
// Written 2026-11-16 after the operator reported "rails doesnt work anymore. i
// cant put in the side curves because the button is missing". Two causes were
// found: the experimental page cut the complementary box out of its own build,
// and nothing checked either control on any page. This checks both, on every
// page that carries them, so a generator that removes a control fails here
// instead of reaching the operator.

import { readFileSync } from "node:fs";
import { chromium } from "playwright-core";

const token = readFileSync(process.env.HOME + "/.config/clothoid-lab/token", "utf8").trim();
const PAGES = [
  "ph-nth-sandbox.html",
  "ph-nth-sandbox-2.html",
  "ph-nth-sandbox-exp.html",
  "ph-11th-sandbox.html",
  "ph-11th-sandbox-2.html",
];
const candidates = [process.env.CHROME_PATH,
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"].filter(Boolean);
let browser = null;
for (const executablePath of candidates) {
  try { browser = await chromium.launch({ executablePath, headless: true }); break; } catch { /* next */ }
}
if (!browser) browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  httpCredentials: { username: "operator", password: token },
  viewport: { width: 1280, height: 1000 },
});

const results = [];
const check = (name, pass, detail) => {
  results.push({ name, pass });
  console.log(`${pass ? "ok  " : "FAIL"}  ${name}${detail ? ` — ${detail}` : ""}`);
};

for (const name of PAGES) {
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", error => errors.push(String(error)));
  await page.goto(`http://127.0.0.1:8003/workbench/${name}`, { waitUntil: "load" });
  await page.waitForTimeout(600);
  const before = await page.evaluate(() => ({
    rails: !!document.getElementById("n-rails"),
    complement: !!document.getElementById("n-complement-box"),
    secondCurve: !!document.getElementById("n-comp-reset") || !!document.getElementById("n-comp-flip"),
    paths: document.querySelectorAll("#n-plot path").length,
  }));
  check(`${name}: the complementary-curve controls are present`,
        before.complement && before.secondCurve,
        before.complement ? "" : "the whole box is missing from the build");
  if (before.rails) {
    await page.click("#n-rails");
    await page.waitForTimeout(450);
    const after = await page.evaluate(() => ({
      paths: document.querySelectorAll("#n-plot path").length,
      blue: document.querySelectorAll('#n-plot path[stroke="#1f5fa8"]').length,
      on: document.getElementById("n-rails").className.includes("is-on"),
    }));
    check(`${name}: rails draws two parallel rails`,
          after.on && after.blue === 2 && after.paths > before.paths,
          `paths ${before.paths} -> ${after.paths}, blue ${after.blue}`);
  } else {
    check(`${name}: rails button exists`, false, "no #n-rails");
  }
  check(`${name}: no page errors`, errors.length === 0, errors.join(" | ").slice(0, 120));
  await page.close();
}

await context.close();
await browser.close();
const bad = results.filter(result => !result.pass).length;
console.log(`\n${results.length} checks, ${bad} failed`);
process.exitCode = bad ? 1 : 0;
