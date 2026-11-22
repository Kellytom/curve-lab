// The piece parity: the TS build vs Python's, group by group: name, instance,
// role, distance, and every control point of every span.
//   PATH="$HOME/node24/bin:$PATH" node app/scripts/parity-piece.mjs
import { readFileSync } from "node:fs";
import { toPiece, buildPiece, buildRibbonPiece } from "../src/lib/piece.ts";

const dump = JSON.parse(readFileSync("/tmp/py-piece.json", "utf8"));
let checked = 0, mismatches = 0;
for (const want of dump) {
  const input = want.input;
  const piece = toPiece({
    name: input.name,
    traces: [{
      name: input.name,
      spans: input.spans,
      width: input.width,
      layer: input.layer,
      terminals: input.terminals,
      mirror: input.mirror,
    }],
    mirror: want.info.mirror,
    stroke: 0.6,
  });
  const built = input.width === null
    ? buildPiece(piece, 0.02)
    : buildRibbonPiece(piece, 0.02);
  checked += 1;
  if (built.groups.length !== want.groups.length) {
    console.error(`${want.piece}: ${built.groups.length} groups vs ${want.groups.length}`);
    mismatches += 1; continue;
  }
  built.groups.forEach((group, i) => {
    const wantGroup = want.groups[i];
    for (const key of ["name", "instance", "role"]) {
      if (group[key] !== wantGroup[key]) {
        console.error(`${want.piece} group ${i}: ${key} ${group[key]} vs ${wantGroup[key]}`);
        mismatches += 1;
      }
    }
    if ((group.distance ?? null) !== (wantGroup.distance ?? null)) {
      console.error(`${want.piece} group ${i}: distance ${group.distance} vs ${wantGroup.distance}`);
      mismatches += 1;
    }
    if (group.spans.length !== wantGroup.spans.length) {
      console.error(`${want.piece} group ${i}: ${group.spans.length} spans vs ${wantGroup.spans.length}`);
      mismatches += 1; return;
    }
    group.spans.forEach((span, k) => {
      for (const key of ["p0", "c1", "c2", "p3"]) {
        for (const axis of [0, 1]) {
          if (Math.abs(span[key][axis] - wantGroup.spans[k][key][axis]) > 1e-9) {
            console.error(`${want.piece} group ${i} span ${k} ${key}[${axis}]: ${span[key][axis]} vs ${wantGroup.spans[k][key][axis]}`);
            mismatches += 1;
          }
        }
      }
    });
  });
  if (built.info.fit_ok !== want.info.fit_ok) {
    console.error(`${want.piece}: fit_ok ${built.info.fit_ok} vs ${want.info.fit_ok}`);
    mismatches += 1;
  }
  if (built.info.mirror !== want.info.mirror) {
    console.error(`${want.piece}: mirror ${built.info.mirror} vs ${want.info.mirror}`);
    mismatches += 1;
  }
  const traceReport = built.info.traces[0], wantReport = want.info.traces[0];
  if (traceReport.fit_error.toFixed(9) !== wantReport.fit_error.toFixed(9)) {
    console.error(`${want.piece}: fit_error ${traceReport.fit_error} vs ${wantReport.fit_error}`);
    mismatches += 1;
  }
  if (traceReport.rails !== wantReport.rails) {
    console.error(`${want.piece}: rails ${traceReport.rails} vs ${wantReport.rails}`);
    mismatches += 1;
  }
}
console.log(`piece parity: ${checked} pieces checked, ${mismatches} mismatches`);
if (mismatches) process.exitCode = 1;
