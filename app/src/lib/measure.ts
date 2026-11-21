// The exact numbers for a curve: grid, bend, arc, inflections, closest.
//
// This is the TypeScript port of `curve_lab/measure.py` — the one reference
// implementation — written for the TypeScript conversion track
// (`state/SCToDo-int.md`, item 1). Every arithmetic step that the Python module
// does in `Fraction` is done here in BigInt fractions: nothing rounds on the
// way in. A float coefficient is read through its decimal text with six places
// at most, exactly as Python reads it, so 0.1 is one tenth, not the binary
// approximation.
//
// The parity rule: a number this module prints must match the Python core on
// the same curve, and `app/scripts/parity-measure.mjs` checks that on every
// stored curve before this module is trusted.

export type Frac = { n: bigint; d: bigint };
export type SpeedRow = Array<number | string>;

function bgcd(a: bigint, b: bigint): bigint {
  let x = a < 0n ? -a : a;
  let y = b < 0n ? -b : b;
  while (y) [x, y] = [y, x % y];
  return x || 1n;
}

export function fr(n: bigint | number, d: bigint | number = 1n): Frac {
  let top = typeof n === "bigint" ? n : BigInt(n);
  let bottom = typeof d === "bigint" ? d : BigInt(d);
  if (bottom < 0n) { top = -top; bottom = -bottom; }
  const g = bgcd(top, bottom);
  return { n: top / g, d: bottom / g };
}

const ZERO: Frac = { n: 0n, d: 1n };
const HALF: Frac = { n: 1n, d: 2n };

const fAdd = (a: Frac, b: Frac): Frac => fr(a.n * b.d + b.n * a.d, a.d * b.d);
const fSub = (a: Frac, b: Frac): Frac => fr(a.n * b.d - b.n * a.d, a.d * b.d);
const fMul = (a: Frac, b: Frac): Frac => fr(a.n * b.n, a.d * b.d);
const fDiv = (a: Frac, b: Frac): Frac => fr(a.n * b.d, a.d * b.n);

/** A coefficient as an exact fraction: a float is read as the decimal it
 * prints to, with six places at most (the precision the pages offer). */
export function toFraction(value: number | string | Frac, maxDecimals = 6): Frac {
  if (typeof value === "object") return value;
  if (typeof value === "string") {
    const m = /^(-?\d+)(?:\.(\d+))?$/.exec(value.trim());
    if (m) return fr(BigInt(`${m[1]}${m[2] ?? ""}`), 10n ** BigInt((m[2] ?? "").length));
    return fr(BigInt(value.trim()));
  }
  const text = value.toFixed(maxDecimals);
  const m = /^(-?\d+)(?:\.(\d+))?$/.exec(text);
  if (!m) return ZERO;
  const [, whole, decimals = ""] = m;
  return fr(BigInt(`${whole}${decimals}`), 10n ** BigInt(decimals.length));
}

/** The integral of h^power over [-1/2, 1/2]. */
export function weight(power: number): Frac {
  if (power % 2) return ZERO;
  return fr(1n, 2n ** BigInt(power) * BigInt(power + 1));
}

/** The coefficients in h = t - 1/2: w(t) = sum c_k h^k. */
export function centred(coefficients: SpeedRow): Frac[] {
  const values = coefficients.map((c) => toFraction(c));
  const out: Frac[] = Array.from({ length: values.length }, () => ZERO);
  values.forEach((coefficient, j) => {
    for (let k = 0; k <= j; k += 1) {
      const binom = binomial(BigInt(j), BigInt(k));
      const halfto = fr(1n, 2n ** BigInt(j - k));
      out[k] = fAdd(out[k], fMul(fMul(coefficient, { n: binom, d: 1n }), halfto));
    }
  });
  return out;
}

function binomial(n: bigint, k: bigint): bigint {
  let result = 1n;
  for (let i = 0n; i < k; i += 1n) result = (result * (n - i)) / (i + 1n);
  return result;
}

function pad(a: Frac[], size: number): Frac[] {
  const out = a.slice();
  while (out.length < size) out.push(ZERO);
  return out;
}

