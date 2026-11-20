// The hybrid polynomials of the prime mover's own walk — no sin, no cos.
//
//   node scripts/prime_mover_hybrid.mjs "7,24,25" [stations]
//
// Every station is the engine's exact rational point on the unit circle
// (`unitWalk`, the same walk as `walker(k) = (24+7i)^(2k+1)/5^(4k)`), and every
// value is computed with the driver's own rational arithmetic. The drawing
// numbers exist only at the end, through `fixed()`, which shifts a BigInt rather
// than turning it into a float.
//
// Writes workbench/hybrid-formulas.json; scripts/hybrid_formulas.py draws it.

import { writeFileSync } from "node:fs";
import path from "node:path";
import {
  TRIPLES, unitWalk, walkFor, rational, multiply, add, subtract,
  rationalText, rationalFloat,
} from "../app/src/scripts/prime-mover-driver.js";

const ROOT = path.resolve(import.meta.dirname, "..");
const OUT = path.join(ROOT, "workbench", "hybrid-formulas.json");

const tripleName = process.argv[2] || "7,24,25";
const COUNT = Number(process.argv[3] || 240);

const pow = (value, n) => {
  let out = rational(1n);
  for (let i = 0; i < n; i += 1) out = multiply(out, value);
  return out;
};

function polys(X, Y) {
  const x = pow(X, 5);          // x = C^5
  const y = pow(Y, 3);          // y = S^3
  const x2 = multiply(x, x);
  const y2 = multiply(y, y);
  const x3 = multiply(x2, x);
  const base = add(x2, y2);
  const midQuad = multiply(rational(2n), multiply(x, y));
  const midCubic = multiply(rational(3n), add(multiply(x2, y), multiply(x, y2)));
  const midQuint = multiply(rational(10n),
    add(multiply(x3, y2), multiply(multiply(x2, y), y2)));
  const midQuintAll = add(
    multiply(rational(5n), add(multiply(multiply(x2, x2), y),
      multiply(x, multiply(y2, y2)))),
    midQuint,
  );
  return {
    x, y,
    "quadratic": add(base, midQuad),
    "cubic": add(base, midCubic),
    "quintic": add(base, midQuint),
    "quintic, all four terms": add(base, midQuintAll),
    "cubic + quintic": add(base, add(midCubic, midQuint)),
    "all five": add(base, add(midQuad, add(midCubic, midQuint))),
  };
}

const rows = unitWalk(COUNT);
const walk = walkFor(tripleName);
const points = [];
const series = {};
const ranges = {};
const exact = [];

for (const row of rows) {
  const X = rational(row.x, row.d);
  const Y = rational(row.y, row.d);
  const values = polys(X, Y);
  const x = rationalFloat(values.x);
  const y = rationalFloat(values.y);
  points.push({ k: row.k, x, y });
  for (const [name, value] of Object.entries(values)) {
    if (name === "x" || name === "y") continue;
    (series[name] ||= []).push({ k: row.k, value: rationalFloat(value) });
    const span = ranges[name] || [Infinity, -Infinity];
    const v = rationalFloat(value);
    ranges[name] = [Math.min(span[0], v), Math.max(span[1], v)];
  }
  if (row.k < 3) {
    exact.push({
      k: row.k,
      X: rationalText(X), Y: rationalText(Y),
      x: rationalText(values.x), y: rationalText(values.y),
      P: Object.fromEntries(Object.entries(values)
        .filter(([name]) => name !== "x" && name !== "y")
        .map(([name, value]) => [name, rationalText(value)])),
    });
  }
}

const document = {
  format: "curve-lab.prime-mover-hybrid/1",
  triple: tripleName,
  turn: walk.turn,
  clue: "x = X^5, y = Y^3 on the prime mover's exact unit walk; no sin, no cos",
  count: COUNT,
  segments: Math.ceil(360 / walk.turn),
  points,
  series,
  ranges,
  exact,
};
writeFileSync(OUT, JSON.stringify(document, null, 1) + "\n");
console.log(`wrote ${path.relative(ROOT, OUT)}: ${COUNT} stations, turn ${walk.turn.toFixed(4)}°`);
console.log(`k = 0: (${exact[0].x}, ${exact[0].y})`);
console.log(`k = 1: (${exact[1].x}, ${exact[1].y})`);
