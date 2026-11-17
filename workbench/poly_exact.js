// Polynomials as coefficient lists, low power first, exact Rational entries.
// Self-contained apart from Exact. The same file loads as a plain script
// (globalThis.PolyExact) or through require from Node.
(function (root, factory) {
  const isCommonJs = typeof module === "object" && module.exports;
  const exact = isCommonJs ? require("./exact.js") : root.Exact;
  const api = factory(exact.Rational);
  if (isCommonJs) module.exports = api;
  else root.PolyExact = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function (Rational) {
  "use strict";

  const ZERO = Rational.from(0);
  const ONE = Rational.from(1);

  function toRationals(values) {
    return values.map((value) => Rational.from(value));
  }

  function trim(poly) {
    const out = poly.slice();
    while (out.length && out[out.length - 1].isZero()) out.pop();
    return out.length ? out : [ZERO];
  }

  function add(left, right) {
    const out = [];
    const length = Math.max(left.length, right.length);
    for (let i = 0; i < length; i += 1) {
      out.push((left[i] || ZERO).add(right[i] || ZERO));
    }
    return trim(out);
  }

  function sub(left, right) {
    return add(left, right.map((value) => value.neg()));
  }

  function scale(poly, factor) {
    const f = Rational.from(factor);
    return trim(poly.map((value) => value.mul(f)));
  }

  function multiply(left, right) {
    const out = [];
    for (let i = 0; i < left.length + right.length - 1; i += 1) out.push(ZERO);
    left.forEach((a, i) => {
      right.forEach((b, j) => {
        out[i + j] = out[i + j].add(a.mul(b));
      });
    });
    return trim(out);
  }

  function integrate(poly) {
    const out = [ZERO];
    poly.forEach((value, i) => out.push(value.div(Rational.from(i + 1))));
    return trim(out);
  }

  function derivative(poly) {
    const out = [];
    for (let i = 1; i < poly.length; i += 1) out.push(poly[i].mul(Rational.from(i)));
    return trim(out);
  }

  function evaluate(poly, t) {
    const x = Rational.from(t);
    let total = ZERO;
    for (let i = poly.length - 1; i >= 0; i -= 1) total = total.mul(x).add(poly[i]);
    return total;
  }

  function degree(poly) {
    return trim(poly).length - 1;
  }

  return { ZERO, ONE, toRationals, trim, add, sub, scale, multiply,
           integrate, derivative, evaluate, degree };
});