/** (arc, chord re, chord im, bend), exactly until the two printed floats. */
export function arcAndChord(speedX: SpeedRow, speedY: SpeedRow):
  { arc: Frac; chordRe: number; chordIm: number; bend: number } {
  let cx = centred(speedX);
  let cy = centred(speedY);
  const size = Math.max(cx.length, cy.length);
  cx = pad(cx, size);
  cy = pad(cy, size);
  let arc = ZERO, chordRe = ZERO, chordIm = ZERO;
  for (let k = 0; k < cx.length; k += 1) {
    for (let l = 0; l < cx.length; l += 1) {
      const w = weight(k + l);
      if (w.n === 0n) continue;
      const xx = fMul(cx[k], cx[l]);
      const yy = fMul(cy[k], cy[l]);
      arc = fAdd(arc, fMul(fAdd(xx, yy), w));
      chordRe = fAdd(chordRe, fMul(fSub(xx, yy), w));
      chordIm = fAdd(chordIm, fMul(fAdd(fMul(cx[k], cy[l]), fMul(cy[k], cx[l])), w));
    }
  }
  const re = Number(chordRe.n) / Number(chordRe.d);
  const im = Number(chordIm.n) / Number(chordIm.d);
  const chordAbs = Math.hypot(re, im);
  const arcFloat = Number(arc.n) / Number(arc.d);
  return { arc, chordRe: re, chordIm: im, bend: chordAbs > 1e-15 ? arcFloat / chordAbs : Infinity };
}

export function bend(speedX: SpeedRow, speedY: SpeedRow): number {
  return arcAndChord(speedX, speedY).bend;
}

export function multiply(left: Frac[], right: Frac[]): Frac[] {
  const product: Frac[] = Array.from({ length: left.length + right.length - 1 }, () => ZERO);
  left.forEach((a, i) => right.forEach((b, j) => { product[i + j] = fAdd(product[i + j], fMul(a, b)); }));
  return product;
}

export function derivative(coefficients: Frac[]): Frac[] {
  return coefficients.slice(1).map((c, i) => ({ n: c.n * BigInt(i + 1), d: c.d }));
}

function trim(p: Frac[]): Frac[] {
  const out = p.slice();
  while (out.length && out[out.length - 1].n === 0n) out.pop();
  return out;
}

/** x(t) and y(t) as exact coefficient lists, from the speed recipes. */
export function curvePolynomials(speedX: SpeedRow, speedY: SpeedRow):
  { x: Frac[]; y: Frac[] } {
  const u = speedX.map((c) => toFraction(c));
  const v = speedY.map((c) => toFraction(c));
  const u2 = multiply(u, u);
  const v2 = multiply(v, v);
  const uv = multiply(u, v);
  const length = Math.max(u2.length, v2.length);
  const xPrime: Frac[] = [];
  const yPrime = uv.map((c) => ({ n: 2n * c.n, d: c.d }));
  for (let i = 0; i < length; i += 1) {
    xPrime.push(fSub(u2[i] ?? ZERO, v2[i] ?? ZERO));
  }
  const x = [ZERO, ...xPrime.map((c, j) => fDiv(c, fr(BigInt(j + 1))))];
  const y = [ZERO, ...yPrime.map((c, j) => fDiv(c, fr(BigInt(j + 1))))];
  return { x: trim(x), y: trim(y) };
}

/** The grid: the least common multiple of the position terms' denominators. */
export function grid(speedX: SpeedRow, speedY: SpeedRow): number {
  const u = speedX.map((c) => toFraction(c));
  const v = speedY.map((c) => toFraction(c));
  const u2 = multiply(u, u);
  const v2 = multiply(v, v);
  const uv = multiply(u, v);
  const length = Math.max(u2.length, v2.length);
  let result = 1n;
  const rows: Frac[][] = [];
  const xPrime: Frac[] = [];
  for (let i = 0; i < length; i += 1) xPrime.push(fSub(u2[i] ?? ZERO, v2[i] ?? ZERO));
  rows.push(xPrime, uv.map((c) => ({ n: 2n * c.n, d: c.d })));
  for (const polynomial of rows) {
    polynomial.forEach((coefficient, j) => {
      if (coefficient.n === 0n) return;
      const denominator = fDiv(coefficient, fr(BigInt(j + 1))).d;
      result = (result / bgcd(result, denominator)) * denominator;
    });
  }
  if (result > BigInt(Number.MAX_SAFE_INTEGER)) return Number(result);
  return Number(result);
}

export function evaluate(coefficients: Frac[], t: Frac): Frac {
  let total = ZERO;
  for (let i = coefficients.length - 1; i >= 0; i -= 1) total = fAdd(fMul(total, t), coefficients[i]);
  return total;
}

/** How close the speed path comes to the origin. */
export function closest(speedX: SpeedRow, speedY: SpeedRow, samples = 800): number {
  const u = speedX.map((c) => toFraction(c));
  const v = speedY.map((c) => toFraction(c));
  let best = Infinity;
  for (let i = 0; i <= samples; i += 1) {
    const t = fr(BigInt(i), BigInt(samples));
    const du = evaluate(u, t), dv = evaluate(v, t);
    best = Math.min(best, Math.hypot(Number(du.n) / Number(du.d), Number(dv.n) / Number(dv.d)));
  }
  return best;
}

