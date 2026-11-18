"""Find a parametric curve's self-intersections by elimination, not by sampling.

A crossing is a pair t ≠ s with z(t) = z(s). Divide by (t - s):

    P(t, s) = (z(t) - z(s)) / (t - s)

which is complex, so two real polynomial equations in s. Eliminate s by their
resultant: R(t) = Res_s(Re P, Im P). The roots of R are the candidate t values;
for each, solve for s and keep the pair when it is real, inside the parameter
range, distinct, and reproduces the point.

This replaces the segment scan that once reported fifty crossings on a straight
curve. The arithmetic here is floating point (resultant built by Sylvester
determinant, roots by np.roots); it is a measurement, not an exactness claim.

    curve = [c0, c1, ...]      # complex coefficients of z(t)

`crossing_pairs(curve)` returns [(t, s)] with t < s, deduplicated.
"""

from __future__ import annotations

import numpy as np

TOLERANCE = 1e-7


def divided_difference(curve):
    """P(t, s): rows[j] is the coefficient of s^j, a polynomial in t.

    (t^k - s^k)/(t - s) = t^(k-1) + t^(k-2) s + ... + s^(k-1)
    """
    degree = len(curve) - 1
    rows = []
    for j in range(degree):
        row = [0j] * degree  # coefficient of t^i
        for k in range(j + 1, degree + 1):
            row[k - 1 - j] += curve[k]
        rows.append(row)
    return rows  # rows[j][i] is the coefficient of t^i s^j


def evaluate_row(row, t):
    value = 0j
    for coefficient in reversed(row):
        value = value * t + coefficient
    return value


def sylvester_determinant(a, b):
    """Determinant of the Sylvester matrix of two coefficient lists in s."""
    a = np.trim_zeros(np.array(a, dtype=complex), "b")
    b = np.trim_zeros(np.array(b, dtype=complex), "b")
    m, n = len(a) - 1, len(b) - 1
    if m <= 0 or n <= 0:
        return 0j
    size = m + n
    matrix = np.zeros((size, size), dtype=complex)
    for i in range(n):
        matrix[i, i:i + m + 1] = a[::-1]
    for i in range(m):
        matrix[n + i, i:i + n + 1] = b[::-1]
    return np.linalg.det(matrix)


def resultant_polynomial(rows_re, rows_im, samples=160):
    """R(t) by evaluating the resultant at enough points, then interpolating."""
    degree_s = max(len(rows_re), len(rows_im))
    degree_t = max(len(row) for row in rows_re + rows_im)
    bound = max(1, degree_s * max(1, degree_t - 1) * 2)
    ts = np.linspace(-0.5, 1.5, samples)
    values = []
    for t in ts:
        a = [evaluate_row(rows_re[j], t) if j < len(rows_re) else 0j for j in range(degree_s)]
        b = [evaluate_row(rows_im[j], t) if j < len(rows_im) else 0j for j in range(degree_s)]
        values.append(sylvester_determinant(a, b))
    values = np.array(values, dtype=complex)
    degree = min(bound, samples - 1)
    coefficients = np.polynomial.polynomial.polyfit(ts, values.real, degree)
    return coefficients


def polynomial_roots(coefficients):
    trimmed = np.trim_zeros(np.array(coefficients, dtype=float), "b")
    if len(trimmed) <= 1:
        return []
    return list(np.roots(trimmed[::-1]))


def crossing_pairs(curve, t_range=(0.0, 1.0)):
    """Every (t, s) with z(t) = z(s), t < s, both inside the range."""
    rows = divided_difference(curve)
    rows_re = [[c.real for c in row] for row in rows]
    rows_im = [[c.imag for c in row] for row in rows]
    coefficients = resultant_polynomial(rows_re, rows_im)
    lo, hi = t_range
    candidates = []
    for root in polynomial_roots(coefficients):
        if abs(root.imag) > 1e-6:
            continue
        t = float(root.real)
        if not (lo - 1e-9 <= t <= hi + 1e-9):
            continue
        # partners: common roots of the two real polynomials in s
        a = np.array([evaluate_row(row, t).real for row in rows])
        b = np.array([evaluate_row(row, t).imag for row in rows])
        a = np.trim_zeros(a, "b")
        b = np.trim_zeros(b, "b")
        if len(a) <= 1 or len(b) <= 1:
            continue
        # common roots: gcd by np.roots intersection
        roots_a = np.roots(a[::-1])
        roots_b = np.roots(b[::-1])
        for ra in roots_a:
            if abs(ra.imag) > 1e-6:
                continue
            s = float(ra.real)
            if abs(s - t) < 1e-6 or not (lo - 1e-9 <= s <= hi + 1e-9):
                continue
            if min((abs(ra - rb) for rb in roots_b), default=1.0) < 1e-5:
                candidates.append((min(t, s), max(t, s)))
    # deduplicate, and confirm the points agree
    pairs = []
    for t, s in sorted(candidates):
        point_t = np.polyval(np.array(curve[::-1]), t)
        point_s = np.polyval(np.array(curve[::-1]), s)
        if abs(point_t - point_s) > 1e-4 * (1 + abs(point_t)):
            continue
        if all(abs(t - a) > 1e-4 or abs(s - b) > 1e-4 for a, b in pairs):
            pairs.append((t, s))
    return pairs
