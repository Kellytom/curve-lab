// Check the generated gallery in a real browser: the six readouts, the save
// buttons, and no page errors.
//
//   node scripts/check-ph-page.mjs
//   node scripts/check-ph-page.mjs http://127.0.0.1:8003/workbench/ph-quintic-gallery.html
//
// Needs the headless Chrome shell on CDP port 9223 (the same one the other
// browser checks use). Exits 1 on any mismatch.

import { chromium } from "playwright-core";

const url = process.argv[2] || "http://127.0.0.1:8003/workbench/ph-quintic-gallery.html";
const expected = {
  "q7-readout": "bend 1.15",
  "q8-readout": "bend 5.58",
  "q9-readout": "bend 2.00",
  "q10-readout": "bend 1.91",
  "q11-readout": "bend 2.04",
  "q13-exact": "arc",
  "q14-readout": "bend 1.997",
};

const browser = await chromium.connectOverCDP("http://127.0.0.1:9223");
const page = await browser.contexts()[0].newPage();
const errors = [];
page.on("pageerror", error => errors.push(error.message));

await page.setViewportSize({ width: 1200, height: 1000 });
await page.goto(`${url}?v=${Date.now()}`, { waitUntil: "load" });

const failures = [];
for (const [id, prefix] of Object.entries(expected)) {
  const text = await page.evaluate(id => {
    const element = document.getElementById(id);
    return element ? element.textContent : null;
  }, id);
  if (text === null) failures.push(`${id}: missing`);
  else if (!text.startsWith(prefix)) failures.push(`${id}: "${text}" does not start with "${prefix}"`);
}

const saveButtons = await page.locator(".save-curve").count();
if (saveButtons !== 6) failures.push(`save buttons: ${saveButtons}, expected 6`);

// the septic sandbox: its numbers must match the Python metrics module
const sandboxUrl = url.replace("ph-quintic-gallery.html", "ph-septic-sandbox.html");
await page.goto(`${sandboxUrl}?v=${Date.now()}`, { waitUntil: "load" });
const septic = await page.evaluate(() => document.getElementById("b-readout").textContent);
if (!septic.startsWith("bend 1.850 | pitch 700 | inflection 0.494 | closest 1.461")) {
  failures.push(`septic readout: "${septic}"`);
}

// Typing a curve's own numbers back must give the same curve. A partial entry
// ("-", "0.") reads as empty in a number input, so a handler that writes the
// field back on every keystroke eats the sign and the decimal point.
const septicBefore = await page.evaluate(() => ({
  readout: document.getElementById("b-readout").textContent,
  values: [...document.querySelectorAll("#b-controls input[type=number]")].map(input => input.value),
}));
const septicInputs = await page.$$("#b-controls input[type=number]");
for (let i = 0; i < septicInputs.length; i++) {
  await septicInputs[i].click();
  await page.keyboard.press("Meta+A");          // select all, so typing replaces
  await page.keyboard.type(septicBefore.values[i], { delay: 20 });
}
const septicAfter = await page.evaluate(() => ({
  readout: document.getElementById("b-readout").textContent,
  values: [...document.querySelectorAll("#b-controls input[type=number]")].map(input => input.value),
}));
if (septicAfter.values.join() !== septicBefore.values.join()) {
  failures.push(`retyped speeds: ${septicBefore.values.join()} -> ${septicAfter.values.join()}`);
}
if (septicAfter.readout !== septicBefore.readout) {
  failures.push(`retyped septic readout: "${septicBefore.readout}" -> "${septicAfter.readout}"`);
}

// the dial: solving to an openness must land on it, and the lift must keep the
// five quintic numbers while adding the two septic ones
const opennessOf = async () => {
  const text = await page.textContent("#b-readout");
  const match = text.match(/open ([0-9.]+)/);
  return match ? Number(match[1]) : null;
};
await page.fill("#b-open-value", "0.30");
await page.click("#b-open");
await page.waitForTimeout(200);
const reached = await opennessOf();
if (reached === null || Math.abs(reached - 0.30) > 0.01) {
  failures.push(`close-to 0.30 gave openness ${reached}`);
}
const liftInputs = await page.$$("#b-controls input[type=number]");
const quintic = ["2", "-5", "6", "0", "4", "-22", "22", "0"];
for (let i = 0; i < liftInputs.length; i++) {
  await liftInputs[i].click();
  await page.keyboard.press("Meta+A");
  await page.keyboard.type(quintic[i], { delay: 10 });
}
await page.fill("#b-open-value", "0.25");
await page.click("#b-lift");
await page.waitForTimeout(200);
const lifted = await page.$$eval("#b-controls input[type=number]", els => els.map(input => input.value));
const liftedOpen = await opennessOf();
if (liftedOpen === null || Math.abs(liftedOpen - 0.25) > 0.01) {
  failures.push(`lift gave openness ${liftedOpen}`);
}
if (Number(lifted[4]) !== 4 || Number(lifted[5]) !== -22 || Number(lifted[6]) !== 22) {
  failures.push(`lift moved the quintic numbers: ${lifted.join()}`);
}

if (errors.length) failures.push(`page errors: ${errors.join(" | ")}`);

await page.close();
await browser.close().catch(() => {});

if (failures.length) {
  console.error("FAIL");
  for (const failure of failures) console.error("  " + failure);
  process.exit(1);
}
console.log(`OK  ${Object.keys(expected).length} readouts, ${saveButtons} save buttons, no page errors`);
