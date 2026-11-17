"""Exact PH offsets in their native form: two polynomials over one.

The curve pages write a curve by its *speed pair* `(u, v)`: the derivative is

    C'(t) = (u² − v², 2uv),

so the speed is the polynomial `σ = u² + v²` and the unit tangent is `C'/σ`.
That is the Pythagorean-hodograph construction: the square root in the normal
is gone, so the offset at signed distance `d` is the rational curve

    O(t) = C(t) + d·(−y'(t), x'(t)) / σ(t),

a ratio of two exact polynomials. No Bézier form is used or needed here:
control points and weights are an export concern (`goals.md` S5).

`point_at` evaluates the offset exactly at a rational parameter. `first_interior_hit`
and `hits_at_scale` answer the lattice question: the smallest scale at which an
interior parameter lands on the integer lattice, and every such point at a given
scale. Both are searches over rational `t = k/q` up to `q_max`, not proofs — a
lattice point at an irrational parameter is missed, as `scripts/ph_quintic_hits.py`
also says.

Two different things in this repository get called "the integer cubic":

- `curve_lab/pyth_cubic.py` — integer *controls* from a Pythagorean triple. The
  curve is not PH, so its offset is fitted only (`scripts/integer_cubic_offset.py`).
- a speed pair such as `integer-105`'s — PH by construction, so its offset is
  exact (`scripts/integer_ph_rail.py`).
"""

from __future__ import annotations

import math
from fractions import Fraction
from math import gcd, lcm


# -- polynomial arithmetic, exact ------------------------------------------

def _multiply(left, right):
    product = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            product[i + j] += a * b
    return product


def _add(left, right):
    out = [Fraction(0)] * max(len(left), len(right))
    for i, a in enumerate(left):
        out[i] += a
    for i, b in enumerate(right):
        out[i] += b
    return out


def _scale(poly, factor):
    return [coefficient * Fraction(factor) for coefficient in poly]


def _integrate(poly):
    """The antiderivative with constant term zero."""
    return [Fraction(0)] + [coefficient / (i + 1)
                            for i, coefficient in enumerate(poly)]


def _derivative(poly):
    return [poly[i] * i for i in range(1, len(poly))]


def evaluate(poly, t):
    total = Fraction(0)
    for coefficient in reversed(poly):
        total = total * Fraction(t) + coefficient
    return total


def _evaluate_float(poly, t):
    total = 0.0
    for coefficient in reversed(poly):
        total = total * t + coefficient
    return total


def _trim(poly):
    out = list(poly)
    while out and out[-1] == 0:
        out.pop()
    return out or [Fraction(0)]


def _as_fractions(values):
    return [Fraction(value) for value in values]


# -- the PH construction ----------------------------------------------------

def hodograph_pair(u, v):
    """`(u² − v², 2uv)`: the derivative of the curve the pair writes."""
    u = _as_fractions(u)
    v = _as_fractions(v)
    return (_add(_multiply(u, u), _scale(_multiply(v, v), -1)),
            _scale(_multiply(u, v), 2))


def speed_squared(u, v):
    """`σ = u² + v²`: the speed, as a polynomial, so the normal is rational."""
    u = _as_fractions(u)
    v = _as_fractions(v)
    return _add(_multiply(u, u), _multiply(v, v))


def curve(u, v):
    """`C(t)` as two coefficient lists, with `C(0)` at the origin."""
    x_prime, y_prime = hodograph_pair(u, v)
    return _trim(_integrate(x_prime)), _trim(_integrate(y_prime))


def point_at(u, v, distance, t):
    """The exact offset point at a rational parameter."""
    x, y, x_prime, y_prime, sigma, d = _forms(u, v, distance)
    speed = evaluate(sigma, t)
    if speed == 0:
        raise ValueError("the speed vanishes at this parameter: a cusp")
    return (evaluate(x, t) - d * evaluate(y_prime, t) / speed,
            evaluate(y, t) + d * evaluate(x_prime, t) / speed)


def _forms(u, v, distance):
    """The four polynomials and the distance, computed once per sampler."""
    x, y = curve(u, v)
    x_prime, y_prime = hodograph_pair(u, v)
    return x, y, x_prime, y_prime, speed_squared(u, v), Fraction(distance)


def exact_sampler(u, v, distance=0):
    """An exact point callable with the polynomials built once.

    A search calls this tens of thousands of times; rebuilding the six
    products each time made a 400-step lattice search take a minute.
    """
    x, y, x_prime, y_prime, sigma, d = _forms(u, v, distance)

    def point(t):
        speed = evaluate(sigma, t)
        if speed == 0:
            raise ValueError("the speed vanishes at this parameter: a cusp")
        return (evaluate(x, t) - d * evaluate(y_prime, t) / speed,
                evaluate(y, t) + d * evaluate(x_prime, t) / speed)

    return point


