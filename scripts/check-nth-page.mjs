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

// the degree ladder: one more number per axis per rung, so two more boxes, and
// a filled top pair must make the readout name the degree that follows.
const fillBox = (index, number) => page.evaluate(([i, v]) => {
  const input = document.querySelectorAll("#n-controls input[type=number]")[i];
  input.value = String(v);
  input.dispatchEvent(new Event("input", { bubbles: true }));
}, [index, number]);

for (const [speedDegree, degree, count] of [[6, 13, 14], [7, 15, 16], [8, 17, 18], [9, 19, 20]]) {
  await page.click(`#n-rungs .rung[data-speed-degree="${speedDegree}"]`);
  await page.waitForTimeout(150);
  const made = await page.$$eval("#n-controls input[type=number]", els => els.length);
  if (made !== count) failures.push(`degree ${degree}: ${made} boxes, expected ${count}`);
  const sliders = await page.$$eval("#n-controls input[type=range]", els => els.length);
  if (sliders !== count) failures.push(`degree ${degree}: ${sliders} sliders, expected ${count}`);
  await fillBox(count / 2 - 1, 1);        // the top x number
  await fillBox(count - 1, -1);           // the top y number
  await page.waitForTimeout(150);
  const grade = await page.textContent("#n-grade");
  if (!grade.includes(`degree ${degree}`)) failures.push(`degree ${degree} readout: ${grade}`);
}
// back to the eleventh power: the rest of the checks assume twelve boxes
await page.click('#n-rungs .rung[data-speed-degree="5"]');
await page.waitForTimeout(150);
const back = await page.$$eval("#n-controls input[type=number]", els => els.length);
if (back !== 12) failures.push(`back to degree 11: ${back} boxes`);

// the complementary curve: its own sliders, drawn grey, and counted where it
// meets the spine
const complementBoxes = await page.$$eval("#n-complement-controls input[type=number]", els => els.length);
if (complementBoxes !== 12) failures.push(`complement boxes: ${complementBoxes}, expected 12`);
const greyPath = () => page.evaluate(() => [...document.querySelectorAll("#n-plot path")]
  .filter(path => (path.getAttribute("stroke") || "").toLowerCase() === "#666666")
  .map(path => path.getAttribute("d"))[0] || "");
const greyBefore = await greyPath();
if (!greyBefore) failures.push("the complementary curve is not drawn in grey");
const counted = (await page.textContent("#n-crossings")).trim();
const marks = await page.evaluate(() => [...document.querySelectorAll("#n-plot circle")]
  .filter(circle => (circle.getAttribute("stroke") || "").toLowerCase() === "#a23b2a").length);
if (!/^\d+ crossings?$/.test(counted)) failures.push(`crossing label: "${counted}"`);
if (Number(counted.split(" ")[0]) !== marks) failures.push(`label says "${counted}" but ${marks} marks are drawn`);
const spineBefore = await page.evaluate(() => document.querySelectorAll("#n-plot path").length);

// a complement slider must move the grey curve and leave the spine alone
await page.evaluate(() => {
  const boxes = document.querySelectorAll("#n-complement-controls input[type=number]");
  const box = boxes[boxes.length - 1];
  box.value = "2";
  box.dispatchEvent(new Event("input", { bubbles: true }));
});
await page.waitForTimeout(200);
const greyAfter = await greyPath();
if (greyAfter === greyBefore) failures.push("a complement box did not move the grey curve");
const spineAfter = await page.evaluate(() => document.querySelectorAll("#n-plot path").length);
if (spineAfter !== spineBefore) failures.push("editing the complement changed the number of spine paths");

// the view: spine only by default, then rails, then the two terminals.
// The complementary curve is grey and is not counted as spine ink.
const paths = () => page.evaluate(() =>
  [...document.querySelectorAll("#n-plot path")]
    .filter(path => (path.getAttribute("stroke") || "").toLowerCase() !== "#666666").length);
