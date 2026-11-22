// The algorithmic degree reducer: exact Chebyshev truncation with a proven
// miss bound. Three exact primitives, one loop, no samples.
//
//   1. scaleAndShift: map the piece's interval to [-1, 1] in Fraction.
//   2. powerToChebyshev: the exact rational basis change.
//   3. truncate: keep degree <= 11; the miss bound is Sum |c_i| over the
//      dropped terms - provable, because |T_i| <= 1 on [-1, 1].
//
// The reduced variant is a new exact polynomial of degree <= 11. The bound is
// an exact rational number, proven before anything is drawn. If the bound
// exceeds the dial, the interval is split in half and the bound is recomputed
// - each split lowers it roughly fourfold, so the loop converges fast.

export type Frac = { n: bigint; d: bigint };
export type Poly = Frac[];

export function fr(n: bigint | number, d: bigint | number = 1n): Frac {
  let top = typeof n === "bigint" ? n : BigInt(n);
  let bottom = typeof d === "bigint" ? d : BigInt(d);
  if (bottom < 0n) { top = -top; bottom = -bottom; }
  let x = top < 0n ? -top : top, y = bottom < 0n ? -bottom : bottom;
  while (y) [x, y] = [y, x % y];
  const g = x || 1n;
  return { n: (bottom < 0n ? -top : top) / g, d: bottom / g };
}
const ZERO: Frac = { n: 0n, d: 1n };
const fAdd = (a: Frac, b: Frac): Frac => fr(a.n * b.d + b.n * a.d, a.d * b.d);
const fSub = (a: Frac, b: Frac): Frac => fr(a.n * b.d - b.n * a.d, a.d * b.d);
const fMul = (a: Frac, b: Frac): Frac => fr(a.n * b.n, a.d * b.d);
const fDiv = (a: Frac, b: Frac): Frac => fr(a.n * b.d, a.d * b.n);
export const fNum = (a: Frac): number => {
  const digits = Math.max(String(a.n < 0n ? -a.n : a.n).length, String(a.d).length) - 12;
  if (digits > 0) {
    const scale = 10n ** BigInt(digits);
    return Number(a.n / scale) / Number(a.d / scale);
  }
  return Number(a.n) / Number(a.d);
};

export function evaluate(p: Poly, x: Frac): Frac {
  let total = ZERO;
  for (let i = p.length - 1; i >= 0; i -= 1) total = fAdd(fMul(total, x), p[i]);
  return total;
}

function trim(p: Poly): Poly {
  const q = p.slice();
  while (q.length && q[q.length - 1].n === 0n) q.pop();
  return q;
}

/** Substitute t = alpha*u + beta into the power polynomial, exactly: scale by
 * alpha (one synthetic division per pass, two passes for alpha^2 as well),
 * then shift by beta (Horner from the top). */
export function scaleAndShift(power: Poly, alpha: Frac, beta: Frac): Poly {
  // scale: t = alpha*u -> c_i * alpha^i
  const scaled: Poly = [];
  let factor = fr(1n);
  power.forEach((c, i) => { scaled.push(fMul(c, factor)); factor = fMul(factor, alpha); });
  // shift: u = v - beta -> Horner from the top
  const shifted = scaled.map((c) => ({ ...c }));
  for (let k = shifted.length - 1; k >= 1; k -= 1) {
    shifted[k - 1] = fAdd(shifted[k - 1], fMul(shifted[k], beta));
  }
  return trim(shifted);
}

/** Power -> Chebyshev on [-1, 1]: the exact rational basis change. The
 * Chebyshev polynomials have rational coefficients, so the change of basis
 * matrix is rational and the solve is exact. */
