// Exact PH offsets: the JS twin of curve_lab/ph_offset.py.
//
// The curve is written by a speed pair (u, v): C'(t) = (u² − v², 2uv). Its
// speed σ = u² + v² is a polynomial, so the offset at distance d is a ratio of
// two exact polynomials:  O(t) = C(t) + d·(−y', x') / σ(t).
//
// Nothing here is a Bézier; control points are the export step. Everything on
// the lattice path is Rational/BigInt. Only floatSampler uses doubles, and it
// is for drawing, never for a lattice answer.
(function (root, factory) {
  const isCommonJs = typeof module === "object" && module.exports;
  const exact = isCommonJs ? require("./exact.js") : root.Exact;
  const poly = isCommonJs ? require("./poly_exact.js") : root.PolyExact;
  const api = factory(exact.Rational, exact.lcm, exact.gcd, poly);
  if (isCommonJs) module.exports = api;
  else root.PhOffset = api;
})(typeof globalThis !== "undefined" ? globalThis : this,
   function (Rational, lcm, gcd, poly) {
  "use strict";

  const ZERO = Rational.from(0);

  function hodographPair(u, v) {
    const uu = poly.multiply(u, u);
    const vv = poly.multiply(v, v);
    return [
      poly.sub(uu, vv),
      poly.scale(poly.multiply(u, v), 2),
    ];
  }

  function speedSquared(u, v) {
    return poly.add(poly.multiply(u, u), poly.multiply(v, v));
  }

  function curve(u, v) {
    const [xPrime, yPrime] = hodographPair(u, v);
    return [poly.integrate(xPrime), poly.integrate(yPrime)];
  }

  function forms(u, v, distance) {
    const [x, y] = curve(u, v);
    const [xPrime, yPrime] = hodographPair(u, v);
    return { x, y, xPrime, yPrime, sigma: speedSquared(u, v),
             distance: Rational.from(distance) };
  }

  function pointAt(u, v, distance, t) {
    const f = forms(u, v, distance);
    const speed = poly.evaluate(f.sigma, t);
    if (speed.isZero()) throw new RangeError("the speed vanishes: a cusp");
    return [
      poly.evaluate(f.x, t).sub(f.distance.mul(poly.evaluate(f.yPrime, t)).div(speed)),
      poly.evaluate(f.y, t).add(f.distance.mul(poly.evaluate(f.xPrime, t)).div(speed)),
    ];
  }

  function latticeScale(point) {
    return lcm(point[0].d, point[1].d);
  }

  function exactSampler(u, v, distance) {
    const f = forms(u, v, distance);
    return function point(t) {
      const speed = poly.evaluate(f.sigma, t);
      if (speed.isZero()) throw new RangeError("the speed vanishes: a cusp");
      return [
        poly.evaluate(f.x, t).sub(f.distance.mul(poly.evaluate(f.yPrime, t)).div(speed)),
        poly.evaluate(f.y, t).add(f.distance.mul(poly.evaluate(f.xPrime, t)).div(speed)),
      ];
    };
  }

  function tOf(k, q) { return new Rational(BigInt(k), BigInt(q)); }

  function firstInteriorHit(u, v, distance = ZERO, qMax = 40) {
    const point = exactSampler(u, v, distance);
    let best = null;
    for (let q = 2; q <= qMax; q += 1) {
      for (let k = 1; k < q; k += 1) {
        if (gcd(BigInt(k), BigInt(q)) !== 1n) continue;
        const at = point(tOf(k, q));
        const scale = latticeScale(at);
        if (best === null || scale < best.scale) best = { scale, t: [k, q], point: at };
      }
    }
    return best;
  }

  function hitsAtScale(u, v, scale, distance = ZERO, qMax = 24) {
    const point = exactSampler(u, v, distance);
    const factor = Rational.from(scale);
    const hits = new Map();
    for (let q = 1; q <= qMax; q += 1) {
      for (let k = 0; k <= q; k += 1) {
        const at = point(tOf(k, q));
        const x = at[0].mul(factor);
        const y = at[1].mul(factor);
        if (!x.isInteger() || !y.isInteger()) continue;
        const key = `${x.n},${y.n}`;
        if (!hits.has(key)) {
          hits.set(key, { point: [x.n, y.n], t: q === 1 ? `${k}` : `${k}/${q}` });
        }
      }
    }
    return [...hits.values()].sort((a, b) =>
      a.point[0] < b.point[0] ? -1 : a.point[0] > b.point[0] ? 1 :
      a.point[1] < b.point[1] ? -1 : a.point[1] > b.point[1] ? 1 : 0);
  }

  function floatSampler(u, v, distance = ZERO) {
    const f = forms(u, v, distance);
    const floats = (p) => p.map((c) => c.toNumber());
    const [x, y, xPrime, yPrime, sigma] = [
      floats(f.x), floats(f.y), floats(f.xPrime), floats(f.yPrime),
      floats(f.sigma)];
    const d = f.distance.toNumber();
    const at = (p, t) => p.reduceRight((total, c) => total * t + c, 0);
    return function point(t) {
      const speed = at(sigma, t);
      if (Math.abs(speed) < 1e-15) return [at(x, t), at(y, t)];
      return [at(x, t) - d * at(yPrime, t) / speed,
              at(y, t) + d * at(xPrime, t) / speed];
    };
  }

  return { hodographPair, speedSquared, curve, pointAt, latticeScale,
           exactSampler, firstInteriorHit, hitsAtScale, floatSampler };
});
