// The exact Chebyshev truncation bound, pinned to the Python reference.
//
// The reference numbers come from Fraction arithmetic straight from the
// definition (substitute, basis change, sum the tail) run against
// curve_lab/measure.py's polynomials; the run is recorded in the commit that
// introduced this file. If this test fails, the desk's "proven bound" is not
// proven and the page must refuse its verdict.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { curvePolynomials, evaluate, fr } from "../src/lib/measure.ts";
import {
  chebTailBound,
  evalChebFloat,
  powerToChebyshev,
  substitute,
} from "../src/lib/reduction/chebyshev.ts";

const registry = JSON.parse(
  readFileSync(new URL("../../workbench/curve-registry.json", import.meta.url), "utf8"),
);

const F = (n, d = 1n) => ({ n, d });
const addF = (a, b) => F(a.n * b.d + b.n * a.d, a.d * b.d);
const mulF = (a, b) => F(a.n * b.n, a.d * b.d);
const asNumber = (a) => Number(a.n) / Number(a.d);
/** mid and half of the piece [lo, hi], exactly. */
const piece = (p, pieces) => {
  const lo = F(BigInt(p), BigInt(pieces));
  const hi = F(BigInt(p + 1), BigInt(pieces));
  const mid = F(lo.n * hi.d + hi.n * lo.d, 2n * lo.d * hi.d);
  const half = F(hi.n * lo.d - lo.n * hi.d, 2n * lo.d * hi.d);
  return { mid, half };
};
function bgcdTest(a, b) {
  let x = a < 0n ? -a : a;
  let y = b < 0n ? -b : b;
  while (y) [x, y] = [y, x % y];
  return x || 1n;
}
/** the exact proven bound over all pieces: max over p of (tailX + tailY). */
function provenBound(x, y, pieces, keep = 11) {
  let worst = F(0n);
  for (let p = 0; p < pieces; p += 1) {
    const { mid, half } = piece(p, pieces);
    const bound = addF(chebTailBound(x, mid, half, keep), chebTailBound(y, mid, half, keep));
    if (bound.n * worst.d > worst.n * bound.d) worst = bound;
  }
  // reduce: the Python reference states the same value in lowest terms
  const g = bgcdTest(worst.n, worst.d);
  return F(worst.n / g, worst.d / g);
}

test("T_3 in power form comes back as itself", () => {
  // T_3(u) = 4u³ − 3u; its Chebyshev series is just c_3 = 1.
  const poly = [F(0n), F(-3n), F(0n), F(4n)];
  assert.deepEqual(powerToChebyshev(poly), [F(0n), F(0n), F(0n), F(1n)]);
});

test("u² is half T_0 plus half T_2", () => {
  const out = powerToChebyshev([F(0n), F(0n), F(1n)]);
  assert.deepEqual(out, [F(1n, 2n), F(0n), F(1n, 2n)]);
});

test("the exact series evaluates to the exact polynomial", () => {
  // P(u) = 1 + 2u + 3u². With T_1 = u and u² = (T_0 + T_2)/2:
  // P = 5/2·T_0 + 2·T_1 + 3/2·T_2.
  // At u = 3/4: T_0 = 1, T_1 = 3/4, T_2 = 1/8 → value = 67/16.
  const c = powerToChebyshev(substitute(
    [F(1n), F(2n), F(3n)],
    F(0n),
    F(1n),
  ));
  assert.deepEqual(c, [F(5n, 2n), F(2n), F(3n, 2n)]);
  const value = addF(addF(c[0], mulF(c[1], F(3n, 4n))), mulF(c[2], F(1n, 8n)));
  assert.equal(asNumber(value), 67 / 16);
});

test("c-0260's proven bound matches the Python reference", () => {
  const curve = registry.curves.find((c) => c.uid === "c-0260");
  const { x, y } = curvePolynomials(curve.speedX, curve.speedY);
  const cases = [
    { pieces: 1, exact: "31003563575167/443048919040" },
    { pieces: 2, exact: "340625579123431691/33183604523663360" },
    { pieces: 4, exact: "512698712749713832528049/3897099505264541114040320" },
  ];
  for (const { pieces, exact } of cases) {
    const worst = provenBound(x, y, pieces);
    const [num, den] = exact.split("/").map(BigInt);
    assert.equal(worst.n, num, `bound numerator at ${pieces} pieces`);
    assert.equal(worst.d, den, `bound denominator at ${pieces} pieces`);
  }
});

test("on c-0260 the measured miss stays under the proven bound", () => {
  const curve = registry.curves.find((c) => c.uid === "c-0260");
  const { x, y } = curvePolynomials(curve.speedX, curve.speedY);
  const KEEP = 11;
  const PIECES = 4;
  const N = 240;
  const size = 2253.62054586377; // the exact bbox diagonal, from the audit run
  let actual = 0;
  for (let k = 0; k <= N; k += 1) {
    const tFrac = fr(BigInt(k), BigInt(N));
    const t = k / N;
    const p = Math.min(PIECES - 1, Math.floor(t * PIECES));
    const { mid, half } = piece(p, PIECES);
    const lo = p / PIECES;
    const hi = (p + 1) / PIECES;
    const u = (2 * t - lo - hi) / (hi - lo);
    // the truncated series: substitute, change basis, THEN cut to keep+1
    const rx = evalChebFloat(powerToChebyshev(substitute(x, mid, half)).slice(0, KEEP + 1), u);
    const ry = evalChebFloat(powerToChebyshev(substitute(y, mid, half)).slice(0, KEEP + 1), u);
    const ex = asNumber(evaluate(x, tFrac));
    const ey = asNumber(evaluate(y, tFrac));
    actual = Math.max(actual, Math.hypot(ex - rx, ey - ry));
  }
  const bound = asNumber(provenBound(x, y, PIECES));
  assert.ok(actual <= bound + 1e-9, `measured miss ${actual} exceeds the proven bound ${bound}`);
  assert.ok(actual / size <= 0.0005, "the miss must sit under the dial");
});
