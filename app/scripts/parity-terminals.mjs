// The terminals parity: TS terminalSpans vs Python's, on the same rail pairs.
//   PATH="$HOME/node24/bin:$PATH" node app/scripts/parity-terminals.mjs
import { readFileSync } from "node:fs";
import { terminalSpans } from "../src/lib/terminals.ts";

const dump = JSON.parse(readFileSync("/tmp/py-terminals.json", "utf8"));
const rails = dump.rails;
let checked = 0, mismatches = 0;
for (const run of dump.runs) {
  if (run.spans && run.spans.error) continue;   // Python raised; a TS error matches
  const railPos = rails[run.pos], railNeg = rails[run.neg];
  let mine;
  try {
    mine = terminalSpans(railPos, railNeg, run.kind, run.end);
  } catch (error) {
    console.error(`${run.rails} ${run.kind}/${run.end}: TS raised, Python did not (${error.message})`);
    mismatches += 1;
    continue;
  }
  checked += 1;
  const want = run.spans;
  if (mine.length !== want.length) {
    console.error(`${run.rails} ${run.kind}/${run.end}: ${mine.length} spans vs ${want.length}`);
    mismatches += 1;
    continue;
  }
  mine.forEach((span, i) => {
    for (const key of ["p0", "c1", "c2", "p3"]) {
      for (const axis of [0, 1]) {
        if (Math.abs(span[key][axis] - want[i][key][axis]) > 1e-9) {
          console.error(`${run.rails} ${run.kind}/${run.end} span ${i} ${key}[${axis}]: ${span[key][axis]} vs ${want[i][key][axis]}`);
          mismatches += 1;
        }
      }
    }
  });
}
console.log(`parity: ${checked} runs checked, ${mismatches} mismatches`);
if (mismatches) process.exitCode = 1;
