"""Integer hits for a polynomial PH curve, at any degree.

    from ph_quintic_hits import hits_at_stops, hits_exact, near_misses

`r(t) = integral of w^2`, `w = u + i v`.  Three questions, three functions:

- `hits_at_stops(u, v)` - the lattice points at `t = m/pitch`.  Exact, cheap,
  and the canonical grid.  It is **not** complete: `x = t, y = t^2` has pitch 1
  and integer points at every integer `t`, while its stops see only `0` and `1`.
- `hits_exact(u, v, box)` - every lattice point in the box.  For each integer
  point `(X, Y)` it takes the gcd of `x(t) - X` and `y(t) - Y` over the
  rationals; a non-constant gcd means the point is on the curve, and its roots
  are the parameters - rational or algebraic.  Complete, and `O(area)`.
- `near_misses(u, v, box)` - how close the curve comes to a lattice point
  between stops.  A different question: it is not a hit list.

Example: `w = 1 + i t` has a hit at `(0, 3)` with `t = sqrt(3)`.  The stops
(pitch 3) miss it; `hits_exact` finds it, because `gcd(t - t^3/3, t^2 - 3)` is
`t^2 - 3`.
"""

from __future__ import annotations

import math
from fractions import Fraction

from ph_quintic_metrics import pitch, to_fraction

__all__ = [
    "curve_polynomials",
    "bounding_box",
    "hits_at_stops",
    "hits_exact",
    "near_misses",
]


def _multiply(left, right):
    product = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            product[i + j] += a * b
    return product


def _subtract(left, right):
    length = max(len(left), len(right))
    return [(left[i] if i < len(left) else Fraction(0))
            - (right[i] if i < len(right) else Fraction(0))
            for i in range(length)]


def _trim(polynomial):
    out = list(polynomial)
    while out and not out[-1]:
        out.pop()
    return out


def _evaluate(polynomial, t):
    total = Fraction(0)
    for coefficient in reversed(polynomial):
        total = total * t + coefficient
    return total


def curve_polynomials(speed_x, speed_y):
    """x(t) and y(t) as coefficient lists, from the speed recipes."""
    u = [to_fraction(coefficient) for coefficient in speed_x]
    v = [to_fraction(coefficient) for coefficient in speed_y]
    u_squared = _multiply(u, u)
    v_squared = _multiply(v, v)
    u_times_v = _multiply(u, v)
    x_prime = _subtract(u_squared, v_squared)
    y_prime = [2 * coefficient for coefficient in u_times_v]
    x = [Fraction(0)] + [coefficient / (j + 1) for j, coefficient in enumerate(x_prime)]
    y = [Fraction(0)] + [coefficient / (j + 1) for j, coefficient in enumerate(y_prime)]
    return _trim(x), _trim(y)


def _poly_divmod(dividend, divisor):
    dividend = _trim(dividend)
    divisor = _trim(divisor)
    if not divisor:
        raise ZeroDivisionError("polynomial division by zero")
    quotient = [Fraction(0)] * max(1, len(dividend) - len(divisor) + 1)
    remainder = list(dividend)
    while len(remainder) >= len(divisor) and _trim(remainder):
        shift = len(remainder) - len(divisor)
        factor = remainder[-1] / divisor[-1]
        quotient[shift] = factor
        for i, coefficient in enumerate(divisor):
            remainder[shift + i] -= factor * coefficient
        remainder = _trim(remainder)
    return _trim(quotient), remainder


def _poly_gcd(left, right):
    a, b = _trim(left), _trim(right)
    while b:
        _, remainder = _poly_divmod(a, b)
        a, b = b, remainder
    if not a:
        return []
    lead = a[-1]
    return [coefficient / lead for coefficient in a]


def _roots_numeric(polynomial, samples=2000):
    """Real roots in [0, 1] of a small polynomial, by scan and bisection."""
    def value(t):
        total = 0.0
        for coefficient in reversed(polynomial):
            total = total * t + float(coefficient)
        return total

    roots = []
    previous = value(0.0)
    for i in range(1, samples + 1):
        t = i / samples
        current = value(t)
        if previous == 0.0:
            roots.append((i - 1) / samples)
        elif previous * current < 0:
            low, high = (i - 1) / samples, t
            for _ in range(60):
                middle = (low + high) / 2
                if value(low) * value(middle) <= 0:
                    high = middle
                else:
                    low = middle
            roots.append((low + high) / 2)
        previous = current
    if value(1.0) == 0.0:
        roots.append(1.0)
    return roots


