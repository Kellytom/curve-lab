// Screenshot every plate from book/render.html at its exact pixel size.
//
//   node scripts/plate_png.mjs book/render.html book/plates
//
// The render page holds one element per plate, sized in whole pixels, and the
// element screenshot crops to that box — no window, no scaling, no margin. The
// image is therefore the plate, not a view of a page. Chrome writes 96 dpi;
// plate_export.py stamps 300 dpi afterwards.

import { resolve } from "node:path";
import { chromium } from "playwright-core";

const [, , htmlPath, outDir] = process.argv;
if (!htmlPath || !outDir) {
  console.error("usage: node scripts/plate_png.mjs <render.html> <out dir>");
  process.exit(1);
}

const candidates = [process.env.CHROME_PATH,
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"].filter(Boolean);
let browser = null;
for (const executablePath of candidates) {
  try { browser = await chromium.launch({ executablePath, headless: true }); break; } catch { /* next */ }
}
if (!browser) browser = await chromium.launch({ headless: true });

const page = await browser.newPage({
  viewport: { width: 3400, height: 3400 },
  deviceScaleFactor: 1,
});
await page.goto("file://" + resolve(htmlPath), { waitUntil: "load" });
await page.waitForTimeout(200);

const ids = await page.locator(".plate").evaluateAll(
  (nodes) => nodes.map((node) => node.id.replace(/^plate-/, "")));
for (const id of ids) {
  await page.locator(`#plate-${id}`).screenshot({
    path: `${outDir}/${id}.png`,
    animations: "disabled",
  });
  console.log(id);
}
await browser.close();
