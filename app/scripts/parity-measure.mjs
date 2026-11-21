// The parity check: the TypeScript port vs the Python reference, curve by curve.
//   PATH="$HOME/node24/bin:$PATH" node app/scripts/parity-measure.mjs
// Zero mismatches is the only passing state; a single differing grid is a fault.

import { readFileSync, writeFileSync, existsSync } from "node:fs";
import path from "node:path";
import { metrics } from "../src/lib/measure.ts";

const ROOT = path.resolve(import.meta.dirname, "..", "..");
const registry = JSON.parse(readFileSync(path.join(ROOT, "workbench", "curve-registry.json"), "utf8"));
const reference = existsSync("/tmp/py-metrics.json")
  ? JSON.parse(readFileSync("/tmp/py-metrics.json", "utf8"))
  : {};

let checked = 0, mismatches = [];
for (const curve of registry.curves) {
  const sx = curve.speedX, sy = curve.speedY;
  if (!sx || !sy || sx.length === 0) continue;
  const want = reference[curve.uid];
  if (!want) continue;
  const got = metrics(sx, sy);
  checked += 1;
  const close = (a, b) => Math.abs(a - b) <= 1e-9 * Math.max(1, Math.abs(b));
  if (got.grid !== want.grid) mismatches.push(`${curve.uid} ${curve.name}: grid ${got.grid} vs ${want.grid}`);
  if (!close(got.bend, want.bend)) mismatches.push(`${curve.uid} ${curve.name}: bend ${got.bend} vs ${want.bend}`);
  if (!close(got.arc, want.arc)) mismatches.push(`${curve.uid} ${curve.name}: arc ${got.arc} vs ${want.arc}`);
  if (!close(got.closest, want.closest)) mismatches.push(`${curve.uid} ${curve.name}: closest ${got.closest} vs ${want.closest}`);
  if (got.inflection_count !== want.inflection_count) mismatches.push(`${curve.uid} ${curve.name}: inflections ${got.inflection_count} vs ${want.inflection_count}`);
  if ((want.inflections || []).length) {
    const w = want.inflections, g = got.inflections;
    if (g.length !== w.length || g.some((v, i) => !close(v, w[i]))) {
      mismatches.push(`${curve.uid} ${curve.name}: inflection lists differ`);
    }
  }
}
console.log(`parity: ${checked} curves checked, ${mismatches.length} mismatches`);
if (mismatches.length) {
  for (const m of mismatches.slice(0, 20)) console.error(m);
  process.exitCode = 1;
}
