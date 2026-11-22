// Behavioural check for /prime-mover/ — the walk, and the points it makes.
//
//   node app/scripts/check-prime-mover-page.mjs        (dev server on :4321)

import { chromium } from "playwright-core";
import { gotoStable } from "./lib/navigate.mjs";

const BASE = process.env.CURVE_LAB_URL || "http://127.0.0.1:4321";
const EXE = process.env.CHROME_PATH || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";

const browser = await chromium.launch({ executablePath: EXE });
const page = await browser.newPage({ viewport: { width: 1300, height: 1800 } });
const errors = [];
page.on("pageerror", (error) => errors.push(String(error)));

const failures = [];
const check = (condition, message) => { if (!condition) failures.push(message); };

const big = (cell) => BigInt(cell.split("/")[0].replace(/[−-]/g, ""));

try {
  await gotoStable(page, `${BASE}/prime-mover/`, { waitUntil: "domcontentloaded", timeout: 90000 });
  await page.waitForTimeout(900);

  const seen = await page.evaluate(() => {
    const board = document.querySelector("#tm-board svg");
    const chart = document.querySelector("#hit-chart svg");
    const rings = [...(board?.querySelectorAll("ellipse") || [])]
      .filter((node) => node.getAttribute("stroke") === "#e08a1e")
      .map((node) => ({ cx: +node.getAttribute("cx"), cy: +node.getAttribute("cy") }));
    const circles = [...(board?.querySelectorAll("ellipse") || [])]
      .filter((node) => node.getAttribute("stroke-dasharray"))
      .map((node) => ({ cx: +node.getAttribute("cx"), cy: +node.getAttribute("cy"), rx: +node.getAttribute("rx") }));
    return {
      board: Boolean(board),
      segments: board ? board.querySelectorAll("line").length : 0,
      rings,
      circles,
      chart: Boolean(chart),
      chartBox: chart ? chart.getAttribute("viewBox") : "",
      chartPoints: chart ? [...chart.querySelectorAll("circle")].length - 1 : 0,
      guides: chart ? [...chart.querySelectorAll("line")]
        .filter((line) => line.getAttribute("stroke-dasharray") === "3 3").length : 0,
      labels: chart ? [...chart.querySelectorAll("text")].map((node) => node.textContent) : [],
      tripleValue: document.getElementById("pm-triple")?.value || "",
      halfChecked: Boolean(document.getElementById("pm-half")?.checked),
      bodyText: document.body.innerText,
      deadControls: [...document.querySelectorAll("#gd-reduce, #gd-labels, #gd-walk")].length,
    };
  });

  check(errors.length === 0, `page errors: ${errors.join("; ")}`);

  // Fig. 1 — the walk, built by reflection
  check(seen.board, "Fig. 1 has no board");
  check(seen.segments >= 24, `Fig. 1 draws ${seen.segments} lines, expected at least 24 for eight triangles`);
  check(seen.circles.length >= 2, "Fig. 1 does not draw the 24 and 25 circles");
  check(seen.rings.length === 23, `Fig. 1 has ${seen.rings.length} hit-point rings, expected 23`);
  const outer = seen.circles.reduce((best, c) => (c.rx > best.rx ? c : best), seen.circles[0] || { rx: 0 });
  const unit = outer.rx / 25;
  const offCircle = seen.rings.filter((ring) =>
    Math.abs(Math.hypot(ring.cx - outer.cx, ring.cy - outer.cy) / unit - 25) > 0.1);
  check(offCircle.length === 0, `${offCircle.length} rings are not on the 25 circle`);

  // the page's own start: the thin triple, with quadrants I and IV ticked
  check(seen.tripleValue === "56,783,785",
    `the page opens on triple ${seen.tripleValue}, expected 56,783,785`);
  check(seen.halfChecked, "the page opens with quadrants I and IV unticked");

  // Fig. 2 — the hit points, drawn with axes
  check(seen.chart, "Fig. 2 has no chart");
  check(seen.chartBox === "0 0 760 760", `the chart is not square: ${seen.chartBox}`);
  // the station count follows the triple: the half walk on (56,783,785) gives 23
  check(seen.chartPoints === 23, `the chart has ${seen.chartPoints} points, expected 23`);
  check(seen.guides === 46, `the chart has ${seen.guides} guides, expected two per point`);
  check(seen.labels.includes("x") && seen.labels.includes("y"), "the chart does not name its axes");

  // the numbers live in the notes; the page must not carry a table of them
  const pageTables = await page.evaluate(() => document.querySelectorAll("#hit-table, #gauss-table").length);
  check(pageTables === 0, "a numeric table is back on the page; it belongs in the notes");

  // Fig. 4 — the spirograph: one curve and its stations, nothing else
  const spiro = await page.evaluate(() => ({
    paths: document.querySelectorAll("#sp-plot path").length,
    dots: document.querySelectorAll("#sp-plot circle.station").length,
    stray: [...document.querySelectorAll("#sp-plot circle")].filter((c) => !c.classList.contains("station")).length,
  }));
  check(spiro.paths === 1, `the spirograph draws ${spiro.paths} paths, expected one curve`);
  check(spiro.dots > 0, "the spirograph has no stations");
  check(spiro.stray === 0, `${spiro.stray} extra circles are drawn on the spirograph`);

  // Fig. 5 — the linkage: a mechanism, a traced path, and five labels
  const linkage = await page.evaluate(() => {
    const svg = document.querySelector("#linkage-plot svg");
    if (!svg) return null;
    return {
      paths: svg.querySelectorAll("path").length,
      lines: svg.querySelectorAll("line").length,
      labels: [...svg.querySelectorAll("text")].map((node) => node.textContent),
    };
  });
  check(Boolean(linkage), "Fig. 8, the linkage, did not render");
  if (linkage) {
    check(linkage.paths >= 1, "the linkage does not draw its coupler curve");
    check(linkage.lines >= 4, `the linkage draws ${linkage.lines} bars, expected the crank, coupler, rocker and ground`);
    for (const name of ["A", "B", "C", "D", "P"]) {
      check(linkage.labels.includes(name), `the linkage does not label ${name}`);
    }
    check(linkage.labels.some((text) => /sampled/.test(text)), "the linkage does not say it is sampled");
  }

  // Fig. 5 — the geared spirograph: a ring, a wheel, a pen, and the rosette
  const geared = await page.evaluate(() => {
    const svg = document.querySelector("#gear-plot svg");
    if (!svg) return null;
    return {
      paths: svg.querySelectorAll("path").length,
      circles: svg.querySelectorAll("circle").length,
      labels: [...svg.querySelectorAll("text")].map((node) => node.textContent).join(" "),
      integerStations: [...svg.querySelectorAll("circle")]
        .filter((c) => ["#2f6fa8", "#c9761f"].includes(c.getAttribute("fill"))).length,
    };
  });
  check(Boolean(geared), "Fig. 7, the geared spirograph, did not render");
  if (geared) {
    check(geared.paths >= 1, "the geared spirograph draws no curve");
    check(geared.circles >= 2, `the geared spirograph draws ${geared.circles} circles, expected the ring, the wheel and the pen`);
    check(geared.integerStations > 0, "the geared spirograph marks no integer station");
    check(/blue: first part/.test(geared.labels), "the geared spirograph does not explain the colours");
    check(/sampled/.test(geared.labels), "the geared spirograph does not say it is sampled");
  }

  // and the notes do carry them, with the laws intact
  await gotoStable(page, `${BASE}/spec/prime-mover-gaussian.html`, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(300);
  const notesRows = await page.evaluate(() => [...document.querySelectorAll("table tr")]
    .map((row) => [...row.children].map((cell) => cell.textContent.trim()))
    // the station table has six columns: k, x, y, a, b, hypotenuse
    .filter((row) => row.length === 6 && /^\d+$/.test(row[0])));
  check(notesRows.length === 12, `the notes carry ${notesRows.length} station rows, expected 12`);
  // x = 24a, y = 7b, and the hypotenuse is 25·625^k
  const wrongLaws = notesRows.filter((row, k) => {
    const xNumerator = big(row[1]);
    const yNumerator = big(row[2]);
    return xNumerator !== 24n * big(row[3])
      || yNumerator !== 7n * big(row[4])
      || row[5] !== (25n * 625n ** BigInt(k)).toString();
  });
  check(wrongLaws.length === 0,
    `${wrongLaws.length} rows in the notes break x = 24a, y = 7b, or the hypotenuse`);


  check(!/NaN|undefined|Infinity/.test(seen.bodyText), "the page printed NaN, undefined or Infinity");

  // no NaN geometry: the denominators are bigger than a double, so a bad conversion
  // shows up as NaN in an attribute rather than as an error
  const geometry = await page.evaluate(() => {
    const bad = [];
    for (const node of document.querySelectorAll("#hit-chart svg *, #sp-plot svg *, #st-plot *")) {
      for (const name of ["cx", "cy", "r", "d", "x1", "y1", "x2", "y2"]) {
        const value = node.getAttribute(name);
        if (value && /NaN|Infinity/.test(value)) bad.push(`${node.tagName}.${name}`);
      }
    }
    return bad;
  });
  check(geometry.length === 0, `NaN geometry: ${geometry.slice(0, 3).join(", ")}`);
  check(seen.deadControls === 0, "a dead control is back on the page");

  // Fig. 9 — the drawings: four panels, each with axes, a legend and Bézier chains
  await gotoStable(page, `${BASE}/prime-mover/`, { waitUntil: "domcontentloaded", timeout: 90000 });
  await page.waitForTimeout(1400);
  const panels = await page.evaluate(() => {
    return [...document.querySelectorAll(".pm-plots svg[data-panel]")].map((svg) => {
      const texts = [...svg.querySelectorAll("text")].map((node) => node.textContent);
      const paths = [...svg.querySelectorAll("path")].map((node) => node.getAttribute("d") || "");
      return {
        key: svg.dataset.panel,
        hasX: texts.includes("x"),
        hasY: texts.includes("y"),
        legend: [...svg.querySelectorAll("text")]
          .filter((node) => Number(node.getAttribute("font-size")) >= 15).length,
        bezier: paths.length > 0 && paths.every((d) => /C/.test(d)),
        polylines: paths.filter((d) => !/C/.test(d)).length,
      };
    });
  });
  check(panels.length === 7, `Fig. 9 draws ${panels.length} panels, expected seven`);

  // Fig. 10 — the driver's table, and the circle taken out: two panels, same furniture
  const reformPanels = await page.evaluate(() => {
    return [...document.querySelectorAll(".pm-reform-plots svg[data-panel]")].map((svg) => {
      const texts = [...svg.querySelectorAll("text")].map((node) => node.textContent);
      return {
        key: svg.dataset.panel,
        hasX: texts.includes("x"),
        hasY: texts.includes("y"),
        legend: [...svg.querySelectorAll("text")]
          .filter((node) => Number(node.getAttribute("font-size")) >= 15).length,
      };
    });
  });
  check(reformPanels.length === 2, `Fig. 10 draws ${reformPanels.length} panels, expected two`);
  check(reformPanels.every((panel) => panel.hasX && panel.hasY), "a Fig. 10 panel does not name both axes");
  check(reformPanels.every((panel) => panel.legend >= 2), "a Fig. 10 panel has no readable legend");

  // Fig. 5 — the character gallery gets the same treatment: axes, legend, Bézier chains
  const gallery = await page.evaluate(() =>
    [...document.querySelectorAll(".pm-gallery:not(.pm-plots):not(.pm-reform-plots) svg[data-panel]")].map((svg) => ({
      x: [...svg.querySelectorAll("text")].some((node) => node.textContent === "x"),
      y: [...svg.querySelectorAll("text")].some((node) => node.textContent === "y"),
      polylines: [...svg.querySelectorAll("path")].filter((node) => !/C/.test(node.getAttribute("d") || "")).length,
      legend: [...svg.querySelectorAll("text")]
        .filter((node) => Number(node.getAttribute("font-size")) >= 15).length,
    })));
  check(gallery.length === 6, `Fig. 5 draws ${gallery.length} panels, expected six`);
  check(gallery.every((panel) => panel.x && panel.y), "a Fig. 5 panel does not name both axes");
  check(gallery.every((panel) => panel.polylines === 0), "a Fig. 5 panel draws a polyline");
  check(gallery.every((panel) => panel.legend >= 1), "a Fig. 5 panel has no 15 px legend");
  for (const name of ["c-0028-curve", "c-0028-remainder", "c-0029-curve", "c-0029-remainder",
    "c-0060-curve", "c-0060-remainder", "quadratic"]) {
    check(panels.some((panel) => panel.key === name), `Fig. 9 is missing the ${name} panel`);
  }
  for (const panel of panels) {
    check(panel.hasX && panel.hasY, `the ${panel.key} panel does not name both axes`);
    check(panel.legend >= 1, `the ${panel.key} panel has no legend at 15 px`);
    check(panel.polylines === 0, `the ${panel.key} panel draws ${panel.polylines} polylines, expected Bézier chains`);
    check(panel.bezier, `the ${panel.key} panel has no cubic Bézier path`);
  }

  // Fig. 9 — the circle taken out: every implementation prints its own exact error.
  // The page is already loaded (the second load above); wait for the table rather
  // than reload a page that has not changed, which a dev-server reload can abort.
  await page.waitForSelector("#pm-circle-split", { timeout: 10000 }).catch(() => {});
  const splitRows = await page.evaluate(() => {
    const table = document.getElementById("pm-circle-split");
    if (!table) return null;
    return [...table.querySelectorAll("tbody tr")].map((row) =>
      [...row.querySelectorAll("td")].map((cell) => cell.textContent.trim()));
  });
  check(Boolean(splitRows), "Fig. 9, the circle taken out, is not on the page");
  if (splitRows) {
    check(splitRows.length >= 10, `Fig. 9 has ${splitRows.length} rows, expected the four ways`);
    const bad = splitRows.filter((cells) => cells[3] !== "0");
    check(bad.length === 0, `Fig. 9 has ${bad.length} rows whose identity is not exact`);
    check(splitRows.some((cells) => /lace/.test(cells[0])), "Fig. 9 does not cover the stored curves");
    check(splitRows.some((cells) => /quadratic/.test(cells[0])), "Fig. 9 does not cover the quadratic split");
  }

  // the heading carries the setting: pick another triple and read the headings
  // (the notes page was visited above, so come back to the page first)
  await gotoStable(page, `${BASE}/prime-mover/`, { waitUntil: "domcontentloaded", timeout: 90000 });
  await page.waitForTimeout(1500);
  const headingOf = () => page.evaluate(() =>
    ["pm-fig1-title", "pm-fig2-title", "pm-fig3-title", "pm-fig4-title"]
      .map((id) => document.getElementById(id)?.textContent || ""));
  const startHeadings = await headingOf();
  check(startHeadings.every((text) => /56,783,785/.test(text)),
    `the headings do not name the start triple: ${startHeadings[0]}`);
  await page.evaluate(() => {
    const chooser = document.getElementById("pm-triple");
    chooser.value = "3,4,5";
    chooser.dispatchEvent(new window.Event("change", { bubbles: true }));
  });
  await page.waitForTimeout(900);
  const movedHeadings = await headingOf();
  check(movedHeadings.every((text) => /3,4,5/.test(text)),
    `the headings did not follow the chooser: ${movedHeadings[0]}`);
  const movedHalf = await page.evaluate(() => document.getElementById("pm-half").checked);
  check(!movedHalf, "quadrants I and IV stayed ticked on a triple that is not thin");
} finally {
  await browser.close();
}

if (failures.length) {
  console.error("FAIL /prime-mover/");
  for (const failure of failures) console.error(`  - ${failure}`);
  process.exit(1);
}
console.log("ok /prime-mover/ — the walk on the circle, exact stations, axes, the circle taken out, and the laws intact");
