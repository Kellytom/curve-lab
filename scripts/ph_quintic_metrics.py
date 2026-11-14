"""Exact metrics for a polynomial PH curve, at any degree.

    from ph_quintic_metrics import metrics
    metrics((2, -3, 3), (2, -12, 12))

The curve is `r(t) = integral of w(t)^2 dt` with `w = u + i v`, and `u`, `v`
are polynomials of any degree.  In the centred frame `h = t - 1/2`,

    w(h) = sum_k c_k h^k

and both integrals are finite sums, because

    integral of h^m over [-1/2, 1/2] = 0                  m odd
                                     = 1 / (2^m (m+1))    m even

so

    arc   = sum_{k,l} (cx_k cx_l + cy_k cy_l) * W(k+l)
    chord = sum_{k,l} (cx_k cx_l - cy_k cy_l) * W(k+l)
          + i sum_{k,l} (cx_k cy_l + cy_k cx_l) * W(k+l)
    bend  = arc / |chord|

Nothing is sampled.  Degree 2 gives the weights 1, 1/12, 1/80 used by the
gallery; degree 3 gives the next row, and so on.  The pitch, the inflection
and the closest approach are computed the same way at every degree.
"""

from __future__ import annotations

import math
from fractions import Fraction
from math import comb, lcm

__all__ = [
    "to_fraction",
    "curve_polynomials",
    "diagnostics",
    "centred",
    "weight",
    "exact_bend",
    "pitch",
    "inflection",
    "closest",
    "metrics",
]


def to_fraction(value, max_decimals: int = 6) -> Fraction:
    """An exact Fraction from a slider value, without binary noise.

    `Fraction(0.1)` is not 1/10, it is the exact binary approximation, and a
    pitch computed from it is meaningless.  Here a float is read as the
    shortest decimal that survives `max_decimals` places; strings are taken
    exactly, so "1/5" stays 1/5.
    """
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, str):
        return Fraction(value)
    return Fraction(f"{float(value):.{max_decimals}f}")


def weight(power: int) -> Fraction:
    """The integral of h^power over [-1/2, 1/2]."""
    if power % 2:
        return Fraction(0)
    return Fraction(1, (2 ** power) * (power + 1))


def centred(coefficients) -> list[Fraction]:
    """The coefficients in h = t - 1/2: w(t) = sum c_k h^k."""
    values = [to_fraction(coefficient) for coefficient in coefficients]
    out = [Fraction(0)] * len(values)
    for j, coefficient in enumerate(values):
        for k in range(j + 1):
            out[k] += coefficient * comb(j, k) * Fraction(1, 2) ** (j - k)
    return out


def exact_bend(speed_x, speed_y):
    """arc, chord (complex) and bend, exactly."""
    cx = centred(speed_x)
    cy = centred(speed_y)
    size = max(len(cx), len(cy))
    cx += [Fraction(0)] * (size - len(cx))
    cy += [Fraction(0)] * (size - len(cy))
    arc = Fraction(0)
    chord_re = Fraction(0)
    chord_im = Fraction(0)
    for k in range(len(cx)):
        for l in range(len(cx)):
            w = weight(k + l)
            if not w:
                continue
            arc += (cx[k] * cx[l] + cy[k] * cy[l]) * w
            chord_re += (cx[k] * cx[l] - cy[k] * cy[l]) * w
            chord_im += (cx[k] * cy[l] + cy[k] * cx[l]) * w
    chord_abs = math.hypot(float(chord_re), float(chord_im))
    bend = float(arc) / chord_abs if chord_abs > 1e-15 else math.inf
    return arc, complex(float(chord_re), float(chord_im)), bend


def _multiply(left, right):
    product = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            product[i + j] += a * b
    return product


def _derivative(coefficients):
    return [coefficients[i] * i for i in range(1, len(coefficients))]


def pitch(speed_x, speed_y) -> int:
    """The lcm of the integrated coefficients' denominators."""
    u = [to_fraction(coefficient) for coefficient in speed_x]
    v = [to_fraction(coefficient) for coefficient in speed_y]
    u_squared = _multiply(u, u)
    v_squared = _multiply(v, v)
    u_times_v = _multiply(u, v)
    x_prime = [u_squared[i] - (v_squared[i] if i < len(v_squared) else 0)
               for i in range(len(u_squared))]
    y_prime = [2 * coefficient for coefficient in u_times_v]
    result = 1
    for polynomial in (x_prime, y_prime):
        for j, coefficient in enumerate(polynomial):
            if not coefficient:
                continue
            result = lcm(result, Fraction(coefficient, j + 1).denominator)
    return result


def _evaluate(coefficients, t):
    total = Fraction(0)
    for coefficient in reversed(coefficients):
        total = total * t + coefficient
    return total


def inflection(speed_x, speed_y, samples: int = 800):
    """Where the tangent turns the other way, or None."""
    u = [to_fraction(coefficient) for coefficient in speed_x]
    v = [to_fraction(coefficient) for coefficient in speed_y]
    left = _multiply(u, _derivative(v))
    right = _multiply(v, _derivative(u))
    length = max(len(left), len(right))
    wronskian = [(left[i] if i < len(left) else Fraction(0))
                 - (right[i] if i < len(right) else Fraction(0))
                 for i in range(length)]
    if not any(wronskian):
        return None                   # a straight line has no inflection
    values = [float(_evaluate(wronskian, Fraction(i, samples)))
              for i in range(samples + 1)]
    for i in range(samples):
        if values[i] == 0.0:
            return i / samples
        if values[i] * values[i + 1] < 0:
            low, high = i / samples, (i + 1) / samples
            for _ in range(50):
                middle = (low + high) / 2
                if values[i] * float(_evaluate(wronskian, Fraction(middle).limit_denominator(10 ** 6))) <= 0:
                    high = middle
                else:
                    low = middle
            return (low + high) / 2
    return None