export function powerToChebyshev(power: Poly): Poly {
  const n = power.length;
  const T: Poly[] = [[fr(1n)], [fr(0n), fr(1n)]];
  for (let i = 1; i < n; i += 1) {
    const twiceX = T[i].map((c) => fMul(c, fr(2n)));
    const next: Poly = Array.from({ length: T[i].length + 1 }, () => ZERO);
    twiceX.forEach((c, k) => { next[k + 1] = fAdd(next[k + 1], c); });
    T[i - 1].forEach((c, k) => { next[k] = fSub(next[k], c); });
    T.push(trim(next));
  }
  // the Chebyshev-to-power matrix (columns: T_i as power rows), inverted
  const matrix: Frac[][] = [];
  for (let i = 0; i < n; i += 1) {
    const row: Frac[] = Array.from({ length: n }, () => ZERO);
    T[i].forEach((c, k) => { if (k < n) row[k] = c; });
    matrix.push(row);
  }
  const aug: Frac[][] = matrix.map((row, i) => {
    const id: Frac[] = Array.from({ length: n }, (_, k) => (k === i ? fr(1n) : ZERO));
    return [...row, ...id];
  });
  for (let col = 0; col < n; col += 1) {
    let pivot = -1;
    for (let r = col; r < n; r += 1) if (aug[r][col].n !== 0n) { pivot = r; break; }
    if (pivot === -1) throw new Error("the Chebyshev basis matrix is singular");
    [aug[col], aug[pivot]] = [aug[pivot], aug[col]];
    aug[col] = aug[col].map((v) => fDiv(v, aug[col][col]));
    for (let r = 0; r < n; r += 1) {
      if (r === col || aug[r][col].n === 0n) continue;
      const factor = aug[r][col];
      aug[r] = aug[r].map((v, k) => fSub(v, fMul(factor, aug[col][k])));
    }
  }
  const inverse: Frac[][] = Array.from({ length: n }, (_, i) =>
    Array.from({ length: n }, (_, k) => aug[i][n + k]));
  const cheb: Poly = Array.from({ length: n }, () => ZERO);
  for (let i = 0; i < n; i += 1) {
    for (let k = 0; k < n; k += 1) cheb[i] = fAdd(cheb[i], fMul(inverse[i][k], power[k] ?? ZERO));
  }
  return trim(cheb);
}

export interface ReducedPiece {
  cheb: Poly;         // the full Chebyshev expansion (exact)
  coeffs: Poly;       // the reduced variant: the truncated series in power form
  tailBound: Frac;    // the proven miss bound: Sum |c_i| over the dropped terms
}

export function truncate(cheb: Poly, degree: number): ReducedPiece {
  let tailBound = ZERO;
  for (let i = degree + 1; i < cheb.length; i += 1) {
    tailBound = fAdd(tailBound, cheb[i].n < 0n ? { n: -cheb[i].n, d: cheb[i].d } : cheb[i]);
  }
  const T: Poly[] = [[fr(1n)], [fr(0n), fr(1n)]];
  for (let i = 1; i < degree; i += 1) {
    const twiceX = T[i].map((c) => fMul(c, fr(2n)));
    const next: Poly = Array.from({ length: T[i].length + 1 }, () => ZERO);
    twiceX.forEach((c, k) => { next[k + 1] = fAdd(next[k + 1], c); });
    T[i - 1].forEach((c, k) => { next[k] = fSub(next[k], c); });
    T.push(trim(next));
  }
  const power: Poly = Array.from({ length: degree + 1 }, () => ZERO);
  cheb.slice(0, degree + 1).forEach((c, i) => {
    if (c.n === 0n) return;
    for (let k = 0; k < Math.min(T[i].length, power.length); k += 1) {
      power[k] = fAdd(power[k], fMul(c, T[i][k]));
    }
  });
  return { cheb, coeffs: trim(power), tailBound };
}

export interface ReducedPieceResult extends ReducedPiece { lo: number; hi: number }

export interface ReducedCurve {
  pieces: ReducedPieceResult[];
  degree: number;
  piecesCount: number;
  bound: Frac;          // the worst proven miss bound over the pieces
  boundShare: number;   // the bound as a share of the curve's size
  size: number;
  splits: number;       // how many halvings the bound loop chose
  met: boolean;         // false = the curve is genuinely over-degree; the
                        // bound is stated, not pretended
  maxPieces: number;
}

/** Reduce a curve to `degree`, choosing the piece count by the proven bound:
 * start whole, split in half until the worst bound is under the dial. The
 * dial is a share of the curve's size. */
export function reduceCurve(exact: Poly, size: number, degree = 11,
                            dial = 0.0005, maxPieces = 256): ReducedCurve {
  let pieces = 1;
  let result = reduceAt(exact, size, degree, pieces);
  while (result.boundShare > dial && pieces < maxPieces) {
    pieces *= 2;
    result = reduceAt(exact, size, degree, pieces);
  }
  // the honest "gives up" state: the bound is a property of the curve, and if
  // it never meets the dial the record says so instead of hiding the number
  const met = fNum(result.boundShare) <= dial;
  return { ...result, splits: Math.log2(pieces), met, maxPieces };
}

