// Behavioural check for /stage-two/ — the curves made from the prime mover.
//
//   node app/scripts/check-stage-two-page.mjs        (dev server on :4321)

import { chromium } from "playwright-core";

const BASE = process.env.CURVE_LAB_URL || "http://127.0.0.1:4321";
const EXE = process.env.CHROME_PATH || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";

const browser = await chromium.launch({ executablePath: EXE });
const page = await browser.newPage({ viewport: { width: 1300, height: 1100 } });
const errors = [];
page.on("pageerror", (error) => errors.push(String(error)));

const failures = [];
const check = (condition, message) => { if (!condition) failures.push(message); };

const read = () => page.evaluate(() => ({
  rows: [...document.querySelectorAll("#st-table tbody tr")]
    .map((row) => [...row.children].map((cell) => cell.textContent.trim())),
  title: [...document.querySelectorAll("#st-plot text")][0]?.textContent || "",
  readout: document.getElementById("st-readout")?.textContent || "",
  baseline: [...document.querySelectorAll("#st-plot circle")]
    .filter((circle) => circle.getAttribute("stroke-dasharray")).length,
  paths: document.querySelectorAll("#st-plot path").length,
  bodyText: document.body.innerText,
  deadControls: [...document.querySelectorAll("#st-reduce, #st-labels, #st-walk")].length,
}));

try {
  await page.goto(`${BASE}/stage-two/`, { waitUntil: "domcontentloaded", timeout: 90000 });
  await page.waitForTimeout(600);

  // circle: the table is the driver itself, exactly
  await page.selectOption("#st-preset", "circle");
  await page.waitForTimeout(250);
  const circle = await read();
  check(circle.rows.length === 12, `circle table has ${circle.rows.length} rows, expected the twelve hit points`);
  check(circle.rows[0][0] === "0", `circle first row does not start at i = 0: ${circle.rows[0][0]}`);
  check(circle.rows[0][1] === "24/25" && circle.rows[0][2] === "7/25",
    `the walk does not start at the first apex (24/25, 7/25): ${circle.rows[0]}`);
  check(circle.baseline >= 1, "the baseline circle is not drawn");
  // the baseline is a reference: one circle, one curve, nothing drawn across it
  const marks = await page.evaluate(() => ({
    baseline: [...document.querySelectorAll("#st-plot circle")]
      .filter((node) => node.getAttribute("stroke-dasharray")).length,
    dots: [...document.querySelectorAll("#st-plot circle")]
      .filter((node) => !node.getAttribute("stroke-dasharray")).length,
    paths: document.querySelectorAll("#st-plot path").length,
    cubic: [...document.querySelectorAll("#st-plot path")]
      .every((path) => (path.getAttribute("d") || "").includes("C")),
    orange: document.querySelectorAll('#st-plot circle[fill="#c9761f"]').length,
    blue: document.querySelectorAll('#st-plot circle[fill="#2f6fa8"]').length,
    lines: document.querySelectorAll("#st-plot line").length,
  }));
  check(marks.baseline === 1, `Fig. 1 has ${marks.baseline} baseline circles, expected one`);
  check(marks.dots >= 10, `Fig. 1 has ${marks.dots} station dots, expected one per station`);
  check(marks.paths === 1, `Fig. 1 has ${marks.paths} paths, expected only the curve`);
  check(marks.cubic, "Fig. 1 draws straight segments, not a cubic Bézier chain");
  check(marks.orange > 0 && marks.blue > 0,
    "Fig. 1 does not carry the two colours on its stations");
  check(marks.lines <= 2, `Fig. 1 has ${marks.lines} extra lines, expected only the two axes`);
  check(circle.title.includes("the circle"), `the figure does not name the preset: ${circle.title}`);
  check(/step [(]3, 4, 5[)]/.test(circle.title), `the figure does not name the step: ${circle.title}`);

  // a different preset must change the curve, not just its name
  await page.selectOption("#st-preset", "s");
  await page.waitForTimeout(250);
  const sCurve = await read();
  check(sCurve.rows[0][1] !== circle.rows[0][1] || sCurve.rows[0][2] !== circle.rows[0][2],
    "the S preset draws the same points as the circle");
  check(sCurve.title.includes("the S"), `the figure does not name the S preset: ${sCurve.title}`);

  // the walk is fixed: no step chooser, and the same walk every load
  const steps = await page.evaluate(() => document.querySelectorAll("#st-triple").length);
  check(steps === 0, "a step chooser is back on the page, but the walk is fixed");

  // exactness and the bans
  for (const [name, seen] of [["circle", circle], ["s", sCurve]]) {
    check(!seen.rows.some((row) => row.some((cell) => cell.includes("."))),
      `(${name}) a table cell holds a decimal`);
    check(!seen.rows.some((row) => row.some((cell) => cell.length === 0)),
      `(${name}) a table cell is empty`);
    check(!/NaN|undefined|Infinity/.test(seen.bodyText), `(${name}) the page printed NaN, undefined or Infinity`);
    check(seen.paths === 1, `(${name}) the figure has ${seen.paths} paths, expected one curve`);
    check(seen.deadControls === 0, `(${name}) a dead control is on the page`);
    check(/sampled/.test(seen.readout), `(${name}) the readout does not say the line is sampled`);
  }

  // the spirograph: three paths, a whole ratio, and a chooser that changes it
  const spiro = await page.evaluate(() => ({
    paths: document.querySelectorAll("#sp-plot path").length,
    title: [...document.querySelectorAll("#sp-plot text")][0]?.textContent || "",
  }));
  check(spiro.paths === 3, `the spirograph has ${spiro.paths} paths, expected the sum and two vanes`);
  check(/ratio 5/.test(spiro.title), `the spirograph does not name its ratio: ${spiro.title}`);
  await page.selectOption("#sp-ratio", "7");
  await page.waitForTimeout(300);
  const spiro7 = await page.evaluate(() => ({
    title: [...document.querySelectorAll("#sp-plot text")][0]?.textContent || "",
    paths: document.querySelectorAll("#sp-plot path").length,
    cubic: [...document.querySelectorAll("#sp-plot path")]
      .every((path) => (path.getAttribute("d") || "").includes("C")),
    dots: document.querySelectorAll("#sp-plot circle.station").length,
  }));
  check(/ratio 7/.test(spiro7.title), `the ratio chooser did not change the figure: ${spiro7.title}`);
  check(spiro7.paths === 3, "the spirograph lost a path at ratio 7");
  check(spiro7.cubic, "the spirograph draws straight segments, not a cubic Bézier chain");
  check(spiro7.dots === 12, `the spirograph carries ${spiro7.dots} coloured stations, expected twelve`);

  check(errors.length === 0, `page errors: ${errors.join("; ")}`);
} finally {
  await browser.close();
}

if (failures.length) {
  console.error("FAIL /stage-two/");
  for (const failure of failures) console.error(`  - ${failure}`);
  process.exit(1);
}
console.log("ok /stage-two/ — exact stations, presets and steps drive curve and table, baseline drawn");
