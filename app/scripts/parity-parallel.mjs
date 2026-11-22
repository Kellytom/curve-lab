// The parallel-rail parity: TS fitSpanOffset/fitChainOffset vs Python's.
//   PATH="$HOME/node24/bin:$PATH" node app/scripts/parity-parallel.mjs
import { readFileSync } from "node:fs";
import { fitSpanOffset, fitChainOffset } from "../src/lib/parallel-bezier.ts";

const dump = JSON.parse(readFileSync("/tmp/py-parallel.json", "utf8"));
let checked = 0, mismatches = 0;
for (const run of dump.runs) {
  const rail = dump.rails.find((r) => run.source.startsWith(r.name));
  const spans = rail.spans.map((s) => ({ p0: s.p0, c1: s.c1, c2: s.c2, p3: s.p3 }));
  const chain = run.source.endsWith("chain");
  const mine = chain
    ? fitChainOffset(spans, run.distance, 0.01)
    : fitSpanOffset(spans[0], run.distance, 0.01);
  checked += 1;
  if (mine.spans.length !== run.spans.length) {
    console.error(`${run.source} d=${run.distance}: ${mine.spans.length} spans vs ${run.spans.length}`);
    mismatches += 1; continue;
  }
  mine.spans.forEach((span, i) => {
    const want = run.spans[i];
    for (const key of ["p0", "c1", "c2", "p3"]) {
      for (const axis of [0, 1]) {
        if (Math.abs(span[key][axis] - want[key][axis]) > 1e-9) {
          console.error(`${run.source} d=${run.distance} span ${i} ${key}[${axis}]: ${span[key][axis]} vs ${want[key][axis]}`);
          mismatches += 1;
        }
      }
    }
  });
  if (Math.abs(mine.error_max - run.error_max) > 1e-9) {
    console.error(`${run.source} d=${run.distance}: error_max ${mine.error_max} vs ${run.error_max}`);
    mismatches += 1;
  }
}
console.log(`parallel parity: ${checked} runs checked, ${mismatches} mismatches`);
if (mismatches) process.exitCode = 1;
