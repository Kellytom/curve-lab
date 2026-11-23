// Prove the side-pillar page is live: each of the six sliders must change both
// the figure and the printed numbers, the figure must hold two open lines, and
// nothing may throw.
//
//   node scripts/check-side-pillars.mjs [base]
//
// The page is drawn by workbench/side_pillars.js after load, so this reads the
// DOM after the script has run, and moves the real inputs rather than calling
// the maths directly (a wiring fault is invisible to the unit tests).

import fs from "node:fs";
import { chromium } from "playwright-core";

const BASE = process.argv[2] || "http://127.0.0.1:8003";
const URL = `${BASE}/workbench/side-pillars.html`;

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
  console.log("no Chrome found: side-pillar check skipped");
  process.exit(1);
}

const fail = [];
const ok = (done, message) => { if (!done) fail.push(message); };

try {
  const page = await browser.newPage({ viewport: { width: 1200, height: 1000 } });
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  await page.goto(URL, { waitUntil: "load" });
  await page.waitForSelector("#sp-figure svg", { timeout: 5000 });

  const lines = await page.$$eval("path.pillar", (paths) => paths.map((p) => p.getAttribute("d")));
  ok(lines.length === 2, `expected 2 pillar lines, found ${lines.length}`);
  for (const d of lines) {
    ok((d.match(/M /g) || []).length === 1, `a pillar line has more than one start: ${d.slice(0, 40)}`);
    ok(!/Z/.test(d), "a pillar line is closed; it must be open");
    ok(/Q /.test(d), "a pillar line has no Q command (the shaft is a quadratic, not a stair)");
  }

  const rowCount = await page.$$eval("#sp-readout tr", (rows) => rows.length);
  ok(rowCount === 9, `expected 9 printed numbers, found ${rowCount}`);

  // each control must move a printed number and the drawing (spec: no dead control)
  const names = ["diameters", "ratio", "swell", "station", "base", "capital"];
  for (const name of names) {
    const before = await page.$eval("#sp-readout", (el) => el.textContent);
    const beforeSvg = await page.$eval("#sp-figure", (el) => el.innerHTML);
    const changed = await page.$eval(`#sp-${name}`, (input) => {
      const lo = Number(input.min);
      const hi = Number(input.max);
      const now = Number(input.value);
      const next = now === hi ? lo : Math.min(hi, now + Math.max(1, Math.round((hi - lo) / 10)));
      input.value = String(next);
      input.dispatchEvent(new Event("input", { bubbles: true }));
      return input.value;
    });
    const after = await page.$eval("#sp-readout", (el) => el.textContent);
    const afterSvg = await page.$eval("#sp-figure", (el) => el.innerHTML);
    ok(after !== before, `control ${name} (-> ${changed}) leaves every printed number unchanged`);
    ok(afterSvg !== beforeSvg, `control ${name} (-> ${changed}) leaves the figure unchanged`);
  }

  // the swell slider cannot be set above the ceiling the notes print
  const ceiling = await page.$eval("#sp-swell", (input) => Number(input.max));
  ok(ceiling > 0 && ceiling <= 25, `the swell maximum reads ${ceiling}`);

  ok(errors.length === 0, `page errors: ${errors.join(" | ")}`);
} finally {
  await browser.close();
}

if (fail.length) {
  console.log(fail.join("\n"));
  process.exit(1);
}
console.log("side pillar: 2 open lines, six live controls, 9 numbers, no errors");