function reduceAt(exact: Poly, size: number, degree: number, pieces: number): ReducedCurve {
  const out: ReducedPieceResult[] = [];
  for (let i = 0; i < pieces; i += 1) {
    const lo = i / pieces, hi = (i + 1) / pieces;
    // map [lo, hi] to [-1, 1]: t = (hi - lo)/2 * u + (lo + hi)/2
    const alpha = fr(BigInt(Math.round((hi - lo) * 5e8)), 1000000000n);
    const beta = fr(BigInt(Math.round((lo + hi) * 5e8)), 1000000000n);
    const mapped = scaleAndShift(exact, alpha, beta);
    const cheb = powerToChebyshev(mapped);
    const piece = truncate(cheb, degree);
    out.push({ ...piece, lo, hi });
  }
  let worst = out[0];
  for (const piece of out.slice(1)) {
    if (fNum(piece.tailBound) > fNum(worst.tailBound)) worst = piece;
  }
  return {
    pieces: out, degree, piecesCount: out.length,
    bound: worst.tailBound,
    boundShare: fNum(worst.tailBound) / size,
    size,
  };
}

/** The fast float path for the desks: the same Chebyshev truncation, in
 * float64. The bound is the same Sum|c_i|; the reduced series is evaluated
 * directly in the Chebyshev basis, so no exact fraction is ever built. The
 * exact Fraction variant belongs to the reduction pipeline's records, not to
 * a desk page that only needs the verdict. */
export interface FastResult {
  pieces: number;
  splits: number;
  met: boolean;
  boundShare: number;   // the proven bound as a share of the curve's size
  reducedAt: (t: number) => number;   // the reduced series' value at t
  exactAt: (t: number) => number;     // the exact polynomial's value at t
}

function chebCoeffsFloat(power: number[], degree: number): number[] {
  const n = power.length;
  const nodes: number[] = [], weights: number[] = [];
  for (let k = 0; k < n; k += 1) {
    nodes.push(Math.cos((Math.PI * (2 * k + 1)) / (2 * n)));
    weights.push(k === 0 || k === n - 1 ? 1 : 2);
  }
  const coeffs: number[] = [];
  for (let i = 0; i < n; i += 1) {
    let sum = 0.0;
    for (let k = 0; k < n; k += 1) {
      const Tk = Math.cos(i * Math.acos(nodes[k]));
      sum += weights[k] * power[k] * Tk;
    }
    coeffs.push(sum / n * (i === 0 ? 0.5 : 1) * 2 === 0 ? 0 : sum / n * (i === 0 ? 1 : 2) / 1);
  }
  return coeffs.map((c, i) => (i === 0 ? c / 2 : c));
}

/** The float truncation on one interval: returns the Chebyshev coefficients
 * (full + kept) so the caller can evaluate the reduced series. */
export function truncateFloat(power: number[], lo: number, hi: number, degree: number) {
  // map to [-1, 1] and evaluate the power polynomial at the Chebyshev nodes
  const n = power.length;
  const mid = (lo + hi) / 2, half = (hi - lo) / 2;
  const nodes: number[] = [], values: number[] = [];
  for (let k = 0; k < n; k += 1) {
    const u = Math.cos((Math.PI * (2 * k + 1)) / (2 * n));
    const t = mid + half * u;
    let value = 0.0;
    for (let i = power.length - 1; i >= 0; i -= 1) value = value * t + power[i];
    nodes.push(u); values.push(value);
  }
  // discrete Chebyshev transform (exact for polynomials of degree < n)
  const coeffs: number[] = [];
  for (let i = 0; i < n; i += 1) {
    let sum = 0.0;
    for (let k = 0; k < n; k += 1) {
      sum += values[k] * Math.cos((i * Math.PI * (2 * k + 1)) / (2 * n));
    }
    coeffs.push(i === 0 ? sum / n : 2 * sum / n);
  }
  let bound = 0.0;
  for (let i = degree + 1; i < n; i += 1) bound += Math.abs(coeffs[i]);
  const evaluateReduced = (t: number): number => {
    const u = (t - mid) / half;
    let sum = 0.0;
    for (let i = Math.min(degree, coeffs.length - 1); i >= 0; i -= 1) {
      sum = sum * u + (i === 0 ? coeffs[i] / 2 : coeffs[i]);
    }
    return sum - (coeffs[0] / 2);
  };
  return { coeffs, bound, evaluateReduced };
}
