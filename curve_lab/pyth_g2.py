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


def _start_direction(case):
    a, b, c = case["a"], case["b"], case["c"]
    return (Fraction(a, c), Fraction(-b, c))


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
    reflected = [_reflect(point, p0, _start_direction(case)) for point in points]
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



def _candidate(a0, b0, a1, b1, length):
    return {
        "a0": a0, "b0": b0, "a1": a1, "b1": b1, "L": length,
        "points": [
            (Fraction(0), Fraction(0)),
            (Fraction(a0), Fraction(-b0)),
            (Fraction(length - a1), Fraction(b1)),
            (Fraction(length), Fraction(0)),
        ],
    }



_ARM_PAIRS = ((3, 4), (4, 3), (5, 12), (12, 5), (8, 15), (15, 8),
              (7, 24), (24, 7), (20, 21), (21, 20))


def _family_candidates():
    out = []
    for a0, b0 in _ARM_PAIRS:
        for a1, b1 in _ARM_PAIRS:
            c0 = isqrt(a0 * a0 + b0 * b0)
            c1 = isqrt(a1 * a1 + b1 * b1)
            lengths = {2 * max(c0, c1), c0 + c1, 2 * min(c0, c1),
                       3 * max(c0, c1) // 2}
            for length in sorted(lengths):
                if length <= a0 or length <= a1:
                    continue
                points = [
                    (Fraction(0), Fraction(0)),
                    (Fraction(a0), Fraction(-b0)),
                    (Fraction(length - a1), Fraction(b1)),
                    (Fraction(length), Fraction(0)),
                ]
                k0 = endpoint_curvature(points, True)
                k1 = endpoint_curvature(points, False)
                if not k0 or not k1:
                    continue
                out.append({
                    "arms": f"{a0}-{b0}-{c0} / {a1}-{b1}-{c1}",
                    "a0": a0, "b0": b0, "a1": a1, "b1": b1,
                    "length": length, "points": points,
                    "k0": k0, "k1": k1,
                    "s0": Fraction(b0, a0), "s1": Fraction(b1, a1),
                })
    return out


def search_asymmetric(limit: int = 12):
    """Search same-tangent arm pairs; reflect/scale B to match curvature."""
    candidates = _family_candidates()
    by_slope = {}
    for candidate in candidates:
        by_slope.setdefault(candidate["s0"], []).append(candidate)

    found = []
    for a in candidates:
        for b in by_slope.get(a["s1"], []):
            reflect_b = a["k1"] * b["k0"] < 0
            k_b = -b["k0"] if reflect_b else b["k0"]
            if k_b == 0:
                continue
            scale_b = a["k1"] / k_b
            if scale_b <= 0:
                continue
            b_points = b["points"]
            if reflect_b:
                direction = (Fraction(b["a0"], isqrt(b["a0"]**2 + b["b0"]**2)),
                             Fraction(-b["b0"], isqrt(b["a0"]**2 + b["b0"]**2)))
                b_points = [_reflect(point, b_points[0], direction)
                            for point in b_points]
            b_scaled = [(scale_b * x, scale_b * y) for x, y in b_points]
            factor = _denominator(b_scaled)
            a_int = [(factor * x, factor * y) for x, y in a["points"]]
            b_int = [(factor * x, factor * y) for x, y in b_scaled]
            if not all(v.denominator == 1 for p in a_int + b_int for v in p):
                continue
            q = a_int[3]
            b_int = _translate(b_int, q[0], q[1])
            if endpoint_curvature(a_int, False) != endpoint_curvature(b_int, True):
                continue
            if (a_int[3][0] - a_int[2][0], a_int[3][1] - a_int[2][1]) != \
                    (b_int[1][0] - b_int[0][0], b_int[1][1] - b_int[0][1]):
                continue
            found.append({
                "a": a, "b": b, "reflect_b": reflect_b,
                "scale": factor, "scale_b": scale_b,
                "a_points": a_int, "b_points": b_int,
                "join": q,
                "tangent": (a_int[3][0] - a_int[2][0],
                            a_int[3][1] - a_int[2][1]),
                "curvature": endpoint_curvature(a_int, False),
            })

    # Keep the smallest, unique joins; do not call the same pair twice.
    seen = set()
    unique = []
    for result in sorted(found, key=lambda r: (r["scale"], r["a"]["length"] + r["b"]["length"])):
        key = (result["a"]["arms"], result["a"]["length"],
               result["b"]["arms"], result["b"]["length"], result["reflect_b"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(result)
    return unique[:limit]


def asymmetric_pair():
    """A scale-1 asymmetric G2 join: A ends where reflected B begins."""
    # A has a 7-24-25 arm at the start and a 3-4-5 arm at the end.
    a = _candidate(7, 24, 4, 3, 50)
    # B has the complementary arms. Reflect it across its start tangent so
    # its curvature sign matches A's end curvature; then translate it to A's
    # end.
    b = _candidate(4, 3, 7, 24, 50)
    b_points = b["points"]
    direction = _start_direction({"a": 4, "b": 3, "c": 5})
    reflected = [_reflect(point, b_points[0], direction) for point in b_points]
    q = a["points"][3]
    b_join = _translate(reflected, q[0], q[1])
    return {
        "a": a, "b": b, "a_points": a["points"], "b_points": b_join,
        "join": q,
        "tangent": (a["points"][3][0] - a["points"][2][0],
                    a["points"][3][1] - a["points"][2][1]),
        "curvature": endpoint_curvature(a["points"], False),
        "g2": (endpoint_curvature(a["points"], False)
               == endpoint_curvature(b_join, True)),
    }


def g1_fallback():
    """A tangent-only join: the base meets an unreflected copy of itself."""
    base = _candidate(3, 4, 3, 4, 10)
    left = base["points"]
    q = left[3]
    right = _translate(right := base["points"], q[0], q[1])
    return {
        "left": left, "right": right, "join": q,
        "tangent": (left[3][0] - left[2][0], left[3][1] - left[2][1]),
        "curvature_left": endpoint_curvature(left, False),
        "curvature_right": endpoint_curvature(right, True),
        "g1": (left[3][0] - left[2][0], left[3][1] - left[2][1])
              == (right[1][0] - right[0][0], right[1][1] - right[0][1]),
        "g2": endpoint_curvature(left, False) == endpoint_curvature(right, True),
    }



def pair_groups(pair):
    """The asymmetric pair as drawing Groups, without a clothoid Design."""
    from .piece import Group

    def span(points):
        return {"p0": points[0], "c1": points[1],
                "c2": points[2], "p3": points[3]}

    return [
        Group("A", [span(pair["a_points"])], instance="A", role="rail"),
        Group("B", [span(pair["b_points"])], instance="B", role="rail"),
    ]


def pair_clearance(pair, clearance: float = 5.0, tol: float = 0.02):
    """The real clearance rule on the scale-1 pair, with the G2 join declared."""
    from .clearance import measure
    from .contact import Contact

    return measure(
        pair_groups(pair),
        clearance=clearance,
        tol=tol,
        contacts=[Contact(pair["join"], radius=2.0, a="A", b="B")],
        roles=("rail",),
    )


def chain_clearance(chain_data, tol: float = 0.01):
    """A coarse clearance/self-intersection probe on a three-piece chain.

    This is a probe, not the full piece clearance. It flattens each cubic and
    reports the minimum distance between the two non-adjacent outer pieces,
    plus a rough self-intersection count inside each flattened piece.
    """
    from .clearance import flatten, segment_distance

    pieces = chain_data["pieces"]
    spans = [
        {"p0": p[0], "c1": p[1], "c2": p[2], "p3": p[3]}
        for p in pieces
    ]
    polys = [flatten([span], tol=tol) for span in spans]

    def cross(a, b, c, d):
        def side(p, q, r):
            return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
        return side(a, b, c) * side(a, b, d) < 0 and side(c, d, a) * side(c, d, b) < 0

    self_hits = 0
    for poly in polys:
        segs = list(zip(poly, poly[1:]))
        for i, (a, b) in enumerate(segs):
            for j, (c, d) in enumerate(segs):
                if j <= i + 1:
                    continue
                if cross(a, b, c, d):
                    self_hits += 1

    def min_between(p, q):
        best = float("inf")
        for a, b in zip(p, p[1:]):
            for c, d in zip(q, q[1:]):
                best = min(best, segment_distance(a, b, c, d)[0])
        return best

    return {
        "nonadjacent_clearance": min_between(polys[0], polys[2]),
        "self_intersections": self_hits,
    }


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
