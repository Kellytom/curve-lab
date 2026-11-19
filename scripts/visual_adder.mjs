// A visual curve adder: each term as its own figure, three across, then the sum.
//
//   node scripts/visual_adder.mjs                 # y = x - x^3 + x^5 - x^7
//   node scripts/visual_adder.mjs --open          # ...and open it
//
// The page is generated, never edited: workbench/adder.html. Each tile is a
// term `c·x^p` drawn over the same window, so the eye compares like with like;
// the last tile is the sum, larger, at the same scale.
//
// Why it is worth having: a polynomial's shape is the sum of its terms, and
// nobody can see that in one formula. Three across is small enough to read and
// large enough to label.

import { execFileSync } from "node:child_process";
import { writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

const WINDOW = 1.25;          // x runs -WINDOW..WINDOW
const TILE = 320;
const BIG = 760;
const SAMPLES = 240;

function termsOf(text) {
  // "x - x^3 + x^5 - x^7" -> [{c: 1, p: 1}, {c: -1, p: 3}, ...]
  const terms = [];
  const cleaned = String(text).replace(/\s+/g, "").replace(/-/g, "+-");
  for (const part of cleaned.split("+")) {
    if (!part) continue;
    const match = part.match(/^(-?\d*\.?\d*)?\*?x(?:\^(-?\d+))?$/);
    if (!match) continue;
    const raw = match[1];
    // "x" and "+x" mean 1: an omitted coefficient is one, not NaN.
    const coef = raw === undefined || raw === "" || raw === "+"
      ? 1
      : raw === "-" ? -1 : Number(raw);
    if (!Number.isFinite(coef)) continue;
    terms.push({ c: coef, p: Math.abs(Number(match[2] ?? 1)) });
  }
  return terms;
}

const value = (terms, x) => terms.reduce((sum, t) => sum + t.c * x ** t.p, 0);

function label(term) {
  const sign = term.c < 0 ? "−" : "";
  const size = Math.abs(term.c) === 1 ? "" : String(Math.abs(term.c));
  return `${sign}${size}x${term.p === 1 ? "" : `^${term.p}`}`;
}

function tileSvg({ caption, terms, note, size = TILE }) {
  const xs = Array.from({ length: SAMPLES }, (_, i) =>
    -WINDOW + (2 * WINDOW * i) / (SAMPLES - 1));
  const ys = xs.map((x) => value(terms, x));
  const top = Math.max(1, ...ys.map((y) => Math.abs(y)));
  const pad = 26;
  const sx = (x) => pad + ((x + WINDOW) / (2 * WINDOW)) * (size - 2 * pad);
  const sy = (y) => size - pad - ((y + top) / (2 * top)) * (size - 2 * pad);
  const d = xs.map((x, i) => `${i ? "L" : "M"}${sx(x).toFixed(1)},${sy(ys[i]).toFixed(1)}`).join("");
  const axis = `stroke="#b9a98a" stroke-width="1"`;
  return `<figure class="tile">
  <svg viewBox="0 0 ${size} ${size}" role="img" aria-label="${caption}">
    <rect width="${size}" height="${size}" fill="#fffdf7"/>
    <line x1="${pad}" y1="${sy(0)}" x2="${size - pad}" y2="${sy(0)}" ${axis}/>
    <line x1="${sx(0)}" y1="${pad}" x2="${sx(0)}" y2="${size - pad}" ${axis}/>
    <path d="${d}" fill="none" stroke="#141414" stroke-width="1.6" stroke-linejoin="round"/>
    <text x="${pad}" y="${pad - 8}" font-family="ui-monospace,Menlo,monospace" font-size="13" fill="#8c6a21">${caption}</text>
  </svg>
  <figcaption>${note}</figcaption>
</figure>`;
}

const expression = process.argv.find((arg) => arg.startsWith("--terms="))?.slice(8)
  || "x - x^3 + x^5 - x^7";
const terms = termsOf(expression);
if (!terms.length) {
  console.error(`could not read a sum of terms from: ${expression}`);
  process.exit(1);
}

const tiles = terms.map((term) => tileSvg({
  caption: label(term),
  terms: [term],
  note: `the term ${label(term)} alone`,
}));
const result = tileSvg({
  caption: "the sum",
  terms,
  note: `${expression} — all ${terms.length} terms added`,
  size: BIG,
});

// Three across, with a plus between terms; a row that is followed by another
// ends with the plus, so the sum reads as one line of typing.
const rows = [];
for (let i = 0; i < tiles.length; i += 3) {
  const row = tiles.slice(i, i + 3);
  const parts = [];
  row.forEach((tile, index) => {
    parts.push(tile);
    if (index < row.length - 1) parts.push('<div class="plus">+</div>');
  });
  if (i + 3 < tiles.length) parts.push('<div class="plus">+</div>');
  rows.push(`<div class="row">${parts.join("")}</div>`);
}
const sumRow = `<div class="row sum"><div class="plus">=</div>${result}</div>`;

const page = `<!doctype html>
<html lang="en" data-theme="light"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Visual curve adder: draft A</title>
<link rel="stylesheet" href="/vendor/pico.min.css">
<link rel="stylesheet" href="/vendor/curve-lab-theme.css">
<link rel="stylesheet" href="/vendor/app-shell.css">
<style>
body{padding:18px;background:#f6f1e4}
h1{font-size:20px;margin:0 0 4px}
p.lead{color:#7b6c4e;margin:0 0 18px}
.row{display:flex;flex-wrap:wrap;align-items:center;gap:10px;margin:0 0 14px}
.tile{margin:0;background:#fffdf7;border:1px solid #d8ccae}
.tile svg{display:block;width:${TILE}px;height:${TILE}px}
.tile figcaption{font:11px/1.5 ui-monospace,Menlo,monospace;color:#7b6c4e;padding:6px 8px;border-top:1px solid #e2d8bf}
.plus{font:700 26px/1 Georgia,serif;color:#8c6a21;padding:0 6px}
.sum{align-items:flex-start;margin-top:22px;padding-top:18px;border-top:1px solid #d8ccae}
.sum .tile svg{width:${BIG}px;height:${BIG}px}
</style>
</head><body>
<div class="draft-a" style="position:fixed;right:.75rem;bottom:.75rem;z-index:9999;background:#1b1b1b;color:#fff;font:12px/1.4 system-ui,sans-serif;padding:.35rem .6rem;border-radius:.25rem;opacity:.9">draft A</div>
<h1>Adding curves, term by term</h1>
<p class="lead">${expression} — each term drawn alone over the same window,
then the sum. Same scale in every figure, so the comparison is honest.</p>
${rows.join("\n")}
${sumRow}
</body></html>
`;

writeFileSync(path.join(ROOT, "workbench", "adder.html"), page);
console.log(`wrote workbench/adder.html · ${terms.length} terms · ${expression}`);

if (process.argv.includes("--open")) {
  execFileSync("open", [path.join(ROOT, "workbench", "adder.html")]);
}
