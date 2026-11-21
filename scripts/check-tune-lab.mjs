// Open /tune/ in headless Chrome and prove the lab redraws: the SVG must change when a
// value changes, and the readout must name both edges.
//
//   node scripts/check-tune-lab.mjs [base]
//
// The page is a live drawing, so this reads the DOM after the script has run.

import fs from "node:fs";
import { chromium } from "playwright-core";

const BASE = process.argv[2] || "http://127.0.0.1:4321";

// the same Chrome candidates scripts/shot.mjs uses: launch the browser already on the machine
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

try {
  await page.goto(`${BASE}/tune/`, { waitUntil: "networkidle" });
  await page.waitForSelector("#lab-preview svg", { timeout: 8000 });

  const firstSvg = await page.$eval("#lab-preview svg", (node) => node.outerHTML);
  const firstReadout = await page.$eval("#lab-readout", (node) => node.textContent.trim());
  if (!/Right edge .* Left edge /.test(firstReadout)) {
    problems.push(`readout does not name both edges: ${firstReadout}`);
  }
  if (!/of the curve's size/.test(firstReadout)) {
    problems.push(`readout is not the expected sentence: ${firstReadout}`);
  }

  // a character rail must not be parallel: the + side has to widen somewhere
  const ratio = Number((firstReadout.match(/\((\d+\.\d+)× at the belly\)/) || [])[1]);
  if (!(ratio > 1.05)) problems.push(`the right edge is parallel (ratio ${ratio})`);

  // move plus and the drawing must change
  await page.$eval("#lab-plus", (node) => {
    node.value = "6";
    node.dispatchEvent(new Event("input", { bubbles: true }));
  });
  await page.waitForTimeout(120);
  const secondSvg = await page.$eval("#lab-preview svg", (node) => node.outerHTML);
  if (secondSvg === firstSvg) problems.push("changing plus did not redraw the picture");

  // width 0.5 with plus 0 and minus 0 is the only parallel setting
  await page.$eval("#lab-plus", (node) => {
    node.value = "0";
    node.dispatchEvent(new Event("input", { bubbles: true }));
  });
  await page.$eval("#lab-minus", (node) => {
    node.value = "0";
    node.dispatchEvent(new Event("input", { bubbles: true }));
  });
  await page.waitForTimeout(120);
  const flat = await page.$eval("#lab-readout", (node) => node.textContent);
  if (!/Right edge .*\(1\.00× at the belly\)/.test(flat)) {
    problems.push(`plus 0 / minus 0 is not flat: ${flat}`);
  }

  // a path curve must say so rather than pretend the values shape it
  await page.selectOption("#lab-curve", "c-0273");
  await page.waitForTimeout(400);
  const pathReadout = await page.$eval("#lab-readout", (node) => node.textContent);
  if (!/stored as a path/.test(pathReadout)) {
    problems.push(`a path curve did not say so: ${pathReadout}`);
  }

  console.log(problems.length ? `FAIL\n- ${problems.join("\n- ")}` : "tune lab: draws, redraws, and says when it is flat or a path");
} finally {
  await browser.close();
}

process.exit(problems.length ? 1 : 0);
