// The clearance parity check: the TypeScript port vs the Python reference.
//   PATH="$HOME/node24/bin:$PATH" node app/scripts/parity-clearance.mjs
// Python dumps /tmp/py-clearance.json (groups, flatten, measure per piece);
// this script recomputes both from the same spans and diffs.

import { readFileSync } from "node:fs";
import { flatten, measure, segmentDistance } from "../src/lib/clearance.ts";

const dump = JSON.parse(readFileSync("/tmp/py-clearance.json", "utf8"));
let mismatches = 0; let checked = 0;

for (const piece of dump) {
  const groups = piece.groups;
  // 1. flattening, point for point, on the named rail group
  for (const [name, reference] of Object.entries(piece.flatten)) {
    const group = groups.find((g) => g.name === name);
    const mine = flatten(group.spans, 0.05);
    checked += 1;
    if (mine.length !== reference.length) {
      console.error(`${piece.piece}/${name} flatten: ${mine.length} points vs ${reference.length}`);
      mismatches += 1;
      continue;
    }
    for (let i = 0; i < mine.length; i += 1) {
      if (Math.abs(mine[i][0] - reference[i][0]) > 1e-9 ||
          Math.abs(mine[i][1] - reference[i][1]) > 1e-9) {
        console.error(`${piece.piece}/${name} flatten[${i}]: ${mine[i]} vs ${reference[i]}`);
        mismatches += 1;
        break;
      }
    }
  }
  // 2. the measured rule
  const mine = measure(groups, 5.0, 0.05);
  checked += 1;
  if (mine.ok !== piece.ok) {
    console.error(`${piece.piece}: ok ${mine.ok} vs ${piece.ok}`);
    mismatches += 1;
  }
  if ((mine.min?.distance ?? Infinity).toFixed(9) !== (piece.min?.distance ?? Infinity).toFixed(9)) {
    console.error(`${piece.piece}: min ${mine.min?.distance} vs ${piece.min?.distance}`);
    mismatches += 1;
  }
  if (mine.crossings.length !== piece.crossings.length) {
    console.error(`${piece.piece}: crossings ${mine.crossings.length} vs ${piece.crossings.length}`);
    mismatches += 1;
  }
  if (mine.violations.length !== piece.violations.length) {
    console.error(`${piece.piece}: violations ${mine.violations.length} vs ${piece.violations.length}`);
    mismatches += 1;
  }
}
console.log(`parity: ${checked} checks, ${mismatches} mismatches`);
if (Number.isNaN(mismatches.length)) { console.error("mismatches is NaN - an unset counter"); process.exitCode = 1; }
if (mismatches.length) process.exitCode = 1;