def bounding_box(speed_x, speed_y, samples=600):
    x, y = curve_polynomials(speed_x, speed_y)
    xs, ys = [], []
    for i in range(samples + 1):
        t = Fraction(i, samples)
        xs.append(float(_evaluate(x, t)))
        ys.append(float(_evaluate(y, t)))
    return (min(xs), max(xs), min(ys), max(ys))


def hits_at_stops(speed_x, speed_y, scale=None):
    """Lattice points at t = m/pitch, on the curve scaled by the pitch.

    `scale` defaults to the pitch, which is the integer grid the gallery
    quotes ("endpoint (15, 4) at pitch 10").  Pass `scale=1` for the curve as
    written.
    """
    x, y = curve_polynomials(speed_x, speed_y)
    grid = pitch(speed_x, speed_y)
    factor = grid if scale is None else to_fraction(scale)
    hits = []
    for m in range(grid + 1):
        t = Fraction(m, grid)
        x_value = factor * _evaluate(x, t)
        y_value = factor * _evaluate(y, t)
        if x_value.denominator == 1 and y_value.denominator == 1:
            hits.append((t, int(x_value), int(y_value)))
    return hits


def hits_exact(speed_x, speed_y, box=None, scale=None, max_points=40000):
    """Every lattice point in the box, by polynomial gcd.

    Exact, but `O(area)`: keep the box small.  A non-constant gcd means the
    point is on the curve; its roots are the parameters, rational or not.
    """
    x, y = curve_polynomials(speed_x, speed_y)
    grid = pitch(speed_x, speed_y)
    factor = grid if scale is None else to_fraction(scale)
    x = [factor * coefficient for coefficient in x]
    y = [factor * coefficient for coefficient in y]
    if box is None:
        box = bounding_box(speed_x, speed_y)
        box = (box[0] * factor, box[1] * factor, box[2] * factor, box[3] * factor)
    min_x, max_x, min_y, max_y = box
    low_x, high_x = math.ceil(min_x - 1e-9), math.floor(max_x + 1e-9)
    low_y, high_y = math.ceil(min_y - 1e-9), math.floor(max_y + 1e-9)
    if (high_x - low_x + 1) * (high_y - low_y + 1) > max_points:
        raise ValueError("box too large; pass a smaller box")
    hits = []
    for X in range(low_x, high_x + 1):
        x_polynomial = _subtract(x, [Fraction(X)])
        for Y in range(low_y, high_y + 1):
            y_polynomial = _subtract(y, [Fraction(Y)])
            common = _poly_gcd(x_polynomial, y_polynomial)
            if len(_trim(common)) <= 1:
                continue
            parameters = _roots_numeric(common)
            hits.append({"point": (X, Y), "parameters": parameters,
                         "gcd_degree": len(_trim(common)) - 1})
    return hits


def near_misses(speed_x, speed_y, box=None, scale=None, samples=4000):
    """Distance from the curve to the nearest lattice point, at cell centres."""
    x, y = curve_polynomials(speed_x, speed_y)
    grid = pitch(speed_x, speed_y)
    factor = grid if scale is None else to_fraction(scale)
    x = [factor * coefficient for coefficient in x]
    y = [factor * coefficient for coefficient in y]
    if box is None:
        box = bounding_box(speed_x, speed_y)
        box = (box[0] * factor, box[1] * factor, box[2] * factor, box[3] * factor)
    min_x, max_x, min_y, max_y = box
    misses = []
    for i in range(samples + 1):
        t = Fraction(i, samples)
        x_value = float(_evaluate(x, t))
        y_value = float(_evaluate(y, t))
        if not (min_x - 1 <= x_value <= max_x + 1 and min_y - 1 <= y_value <= max_y + 1):
            continue
        nearest_x, nearest_y = round(x_value), round(y_value)
        distance = math.hypot(x_value - nearest_x, y_value - nearest_y)
        misses.append((distance, t, (nearest_x, nearest_y)))
    misses.sort()
    return misses


if __name__ == "__main__":
    print("the pick, stops:", hits_at_stops((2, -3, 3), (2, -12, 12)))
    print("w = 1 + i t, stops:", hits_at_stops((1, 0, 0), (0, 1, 0)))
    print("w = 1 + i t, exact:", hits_exact((1, 0, 0), (0, 1, 0), (-1, 2, -1, 4)))
    print("w = 1 + i t, nearest misses:",
          [(round(d, 4), str(t), point) for d, t, point in near_misses((1, 0, 0), (0, 1, 0))[:3]])
