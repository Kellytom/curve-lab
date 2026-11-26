// The reducer parity: the TS coefficients must be IDENTICAL to the Python
// twin's - the interpolating polynomial is unique in any exact arithmetic.
//   PATH="$HOME/node24/bin:$PATH" node app/scripts/parity-reduce.mjs
import { readFileSync } from "node:fs";
import { reduceCurve } from "../src/lib/reduction/reduce.ts";
import { toFraction, curvePolynomials } from "../src/lib/measure.ts";

const reg = JSON.parse(readFileSync(new URL("../../workbench/curve-registry.json", import.meta.url), "utf8"));
const ref = JSON.parse(readFileSync(new URL("../../reduction/parity/reduce-reference.json", import.meta.url), "utf8"));
const c = reg.curves.find((r) => r.uid === "c-0001");
const u = c.speedX.map((v) => toFraction(v));
const v = c.speedY.map((v) => toFraction(v));
const { x: xPoly } = curvePolynomials(u, v);
const exact = xPoly.map((f) => ({ n: f.n, d: f.d }));
const result = reduceCurve(exact, 20.0, 11, 0.0005, 64);

let mismatches = 0;
result.pieces.forEach((piece, i) => {
  const want = ref.pieces[i];
  if (!want) return;
  if (piece.coeffs.length !== want.coeffs.length) {
    console.error(`piece ${i}: ${piece.coeffs.length} coefficients vs ${want.coeffs.length}`);
    mismatches += 1; return;
  }
  piece.coeffs.forEach((co, k) => {
    if (co.n !== BigInt(want.coeffs[k][0]) || co.d !== BigInt(want.coeffs[k][1])) {
      console.error(`piece ${i} coeff ${k}: ${co.n}/${co.d} vs ${want.coeffs[k][0]}/${want.coeffs[k][1]}`);
      mismatches += 1;
    }
  });
});
console.log(`reduce parity: ${ref.pieces.length} pieces, ${mismatches} mismatches`);
if (mismatches) process.exitCode = 1;
