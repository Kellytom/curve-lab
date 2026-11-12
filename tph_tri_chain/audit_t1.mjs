// Audit Fig. T1 with Playwright: measure the rendered label boxes, count
// overlaps, check the 25 vertex pairs against chain.py, and optionally write
// the PNG.
//
//   node tph_tri_chain/audit_t1.mjs
//   node tph_tri_chain/audit_t1.mjs --png tph_tri_chain/out/t1.png --width 980
//
// The boxes are SVG user units from getBBox(), so the count does not depend on
// the CSS size of the figure. The vertex pairs are re-derived from chain.py,
// which is the one source of truth for the data on the page.

import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath, pathToFileURL } from "node:url";
import { chromium } from "playwright-core";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.dirname(HERE);

const args = process.argv.slice(2);
const opt = (name, fallback = null) => {
  const i = args.indexOf(name);
  return i === -1 ? fallback : args[i + 1];
};
const url = opt("--url");
const png = opt("--png");
const width = Number(opt("--width", "980"));

// The page is plain HTML with relative scripts, so the file on disk renders the
// same as the served copy. Prefer the server when it is up; fall back to the
// file so the audit never depends on :8003 being started first.
const served = "http://127.0.0.1:8003/tph_tri_chain/tph-tri-sandbox.html";
let pageUrl = url;
if (!pageUrl) {
  try {
    const r = await fetch(served, { signal: AbortSignal.timeout(1500) });
    pageUrl = r.ok ? served : pathToFileURL(path.join(HERE, "tph-tri-sandbox.html")).href;
  } catch {
    pageUrl = pathToFileURL(path.join(HERE, "tph-tri-sandbox.html")).href;
  }
}

// ---------------------------------------------------------------- chain.py
const snippet = `
import sys, json
sys.path.insert(0, ${JSON.stringify(HERE)})
from fractions import Fraction as F
from sandbox import chain, grid, N
rows, _ = chain(F(0), F(3), N)
g = grid(rows)
x = y = F(0)
right = [[0, 0]]
for r in rows:
    x += r["dx"]; y += r["dy"]
    right.append([int(x * g), int(y * g)])
mirror = [[X, -Y] for X, Y in right]
print(json.dumps(list(reversed(mirror)) + right[1:]))
`;
const expected = JSON.parse(
  execFileSync(path.join(ROOT, ".venv/bin/python"), ["-c", snippet], {
    cwd: ROOT,
    encoding: "utf8",
  })
);

// ---------------------------------------------------------------- browser
// Keep one headless browser open on :9223 and attach to it. It is the
// headless-only binary, so no window or Dock icon appears; a check never
// launches a second Chrome. Falls back to launching the same shell once.
const CDP = "http://127.0.0.1:9223";
const SHELL = `${process.env.HOME}/.cache/puppeteer/chrome-headless-shell/mac-133.0.6943.98/chrome-headless-shell-mac-x64/chrome-headless-shell`;

let browser = null;
let launched = false;
try {
  const r = await fetch(`${CDP}/json/version`, { signal: AbortSignal.timeout(1200) });
  if (r.ok) browser = await chromium.connectOverCDP(CDP);
} catch {}
if (!browser) {
  const exe = [process.env.CHROME_PATH, SHELL].filter(Boolean).find((f) => fs.existsSync(f));
  if (!exe) {
    console.error("no headless Chrome found");
    process.exit(1);
  }
  browser = await chromium.launch({ executablePath: exe, headless: true });
  launched = true;
}
const context = browser.contexts()[0] || (await browser.newContext());

const page = await context.newPage();
await page.setViewportSize({ width: width + 80, height: 1200 });
await page.goto(pageUrl, { waitUntil: "load", timeout: 20000 });
await page.waitForSelector("#t1 svg");