def closest(speed_x, speed_y, samples: int = 800) -> float:
    """How close the speed path comes to the origin."""
    u = [to_fraction(coefficient) for coefficient in speed_x]
    v = [to_fraction(coefficient) for coefficient in speed_y]
    best = math.inf
    for i in range(samples + 1):
        t = Fraction(i, samples)
        best = min(best, math.hypot(float(_evaluate(u, t)), float(_evaluate(v, t))))
    return best


def inflections(speed_x, speed_y, samples: int = 800) -> list:
    """Every inflection in (0, 1): the roots of the Wronskian p q' - q p'.

    The Wronskian has degree at most 2k - 1 for a speed of degree k, so this
    list can never be longer than that. A shorter list is the useful reading:
    it says the top powers are not turning the curve, so they can go.
    """
    u = [to_fraction(coefficient) for coefficient in speed_x]
    v = [to_fraction(coefficient) for coefficient in speed_y]
    left = _multiply(u, _derivative(v))
    right = _multiply(v, _derivative(u))
    length = max(len(left), len(right))
    wronskian = [(left[i] if i < len(left) else Fraction(0))
                 - (right[i] if i < len(right) else Fraction(0))
                 for i in range(length)]
    if not any(wronskian):
        return []                     # a straight line: no curvature, no inflection
    values = [float(_evaluate(wronskian, Fraction(i, samples)))
              for i in range(samples + 1)]
    found = []
    for i in range(samples):
        if values[i] == 0.0 or values[i] * values[i + 1] < 0:
            low, high = i / samples, (i + 1) / samples
            for _ in range(50):
                middle = (low + high) / 2
                if values[i] * float(_evaluate(wronskian, Fraction(middle).limit_denominator(10 ** 6))) <= 0:
                    high = middle
                else:
                    low = middle
            where = (low + high) / 2
            if not any(abs(other - where) < 1e-4 for other in found):
                found.append(where)
    return found


def metrics(speed_x, speed_y) -> dict:
    """Everything the gallery shows, at any degree."""
    arc, chord, bend = exact_bend(speed_x, speed_y)
    every = inflections(speed_x, speed_y)
    return {
        "bend": bend,
        "arc": float(arc),
        "chord": chord,
        "chord_length": abs(chord),
        "pitch": pitch(speed_x, speed_y),
        "inflection": inflection(speed_x, speed_y),
        "inflections": every,
        "inflection_count": len(every),
        "inflection_max": 2 * max(len(speed_x), len(speed_y)) - 3,
        "closest": closest(speed_x, speed_y),
    }




def curve_polynomials(speed_x, speed_y):
    """x(t) and y(t) as coefficient lists, from the speed recipes."""
    u = [to_fraction(coefficient) for coefficient in speed_x]
    v = [to_fraction(coefficient) for coefficient in speed_y]
    u_squared = _multiply(u, u)
    v_squared = _multiply(v, v)
    u_times_v = _multiply(u, v)
    x_prime = [u_squared[i] - (v_squared[i] if i < len(v_squared) else 0)
               for i in range(len(u_squared))]
    y_prime = [2 * coefficient for coefficient in u_times_v]
    x = [Fraction(0)] + [coefficient / (j + 1) for j, coefficient in enumerate(x_prime)]
    y = [Fraction(0)] + [coefficient / (j + 1) for j, coefficient in enumerate(y_prime)]
    return _trim(x), _trim(y)


def _trim(polynomial):
    out = list(polynomial)
    while out and not out[-1]:
        out.pop()
    return out


def diagnostics(speed_x, speed_y):
    """The degeneracy checks, in one place, with a level and a message."""
    x, y = curve_polynomials(speed_x, speed_y)

    def degree(polynomial):
        for k in range(len(polynomial) - 1, -1, -1):
            if polynomial[k]:
                return k
        return 0

    def is_zero(polynomial):
        return all(not coefficient for coefficient in polynomial) or not polynomial

    degree_x, degree_y = degree(x), degree(y)
    m = metrics(speed_x, speed_y)
    report = [{"code": "degree", "level": "info",
               "message": f"degree {max(degree_x, degree_y)} (x {degree_x}, y {degree_y})"}]
    if degree_x == 0 and degree_y == 0:
        report.append({"code": "point", "level": "error",
                       "message": "the curve is a single point"})
    if is_zero(x) or is_zero(y):
        report.append({"code": "axis-line", "level": "error",
                       "message": "one coordinate is identically zero: an axis-aligned straight line"})
    if m["bend"] <= 1 + 1e-9:
        report.append({"code": "straight", "level": "warning",
                       "message": "the curve is a straight line (bend 1.00)"})
    if m["closest"] <= 1e-9:
        report.append({"code": "cusp", "level": "error",
                       "message": "the speed vanishes: a cusp"})
    if m["inflection"] is None:
        report.append({"code": "no-inflection", "level": "warning",
                       "message": "no inflection: a C, not an S"})
    return report


if __name__ == "__main__":
    for label, u, v in [
        ("the pick", (2, -3, 3), (2, -12, 12)),
        ("the target", (Fraction(1, 5), -2, 2), (Fraction(2, 5), Fraction(-3, 2), Fraction(8, 5))),
        ("degree 7", (1, 0, 0, 0), (0, 1, 0, 0)),
    ]:
        m = metrics(u, v)
        print(f"{label:10s} bend {m['bend']:6.3f}  pitch {m['pitch']:>6}  "
              f"inflection {m['inflection']}  closest {m['closest']:.2f}")
