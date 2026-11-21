// The cone-terminal parity: TS coneTerminal vs Python's cone_terminal.
import { readFileSync } from "node:fs";
import { coneTerminal } from "../src/lib/terminals.ts";
const dump = JSON.parse(readFileSync("/tmp/py-cone.json", "utf8"));
let checked = 0, mismatches = 0;
for (const run of dump.runs) {
  const railPos = dump.rails[run.pos], railNeg = dump.rails[run.neg];
  let mine;
  try {
    mine = coneTerminal(railPos, railNeg, run.end, run.symmetric, run.centre, run.tangent);
  } catch (error) {
    console.error(`${run.pos} ${run.end} symmetric=${run.symmetric}: TS raised (${error.message})`);
    mismatches += 1; continue;
  }
  checked += 1;
  for (const key of ["tip"]) {
    for (const axis of [0, 1]) {
      if (Math.abs(mine[key][axis] - run.spans.tip[axis]) > 1e-9) {
        console.error(`${run.pos} ${run.end} ${key}[${axis}]: ${mine[key][axis]} vs ${run.spans.tip[axis]}`);
        mismatches += 1;
      }
    }
  }
  if (mine.spans.length !== run.spans.spans.length) {
    console.error(`${run.pos} ${run.end}: ${mine.spans.length} spans vs ${run.spans.spans.length}`);
    mismatches += 1; continue;
  }
  mine.spans.forEach((span, i) => {
    for (const key of ["p0", "c1", "c2", "p3"]) {
      for (const axis of [0, 1]) {
        if (Math.abs(span[key][axis] - run.spans.spans[i][key][axis]) > 1e-9) {
          console.error(`${run.pos} ${run.end} span ${i} ${key}[${axis}]: ${span[key][axis]} vs ${run.spans.spans[i][key][axis]}`);
          mismatches += 1;
        }
      }
    }
  });
  if (Math.abs(mine.axisTwist - run.spans.axis_twist) > 1e-9) {
    console.error(`${run.pos} ${run.end} axisTwist: ${mine.axisTwist} vs ${run.spans.axis_twist}`);
    mismatches += 1;
  }
}
console.log(`cone parity: ${checked} runs checked, ${mismatches} mismatches`);
if (mismatches) process.exitCode = 1;
