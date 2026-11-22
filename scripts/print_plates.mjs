// Print plates: white ground, 300 dpi, two grey tones, turned as the record says.
//
//   node scripts/print_plates.mjs --only c-0273,c-0290
//   node scripts/print_plates.mjs --all
//
// For each record: the spine (or the stored path) is turned by the record's `transform`,
// split at the vertical axis, and the two halves are drawn in two greys — one tone left,
// one tone right — so a two-colour press can tell them apart. Character rails are drawn
// from the record's own width, plus and minus when it has rows to build them from.
//
// Writes book/print/<uid>.svg and <uid>.png (long side 3000 px, 300 dpi).

import { existsSync, mkdirSync, readdirSync, readFileSync, renameSync, rmSync, writeFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import path from "node:path";
import { chromium } from "playwright-core";
import { setDpi } from "./lib/png-dpi.mjs";
import { turn, frame as frameFor } from "./lib/plate-frame.mjs";
import { rowFor as plateRow } from "./lib/plate-row.mjs";

// d3 does the geometry: the extents and the line generator. It is a dependency the app
// already carries (app/node_modules), so the plate uses the same library as the pages.
const d3 = await import(new URL("../app/node_modules/d3/dist/d3.mjs", import.meta.url).href);

const ROOT = path.resolve(import.meta.dirname, "..");
const OUT = path.join(ROOT, "book", "print");
const WEB = path.join(ROOT, "app", "public", "plates-web");
mkdirSync(OUT, { recursive: true });
mkdirSync(WEB, { recursive: true });

// The web copy: PNG at 1600 px. PNG is the one format that opens everywhere — LibreOffice,
// Pages, Word, a browser, a print shop — so the copy in git is a PNG too, not WebP. It is
// about three times the WebP and worth it: a picture nobody can place in a document is not
// preserved.
// The screenshot arrives as RGBA with three identical channels: the two greys are stored
// three times over. Rewrite it as grey + alpha — half the bytes, the same picture, and the
// `grey` in the file name becomes true.
function greyAlpha(file) {
  const temp = file.replace(/\.png$/, ".grey.png");
  try {
    execFileSync("sips", ["--matchTo", "/System/Library/ColorSync/Profiles/Generic Gray Profile.icc",
      file, "--out", temp], { stdio: "ignore" });
    renameSync(temp, file);
  } catch { rmSync(temp, { force: true }); }
}

const WEB_SIDE = 1600;
function webCopy(uid, png) {
  const small = path.join(WEB, `${uid}.tmp.png`);
  try {
    // resize, then drop to grey: the plate is grey on white, so an RGB PNG carries three
    // channels for one. Grey is about half the bytes and opens in every program.
    execFileSync("sips", ["-Z", String(WEB_SIDE), png, "--out", small], { stdio: "ignore" });
    execFileSync("sips", ["--matchTo", "/System/Library/ColorSync/Profiles/Generic Gray Profile.icc",
      small, "--out", path.join(WEB, `${uid}-${WEB_SIDE}-grey.png`)], { stdio: "ignore" });
  } catch { /* no sips: the 3000 px plate is still there */ }
  rmSync(small, { force: true });
}

const PLATE = (await import(path.join(ROOT, "workbench", "plate_math.js"))).default
  || (await import(path.join(ROOT, "workbench", "plate_math.js")));

const registry = JSON.parse(readFileSync(path.join(ROOT, "workbench", "curve-registry.json"), "utf8"));
// The saved values are the database's, exported to data/curves.json. The old
// workbench/curve-notes.json was a stale copy whose nulls fell through to the row
// preset, which is how the stored paths (c-0275..c-0368) gained a band they never
// asked for (2026-11-21).
const saved = JSON.parse(readFileSync(path.join(ROOT, "data", "curves.json"), "utf8"));
const noteOf = new Map((saved.rows || []).map((row) => [row.uid, row.note || {}]));
// The desk's decisions live in ONE copy: data/sandbox-curves.json (the database export).
// Reading the old workbench path in silence used the defaults for every curve, which is how
// character values stopped reaching the plates.
const DECISIONS = path.join(ROOT, "data", "sandbox-curves.json");
const decisionsRaw = existsSync(DECISIONS) ? JSON.parse(readFileSync(DECISIONS, "utf8")) : {};
const decisions = decisionsRaw.rows || decisionsRaw.curves || [];
if (!decisions.length) {
  console.log("WARNING: data/sandbox-curves.json is missing or empty — every plate will use " +
    "the defaults (1.5 %, plus 2, minus 2, bow). Run: node scripts/export-data.mjs");
}
const extra = new Map(decisions.map((row) => [row.uid || row.name, row]));

const LONG_SIDE = 3000;
const STROKE = 0.0035;                // 3.5/1000 of the long side, the book rule
const LEFT = "#2b2b2b";               // the stroke
const RIGHT = "#8d8d8d";              // the lighter stroke tone of the two-tone split
const LIGHT_BAND = "#e2e2e2";          // between the left rail and the spine
const DARK_BAND = "#8a8a8a";           // between the right rail and the spine

const args = process.argv.slice(2);
const only = (() => {
  const at = args.indexOf("--only");
  return at >= 0 ? new Set(args[at + 1].split(",")) : null;
})();
const missing = args.includes("--missing");
// one tone (a single black) or two (dark left, grey right); the brief asked for two
const toneArg = (args.find((a) => a.startsWith("--tone=")) || "--tone=two").split("=")[1];
const singleTone = toneArg === "one";

// the one law lives in scripts/lib/plate-row.mjs: note -> desk row -> defaults
const rowFor = (record, extra) => plateRow(record, {
  note: noteOf.get(record.uid) || {},
  desk: extra.get(record.uid) || extra.get((record.aliases || [])[0]) || {},
});

/** the polyline split where it crosses x = 0, both halves returned in order */
function halves(points) {
  const left = [], right = [];
  for (let i = 0; i < points.length - 1; i += 1) {
    const a = points[i], b = points[i + 1];
    const target = ((a[0] + b[0]) / 2) < 0 ? left : right;
    target.push(a);
    if ((a[0] >= 0) !== (b[0] >= 0)) {
      const t = a[0] / (a[0] - b[0]);
      const crossing = [0, a[1] + (b[1] - a[1]) * t];
      left.push(crossing); right.push(crossing);
    }
  }
  const last = points[points.length - 1];
  (last[0] < 0 ? left : right).push(last);
  return { left, right };
}

function plateSvg(record) {
  const row = rowFor(record, extra);
  const degrees = Number(record.transform?.degrees || 0);
  let spine;
  let rails = [];
  if (Array.isArray(record.path) && record.path.length > 2 && PLATE.pathGroup) {
    // a stored outline: the rails are built from the walk itself, same character law and
    // the same continuous fold cap as the page. A saved width draws the two bands; zero is
    // the clean two-tone spine.
    const group = PLATE.pathGroup(record.path, {
      widthPercent: row.width.percent, plus: row.character.plus,
      minus: row.character.minus, profile: row.character.profile,
    });
    if (group && group.paths.length) {
      spine = group.paths[0];
      rails = group.paths.slice(1);
    } else {
      spine = record.path.map(([x, y]) => [x, y]);
    }
  } else if (Array.isArray(record.path) && record.path.length > 2) {
    spine = record.path.map(([x, y]) => [x, y]);
  } else {
    // rails come from the polynomial; a row whose coefficients are too large for the
    // curvature routine falls back to the spine alone rather than failing the export
    let group = null;
    try { group = PLATE.group ? PLATE.group(row) : null; } catch { group = null; }
    if (group && group.paths && group.paths.length) {
      spine = group.paths[0];
      rails = group.paths.slice(1);
    } else {
      spine = PLATE.spine(row.speedX, row.speedY, 400).map((s) => [s.x, s.y]);
    }
  }
  spine = turn(spine, degrees);
  rails = rails.map((rail) => turn(rail, degrees));

  const all = [...spine, ...rails.flat()];
  const [x0, x1] = d3.extent(all, (p) => p[0]);
  const [y0, y1] = d3.extent(all, (p) => p[1]);
  const w = x1 - x0 || 1, h = y1 - y0 || 1;
  const long = Math.max(w, h);
  const margin = 0.012 * long;
  const boxW = w + 2 * margin, boxH = h + 2 * margin;
  const scale = LONG_SIDE / Math.max(boxW, boxH);      // the canvas long side is exactly 3000
  const pxW = Math.round(boxW * scale);
  const pxH = Math.round(boxH * scale);
  const k = scale;
  const ox = (pxW - w * k) / 2 - x0 * k;
  const oy = (pxH + h * k) / 2 + y0 * k;
  const px = ([x, y]) => [ox + x * k, oy - y * k];
  const gen = d3.line().x((p) => px(p)[0]).y((p) => px(p)[1]).curve(d3.curveLinear);
  const line = (points, colour, width) => points.length < 2 ? "" :
    `<path d="${gen(points)}" fill="none" stroke="${colour}" stroke-width="${width.toFixed(2)}" ` +
    `stroke-linecap="round" stroke-linejoin="round"/>`;

  const stroke = Math.max(1, STROKE * LONG_SIDE);
  // two tones without cutting the line: the whole spine is dark, then the same spine is
  // drawn again in the light tone inside a clip over x ≥ 0
  // the split is the figure's own centre line, so both tones always appear; a curve whose
  // centre is the y axis is split there
  const axisX = (x0 + x1) / 2;
  const axis = px([axisX, 0])[0].toFixed(2);
  // the bands: between each rail and the spine, filled. The right rail's band is the dark
  // grey, the left rail's the light one; the spine and the rails are then stroked on top.
  const band = (rail, fill) => (rail && rail.length > 2)
    ? `<path d="${gen([...spine, ...[...rail].reverse()])}Z" fill="${fill}" stroke="none"/>`
    : "";
  const bands = rails.length >= 2
    ? band(rails[0], LIGHT_BAND) + band(rails[1], DARK_BAND)
    : "";
  const body = singleTone
    ? [
        bands,
        ...rails.map((rail) => line(rail, "#3a3a3a", stroke * 0.6)),
        line(spine, LEFT, stroke),
      ].join("")
    : [
        bands,
        ...rails.map((rail) => line(rail, "#3a3a3a", stroke * 0.6)),
        line(spine, LEFT, stroke),
        `<clipPath id="right"><rect x="${axis}" y="0" width="${(pxW - Number(axis)).toFixed(2)}" height="${pxH}"/></clipPath>`,
        `<g clip-path="url(#right)">${line(spine, RIGHT, stroke)}</g>`,
      ].join("");
  return { svg: `<svg xmlns="http://www.w3.org/2000/svg" width="${pxW}" height="${pxH}" viewBox="0 0 ${pxW} ${pxH}">${body}</svg>`,
    pxW, pxH, degrees, rails: rails.length };
}

const records = registry.curves.filter((record) => {
  if (only && !only.has(record.uid)) return false;
  if (missing && existsSync(path.join(OUT, `${record.uid}.png`))) return false;
  return true;
});
const browser = await chromium.launch({
  executablePath: process.env.CHROME_PATH || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
});
const page = await browser.newPage();

let done = 0;
for (const record of records) {
  const { svg, pxW, pxH, degrees, rails } = plateSvg(record);
  // Naming: <uid>-<long side>-<tone>-<dpi>.<ext>. The size and tone are in the name so a
  // folder of renders can be read without opening one.
  const svgPath = path.join(OUT, `${record.uid}.svg`);
  const pngPath = path.join(OUT, `${record.uid}-${LONG_SIDE}-grey-300dpi.png`);
  writeFileSync(svgPath, svg);
  await page.setViewportSize({ width: pxW, height: pxH });
  // omitBackground keeps the alpha: what is not drawn is transparent, not white
  await page.setContent(`<body style="margin:0;background:transparent">${svg}</body>`);
  await page.screenshot({ path: pngPath, clip: { x: 0, y: 0, width: pxW, height: pxH },
    omitBackground: true });
  greyAlpha(pngPath);
  setDpi(pngPath, 300);
  webCopy(record.uid, pngPath);
  done += 1;
  if (done <= 12 || done % 50 === 0) {
    console.log(`${record.uid.padEnd(8)} ${record.name.slice(0, 26).padEnd(26)} ` +
      `turn ${String(degrees).padStart(3)}°  ${pxW}×${pxH}  rails ${rails}`);
  }
}
await browser.close();

// a plate is replaced, never duplicated: the expected names are known, so anything else in
// the folder is an orphan and is removed
const expected = new Set();
for (const record of registry.curves) {
  expected.add(`${record.uid}.svg`);
  expected.add(`${record.uid}-${LONG_SIDE}-grey-300dpi.png`);
}
let pruned = 0;
for (const file of readdirSync(OUT)) {
  if (expected.has(file)) continue;
  rmSync(path.join(OUT, file));
  pruned += 1;
}
console.log(`${done} plates written to book/print at ${LONG_SIDE} px, 300 dpi` +
  (pruned ? `; ${pruned} orphan files removed` : ""));
