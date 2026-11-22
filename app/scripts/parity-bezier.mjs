// The bezier parity check: TS fit_chain vs Python's on a circle of known geometry.
//   PATH="$HOME/node24/bin:$PATH" node app/scripts/parity-bezier.mjs
import { readFileSync } from "node:fs";
import { fitChain, cubicAt } from "../src/lib/bezier.ts";

const dump = JSON.parse(readFileSync("/tmp/py-bezier.json", "utf8"));
const R = dump.R;
const point = (s) => [R * Math.sin(s / R), R * (1 - Math.cos(s / R))];
const tangent = (s) => s / R;
const chain = {
  segments: dump.segments.map((s) => ({ s_base: s.s_base, length: s.length })),
  point, tangent,
};

const mine = fitChain(chain, 0.02, 64, 2);
let mismatches = 0, checked = 0;

if (mine.spans.length !== dump.spans.length) {
  console.error(`span count ${mine.spans.length} vs ${dump.spans.length}`);
  mismatches += 1;
}
dump.spans.forEach((want, i) => {
  const got = mine.spans[i];
  checked += 1;
  for (const key of ["s0", "s1"]) {
    if (got[key] !== want[key]) { console.error(`span ${i} ${key}: ${got[key]} vs ${want[key]}`); mismatches += 1; }
  }
  for (const key of ["p0", "c1", "c2", "p3"]) {
    for (const axis of [0, 1]) {
      if (Math.abs(got[key][axis] - want[key][axis]) > 1e-9) {
        console.error(`span ${i} ${key}[${axis}]: ${got[key][axis]} vs ${want[key][axis]}`);
        mismatches += 1;
      }
    }
  }
  if (got.clamped !== want.clamped) { console.error(`span ${i} clamped: ${got.clamped} vs ${want.clamped}`); mismatches += 1; }
});
for (const key of ["spans", "error_max"]) {
  const a = mine.report[key], b = dump.report[key];
  const same = typeof b === "number" ? Math.abs(a - b) <= 1e-12 * Math.max(1, Math.abs(b)) : a === b;
  if (!same) { console.error(`report ${key}: ${a} vs ${b}`); mismatches += 1; }
  checked += 1;
}
// the independent check: the fitted cubics really lie on the circle
let worst = 0.0;
for (const span of mine.spans) {
  for (let i = 0; i < 9; i += 1) {
    const [x, y] = cubicAt(span, i / 8);
    const radiusError = Math.abs(Math.hypot(x, y - R) - R);
    worst = Math.max(worst, radiusError);
  }
}
console.log(`circle check: worst radius error ${worst.toExponential(3)}`);
console.log(`parity: ${checked} checks, ${mismatches} mismatches`);
if (mismatches) process.exitCode = 1;
