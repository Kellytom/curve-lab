// The layout gate: the page holds at 100%, at the width 150% zoom implies, and on a
// phone. Browser zoom shrinks the layout width, so 1280 at 150% is 853 CSS pixels —
// that is how it is emulated here.
//
//   node app/scripts/check-layout.mjs        (dev server on :4321)

import { chromium } from "playwright-core";

const BASE = process.env.CURVE_LAB_URL || "http://127.0.0.1:4321";
const EXE = process.env.CHROME_PATH || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";

const VIEWS = [
  { label: "100% (1280)", width: 1280, headerMax: 96 },
  { label: "150% → 853", width: 853, headerMax: 220 },
  { label: "150% at 1024 → 683", width: 683, headerMax: 220 },
  { label: "phone 420", width: 420, headerMax: 240 },
];

const PAGES = ["/prime-mover/"];

const browser = await chromium.launch({ executablePath: EXE });
const failures = [];
const check = (condition, message) => { if (!condition) failures.push(message); };

try {
  for (const route of PAGES) {
    for (const view of VIEWS) {
      const page = await browser.newPage({ viewport: { width: view.width, height: 900 } });
      await page.goto(BASE + route, { waitUntil: "domcontentloaded", timeout: 30000 });
      await page.waitForTimeout(700);

      const measured = await page.evaluate(() => {
        const header = document.querySelector(".site-header")?.getBoundingClientRect();
        const brand = document.querySelector(".brand")?.getBoundingClientRect();
        return {
          header: header ? Math.round(header.height) : 0,
          brand: brand ? Math.round(brand.height) : 0,
          overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
          scrollWidth: document.documentElement.scrollWidth,
          clientWidth: document.documentElement.clientWidth,
        };
      });

      check(!measured.overflow,
        `${route} at ${view.label}: the document scrolls sideways (${measured.scrollWidth} > ${measured.clientWidth})`);
      check(measured.brand <= 30,
        `${route} at ${view.label}: the brand wrapped (${measured.brand}px tall)`);
      check(measured.header <= view.headerMax,
        `${route} at ${view.label}: the header is ${measured.header}px, over its ${view.headerMax}px budget`);

      await page.close();
    }
  }
} finally {
  await browser.close();
}

if (failures.length) {
  console.error("FAIL layout");
  for (const failure of failures) console.error(`  - ${failure}`);
  process.exit(1);
}
console.log("ok layout — no sideways scroll, brand on one line, header within budget at 100%, 150% and phone");
