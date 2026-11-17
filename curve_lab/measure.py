"""The exact numbers for a curve: grid, bend, arc, inflections, closest.

This is the one reference implementation. A page, a script or a report that
quotes a grid or a bend for a stored curve should get the number from here, or
from a file this module wrote, and should never compute it a second time in
floating point.

Why it matters, measured 2026-11-16. `loop-13-15-17-mid-1` has a constant x
speed of 1 and a y speed with whole numbers up to 1.03e8. The exact grid is 36.
The page's JavaScript, which scales the row to whole numbers and then squares
it, got 5,148 — 36 times 11 times 13 — because a squared coefficient reached
1.06e16, past the 9.0e15 where a double stops counting by ones. Two arithmetic
lines, two answers, one curve. This module is the answer that survives.

Vocabulary, because two words are used for one thing. The *grid* is the
denominator a curve's integers need: grid 36 means the position terms are whole
numbers once multiplied by 36, and a page writes it "grid 1/36". Older code and
some pages call the same number the *pitch*. Both appear here; `grid` is the
name to use in new text.

Everything is `Fraction` until a float is printed, so nothing rounds on the way
in. Coefficients given as floats are read through their decimal text, not their
binary value: 0.1 is one tenth, not 0.1000000000000000055511151231257827.
"""

from __future__ import annotations

import math
from fractions import Fraction
from math import comb

__all__ = [
    "arc_and_chord",
    "bend",
    "centred",
    "closest",
    "curve_polynomials",
    "grid",
    "inflection",
    "inflections",
    "metrics",
    "speeds_from_terms",
    "to_fraction",
    "weight",
]


def to_fraction(value, max_decimals: int = 6) -> Fraction:
    """A coefficient as an exact fraction.

    A float is read as the decimal it prints to, with six places at most. That
    is deliberate: a page writes 0.1 and means one tenth, while the float holds
    a binary approximation. Six places is the precision the pages offer, so it
    is the precision taken here.
    """
    if isinstance(value, Fraction):
        return value
    if isinstance(value, str):
        return Fraction(value)
    return Fraction(f"{float(value):.{max_decimals}f}")


def weight(power: int) -> Fraction:
    """The integral of h^power over [-1/2, 1/2]."""
    if power % 2:
        return Fraction(0)
    return Fraction(1, (2**power) * (power + 1))


def centred(coefficients) -> list[Fraction]:
    """The coefficients in h = t - 1/2: w(t) = sum c_k h^k.

    Centring puts the integral's symmetry at h = 0, which is what makes the
    arc an ordinary dot product of the squared rows instead of a double sum
    over t.
    """
    values = [to_fraction(coefficient) for coefficient in coefficients]
    out = [Fraction(0)] * len(values)
    for j, coefficient in enumerate(values):
        for k in range(j + 1):
            out[k] += coefficient * comb(j, k) * Fraction(1, 2) ** (j - k)
    return out


def arc_and_chord(speed_x, speed_y):
    """(arc, chord, bend), exactly: the arc is a Fraction, the chord a complex.

    The arc length of a polynomial speed path is the integral of p^2 + q^2 over
    t in [0, 1], and the chord is the integral of (p + i q)^2. Both are exact
    because they are polynomials in t, not sampled curves.
    """
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
    bend_value = float(arc) / chord_abs if chord_abs > 1e-15 else math.inf
    return arc, complex(float(chord_re), float(chord_im)), bend_value


def bend(speed_x, speed_y) -> float:
    """Arc over chord. 1.00 is a straight line; larger is a fuller loop."""
    return arc_and_chord(speed_x, speed_y)[2]


def _multiply(left, right):
    product = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            product[i + j] += a * b
    return product


def _derivative(coefficients):
    return [coefficients[i] * i for i in range(1, len(coefficients))]


def curve_polynomials(speed_x, speed_y):
    """x(t) and y(t) as coefficient lists, from the speed recipes."""
    u = [to_fraction(coefficient) for coefficient in speed_x]
    v = [to_fraction(coefficient) for coefficient in speed_y]
    u_squared = _multiply(u, u)
    v_squared = _multiply(v, v)
    u_times_v = _multiply(u, v)
    # Reach as far as the longer square. Building this over the x row alone
    # drops the y terms past its length, which shortens the position and
    # under-reports the grid.
    length = max(len(u_squared), len(v_squared))
    x_prime = [
        (u_squared[i] if i < len(u_squared) else Fraction(0))
        - (v_squared[i] if i < len(v_squared) else Fraction(0))
        for i in range(length)
    ]
    y_prime = [2 * coefficient for coefficient in u_times_v]
    x = [Fraction(0)] + [coefficient / (j + 1) for j, coefficient in enumerate(x_prime)]
    y = [Fraction(0)] + [coefficient / (j + 1) for j, coefficient in enumerate(y_prime)]
    return _trim(x), _trim(y)


