#!/usr/bin/env node
// Coupler curves: what a four-bar linkage draws.
//
//     node scripts/coupler_curves.ts
//     node scripts/coupler_curves.ts --write
//     node scripts/coupler_curves.ts --wide
//     node scripts/coupler_curves.ts --random 500
//
// The TypeScript twin of scripts/coupler_curves.py. The Python module stays for
// tests/test_crossing_calibration.py until that moves; this script writes
// workbench/coupler-curves.json.

import { writeFileSync } from "node:fs";
import path from "node:path";
import { searchFound, searchRandom } from "../app/src/lib/coupler-curves.ts";

const ROOT = path.resolve(import.meta.dirname, "..");
const OUT = path.join(ROOT, "workbench", "coupler-curves.json");
const args = process.argv.slice(2);
const at = (flag: string): number => {
  const index = args.indexOf(flag);
  return index >= 0 ? Number(args[index + 1]) : 0;
};
const minCrossings = args.includes("--min-crossings") ? at("--min-crossings") : 2;
const randomCount = at("--random");

if (randomCount) {
  const found = searchRandom(randomCount, minCrossings);
  console.log(`${found.length} of ${randomCount} random couplers with ${minCrossings}+ crossings`);
  for (const item of found.slice(0, 8)) {
    console.log(`  r2 ${item.r2} r3 ${item.r3} r4 ${item.r4} ground ${item.d} ` +
      `a ${item.a} b ${item.b} -> ${item.crossings} crossings · mirror ${item.mirror}`);
  }
  process.exit(0);
}

const wide = args.includes("--wide");
const found = searchFound({ wide, minCrossings });
console.log(`${found.length} coupler curves with ${minCrossings}+ crossings`);
for (const item of found.slice(0, 8)) {
  console.log(`  r2 ${item.r2} r3 ${item.r3} r4 ${item.r4} ground ${item.d} ` +
    `a ${item.a} b ${item.b} → ${item.crossings} crossings · mirror ${item.mirror}`);
}

if (args.includes("--write") && found.length) {
  writeFileSync(OUT, `${JSON.stringify({
    format: "curve-lab.coupler-curves/1",
    note: "four-bar coupler curves, sampled (cos/sin of a general angle); crossings counted on the polyline",
    curves: found.slice(0, 20),
  }, null, 1)}\n`);
  console.log(`wrote ${path.relative(ROOT, OUT)}`);
}
