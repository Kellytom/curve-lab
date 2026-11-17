// Export the saved curves from the sandbox seed to one data file.
//
//   node scripts/real_curves.mjs
//
// The seed is the operator's kept set: 27 curves, each a PH speed pair, with
// the character data the page uses (plus/minus/profile) kept for later. The
// `×` in the operator's copy of the list was the UI's dismiss button, so the
// crossed-out curves are not here.

import { readFileSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const PlateMath = require("../workbench/plate_math.js");

const SOURCE = "workbench/ph_nth_panels.js";
const OUT = "workbench/real-curves.json";

const text = readFileSync(SOURCE, "utf8");
const open = text.indexOf("[", text.indexOf("const SEED = ["));
if (open < 0) throw new Error("no SEED array in " + SOURCE);

let depth = 0;
let end = -1;
let inString = false;
let quote = "";
for (let i = open; i < text.length; i += 1) {
  const c = text[i];
  if (inString) {
    if (c === "\\") { i += 1; continue; }
    if (c === quote) inString = false;
    continue;
  }
  if (c === '"' || c === "'" || c === "`") { inString = true; quote = c; continue; }
  if (c === "[") depth += 1;
  if (c === "]") {
    depth -= 1;
    if (depth === 0) { end = i + 1; break; }
  }
}
if (end < 0) throw new Error("the SEED array is not closed");

const seed = eval("(" + text.slice(open, end) + ")");
// One curve we made here, not from the sandbox: u = 1, v = (2t − 1)². Both
// speeds are even about t = 1/2, so it is a half turn about its midpoint, with
// a horizontal tangent there (grid 15, station (0, 5)).
const made = [{ name: "new-symmetric", speedX: [1], speedY: [1, -4, 4],
                from: "new" }];

// The found set stores terms (power, x, y); turn them into speed rows.
const foundData = JSON.parse(readFileSync("workbench/found-curves.json", "utf8"));
const rows = seed.map((row) => ({ ...row, source: "seed" }))
  .concat(made.map((row) => ({ ...row, source: "new" })));
const seen = new Set(rows.map((row) => row.name));
for (const row of foundData.curves) {
  if (seen.has(row.name)) continue;
  const top = Math.max(...row.terms.map((term) => term.power));
  const speedX = new Array(top + 1).fill(0);
  const speedY = new Array(top + 1).fill(0);
  row.terms.forEach((term) => {
    speedX[term.power] = term.x;
    speedY[term.power] = term.y;
  });
  rows.push({ name: row.name, speedX, speedY, source: "found",
              found: row.measured });
  seen.add(row.name);
}

const curves = rows.map((row) => {
  const symmetry = PlateMath.symmetry({ speedX: row.speedX, speedY: row.speedY });
  const category = row.source === "found"
    ? (symmetry.symmetric ? "symmetric" : "asymmetric")
    : (["u-bowl", "wave-coarse"].includes(row.name) ? "symmetric" : "asymmetric");
  return {
  name: row.name,
  speedX: row.speedX,
  speedY: row.speedY,
  ...(row.width ? { width: row.width } : {}),
  ...(row.character ? { character: row.character } : {}),
  ...(row.shear !== undefined ? { shear: row.shear } : {}),
  ...(row.hook ? { hook: row.hook } : {}),
  ...(row.source ? { source: row.source } : {}),
  ...(row.found ? { found: row.found } : {}),
  symmetry, category,
  };
});

const data = {
  format: "real-curves/1",
  note: "The operator's kept set from the sandbox seed. Speed rows are the PH pair (u, v); character data is kept for the later rails.",
  count: curves.length,
  curves,
};
writeFileSync(OUT, JSON.stringify(data, null, 1) + "\n");
console.log(`${OUT}: ${curves.length} curves`);
