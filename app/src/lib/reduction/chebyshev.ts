// The proven truncation bound, exactly.
//
// A position polynomial P(t) is cut to degree `keep` on a piece [lo, hi] by
// rewriting it as a Chebyshev series in u = (2t − lo − hi)/(hi − lo) and
// dropping every coefficient past `keep`. Because |T_k(u)| ≤ 1 on [−1, 1],
// the sum of the dropped coefficients' absolute values is a guarantee: the
// worst miss on the piece is at most that sum. This module computes that sum
// in BigInt fractions — no float ever touches the bound.
//
// The path: substitute t = mid + half·u into the power form (binomial
// expansion, exact), then change basis from powers of u to Chebyshev
// polynomials (triangular solve against T_k's power forms, exact). The
// faults this replaces are in `state/REGRESSIONS-int.md` (row 54): a running
// sum standing in for the integral, and squared rows truncated at the speed
// rows' length.

import type { Frac } from "../measure.ts";

const ZERO: Frac = { n: 0n, d: 1n };
const ONE: Frac = { n: 1n, d: 1n };

function bgcd(a: bigint, b: bigint): bigint {
  let x = a < 0n ? -a : a;
  let y = b < 0n ? -b : b;
  while (y) [x, y] = [y, x % y];
  return x || 1n;
}

export function fr(n: bigint, d: bigint = 1n): Frac {
  if (d < 0n) [n, d] = [-n, -d];
  const g = bgcd(n, d);
  return { n: n / g, d: d / g };
}

const add = (a: Frac, b: Frac): Frac => fr(a.n * b.d + b.n * a.d, a.d * b.d);
const neg = (a: Frac): Frac => ({ n: -a.n, d: a.d });
const absF = (a: Frac): Frac => ({ n: a.n < 0n ? -a.n : a.n, d: a.d });

/** Q(u) = P(mid + half·u), exactly: expand each a_j·(mid + half·u)^j. */
export function substitute(coefficients: Frac[], mid: Frac, half: Frac): Frac[] {
  const out: Frac[] = Array.from({ length: coefficients.length }, () => ZERO);
  // powers of mid and half, precomputed (mid may be zero)
  const midPows: Frac[] = [ONE];
  for (let i = 0; i < coefficients.length; i += 1) {
    midPows.push(fr(midPows[i].n * mid.n, midPows[i].d * mid.d));
  }
  const halfPows: Frac[] = [ONE];
  for (let i = 0; i < coefficients.length; i += 1) {
    halfPows.push(fr(halfPows[i].n * half.n, halfPows[i].d * half.d));
  }
  coefficients.forEach((a, j) => {
    if (a.n === 0n) return;
    for (let k = 0; k <= j; k += 1) {
      let binom = 1n;
      for (let i = 0n; i < k; i += 1n) binom = (binom * BigInt(j - Number(i))) / (i + 1n);
      const m = midPows[j - k];
      const h = halfPows[k];
      out[k] = add(out[k], fr(a.n * m.n * h.n * binom, a.d * m.d * h.d));
    }
  });
  return out;
}

/** The Chebyshev polynomials T_0 … T_degree in power form, exact. */
function chebPowerForms(degree: number): Frac[][] {
  const forms: Frac[][] = [[ONE]];
  if (degree >= 1) forms.push([ZERO, ONE]);
  for (let k = 1; k < degree; k += 1) {
    // T_{k+1} = 2u·T_k − T_{k-1}; 2u·T_k shifts T_k up one degree and doubles
    const shifted: Frac[] = [ZERO, ...forms[k].map((c) => fr(2n * c.n, c.d))];
    const lower = forms[k - 1].map(neg);
    const size = shifted.length;
    const merged: Frac[] = Array.from({ length: size }, () => ZERO);
    for (let i = 0; i < size; i += 1) {
      merged[i] = add(shifted[i] ?? ZERO, lower[i] ?? ZERO);
    }
    forms.push(merged);
  }
  return forms;
}

/** P in powers of u → the same polynomial as a Chebyshev series, exact. */
export function powerToChebyshev(coefficients: Frac[]): Frac[] {
  const degree = coefficients.length - 1;
  const forms = chebPowerForms(degree);
  const work = coefficients.map((c) => ({ ...c }));
  const out: Frac[] = Array.from({ length: degree + 1 }, () => ZERO);
  for (let k = degree; k >= 0; k -= 1) {
    // T_k's leading term: u^k for k = 0, 2^(k-1)·u^k for k ≥ 1
    const lead: Frac = k === 0 ? ONE : fr(2n ** BigInt(k - 1));
    const ck = fr(
      (work[k] ?? ZERO).n * lead.d,
      (work[k] ?? ZERO).d * lead.n,
    );
    out[k] = ck;
    if (ck.n !== 0n) {
      for (let j = 0; j <= k; j += 1) {
        work[j] = add(work[j], fr(-ck.n * forms[k][j].n, ck.d * forms[k][j].d));
      }
    }
  }
  return out;
}

/** The proven bound: Σ|c_k| for k > keep, on the piece, exact. */
export function chebTailBound(
  coefficients: Frac[],
  mid: Frac,
  half: Frac,
  keep: number,
): Frac {
  const q = substitute(coefficients, mid, half);
  const c = powerToChebyshev(q);
  let sum = ZERO;
  for (let k = keep + 1; k < c.length; k += 1) sum = add(sum, absF(c[k]));
  return sum;
}

/** The truncated Chebyshev series at u (float, drawing only).
 *
 * The coefficients are the TRUE expansion's: Q(u) = Σ c_k·T_k(u) with T_0 = 1,
 * so the constant term enters whole — not halved as in the DCT convention. */
export function evalChebFloat(coefficients: Frac[], u: number): number {
  const clamped = Math.max(-1, Math.min(1, u));
  const angle = Math.acos(clamped);
  let sum = Number(coefficients[0].n) / Number(coefficients[0].d);
  for (let k = 1; k < coefficients.length; k += 1) {
    const c = coefficients[k];
    if (c.n === 0n) continue;
    sum += (Number(c.n) / Number(c.d)) * Math.cos(k * angle);
  }
  return sum;
}
