// The delivered coefficients: whole numbers on the grid, the miss under the dial.
import { readFileSync } from "node:fs";
import { toFraction, curvePolynomials } from "../src/lib/measure.ts";
import { reduceCurve } from "../src/lib/reduction/reduce.ts";
const reg = JSON.parse(readFileSync(new URL("../../workbench/curve-registry.json", import.meta.url), "utf8"));
const c = reg.curves.find((r) => r.uid === "c-0001");
const u = c.speedX.map((v) => toFraction(v));
const v = c.speedY.map((v) => toFraction(v));
const { x: xPoly } = curvePolynomials(u, v);
const exact = xPoly.map((f) => ({ n: f.n, d: f.d }));
const result = reduceCurve(exact, 20.0, 11, 0.0005, 64);
for (const piece of result.pieces) {
  console.log(`piece [${piece.lo} → ${piece.hi}] coeffs:`, piece.coeffs.map((f) => f.n + (f.d === 1n ? "" : "/" + f.d)).join("  "));
}
console.log('boundShare', (result.boundShare * 100).toExponential(2) + '%', 'met', result.met, 'pieces', result.piecesCount);
