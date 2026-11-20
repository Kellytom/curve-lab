// Sweep every sensible combination of the prime-mover builder, in a real browser,
// and report which produce a visible curve rather than a runaway spiral.
//
//   node scripts/sweep_prime_mover.mjs            # print the table
//   node scripts/sweep_prime_mover.mjs --write    # keep the winners
//
// The page always fits the drawing to its own bbox, so "invisible" does not mean
// off-screen: it means one far station dominates the scale and the rest of the
// curve becomes a speck. The test is therefore concentration — the extent of the
// middle 80% of the stations compared with the full extent. A curve whose middle
// is under a quarter of its span is a runaway, whatever it looks like on paper.

import { writeFileSync } from "node:fs";
import path from "node:path";
import { chromium } from "playwright-core";

const ROOT = path.resolve(import.meta.dirname, "..");
const FACTORS = ["2+i", "3+2i", "3+4i", "5+2i"];
const STEPS = [3, 5, 7, 10];
const LAGS = [0, 27, 90, 180];
const DAMPERS = [100, 80, 60];
const ONSETS = [0, 2];

const browser = await chromium.launch({
  executablePath: process.env.CHROME_PATH || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
});
const page = await browser.newPage({ viewport: { width: 1200, height: 900 } });
await page.goto(process.env.CURVE_LAB_URL || "http://127.0.0.1:4321/sandbox/", { waitUntil: "load" });
await page.waitForTimeout(600);

async function apply(settings) {
  return page.evaluate((values) => {
    const set = (id, value) => {
      const element = document.getElementById(id);
      element.value = value;
      element.dispatchEvent(new Event("input", { bubbles: true }));
    };
    set("pm-factor", values.factor);
    set("pm-steps", values.steps);
    set("pm-lag", values.lag);
    set("pm-damp", values.damper);
    set("pm-damp-lag", values.onset);
    const pathElement = document.querySelector("#pm-plot path");
    return pathElement ? pathElement.getAttribute("d") : "";
  }, settings);
}

function pointsOf(d) {
  return (d.match(/-?\d+(\.\d+)?,-?\d+(\.\d+)?/g) || []).map((pair) => pair.split(",").map(Number));
}

function crossings(points) {
  const seen = new Set();
  for (let i = 0; i < points.length - 1; i += 1) {
    const [ax, ay] = points[i];
    const [bx, by] = points[i + 1];
    for (let j = i + 2; j < points.length - 1; j += 1) {
      const [cx, cy] = points[j];
      const [dx, dy] = points[j + 1];
      const den = (bx - ax) * (dy - cy) - (by - ay) * (dx - cx);
      if (Math.abs(den) < 1e-12) continue;
      const s = ((cx - ax) * (dy - cy) - (cy - ay) * (dx - cx)) / den;
      const w = ((cx - ax) * (by - ay) - (cy - ay) * (bx - ax)) / den;
      if (s > 0 && s < 1 && w > 0 && w < 1) seen.add(`${Math.round(ax + (bx - ax) * s)}:${Math.round(ay + (by - ay) * s)}`);
    }
  }
  return seen.size;
}

function concentration(points) {
  if (points.length < 4) return 0;
  const xs = points.map((p) => p[0]).sort((a, b) => a - b);
  const ys = points.map((p) => p[1]).sort((a, b) => a - b);
  const span = Math.max(xs.at(-1) - xs[0], ys.at(-1) - ys[0]) || 1;
  const lo = Math.floor(points.length * 0.1);
  const hi = Math.ceil(points.length * 0.9);
  const middle = points.slice(lo, hi);
  const mxs = middle.map((p) => p[0]);
  const mys = middle.map((p) => p[1]);
  const middleSpan = Math.max(Math.max(...mxs) - Math.min(...mxs), Math.max(...mys) - Math.min(...mys)) || 0;
  return middleSpan / span;
}

const rows = [];
for (const factor of FACTORS) {
  for (const steps of STEPS) {
    for (const lag of LAGS) {
      for (const damper of DAMPERS) {
        for (const onset of ONSETS) {
          if (onset >= steps) continue;
          const d = await apply({ factor, steps, lag, damper, onset });
          const points = pointsOf(d);
          if (points.length < 3) continue;
          rows.push({
            factor, steps, lag, damper, onset,
            points: points.length,
            crossings: crossings(points),
            concentration: Math.round(concentration(points) * 100) / 100,
          });
        }
      }
    }
  }
}
await browser.close();

const visible = rows.filter((row) => row.concentration >= 0.25);
const interesting = visible.filter((row) => row.crossings >= 1);
console.log(`${rows.length} combinations · ${visible.length} stay concentrated (middle ≥ 25% of the span) · ${interesting.length} also cross themselves`);
for (const row of interesting.sort((a, b) => b.crossings - a.crossings).slice(0, 12)) {
  console.log(`  ${row.factor.padEnd(5)} steps ${String(row.steps).padStart(2)} · lag ${String(row.lag).padStart(3)}° · damper ${row.damper}% from ${row.onset} → ${row.crossings} crossings · concentration ${row.concentration}`);
}
const worst = rows.filter((row) => row.concentration < 0.25).slice(0, 5);
if (worst.length) {
  console.log("runaway examples:");
  for (const row of worst) console.log(`  ${row.factor} steps ${row.steps} lag ${row.lag} damper ${row.damper} from ${row.onset} → concentration ${row.concentration}`);
}

if (process.argv.includes("--write")) {
  writeFileSync(path.join(ROOT, "workbench", "prime-mover-sweep.json"), JSON.stringify({
    format: "curve-lab.prime-mover-sweep/1",
    note: "every builder combination, written from a real browser; concentration = middle 80% of the stations over the full span",
    combinations: rows,
  }, null, 1) + "\n");
  console.log("wrote workbench/prime-mover-sweep.json");
}
