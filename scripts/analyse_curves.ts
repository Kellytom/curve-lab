#!/usr/bin/env node
// Measure every curve, so two curves can be compared as numbers.
//
//     node scripts/analyse_curves.ts            # report and write
//     node scripts/analyse_curves.ts --limit 10 # a quick pass
//     node scripts/analyse_curves.ts --check    # no write
//     node scripts/analyse_curves.ts --out /tmp/analysis.json
//
// The TypeScript port of scripts/analyse_curves.py (retired when this landed). Writes
// `workbench/curve-analysis.json` (registered format); the database is loaded from that file by
// `app/scripts/load-analysis.mjs`, so the analyser computes and Prisma writes: one writer.

import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { analyse, type CurveRecord } from "../app/src/lib/curve-analysis.ts";

const ROOT = path.resolve(import.meta.dirname, "..");
const REGISTRY = path.join(ROOT, "workbench", "curve-registry.json");
const OUT = path.join(ROOT, "workbench", "curve-analysis.json");

const args = process.argv.slice(2);
const limitAt = args.indexOf("--limit");
const limit = limitAt >= 0 ? Number(args[limitAt + 1]) || 0 : 0;
const outAt = args.indexOf("--out");
const out = outAt >= 0 ? path.resolve(args[outAt + 1]) : OUT;
const check = args.includes("--check");

const registry = JSON.parse(readFileSync(REGISTRY, "utf8")) as { curves: CurveRecord[] };
const curves = limit ? registry.curves.slice(0, limit) : registry.curves;

const rows = curves.map((curve, index) => {
  if ((index + 1) % 25 === 0) console.log(`  ${index + 1} of ${curves.length}`);
  try {
    return analyse(curve);
  } catch (error) {
    return {
      uid: curve.uid, name: curve.name, kind: "error", method: "sampled",
      error: String(error instanceof Error ? error.message : error).slice(0, 120),
    };
  }
});

const exact = rows.filter((row) => row.method === "exact").length;
const crossed = rows.filter((row) => "crossings" in row && row.crossings).length;
console.log(`${rows.length} curves · ${exact} exact · ${crossed} with crossings`);
for (const key of ["crossings", "inflections", "maxCurvature", "mirrorY"] as const) {
  const values = rows
    .map((row) => (row as Record<string, unknown>)[key])
    .filter((value): value is number => typeof value === "number");
  const sorted = values.length ? [...values].sort((a, b) => a - b) : [0];
  console.log(`  ${key}: min ${sorted[0]} median ${sorted[Math.floor(sorted.length / 2)]} ` +
    `max ${sorted[sorted.length - 1]}`);
}

if (check) process.exit(0);
writeFileSync(out, `${JSON.stringify({ format: "curve-lab.curve-analysis/1", curves: rows }, null, 1)}\n`);
console.log(`wrote ${path.relative(ROOT, out)}`);
