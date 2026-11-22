// The degree-11 reducer: exact at the chosen knots, the interior miss in
// Fraction. Port twin: reduction/parity/reduce_reference.py (same algorithm
// in Python Fraction) — the solved coefficients are the UNIQUE interpolating
// polynomial at the chosen rational nodes, so parity means identical
// coefficients, not close ones.
//
// Method: split [0, 1] into equal pieces; on each piece, interpolate the
// exact polynomial at `degree + 1` rational nodes shaped like Chebyshev
// points (clustered at the piece ends, rounded to 1e-9 rationals — cosines
// are not rational, so the nodes are chosen rationals in the Chebyshev
// shape); solve the Vandermonde system exactly by Gaussian elimination over
// Fraction. The interior miss is then measured exactly on a 65-point
// Fraction grid and reported as a share of the curve's size.

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
export const fNum = (a: Frac): number => Number(a.n) / Number(a.d);

export function evaluate(p: Poly, x: Frac): Frac {
  let total = ZERO;
  for (let i = p.length - 1; i >= 0; i -= 1) total = fAdd(fMul(total, x), p[i]);
  return total;
}

/** `degree + 1` rational nodes in [lo, hi], clustered toward the piece ends
 * in the Chebyshev shape and rounded to 1e-9 — the interpolation is exact at
 * exactly these rationals. The same rounding runs in the Python twin, so the
 * nodes match. */
export function chebyshevNodes(lo: number, hi: number, count: number): Frac[] {
  const nodes: Frac[] = [];
  for (let i = 0; i < count; i += 1) {
    const t = Math.cos((Math.PI * (2 * i + 1)) / (2 * count));
    const x = (lo + hi) / 2 + (hi - lo) / 2 * t;
    const rounded = Math.round(x * 1e9) / 1e9;
    nodes.push(fr(BigInt(Math.round(rounded * 1e9)), 1000000000n));
  }
  return nodes;
}

/** Solve the Vandermonde system exactly: the polynomial of degree n−1 with
 * p(x_j) = y_j at n distinct nodes, by Gaussian elimination over Fraction. */
export function interpolate(nodes: Frac[], values: Frac[]): Poly {
  const n = nodes.length;
  const m: Frac[][] = nodes.map((x, i) => {
    const row: Frac[] = [];
    let power = fr(1n);
    for (let k = 0; k < n; k += 1) { row.push(power); power = fMul(power, x); }
    row.push(values[i]);
    return row;
  });
  for (let col = 0; col < n; col += 1) {
    let pivot = -1;
    for (let r = col; r < n; r += 1) if (m[r][col].n !== 0n) { pivot = r; break; }
    if (pivot === -1) throw new Error("singular system: duplicate nodes");
    [m[col], m[pivot]] = [m[pivot], m[col]];
    m[col] = m[col].map((v) => fDiv(v, m[col][col]));
    for (let r = 0; r < n; r += 1) {
      if (r === col || m[r][col].n === 0n) continue;
      const factor = m[r][col];
      m[r] = m[r].map((v, k) => fSub(v, fMul(factor, m[col][k])));
    }
  }
  return Array.from({ length: n }, (_, r) => m[r][n]);
}

export interface PieceResult {
  lo: number; hi: number;
  coeffs: Poly;      // the reduced piece, degree <= 11
  maxMiss: Frac;     // the exact interior miss over the piece
  maxMissAt: Frac;
}

/** Reduce one exact polynomial to `degree` on [lo, hi]. */
export function reducePiece(exact: Poly, lo: number, hi: number, degree = 11): PieceResult {
  const nodes = chebyshevNodes(lo, hi, degree + 1);
  const values = nodes.map((x) => evaluate(exact, x));
  const coeffs = interpolate(nodes, values);
  const steps = 64;
  let maxMiss = ZERO, maxMissAt = fr(BigInt(Math.round(lo * 1e9)), 1000000000n);
  for (let i = 0; i <= steps; i += 1) {
    const x = fr(
      BigInt(Math.round(lo * 1e9)) * (BigInt(steps) - BigInt(i)) +
      BigInt(Math.round(hi * 1e9)) * BigInt(i),
      BigInt(steps) * 1000000000n);
    const miss = fSub(evaluate(exact, x), evaluate(coeffs, x));
    if (fNum(miss) > fNum(maxMiss)) { maxMiss = miss; maxMissAt = x; }
  }
  return { lo, hi, coeffs, maxMiss, maxMissAt };
}

export interface ReducedCurve {
  pieces: PieceResult[];
  degree: number;
  piecesCount: number;
  maxMiss: Frac;        // the worst interior miss over all pieces (exact)
  maxMissAt: Frac;      // where it happens (t in [0, 1])
  maxMissShare: number; // the miss as a share of the curve's size
  size: number;         // the bounding-box diagonal of the exact curve
}

/** Reduce a whole curve: split [0, 1] into `pieces` equal intervals.
 * `size` is the bounding-box diagonal of the exact curve, for the share. */
export function reduceCurve(exact: Poly, size: number, degree = 11, pieces = 2): ReducedCurve {
  const out: PieceResult[] = [];
  for (let i = 0; i < pieces; i += 1) {
    const lo = i / pieces, hi = (i + 1) / pieces;
    out.push(reducePiece(exact, lo, hi, degree));
  }
  let worst = out[0];
  for (const piece of out.slice(1)) {
    if (fNum(piece.maxMiss) > fNum(worst.maxMiss)) worst = piece;
  }
  const globalAt = fr(
    BigInt(Math.round(worst.lo * 1e9)) +
    BigInt(Math.round((worst.maxMissAt[0] / 1e9 - worst.lo) * 1e9 * pieces)) * 0n +
    BigInt(Math.round((fNum(worst.maxMissAt) - worst.lo) * pieces * 1e9)), 1000000000n * BigInt(pieces));
  void globalAt;
  return {
    pieces: out, degree, piecesCount: pieces,
    maxMiss: worst.maxMiss,
    maxMissAt: fr(BigInt(Math.round((fNum(worst.maxMissAt) * pieces - Math.round(worst.lo * pieces)) * 1e9)), 1000000000n * BigInt(pieces)),
    maxMissShare: fNum(worst.maxMiss) / size,
    size,
  };
}