const shot = await page.evaluate((targetWidth) => {
  const svg = document.querySelector("#t1 svg");
  const box = (el) => {
    const b = el.getBBox();
    // getScreenCTM is in CSS px; the difference gives user units, so the count
    // does not move when the page is resized or the PNG width changes.
    const m = svg.getScreenCTM().inverse().multiply(el.getScreenCTM());
    const pts = [
      [b.x, b.y],
      [b.x + b.width, b.y],
      [b.x, b.y + b.height],
      [b.x + b.width, b.y + b.height],
    ].map(([px, py]) => new DOMPoint(px, py).matrixTransform(m));
    const xs = pts.map((p) => p.x);
    const ys = pts.map((p) => p.y);
    return {
      x: Math.min(...xs),
      y: Math.min(...ys),
      w: Math.max(...xs) - Math.min(...xs),
      h: Math.max(...ys) - Math.min(...ys),
    };
  };
  const texts = [...svg.querySelectorAll("text")];
  const pair = /^\(\s*-?\d+,\s*-?\d+\s*\)$/;
  const letter = /^[A-D]$/;  const labels = texts
    .filter((el) => pair.test(el.textContent.trim()))
    .map((el) => ({ i: +el.dataset.i, text: el.textContent.trim(), box: box(el) }));
  const hits = texts
    .filter((el) => letter.test(el.textContent.trim()))
    .map((el) => ({ text: el.textContent.trim(), box: box(el) }));
  const rings = [...svg.querySelectorAll("circle.hitring")].map((el) => {
    const b = box(el);
    return { x: b.x - 1, y: b.y - 1, w: b.w + 2, h: b.h + 2 };
  });
  svg.style.width = `${targetWidth}px`;
  svg.style.height = "auto";
  const rect = svg.getBoundingClientRect();
  return {
    labels,
    hits,
    rings,
    all: texts
      .filter((el) => el.textContent.trim())
      .map((el) => ({ t: el.textContent.trim(), box: box(el) })),
    verts: T1.verts,
    leaders: svg.querySelectorAll("g.leaders line").length,
    size: [Math.round(rect.width), Math.round(rect.height)],
    viewBox: (svg.getAttribute("viewBox") || "").split(/\s+/).map(Number).slice(2),
  };
}, width);

// ---------------------------------------------------------------- audit
const overlap = (a, b) => {
  const w = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x);
  const h = Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y);
  return w > 0 && h > 0 ? { w, h } : null;
};

const bad = [];
for (let i = 0; i < shot.labels.length; i++) {
  for (let j = i + 1; j < shot.labels.length; j++) {
    const o = overlap(shot.labels[i].box, shot.labels[j].box);
    if (o) bad.push({ a: shot.labels[i], b: shot.labels[j], o });
  }
}

console.log(`Fig. T1 — ${shot.labels.length} vertex labels, ${shot.hits.length} hit letters`);
console.log(`label boxes: ${bad.length} overlapping pairs (${shot.leaders} leader lines)`);
for (const { a, b, o } of bad) {
  console.log(
    `  ${a.text} (i=${a.i}) x ${b.text} (i=${b.i}) — overlap ${o.w.toFixed(1)} x ${o.h.toFixed(1)} px`
  );
}

const letterBad = [];
for (const h of shot.hits) {
  for (const l of shot.labels) {
    const o = overlap(h.box, l.box);
    if (o) letterBad.push(`${h.text} x ${l.text} (${o.w.toFixed(1)}x${o.h.toFixed(1)})`);
  }
  for (const r of shot.rings) {
    const o = overlap(h.box, r);
    if (o) letterBad.push(`${h.text} x its ring (${o.w.toFixed(1)}x${o.h.toFixed(1)})`);
  }
}
console.log(`hit letters vs labels/rings: ${letterBad.length} overlaps`);
for (const s of letterBad) console.log(`  ${s}`);

const same =
  shot.verts.length === expected.length &&
  shot.verts.every((p, i) => p[0] === expected[i][0] && p[1] === expected[i][1]);
console.log(
  `vertex pairs: ${same ? "25/25 match chain.py" : "MISMATCH"} ` +
    `(${shot.verts.length} on the page, ${expected.length} from chain.py)`
);
if (!same) {
  shot.verts.forEach((p, i) => {
    const e = expected[i];
    if (!e || p[0] !== e[0] || p[1] !== e[1]) console.log(`  i=${i}: page ${p} vs chain.py ${e}`);
  });
}

// every text box against every other: labels must not sit on ticks, the
// legend, the title, or each other.
const textBad = [];
for (let i = 0; i < shot.all.length; i++) {
  for (let j = i + 1; j < shot.all.length; j++) {
    const o = overlap(shot.all[i].box, shot.all[j].box);
    if (o) textBad.push(`${shot.all[i].t} x ${shot.all[j].t} (${o.w.toFixed(1)}x${o.h.toFixed(1)})`);
  }
}
console.log(`all text boxes: ${textBad.length} overlapping pairs`);
for (const s of textBad) console.log(`  ${s}`);

const outside = shot.all.filter(
  ({ box: b }) => b.x < 0 || b.y < 0 || b.x + b.w > shot.viewBox[0] || b.y + b.h > shot.viewBox[1]
);
console.log(`text boxes outside the figure: ${outside.length}`);
for (const { t, box: b } of outside) {
  console.log(`  ${t} at (${b.x.toFixed(1)}, ${b.y.toFixed(1)}) ${b.w.toFixed(1)}x${b.h.toFixed(1)}`);
}

if (png) {
  await page.locator("#t1 svg").screenshot({ path: png });
  const bytes = fs.statSync(png).size;
  console.log(`png: ${png} ${shot.size[0]}x${shot.size[1]} ${(bytes / 1024).toFixed(1)} KB`);
}

await page.close();
if (launched) await browser.close();
process.exit(bad.length === 0 && same ? 0 : 1);
