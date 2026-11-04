"""Exact mirror-join probes for the integer cubic family.

The symmetric cubic has opposite endpoint curvatures. Reflecting it across its
endpoint tangent gives a curve with the same tangent and curvature at the
join, and scaling by the hypotenuse clears the reflection denominators. This
module builds that two-piece join and the three-piece chain with a mirror at
each end, using exact rational arithmetic.

It is a probe, not a general G2 solver. The mirrored pieces are symmetric; the
outer ends of the chain are free, and clearance is not checked.
"""

from __future__ import annotations

from fractions import Fraction
from functools import reduce
from math import gcd, isqrt

from . import pyth_cubic


def _lcm(a: int, b: int) -> int:
    return abs(a * b) // gcd(a, b) if a and b else 0


def _denominator(points) -> int:
    return reduce(
        _lcm,
        [abs(value.denominator) for point in points for value in point],
        1,
    )


def _reflect(point, origin, direction):
    """Reflect a point across a line with a rational unit direction."""
    vx, vy = point[0] - origin[0], point[1] - origin[1]
    dot = vx * direction[0] + vy * direction[1]
    return (
        origin[0] + 2 * dot * direction[0] - vx,
        origin[1] + 2 * dot * direction[1] - vy,
    )


def _as_fraction(points):
    return [(Fraction(x), Fraction(y)) for x, y in points]


def _scale(points, factor):
    return [(factor * x, factor * y) for x, y in points]


def _translate(points, dx, dy):
    return [(x + dx, y + dy) for x, y in points]


def _end_direction(case):
    a, b, c = case["a"], case["b"], case["c"]
    return (Fraction(a, c), Fraction(-b, c))


def mirror_at_end(case):
    """A copy whose start sits on the original end, ready to join there."""
    points = _as_fraction(
        (case["p0"], case["p1"], case["p2"], case["p3"]))
    q = points[3]
    reflected = [_reflect(point, q, _end_direction(case)) for point in points]
    start = reflected[0]
    return _translate(reflected, q[0] - start[0], q[1] - start[1])


def mirror_at_start(case):
    """A copy whose end sits on the original start, ready to precede it."""
    points = _as_fraction(
        (case["p0"], case["p1"], case["p2"], case["p3"]))
    p0 = points[0]
    reflected = [_reflect(point, p0, _end_direction(case)) for point in points]
    end = reflected[3]
    return _translate(reflected, p0[0] - end[0], p0[1] - end[1])


def endpoint_curvature(points, start: bool):
    """Signed curvature at an endpoint; None if the arm length is not integer."""
    if start:
        v = (points[1][0] - points[0][0], points[1][1] - points[0][1])
        w = (points[2][0] - 2 * points[1][0] + points[0][0],
             points[2][1] - 2 * points[1][1] + points[0][1])
    else:
        v = (points[3][0] - points[2][0], points[3][1] - points[2][1])
        w = (points[3][0] - 2 * points[2][0] + points[1][0],
             points[3][1] - 2 * points[2][1] + points[1][1])
    cross = v[0] * w[1] - v[1] * w[0]
    length_sq = int(v[0] * v[0] + v[1] * v[1])
    length = isqrt(length_sq)
    if length * length != length_sq:
        return None
    return Fraction(2, 3) * cross / Fraction(length ** 3)


def _integral(points):
    return all(value.denominator == 1 for point in points for value in point)


def chain(case):
    """The three-piece chain C–A–B, scaled by the hypotenuse."""
    base = _as_fraction((case["p0"], case["p1"], case["p2"], case["p3"]))
    before = mirror_at_start(case)
    after = mirror_at_end(case)
    scale = case["c"]
    pieces = [_scale(before, scale), _scale(base, scale),
              _scale(after, scale)]
    # A global scale preserves the joins and clears every denominator.
    if not all(_integral(piece) for piece in pieces):
        factor = max(_denominator(piece) for piece in pieces)
        pieces = [_scale(piece, factor) for piece in pieces]
        scale *= factor
    return {
        "label": case["label"],
        "scale": scale,
        "pieces": [[(int(x), int(y)) for x, y in piece] for piece in pieces],
    }


def join_report(chain_data):
    """Exact tangent and curvature comparisons at the two joins."""
    c, a, b = chain_data["pieces"]
    joins = []
    for name, left, right in (("start", c, a), ("end", a, b)):
        tv_left = (left[3][0] - left[2][0], left[3][1] - left[2][1])
        tv_right = (right[1][0] - right[0][0], right[1][1] - right[0][1])
        k_left = endpoint_curvature(left, False)
        k_right = endpoint_curvature(right, True)
        joins.append({
            "name": name,
            "point": left[3],
            "tangent": tv_left,
            "tangent_match": tv_left == tv_right,
            "curvature_left": k_left,
            "curvature_right": k_right,
            "curvature_match": k_left == k_right,
            "g2": tv_left == tv_right and k_left == k_right,
        })
    return joins


def probe_all():
    out = []
    for case in pyth_cubic.cases():
        data = chain(case)
        joins = join_report(data)
        out.append({
            "label": case["label"],
            "scale": data["scale"],
            "joins": joins,
            "g2": all(join["g2"] for join in joins),
        })
    return out