def float_sampler(u, v, distance=0):
    """Point and tangent callables in floats, for a fit or a drawing.

    Exactness is checked with `point_at`; every measurement here is a float,
    which is what a fit error and an SVG coordinate are.
    """
    x = [float(c) for c in curve(u, v)[0]]
    y = [float(c) for c in curve(u, v)[1]]
    x_prime = [float(c) for c in hodograph_pair(u, v)[0]]
    y_prime = [float(c) for c in hodograph_pair(u, v)[1]]
    sigma = [float(c) for c in speed_squared(u, v)]
    d = float(Fraction(distance))

    def point(t):
        speed = _evaluate_float(sigma, t)
        if abs(speed) < 1e-15:
            return _evaluate_float(x, t), _evaluate_float(y, t)
        return (_evaluate_float(x, t)
                - d * _evaluate_float(y_prime, t) / speed,
                _evaluate_float(y, t)
                + d * _evaluate_float(x_prime, t) / speed)

    def tangent(t):
        return math.atan2(_evaluate_float(y_prime, t),
                          _evaluate_float(x_prime, t))

    return point, tangent


def point_at_float(u, v, distance, t):
    """One point in floats, through the same polynomial ratio."""
    point, _ = float_sampler(u, v, distance)
    return point(t)


def curvature_peak(u, v, samples=4000):
    """The largest |κ| on `t ∈ [0, 1]`, so a caller can check for a fold.

    `κ = (x'y'' − y'x'') / σ³` because `|C'| = σ` for this parameterisation.
    Floats: this is a check, not a claim.
    """
    x_prime, y_prime = hodograph_pair(u, v)
    x_second = _derivative(x_prime)
    y_second = _derivative(y_prime)
    sigma = speed_squared(u, v)

    def at(t):
        speed = float(evaluate(sigma, t))
        if speed == 0:
            return float("inf")
        cross = (float(evaluate(x_prime, t)) * float(evaluate(y_second, t))
                 - float(evaluate(y_prime, t)) * float(evaluate(x_second, t)))
        return abs(cross) / speed ** 3

    return max(at(i / samples) for i in range(samples + 1))


# -- the lattice ------------------------------------------------------------

def lattice_scale(point):
    """The least whole-number scale that puts this rational point on the lattice."""
    return lcm(point[0].denominator, point[1].denominator)


def first_interior_hit(u, v, distance=0, q_max=24):
    """The smallest scale at which a *new* lattice point appears.

    Searches `t = k/q` with `2 ≤ q ≤ q_max` and `0 < k < q`. Returns the scale,
    the parameter as a `(k, q)` pair, and the model-space point, all exact.
    """
    best = None
    point = exact_sampler(u, v, distance)
    for q in range(2, q_max + 1):
        for k in range(1, q):
            if gcd(k, q) != 1:
                continue
            t = Fraction(k, q)
            at = point(t)
            scale = lattice_scale(at)
            if best is None or scale < best["scale"]:
                best = {"scale": scale, "t": (k, q), "point": at}
    return best


def hits_at_scale(u, v, scale, distance=0, q_max=24):
    """Every distinct lattice point on the curve at `scale`, over `t = k/q`.

    De-duplicated by point, so `t = 1/2` and `t = 2/4` are one hit.
    """
    factor = Fraction(scale)
    point = exact_sampler(u, v, distance)
    hits = {}
    for q in range(1, q_max + 1):
        for k in range(q + 1):
            t = Fraction(k, q)
            x, y = point(t)
            x, y = x * factor, y * factor
            if x.denominator == 1 and y.denominator == 1:
                hits[(int(x), int(y))] = t
    return sorted(({"point": point, "t": str(t)}
                   for point, t in hits.items()),
                  key=lambda hit: (hit["point"][0], hit["point"][1]))


def assert_rails_are_labelled(exact, fitted):
    """Fail if the two rails are swapped or mislabelled.

    The exact rail is a ratio of polynomials; the fitted rail is a cubic chain
    with a measured miss. Swapping them is the fault this guards.
    """
    if exact.get("kind") != "exact" or fitted.get("kind") != "fitted":
        raise ValueError("the exact rail must say exact and the fit must say fitted")
    if "coefficients" not in exact:
        raise ValueError("the exact rail has no polynomial data: the rails are swapped")
    if "spans" not in fitted or "error" not in fitted:
        raise ValueError("the fitted rail has no cubic spans: the rails are swapped")