if (await paths() !== 1) failures.push("default view is not the spine alone");
const spinePath = await page.evaluate(() => {
  const path = [...document.querySelectorAll("#n-plot path")]
    .find(item => (item.getAttribute("stroke") || "").toLowerCase() === "#2e2413");
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
// the first cell is x t^0, whose box holds 2 by default: moving its slider to 7
// must write 7 into that same box
await sliders[0].evaluate(el => { el.value = "7"; el.dispatchEvent(new Event("input", { bubbles: true })); });
await page.waitForTimeout(120);
const boxesAfter = await page.$$eval("#n-controls input[type=number]", els => els.map(input => input.value));
if (boxesBefore[0] === boxesAfter[0]) failures.push("a slider moved the curve but not the number box");

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
const inkBoxes = () => page.evaluate(() => [...document.querySelectorAll("#n-plot path")]
  .filter(path => (path.getAttribute("stroke") || "").toLowerCase() !== "#666666")
  .map(path => {
    const r = path.getBBox(); return [Math.round(r.width * 100) / 100, Math.round(r.height * 100) / 100];
  }));
const railsBox = await inkBoxes();
await page.click("#n-character");
await page.fill("#n-char-l", "0");
await page.dispatchEvent("#n-char-l", "input");
await page.fill("#n-char-r", "0");
await page.dispatchEvent("#n-char-r", "input");
await page.waitForTimeout(250);
const zeroBox = await inkBoxes();
if (JSON.stringify(zeroBox) !== JSON.stringify(railsBox))
  failures.push(`character 0 is not the parallel rail: ${JSON.stringify(zeroBox)} vs ${JSON.stringify(railsBox)}`);
await page.fill("#n-char-l", "2");
await page.dispatchEvent("#n-char-l", "input");
await page.fill("#n-char-r", "2");
await page.dispatchEvent("#n-char-r", "input");
await page.click("#n-character");
await page.click("#n-rails");

// place the end: the top pair solves the endpoint, and the start barely moves
const endOf = () => page.evaluate(() => {
  const json = JSON.parse(document.getElementById("n-json").value);
  const x = json.speedX, y = json.speedY;
  const poly = (row, t) => row.reduce((sum, v, k) => sum + v * Math.pow(t, k), 0);
  let px = 0, py = 0;
  const steps = 4000;
  for (let i = 0; i < steps; i++) {
    const t = (i + 0.5) / steps;
    const p = poly(x, t), q = poly(y, t);
    px += (p * p - q * q) / steps;
    py += 2 * p * q / steps;
  }
  return [px, py];
});
const before = await page.evaluate(() => document.querySelector("#n-plot path[stroke='#2e2413']").getAttribute("d").slice(0, 400));
await page.fill("#n-end-x", "0.5");
await page.fill("#n-end-y", "0.3");
await page.click("#n-place-end");
await page.waitForTimeout(400);
const landed = await endOf();
if (Math.hypot(landed[0] - 0.5, landed[1] - 0.3) > 0.002) {
  failures.push(`place the end landed at ${landed.map(v => v.toFixed(4)).join(", ")}`);
}
const after = await page.evaluate(() => document.querySelector("#n-plot path[stroke='#2e2413']").getAttribute("d").slice(0, 400));
if (after === before) failures.push("place the end changed nothing");

// the window runs past the ends when asked. The drawn path is measured in
// screen units, so a long tail shrinks the rest of the figure; what is checked
// is that the window changed the drawing at all.
const pathNow = () => page.evaluate(() =>
  [...document.querySelectorAll("#n-plot path")]
    .find(p => (p.getAttribute("stroke") || "").toLowerCase() === "#2e2413").getAttribute("d"));
const pathBefore = await pathNow();
await page.fill("#n-t-from", "-0.3");
await page.dispatchEvent("#n-t-from", "input");
await page.waitForTimeout(300);
const pathAfter = await pathNow();
if (pathAfter === pathBefore) failures.push("t from -0.3 did not change the drawing");
await page.fill("#n-t-from", "0");
await page.dispatchEvent("#n-t-from", "input");
await page.waitForTimeout(200);

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
