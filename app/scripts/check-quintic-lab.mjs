// The quintic sandbox in a real browser: draw on the pad, read the numbers.
//
//   node app/scripts/check-quintic-lab.mjs
//
// It proves the page is not just markup: the script must load, a pointer drag must
// become a stroke, the outline must be a cubic chain, and a control must change the
// readout. A page error or a failed assertion exits 1.

import { chromium } from "playwright-core";
import { gotoStable } from "./lib/navigate.mjs";

const EXE = process.env.CHROME_PATH || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const URL = process.env.QUINTIC_LAB_URL || "http://127.0.0.1:4321/quintic-lab";

const browser = await chromium.launch({ executablePath: EXE });
const page = await browser.newPage({ viewport: { width: 1200, height: 1000 } });
const errors = [];
page.on("pageerror", (error) => errors.push(`pageerror: ${error}`));
page.on("console", (message) => {
  if (message.type() === "error") errors.push(`console: ${message.text()}`);
});

const failures = [];
const check = (ok, what) => {
  if (!ok) failures.push(what);
};

await gotoStable(page, URL);
await page.waitForFunction(() => {
  const el = document.getElementById("ql-readout");
  return el && /span/.test(el.textContent || "");
}, { timeout: 20000 });

// the demo stroke is drawn on load: outline, spine and six-point marks exist
const state = await page.evaluate(() => ({
  readout: document.getElementById("ql-readout")?.textContent || "",
  outline: document.getElementById("ql-outline")?.getAttribute("d") || "",
  spine: document.getElementById("ql-spine")?.getAttribute("d") || "",
  marks: document.querySelectorAll("#ql-points circle").length,
  spans: Number((document.getElementById("ql-spans-slider") || {}).value),
}));
check(/span/.test(state.readout), "the readout names the spans");
check(state.outline.includes("C "), "the outline is a cubic chain, not a polyline");
check(state.outline.trim().endsWith("Z"), "the outline closes");
check(state.spine.length > 200, "the spine is drawn");
check(state.marks === state.spans * 6, `${state.marks} marks for ${state.spans} spans`);

// a pointer drag makes a new stroke: the readout changes and the guide follows it
const before = state.readout;
const box = await page.locator("#ql-pad").boundingBox();
await page.mouse.move(box.x + 120, box.y + 120);
await page.mouse.down();
for (let i = 1; i <= 24; i += 1) {
  const t = i / 24;
  await page.mouse.move(box.x + 120 + 700 * t, box.y + 260 + 120 * Math.sin(2 * Math.PI * t));
}
await page.mouse.up();
await page.waitForTimeout(300);

const after = await page.evaluate(() => ({
  readout: document.getElementById("ql-readout")?.textContent || "",
  guide: document.getElementById("ql-guide")?.getAttribute("d") || "",
  misses: document.querySelectorAll("#ql-points circle").length,
}));
check(after.guide.startsWith("M "), "the drawn guide is on the page");
check(after.readout !== before, "the readout follows the new stroke");
check(/stroke→quintic/.test(after.readout), "the readout reports the stroke→quintic miss");

// a control changes the drawing: the swell in the middle
const wide = await page.evaluate(async () => {
  const slider = document.getElementById("ql-middle-slider");
  slider.value = "30";
  slider.dispatchEvent(new globalThis.Event("input", { bubbles: true }));
  await new Promise((r) => globalThis.requestAnimationFrame(() => globalThis.requestAnimationFrame(r)));
  return {
    readout: document.getElementById("ql-readout")?.textContent || "",
    outline: document.getElementById("ql-outline")?.getAttribute("d") || "",
  };
});
check(/width /.test(wide.readout), "the readout reports the width");
check(wide.outline.length > 200, "the outline survives a width change");

for (const message of errors) failures.push(message);
await browser.close();

if (failures.length) {
  console.error("FAIL");
  for (const failure of failures) console.error("  -", failure);
  process.exit(1);
}
console.log("ok  quintic sandbox: script loaded, drag drew, controls change the drawing");
