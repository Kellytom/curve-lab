// Where the fold falls, in CSS pixels, for the pages the operator named.
//
//   node scripts/fold_report.mjs            # 1200 px wide
//   node scripts/fold_report.mjs 1440       # the width of the window you use
//
// "Above the fold" is what the reader sees before scrolling. It is not a breakpoint; it is a
// height at the window the operator actually uses. This prints the top of each named anchor,
// so the fold can be re-measured instead of guessed. The app must be up on 127.0.0.1:4321.

import { chromium } from "playwright-core";

const WIDTH = Number(process.argv[2] || 1200);
const BASE = process.env.CURVE_LAB_URL || "http://127.0.0.1:4321";

// The operator's own calibration, 2026-11-23: each of these is just at the fold.
const ANCHORS = [
  { page: "/plates", text: "c-0022", note: "just below the fold" },
  { page: "/review/", text: "wave3-balance", note: "just below the fold" },
  { page: "/reduce/", text: "logspiral-fit", note: "just below the fold" },
  { page: "/", text: "Square and frame lab", note: "just above the fold", inWindow: true },
];

const browser = await chromium.launch({
  executablePath: process.env.CHROME_PATH
    || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  headless: true,
});
const page = await browser.newPage({ viewport: { width: WIDTH, height: 900 } });

for (const anchor of ANCHORS) {
  await page.goto(`${BASE}${anchor.page}`, { waitUntil: "load", timeout: 90000 });
  await page.waitForTimeout(400);
  const found = await page.evaluate((needle) => {
    // the innermost element that starts with the words, so a card is not counted as its page
    const hits = [...document.querySelectorAll("*")]
      .filter((node) => (node.textContent || "").trim().startsWith(needle));
    if (!hits.length) return null;
    const node = hits[hits.length - 1];
    const box = node.getBoundingClientRect();
    return Math.round(box.top + scrollY);
  }, anchor.text);
  const where = found === null ? "not found (a window still is a picture, not text)" : `${found} px`;
  console.log(`${anchor.page.padEnd(10)} "${anchor.text}" ${anchor.note.padEnd(20)} top ${where}`);
}

await browser.close();
