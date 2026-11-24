#!/usr/bin/env node
// The recipe that worked: a mirrored root pair, then a stack at one half.
//
//     node scripts/root_search.ts
//     node scripts/root_search.ts --write
//     node scripts/root_search.ts --second 1/3 --x 1,2
//
// The TypeScript twin of scripts/root_search.py. The Python module stays for adder_roots.py
// until that consumer moves; this script writes workbench/root-candidates.json.

import { writeFileSync } from "node:fs";
import path from "node:path";
import { search, type Second } from "../app/src/lib/root-search.ts";

const ROOT = path.resolve(import.meta.dirname, "..");
const OUT = path.join(ROOT, "workbench", "root-candidates.json");
const args = process.argv.slice(2);

const secondAt = args.indexOf("--second");
let second: Second = null;
if (secondAt >= 0) {
  const [p2, q2] = args[secondAt + 1].split("/").map(Number);
  if (p2 > 0 && q2 > p2) second = { p: p2, q: q2 };
}
const xAt = args.indexOf("--x");
const xRow = xAt >= 0
  ? (args[xAt + 1].split(",").map(Number) as [number, number])
  : ([1, 2] as [number, number]);

const rows = search({ second, xRow });
if (!rows.length) {
  console.log("no candidates");
  process.exit(1);
}
console.log(`${rows.length} candidates · best ${rows[0].crossings} pairs at grid ${rows[0].grid}`);
for (const row of rows.slice(0, 10)) {
  console.log(`  ${row.name.padEnd(22)} ${String(row.crossings).padStart(2)} pairs · ` +
    `${String(row.places).padStart(2)} places · inflections ${row.inflections} · ` +
    `grid ${row.grid.toLocaleString("en-US")} · grace ${row.grace}`);
}

if (args.includes("--write")) {
  writeFileSync(OUT, `${JSON.stringify({
    format: "curve-lab.root-candidates/1",
    note: "mirrored root pair + stack at 1/2; crossing pairs, inflections and the exact grid",
    candidates: rows,
  }, null, 1)}\n`);
  console.log(`wrote ${path.relative(ROOT, OUT)}`);
}