def _trim(polynomial):
    out = list(polynomial)
    while out and not out[-1]:
        out.pop()
    return out


def grid(speed_x, speed_y) -> int:
    """The grid: the least common multiple of the position terms' denominators.

    Read off the squared speed rows, because the position is their integral
    term by term and each term is divided by one more than its power.
    """
    u = [to_fraction(coefficient) for coefficient in speed_x]
    v = [to_fraction(coefficient) for coefficient in speed_y]
    u_squared = _multiply(u, u)
    v_squared = _multiply(v, v)
    u_times_v = _multiply(u, v)
    length = max(len(u_squared), len(v_squared))
    x_prime = [
        (u_squared[i] if i < len(u_squared) else Fraction(0))
        - (v_squared[i] if i < len(v_squared) else Fraction(0))
        for i in range(length)
    ]
    y_prime = [2 * coefficient for coefficient in u_times_v]
    result = 1
    for polynomial in (x_prime, y_prime):
        for j, coefficient in enumerate(polynomial):
            if not coefficient:
                continue
            result = math.lcm(result, Fraction(coefficient, j + 1).denominator)
    return result


def _evaluate(coefficients, t):
    total = Fraction(0)
    for coefficient in reversed(coefficients):
        total = total * t + coefficient
    return total


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
    wronskian = [
        (left[i] if i < len(left) else Fraction(0))
        - (right[i] if i < len(right) else Fraction(0))
        for i in range(length)
    ]
    if not any(wronskian):
        return []  # a straight line: no curvature, no inflection
    values = [float(_evaluate(wronskian, Fraction(i, samples))) for i in range(samples + 1)]
    found = []
    for i in range(samples):
        if values[i] == 0.0 or values[i] * values[i + 1] < 0:
            low, high = i / samples, (i + 1) / samples
            for _ in range(50):
                middle = (low + high) / 2
                if values[i] * float(
                    _evaluate(wronskian, Fraction(middle).limit_denominator(10**6))
                ) <= 0:
                    high = middle
                else:
                    low = middle
            where = (low + high) / 2
            if 1e-6 < where < 1 - 1e-6 and not any(abs(other - where) < 1e-4 for other in found):
                found.append(where)
    return found


def inflection(speed_x, speed_y, samples: int = 800):
    """Where the tangent turns the other way first, or None.

    Read from `inflections`, so the single value and the count can never
    disagree, and a root at the very start or end does not count.
    """
    found = inflections(speed_x, speed_y, samples)
    return found[0] if found else None


def speeds_from_terms(terms):
    """(speed_x, speed_y) rows from a record's terms.

    A record lists `{"power": k, "x": ..., "y": ...}`; a row is indexed by
    power, with zeros where a power carries nothing. This is the only place a
    record becomes rows, so a page and a test cannot build different ones.
    """
    if not terms:
        raise ValueError("a record with no terms has no curve")
    length = max(int(term["power"]) for term in terms) + 1
    speed_x = [Fraction(0)] * length
    speed_y = [Fraction(0)] * length
    for term in terms:
        power = int(term["power"])
        speed_x[power] += to_fraction(term["x"])
        speed_y[power] += to_fraction(term["y"])
    return speed_x, speed_y


def metrics(speed_x, speed_y) -> dict:
    """Everything a gallery shows, at any degree.

    `grid` and `pitch` carry the same number. `pitch` stays for the pages and
    scripts that already read it; new code should read `grid`.
    """
    arc, chord, bend_value = arc_and_chord(speed_x, speed_y)
    every = inflections(speed_x, speed_y)
    grid_value = grid(speed_x, speed_y)
    return {
        "bend": bend_value,
        "arc": float(arc),
        "arc_exact": arc,
        "chord": chord,
        "chord_length": abs(chord),
        "grid": grid_value,
        "pitch": grid_value,
        "inflection": every[0] if every else None,
        "inflections": every,
        "inflection_count": len(every),
        "inflection_max": 2 * max(len(speed_x), len(speed_y)) - 3,
        "closest": closest(speed_x, speed_y),
    }
