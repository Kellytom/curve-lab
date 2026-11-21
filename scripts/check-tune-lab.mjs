// Open /tune/ and /tune/<uid> in headless Chrome and prove both are live: the SVG must
// change when a value changes, the readout must name both edges, the flat case must read
// 1.00×, a path curve must say it prints the spine, and the per-curve page must redraw
// without submitting its form.
//
//   node scripts/check-tune-lab.mjs [base]
//
// The pages are live drawings, so this reads the DOM after the script has run.

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

const setInput = async (selector, value) => {
  await page.$eval(selector, (node, next) => {
    node.value = String(next);
    node.dispatchEvent(new Event("input", { bubbles: true }));
  }, value);
  await page.waitForTimeout(140);
};
const svgOf = (selector) => page.$eval(selector, (node) => node.outerHTML);
const readoutOf = (selector) => page.$eval(selector, (node) => node.textContent);

try {
  await page.goto(`${BASE}/tune/`, { waitUntil: "networkidle" });
  await page.waitForSelector("#lab-preview svg", { timeout: 8000 });

  const firstSvg = await svgOf("#lab-preview svg");
  const firstReadout = await readoutOf("#lab-readout");
  if (!/Right edge .* Left edge /.test(firstReadout)) {
    problems.push(`readout does not name both edges: ${firstReadout}`);
  }
  if (!/of the curve's size/.test(firstReadout)) {
    problems.push(`readout is not the expected sentence: ${firstReadout}`);
  }
  if (!/Band width [\d.]+ %/.test(firstReadout)) {
    problems.push(`readout does not name the band width: ${firstReadout}`);
  }

  // a character rail must not be parallel: the + side has to widen somewhere
  const ratio = Number((firstReadout.match(/\((\d+\.\d+)× at the belly\)/) || [])[1]);
  if (!(ratio > 1.05)) problems.push(`the right edge is parallel (ratio ${ratio})`);

  // move plus and the drawing must change
  await setInput("#lab-plus", 6);
  if ((await svgOf("#lab-preview svg")) === firstSvg) {
    problems.push("changing plus did not redraw the picture");
  }

  // the profile must change the drawing too
  const beforeProfile = await svgOf("#lab-preview svg");
  await page.selectOption("#lab-profile", "taper");
  await page.waitForTimeout(140);
  if ((await svgOf("#lab-preview svg")) === beforeProfile) {
    problems.push("changing the profile did not redraw the picture");
  }
  await page.selectOption("#lab-profile", "bow");

  // plus 0 and minus 0 is the flat case: both edges parallel, so the ratio is 1.00×
  await setInput("#lab-plus", 0);
  await setInput("#lab-minus", 0);
  const flat = await readoutOf("#lab-readout");
  if (!/Right edge .*\(1\.00× at the belly\)/.test(flat)) {
    problems.push(`plus 0 / minus 0 is not flat: ${flat}`);
  }

  // a stored path draws the plate's band, like the polyline case below
  await page.selectOption("#lab-curve", "c-0273");
  await page.waitForFunction(
    () => /stored points/.test(document.getElementById("lab-readout")?.textContent || ""),
    { timeout: 8000 },
  );
  const pathPaths = await page.$$eval("#lab-preview svg path", (nodes) => nodes.length);
  if (pathPaths < 5) problems.push(`a path curve drew ${pathPaths} paths, not a band`);

  // a polyline is the plate's rail branch: it must draw a band and answer the width
  await page.selectOption("#lab-curve", "c-0143");
  await page.waitForFunction(
    () => /stored points/.test(document.getElementById("lab-readout")?.textContent || ""),
    { timeout: 8000 },
  );
  const polyPaths = await page.$$eval("#lab-preview svg path", (nodes) => nodes.length);
  if (polyPaths < 5) problems.push(`a polyline drew ${polyPaths} paths, not a band`);

  // the first paint and the live redraw must use the same maths. A cached server module
  // once showed the old guard's 1.5 % until the first touch moved the band to 2.29 %.
  await page.goto(`${BASE}/tune/c-0002`, { waitUntil: "networkidle" });
  await page.waitForSelector("#tune-preview svg", { timeout: 8000 });
  const first = await readoutOf("#tune-readout");
  const firstUsed = Number((first.match(/each edge ([\d.]+) %/) || [])[1]);
  const firstPicture = await svgOf("#tune-preview svg");
  await setInput('input[name="plus"]', 2);
  const live = await readoutOf("#tune-readout");
  const liveUsed = Number((live.match(/Band width ([\d.]+) %/) || [])[1]);
  if (!(Math.abs(firstUsed - liveUsed) <= 0.11)) {
    problems.push(`first paint ${firstUsed} % and live redraw ${liveUsed} % disagree`);
  }
  // the same values must draw the same picture: a different frame made the first touch
  // shift the whole drawing even when the width was right
  if ((await svgOf("#tune-preview svg")) !== firstPicture) {
    problems.push("the first paint and the live redraw draw different pictures");
  }

  // a slider and its number move together
  const beforeSlider = await svgOf("#tune-preview svg");
  await page.$eval("#widthPct-slider", (node) => {
    node.value = "1.5";
    node.dispatchEvent(new Event("input", { bubbles: true }));
  });
  await page.waitForTimeout(150);
  const mirrored = await page.$eval('input[name="widthPct"]', (node) => node.value);
  if (Number(mirrored) !== 1.5) problems.push(`the width slider did not reach the number: ${mirrored}`);
  if ((await svgOf("#tune-preview svg")) === beforeSlider) {
    problems.push("moving the width slider did not redraw the picture");
  }

  // a refused save is said beside the buttons, and the buttons come back. An empty name
  // is refused before any write, so this exercises the save path without touching the desk.
  await page.$eval('input[name="curveName"]', (node) => { node.value = ""; });
  await page.click('button[formaction*="mode=new"]');
  await page.waitForFunction(
    () => /not saved/.test(document.getElementById("tune-status")?.textContent || ""),
    { timeout: 15000 },
  );
  const stillDisabled = await page.$$eval('#tune-form button[formaction]',
    (nodes) => nodes.some((node) => node.disabled));
  if (stillDisabled) problems.push("the save buttons stayed disabled after a refusal");

  // the per-curve page redraws in place: no navigation, no submit. The width is still cut
  // by the original fold guard, and the readout must say the number it was cut to.
  await page.goto(`${BASE}/tune/c-0001`, { waitUntil: "networkidle" });
  await page.waitForSelector("#tune-preview svg", { timeout: 8000 });
  const uidBefore = await svgOf("#tune-preview svg");
  const urlBefore = page.url();
  await setInput('input[name="plus"]', 3);
  const uidAfter = await svgOf("#tune-preview svg");
  if (uidAfter === uidBefore) problems.push("/tune/c-0001 did not redraw as a value changed");
  if (page.url() !== urlBefore) problems.push("/tune/c-0001 navigated instead of redrawing");
  const uidReadout = await readoutOf("#tune-readout");
  if (!/Band width [\d.]+ %/.test(uidReadout)) {
    problems.push(`/tune/c-0001 readout does not name the band width: ${uidReadout}`);
  }
  // "asked" appears only when the fold guard cut the width; the band width is always named
  if (!/Band width [\d.]+ %/.test(uidReadout)) {
    problems.push(`/tune/c-0001 readout does not name the band width: ${uidReadout}`);
  }

  // the desk: a name for a new curve, a save, a new curve, and the family list
  const name = await page.$eval('#tune-form input[name="curveName"]',
    (node) => node.getAttribute("placeholder"));
  if (!name) problems.push("the desk has no name field for a new curve");
  const buttons = await page.$$eval('#tune-form button', (nodes) =>
    nodes.map((node) => node.textContent.trim().toLowerCase()));
  if (!buttons.includes("save")) problems.push(`no save button: ${buttons}`);
  if (!buttons.includes("save as a new curve")) problems.push(`no new-curve button: ${buttons}`);
  if (buttons.some((text) => text === "save + render")) {
    problems.push("the old save + render button is still there");
  }
  const versions = await page.$eval(".tune-versions", (node) => node.textContent);
  if (!/Curves from this spine/.test(versions)) {
    problems.push("the page does not list the curves from this spine");
  }

  console.log(problems.length
    ? `FAIL\n- ${problems.join("\n- ")}`
    : "tune lab: both pages draw live, the flat case reads 1.00×, and stored outlines draw bands");
} finally {
  await browser.close();
}

process.exit(problems.length ? 1 : 0);
