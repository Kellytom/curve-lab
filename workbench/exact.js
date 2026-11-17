// Exact rationals, on BigInt. This is the JS answer to Python's Fraction:
// one normalised pair of arbitrary-precision integers, no floating point on
// the exact path. Loaded as a plain script (globalThis.Exact) or required
// from Node.
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.Exact = factory();
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  function gcd(a, b) {
    a = a < 0n ? -a : a;
    b = b < 0n ? -b : b;
    while (b) { const t = a % b; a = b; b = t; }
    return a;
  }

  function lcm(a, b) {
    if (a === 0n || b === 0n) return 0n;
    return (a / gcd(a, b)) * b;
  }

  class Rational {
    constructor(numerator, denominator = 1n) {
      let n = BigInt(numerator);
      let d = BigInt(denominator);
      if (d === 0n) throw new RangeError("a rational with denominator zero");
      if (d < 0n) { n = -n; d = -d; }
      const g = gcd(n, d) || 1n;
      this.n = n / g;
      this.d = d / g;
      Object.freeze(this);
    }

    static from(value) {
      if (value instanceof Rational) return value;
      if (typeof value === "bigint") return new Rational(value);
      if (typeof value === "number") {
        if (!Number.isInteger(value)) {
          throw new TypeError("use a string like '3/7' for a fraction, not a float");
        }
        return new Rational(BigInt(value));
      }
      if (typeof value === "string") {
        const text = value.trim();
        const slash = text.indexOf("/");
        if (slash < 0) return new Rational(BigInt(text));
        return new Rational(BigInt(text.slice(0, slash)), BigInt(text.slice(slash + 1)));
      }
      throw new TypeError(`cannot read a rational from ${typeof value}`);
    }

    add(other) {
      const o = Rational.from(other);
      return new Rational(this.n * o.d + o.n * this.d, this.d * o.d);
    }

    sub(other) {
      const o = Rational.from(other);
      return new Rational(this.n * o.d - o.n * this.d, this.d * o.d);
    }

    mul(other) {
      const o = Rational.from(other);
      return new Rational(this.n * o.n, this.d * o.d);
    }

    div(other) {
      const o = Rational.from(other);
      if (o.n === 0n) throw new RangeError("division by zero");
      return new Rational(this.n * o.d, this.d * o.n);
    }

    neg() { return new Rational(-this.n, this.d); }

    abs() { return this.n < 0n ? this.neg() : this; }

    compare(other) {
      const o = Rational.from(other);
      const left = this.n * o.d;
      const right = o.n * this.d;
      return left < right ? -1 : left > right ? 1 : 0;
    }

    equals(other) { return this.compare(other) === 0; }

    isZero() { return this.n === 0n; }

    isInteger() { return this.d === 1n; }

    toNumber() { return Number(this.n) / Number(this.d); }

    toString() { return this.d === 1n ? `${this.n}` : `${this.n}/${this.d}`; }
  }

  const ZERO = new Rational(0n);
  const ONE = new Rational(1n);

  return { Rational, ZERO, ONE, gcd, lcm };
});
