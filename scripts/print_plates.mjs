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

import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { chromium } from "playwright-core";
import { setDpi } from "./lib/png-dpi.mjs";

const ROOT = path.resolve(import.meta.dirname, "..");
const OUT = path.join(ROOT, "book", "print");
mkdirSync(OUT, { recursive: true });

const PLATE = (await import(path.join(ROOT, "workbench", "plate_math.js"))).default
  || (await import(path.join(ROOT, "workbench", "plate_math.js")));

const registry = JSON.parse(readFileSync(path.join(ROOT, "workbench", "curve-registry.json"), "utf8"));
const notes = JSON.parse(readFileSync(path.join(ROOT, "workbench", "curve-notes.json"), "utf8"));
const noteOf = new Map((notes.curves || []).map((row) => [row.uid, row]));

const LONG_SIDE = 3000;
const STROKE = 0.0035;                // 3.5/1000 of the long side, the book rule
const LEFT = "#2b2b2b";               // the darker tone
const RIGHT = "#8d8d8d";              // the lighter tone

const args = process.argv.slice(2);
const only = (() => {
  const at = args.indexOf("--only");
  return at >= 0 ? new Set(args[at + 1].split(",")) : null;
})();
const missing = args.includes("--missing");

function rowFor(record) {
  const note = noteOf.get(record.uid) || {};
  return {
    name: record.name,
    speedX: record.speedX || [],
    speedY: record.speedY || [],
    width: { percent: note.width_pct ?? note.widthPct ?? 0 },
    character: {
      plus: note.plus ?? 0, minus: note.minus ?? 0,
      profile: note.profile || undefined,
    },
  };
}

function turn(points, degrees) {
  if (!degrees) return points;
  const a = (degrees * Math.PI) / 180, c = Math.cos(a), s = Math.sin(a);
  return points.map(([x, y]) => [x * c - y * s, x * s + y * c]);
}

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
  const row = rowFor(record);
  const degrees = Number(record.transform?.degrees || 0);
  let spine;
  let rails = [];
  if (record.kind === "path" && Array.isArray(record.path) && record.path.length > 2) {
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
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
  for (const [x, y] of all) {
    if (x < x0) x0 = x; if (x > x1) x1 = x;
    if (y < y0) y0 = y; if (y > y1) y1 = y;
  }
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
  const line = (points, colour, width) => points.length < 2 ? "" :
    `<polyline points="${points.map((p) => px(p).map((v) => v.toFixed(2)).join(",")).join(" ")}" ` +
    `fill="none" stroke="${colour}" stroke-width="${width.toFixed(2)}" ` +
    `stroke-linecap="round" stroke-linejoin="round"/>`;

  const stroke = Math.max(1, STROKE * LONG_SIDE);
  // two tones without cutting the line: the whole spine is dark, then the same spine is
  // drawn again in the light tone inside a clip over x ≥ 0
  // the split is the figure's own centre line, so both tones always appear; a curve whose
  // centre is the y axis is split there
  const axisX = (x0 + x1) / 2;
  const axis = px([axisX, 0])[0].toFixed(2);
  const body = [
    `<rect width="${pxW}" height="${pxH}" fill="#ffffff"/>`,
    ...rails.map((rail) => line(rail, "#c4c4c4", stroke * 0.7)),
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
  const svgPath = path.join(OUT, `${record.uid}.svg`);
  const pngPath = path.join(OUT, `${record.uid}.png`);
  writeFileSync(svgPath, svg);
  await page.setViewportSize({ width: pxW, height: pxH });
  await page.setContent(`<body style="margin:0;background:#fff">${svg}</body>`);
  await page.screenshot({ path: pngPath, clip: { x: 0, y: 0, width: pxW, height: pxH } });
  setDpi(pngPath, 300);
  done += 1;
  if (done <= 12 || done % 50 === 0) {
    console.log(`${record.uid.padEnd(8)} ${record.name.slice(0, 26).padEnd(26)} ` +
      `turn ${String(degrees).padStart(3)}°  ${pxW}×${pxH}  rails ${rails}`);
  }
}
await browser.close();
console.log(`${done} plates written to book/print at ${LONG_SIDE} px, 300 dpi`);