/** The nearest fraction to x with a denominator at most maxD — a faithful
 * port of CPython's Fraction.limit_denominator (best upper and lower
 * approximations from the continued fraction, closest wins, ties to the
 * smaller denominator). `self` here is the EXACT binary value of the double —
 * built from the IEEE bits, the same integers Python's Fraction(middle)
 * holds — and the closeness comparison is exact, not float. The bisection in
 * `inflections` depends on this matching Python exactly. */
export function limitDenominator(x: number, maxD = 1_000_000n): Frac {
  const buf = new ArrayBuffer(8);
  new Float64Array(buf)[0] = x;
  const bits = new BigUint64Array(buf)[0];
  const negative = (bits >> 63n) === 1n;
  const exponent = Number((bits >> 52n) & 0x7ffn);
  const mantissa = bits & ((1n << 52n) - 1n);
  let n: bigint, d: bigint;
  if (exponent === 0) { n = mantissa; d = 1n << 1074n; }
  else { n = mantissa | (1n << 52n); d = 1n << BigInt(1075 - exponent); }
  if (negative) n = -n;
  // CPython's early return tests the REDUCED denominator: the exact value of a
  // double is m/2^k, and 32768 <= 1e6 makes the loop unnecessary for it. My
  // first port tested the raw 2^k and looped into a zero remainder instead.
  const g = bgcd(n, d);
  n /= g; d /= g;
  if (d <= maxD) return { n, d };
  const selfN = n, selfD = d;   // the exact self, captured before the loop
                                // mutates n and d into the CF tail
  let p0 = 0n, q0 = 1n, p1 = 1n, q1 = 0n;
  for (;;) {
    const a = n / d;
    const q2 = q0 + a * q1;
    if (q2 > maxD) break;
    [p0, q0, p1, q1] = [p1, q1, p0 + a * p1, q2];
    [n, d] = [d, n - a * d];
  }
  const k = (maxD - q0) / q1;
  const bound1 = fr(p0 + k * p1, q0 + k * q1);
  const bound2 = { n: p1, d: q1 };
  // exact closeness: |bound - self| cross-multiplied over the shared self.d
  const numerator = (b: Frac) => {
    const left = b.n * selfD - selfN * b.d;
    return left < 0n ? -left : left;
  };
  const forTwo = numerator(bound2) * bound1.d;
  const forOne = numerator(bound1) * bound2.d;
  if (forTwo <= forOne) return bound2;
  return bound1;
}

/** Every inflection in (0, 1): the roots of the Wronskian p q' - q p'. */
export function inflections(speedX: SpeedRow, speedY: SpeedRow, samples = 800): number[] {
  const u = speedX.map((c) => toFraction(c));
  const v = speedY.map((c) => toFraction(c));
  const left = multiply(u, derivative(v));
  const right = multiply(v, derivative(u));
  const length = Math.max(left.length, right.length);
  const wronskian: Frac[] = [];
  for (let i = 0; i < length; i += 1) wronskian.push(fSub(left[i] ?? ZERO, right[i] ?? ZERO));
  if (!wronskian.some((c) => c.n !== 0n)) return [];
  const values: number[] = [];
  for (let i = 0; i <= samples; i += 1) {
    values.push(Number(evaluate(wronskian, fr(BigInt(i), BigInt(samples))).n) /
      Number(evaluate(wronskian, fr(BigInt(i), BigInt(samples))).d));
  }
  const found: number[] = [];
  for (let i = 0; i < samples; i += 1) {
    if (values[i] === 0.0 || values[i] * values[i + 1] < 0) {
      let low = i / samples, high = (i + 1) / samples;
      for (let step = 0; step < 50; step += 1) {
        const middle = (low + high) / 2;
        const at = evaluate(wronskian, limitDenominator(middle, 1_000_000n));
        if (values[i] * (Number(at.n) / Number(at.d)) <= 0) high = middle;
        else low = middle;
      }
      const where = (low + high) / 2;
      if (1e-6 < where && where < 1 - 1e-6 && !found.some((other) => Math.abs(other - where) < 1e-4)) {
        found.push(where);
      }
    }
  }
  return found;
}

export function inflection(speedX: SpeedRow, speedY: SpeedRow, samples = 800): number | null {
  const found = inflections(speedX, speedY, samples);
  return found.length ? found[0] : null;
}

/** Everything a gallery shows, at any degree, JSON-ready. */
export function metrics(speedX: SpeedRow, speedY: SpeedRow) {
  const { arc, bend: bendValue } = arcAndChord(speedX, speedY);
  const every = inflections(speedX, speedY);
  const gridValue = grid(speedX, speedY);
  return {
    bend: bendValue,
    arc: Number(arc.n) / Number(arc.d),
    grid: gridValue,
    pitch: gridValue,
    inflection: every.length ? every[0] : null,
    inflections: every,
    inflection_count: every.length,
    inflection_max: 2 * Math.max(speedX.length, speedY.length) - 3,
    closest: closest(speedX, speedY),
  };
}
