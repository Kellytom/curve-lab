// Check the eleventh-power page in a real browser: the twelve speed boxes, the
// width law, the terminal rule, the serif and the openness dial.
//
//   node scripts/check-nth-page.mjs

import { chromium } from "playwright-core";

const url = "http://127.0.0.1:8003/workbench/ph-nth-sandbox.html";
const failures = [];

const candidates = [
  process.env.CHROME_PATH,
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  `${process.env.HOME}/.cache/puppeteer/chrome-headless-shell/mac-133.0.6943.98/chrome-headless-shell-mac-x64/chrome-headless-shell`,
].filter(Boolean);

let browser = null;
for (const executablePath of candidates) {
  try {
    browser = await chromium.launch({ executablePath, headless: true });
    break;
  } catch (error) { /* try the next one */ }
}
if (!browser) browser = await chromium.launch({ headless: true });

const page = await browser.newPage({ viewport: { width: 1120, height: 1000 } });
const errors = [];
page.on("pageerror", error => errors.push(error.message));
await page.goto(`${url}?v=${Date.now()}`, { waitUntil: "load" });

const boxes = await page.$$eval("#n-controls input[type=number]", els => els.length);
if (boxes !== 12) failures.push(`speed boxes: ${boxes}, expected 12`);

// the view: spine only by default, then rails, then the two terminals
const paths = () => page.evaluate(() => document.querySelectorAll("#n-plot path").length);
if (await paths() !== 1) failures.push("default view is not the spine alone");
const spinePath = await page.evaluate(() => {
  const path = document.querySelector("#n-plot path");
  return { d: path.getAttribute("d"), length: Math.round(path.getTotalLength()) };
});
if (/NaN|undefined/.test(spinePath.d) || spinePath.length < 2) {
  failures.push(`the spine is not drawn: length ${spinePath.length}`);
}
await page.click("#n-rails");
if (await paths() !== 3) failures.push("rails toggle did not add two paths");
await page.click("#n-terminal-end");
if (await paths() !== 4) failures.push("end terminal did not add an arc");
await page.click("#n-terminal-start");
if (await paths() !== 5) failures.push("start terminal did not add an arc");
await page.click("#n-terminal-start");
await page.click("#n-terminal-end");
await page.click("#n-rails");
if (await paths() !== 1) failures.push("toggles did not return to the spine alone");

// the sliders must write the number boxes
const boxesBefore = await page.$$eval("#n-controls input[type=number]", els => els.map(input => input.value));
const sliders = await page.$$("#n-controls input[type=range]:not(.decade)");
await sliders[1].evaluate(el => { el.value = "4"; el.dispatchEvent(new Event("input", { bubbles: true })); });
await page.waitForTimeout(120);
const boxesAfter = await page.$$eval("#n-controls input[type=number]", els => els.map(input => input.value));
if (boxesBefore[1] === boxesAfter[1]) failures.push("a slider moved the curve but not the number box");

// the readout must quote the half-width the dial holds
await page.fill("#n-d", "3");
await page.dispatchEvent("#n-d", "input");
const widthText = await page.textContent("#n-width-readout");
const quoted = Number((widthText.match(/d ([0-9.]+)%/) || [])[1]);
if (!Number.isFinite(quoted) || Math.abs(quoted - 3) > 0.002) failures.push(`width readout: ${widthText}`);

// character offsets: two rails and the spine, and at character 0 the rails must
// be exactly the parallel rails
await page.click("#n-rails");
await page.waitForTimeout(150);
const railsBox = await page.evaluate(() => [...document.querySelectorAll("#n-plot path")].map(p => {
  const r = p.getBBox(); return [Math.round(r.width * 100) / 100, Math.round(r.height * 100) / 100];
}));
await page.click("#n-character");
await page.fill("#n-char-l", "0");
await page.dispatchEvent("#n-char-l", "input");
await page.fill("#n-char-r", "0");
await page.dispatchEvent("#n-char-r", "input");
await page.waitForTimeout(250);
const zeroBox = await page.evaluate(() => [...document.querySelectorAll("#n-plot path")].map(p => {
  const r = p.getBBox(); return [Math.round(r.width * 100) / 100, Math.round(r.height * 100) / 100];
}));
if (JSON.stringify(zeroBox) !== JSON.stringify(railsBox))
  failures.push(`character 0 is not the parallel rail: ${JSON.stringify(zeroBox)} vs ${JSON.stringify(railsBox)}`);
await page.fill("#n-char-l", "2");
await page.dispatchEvent("#n-char-l", "input");
await page.fill("#n-char-r", "2");
await page.dispatchEvent("#n-char-r", "input");
await page.click("#n-character");
await page.click("#n-rails");

