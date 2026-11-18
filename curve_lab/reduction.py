"""Is a parametric curve traced once, or is it a cover of a simpler one?

The test, in words: evaluate the recipe at t and at s and subtract. Both
differences are divisible by (t - s); divide it out. If what is left shares a
factor in s, that factor is the pairing — which other parameter lands on the
same point — and the curve is a cover. If not, the recipe is proper: every
point is hit once, and there is no lower-degree version of the same curve.

`reduce_curve` then tries to name the simpler curve. A cover by a monomial,
`P(t) = Q(t^k)`, is reduced directly: the exponents of x and y must all be
multiples of k. A cover by a general polynomial is detected and its pairing
printed, but the substitution is not constructed yet — that is the honest
boundary of this file.

Everything is `Fraction`; no floats decide a verdict.
"""

from __future__ import annotations

from fractions import Fraction

SAMPLES = (Fraction(2), Fraction(3), Fraction(5), Fraction(7))


# -- univariate polynomials over Q, as [c0, c1, ...] ---------------------------

def trim(poly):
    while len(poly) > 1 and poly[-1] == 0:
        poly.pop()
    return poly


def degree(poly):
    return len(trim(list(poly))) - 1


def divmod_poly(a, b):
    a = list(a)
    b = trim(list(b))
    if b == [0]:
        raise ZeroDivisionError("polynomial division by zero")
    quotient = [Fraction(0)] * max(1, len(a) - len(b) + 1)
    while len(a) >= len(b) and a != [0]:
        a = trim(a)
        if len(a) < len(b):
            break
        shift = len(a) - len(b)
        factor = a[-1] / b[-1]
        quotient[shift] = factor
        for i, coefficient in enumerate(b):
            a[shift + i] -= factor * coefficient
        a = trim(a)
    return trim(quotient), trim(a)


def gcd_poly(a, b):
    a, b = trim(list(a)), trim(list(b))
    while b != [0]:
        _, remainder = divmod_poly(a, b)
        a, b = b, remainder
    if a == [0]:
        return [Fraction(1)]
    lead = a[-1]
    return [coefficient / lead for coefficient in a]


# -- the divided difference of a polynomial, as a polynomial in s ------------
#
#   p(t) - p(s) = (t - s) * sum_k c_k * (t^(k-1) + t^(k-2) s + ... + s^(k-1))
#
# so each term of p contributes a polynomial in s whose coefficients are
# monomials in t.

def divided_difference(poly):
    rows = []  # rows[j] = polynomial in t, the coefficient of s^j
    for power, coefficient in enumerate(poly):
        if coefficient == 0 or power == 0:
            continue
        for j in range(power):
            while len(rows) <= j:
                rows.append([Fraction(0)])
            t_power = power - 1 - j
            row = rows[j]
            while len(row) <= t_power:
                row.append(Fraction(0))
            row[t_power] += coefficient
    return rows or [[Fraction(0)]]


def evaluate_row(row, t0):
    value = Fraction(0)
    for power, coefficient in enumerate(row):
        value += coefficient * t0 ** power
    return value


def values_in_s(rows, t0):
    return [evaluate_row(row, t0) for row in rows]


def pairing_degree(x, y, t0):
    """Degree in s of the common factor at a generic t0; 0 means proper."""
    a = values_in_s(divided_difference(x), t0)
    b = values_in_s(divided_difference(y), t0)
    return degree(gcd_poly(a, b))


def is_proper(x, y):
    """Proper when no generic parameter has a partner landing on the same point."""
    return all(pairing_degree(x, y, t0) == 0 for t0 in SAMPLES)


def _common_power(x, y):
    """The largest k such that both x and y are polynomials in t^k, or 1."""
    exponents = set()
    for poly in (x, y):
        for power, coefficient in enumerate(poly):
            if coefficient:
                exponents.add(power)
    if not exponents:
        return 1
    smallest = min(exponents)
    if smallest == 0:
        return 1
    import math
    k = smallest
    for power in exponents:
        k = math.gcd(k, power)
    return max(1, k)


def reduce_curve(x, y):
    """Return a verdict: proper, or a monomial collapse, or an unnamed cover.

    x and y are coefficient lists in t (Fraction or int). The result is a dict:

        {"proper": True}
        {"proper": False, "cover": k, "curve": (qx, qy)}     # P(t) = Q(t^k)
        {"proper": False, "cover": k, "curve": None}         # cover, not named
    """
    x = [Fraction(c) for c in x]
    y = [Fraction(c) for c in y]
    if is_proper(x, y):
        return {"proper": True}
    k = _common_power(x, y)
    if k > 1:
        qx = [x[i] for i in range(0, len(x), k)]
        qy = [y[i] for i in range(0, len(y), k)]
        if (qx, qy) != (x, y):
            return {"proper": False, "cover": k, "curve": (trim(qx), trim(qy)),
                    "substitution": f"u = t^{k}"}
    # A cover whose substitution is not a monomial: the pairing is known, the
    # substitution is not constructed here.
    return {"proper": False, "cover": None, "curve": None,
            "note": "cover detected; substitution is not monomial"}
