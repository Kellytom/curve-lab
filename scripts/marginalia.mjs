// Marginalia: every curve as an ornament, at a quarter of the text width.
//
//   node scripts/marginalia.mjs
//
// One single-stroke SVG per registry curve, the spine only (no character rails), drawn with
// currentColor and a non-scaling stroke so it holds at any size. The manifest records the
// natural box, so the theme can say "a quarter of the column" and the gallery can go four-up.
//
// The SVGs are generated output and gitignored; the manifest is tracked so the theme and its
// test know the set without drawing it. Model y is up; the SVG flip happens here.

import { createRequire } from "node:module";
import { mkdirSync, readFileSync, readdirSync, rmSync } from "node:fs";
import path from "node:path";
import { writeIfChanged } from "./lib/write-if-changed.mjs";

const require = createRequire(import.meta.url);
const P = require("../workbench/plate_math.js");

const ROOT = path.resolve(import.meta.dirname, "..");
const OUT = path.join(ROOT, "app", "public", "ornaments");
const MANIFEST = path.join(ROOT, "app", "src", "theme", "marginalia", "ornaments.json");
const SCALE = 0.25;

const registry = JSON.parse(readFileSync(path.join(ROOT, "workbench", "curve-registry.json"), "utf8"));
// the star values live in the database export, not the seed
const starsOf = new Map();
try {
  const exported = JSON.parse(readFileSync(path.join(ROOT, "data", "curves.json"), "utf8"));
  for (const row of exported.rows || []) starsOf.set(row.uid, row.stars ?? null);
} catch { /* the manifest falls back to the seed's importance */ }
mkdirSync(OUT, { recursive: true });
mkdirSync(path.dirname(MANIFEST), { recursive: true });

const spineOf = (record) => {
  if (record.speedX?.length || record.speedY?.length) {
    return P.spine(record.speedX || [0], record.speedY || [0], 260).map((s) => [s.x, s.y]);
  }
  if (!record.path?.length) return [];
  const [x0, y0, x1, y1] = P.bbox(record.path);
  const size = Math.hypot(x1 - x0, y1 - y0) || 1;
  return P.refinePath(record.path, size / 500);
};

// Write only when the bytes change. The dev server watches this folder, and the launch
// agent re-runs `npm run dev` on a loop, so an unconditional write reloaded every page
// every ten seconds (2026-11-22, the operator: "the page keeps refreshing constantly").
// The rule lives in scripts/lib/write-if-changed.mjs with its own test.
let written = 0;
let unchanged = 0;
const write = (file, text) => {
  if (writeIfChanged(file, text)) written += 1; else unchanged += 1;
};

const manifest = [];
let drawn = 0;
for (const record of registry.curves) {
  const points = spineOf(record);
  if (points.length < 2) continue;
  const [x0, y0, x1, y1] = P.bbox(points);
  // A pixel-scale viewBox (long side 640) so the dot dash is a length in the drawing's own
  // pixels, not in model units. The stroke is non-scaling, so it holds at every use.
  const LONG = 640;
  const k = LONG / (Math.max(x1 - x0, y1 - y0) || 1);
  const pad = 6;
  const flip = y0 + y1;
  const d = points
    .map(([x, y], i) => `${i ? "L" : "M"}${((x - x0) * k + pad).toFixed(1)},${((flip - y - y0) * k + pad).toFixed(1)}`)
    .join("");
  const width = (x1 - x0) * k + 2 * pad;
  const height = (y1 - y0) * k + 2 * pad;
  // Overlapping dots, no Béziers: a zero-length dash with a round cap, spaced closer than
  // the dot diameter. The line reads as one soft stroke.
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width.toFixed(1)} ${height.toFixed(1)}" ` +
    `role="presentation" aria-hidden="true"><path d="${d}" fill="none" stroke="currentColor" ` +
    `stroke-width="2.2" vector-effect="non-scaling-stroke" stroke-linecap="round" ` +
    `stroke-dasharray="0.02 1.35"/></svg>\n`;
  write(path.join(OUT, `${record.uid}.svg`), svg);
  manifest.push({
    uid: record.uid,
    name: record.name,
    family: record.family_id || record.family || "",
    stars: starsOf.get(record.uid) ?? record.importance ?? null,
    file: `/ornaments/${record.uid}.svg`,
    width: Number(width.toFixed(4)),
    height: Number(height.toFixed(4)),
  });
  drawn += 1;
}

write(MANIFEST, `${JSON.stringify({
  format: "curve-lab.marginalia/1",
  note: "One soft-stroke ornament per curve (overlapping dots, no Béziers). Displayed at a quarter of the text width; " +
    "the SVGs are generated and gitignored, the manifest is the record.",
  scale: SCALE,
  count: manifest.length,
  curves: manifest,
}, null, 1)}\n`);
console.log(`${drawn} ornaments checked; ${written} written, ${unchanged} unchanged; manifest at ` +
  `${path.relative(ROOT, MANIFEST)} · scale ${SCALE}`);

// A curve that left the registry leaves its ornament behind unless it is removed here.
const keep = new Set(manifest.map((row) => `${row.uid}.svg`));
let removed = 0;
for (const file of readdirSync(OUT)) {
  if (file.endsWith(".svg") && !keep.has(file)) { rmSync(path.join(OUT, file)); removed += 1; }
}
if (removed) console.log(`${removed} stale ornament(s) removed`);
