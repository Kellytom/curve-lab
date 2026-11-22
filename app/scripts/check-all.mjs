// Run every page check and report all failures in one pass.
//
// The old `a && b && c` chain stopped at the first failure, so one lap revealed
// one fault. This runs each check, keeps every output, and prints a single list.
//
//   node app/scripts/check-all.mjs
//   node app/scripts/check-all.mjs --changed        only the routes in the diff
//   CURVE_LAB_READ_ONLY=1 node app/scripts/check-all.mjs
//   CURVE_LAB_URL=http://127.0.0.1:4322 node app/scripts/check-all.mjs   a built server

import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const CHECKS = [
  "check-pages.mjs",
  "check-stars.mjs",
  "check-names.mjs",
  "check-prime-mover-page.mjs",
  "check-layout.mjs",
  "check-review.mjs",
];
const extra = process.argv.slice(2);
const results = [];

for (const file of CHECKS) {
  const path = fileURLToPath(new URL(file, import.meta.url));
  const args = file === "check-pages.mjs" ? [path, ...extra] : [path];
  const run = spawnSync(process.execPath, args, { encoding: "utf8", env: process.env });
  const output = `${run.stdout || ""}${run.stderr || ""}`.trim();
  if (run.status === 0) {
    console.log(`ok   ${file}`);
    if (output) console.log(output.split("\n").map((line) => `     ${line}`).join("\n"));
  } else {
    console.error(`FAIL ${file}`);
    if (output) console.error(output.split("\n").map((line) => `     ${line}`).join("\n"));
  }
  results.push({ file, status: run.status });
}

const failed = results.filter((result) => result.status !== 0);
if (failed.length) {
  console.error(`\n${failed.length} of ${results.length} checks failed: ${failed.map((result) => result.file).join(", ")}`);
  process.exit(1);
}
console.log(`\nall ${results.length} page checks passed`);