// the gallery: two columns, every spine drawn
const gallery = await page.evaluate(() => {
  const figures = [...document.querySelectorAll("#n-gallery > figure")];
  const cells = figures.map(f => { const r = f.getBoundingClientRect(); return r.y; });
  const paths = [...document.querySelectorAll("#n-gallery svg path")];
  return {
    count: figures.length,
    twoColumns: cells.length > 1 && cells[0] === cells[1],
    bad: paths.filter(p => /NaN/.test(p.getAttribute("d")) || p.getTotalLength() < 1).length,
    first: figures.slice(0, 2).map(f => f.querySelector(".gallery-name").textContent).join(", "),
  };
});
if (gallery.count < 27) failures.push(`gallery figures: ${gallery.count}`);
if (!gallery.twoColumns) failures.push("gallery is not two columns");
if (gallery.bad) failures.push(`gallery paths not drawn: ${gallery.bad}`);
if (!gallery.first.startsWith("amper")) failures.push(`gallery order starts: ${gallery.first}`);

// a gallery cell opens in place: variables, JSON, and a load back into the sandbox
const firstCell = page.locator("#n-gallery > figure").first();
await firstCell.locator(".gallery-open").click();
await page.waitForTimeout(200);
const opened = await page.evaluate(() => {
  const figure = document.querySelector("#n-gallery figure");
  return {
    open: figure.classList.contains("open"),
    hidden: figure.querySelector(".more").hidden,
    json: figure.querySelector("textarea").value,
    variables: figure.querySelector(".more .mono").textContent,
  };
});
if (!opened.open || opened.hidden) failures.push("the gallery cell did not open in place");
if (!opened.json.includes('"speedX"') || opened.json.length < 40) failures.push("the cell has no JSON to copy");
if (!opened.variables.includes("2, -5, 6")) failures.push("the cell does not show its variables");
await firstCell.locator(".gallery-load").click();
await page.waitForTimeout(300);
if (!(await page.textContent("#n-readout")).startsWith("bend 4.163")) {
  failures.push("gallery load did not bring amper into the sandbox");
}
await firstCell.locator(".gallery-close").click();

const notes = await page.getAttribute('a[href="ph-nth-serif-notes.html"]', "href");
if (!notes) failures.push("the serif notes link is missing");

// the notes page must draw all four strokes, the spine included
await page.goto("http://127.0.0.1:8003/workbench/ph-nth-serif-notes.html?v=" + Date.now(), { waitUntil: "load" });
await page.waitForTimeout(400);
const notesPaths = await page.evaluate(() =>
  [...document.querySelectorAll("#plot path")].map(path => ({
    d: path.getAttribute("d"), length: Math.round(path.getTotalLength()),
  })));
if (notesPaths.length !== 4) failures.push(`notes paths: ${notesPaths.length}, expected 4`);
notesPaths.forEach((path, i) => {
  if (/NaN|undefined/.test(path.d) || path.length < 2) failures.push(`notes path ${i} is not drawn`);
});

// part 2: the same sandbox over fitted curves
await page.goto("http://127.0.0.1:8003/workbench/ph-nth-sandbox-2.html?v=" + Date.now(), { waitUntil: "load" });
await page.waitForTimeout(300);
const part2 = await page.evaluate(() => {
  const figures = [...document.querySelectorAll("#n-gallery > figure")];
  return {
    count: figures.length,
    tags: [...new Set(figures.map(f => f.querySelector(".tag").textContent))],
    bad: [...document.querySelectorAll("#n-gallery svg path")]
      .filter(p => /NaN/.test(p.getAttribute("d"))).length,
    boxes: document.querySelectorAll("#n-controls input[type=number]").length,
  };
});
if (part2.count < 40) failures.push(`part 2 gallery: ${part2.count}`);
if (!part2.tags.includes("fitted")) failures.push(`part 2 tags: ${part2.tags.join()}`);
if (part2.bad) failures.push(`part 2 paths not drawn: ${part2.bad}`);
if (part2.boxes !== 12) failures.push(`part 2 boxes: ${part2.boxes}`);

if (errors.length) failures.push(`page errors: ${errors.join(" | ")}`);

await page.close();
await browser.close().catch(() => {});

if (failures.length) {
  console.error("FAIL");
  for (const failure of failures) console.error("  " + failure);
  process.exit(1);
}
console.log("OK  12 boxes, spine by default, offsets, character, shear, hook, terminals, gallery of " + gallery.count);
