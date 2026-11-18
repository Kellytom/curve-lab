"""The interesting things on a parametric curve: flats, verticals, inflections,
cusps, self-crossings, symmetry and bend.

The original finds were interesting for these reasons, not for their outline, so
the finder measures the same list. Positions are polynomials in t; every root is
located numerically (sign change plus bisection), and every count is reported
with the rule that produced it. The crossing count is a count of **parameter
pairs** — three passes through one point are three pairs — matching
`app/src/content/docs/docs/clearance.md` and the register.
"""

from __future__ import annotations

import math
from fractions import Fraction

SAMPLES = 240


def value(poly, t):
    out = 0.0
    for coefficient in reversed(poly):
        out = out * t + float(coefficient)
    return out


def derivative(poly):
    return [poly[i] * i for i in range(1, len(poly))] or [Fraction(0)]


def roots_in_unit(poly, samples: int = SAMPLES):
    """Every sign change of `poly` on [0, 1], refined by bisection."""
    found = []
    step = 1.0 / samples
    previous_t, previous = 0.0, value(poly, 0.0)
    for i in range(1, samples + 1):
        t = i * step
        current = value(poly, t)
        if previous == 0.0:
            found.append(previous_t)
        elif current == 0.0 or (previous < 0) != (current < 0):
            lo, hi = previous_t, t
            for _ in range(60):
                mid = (lo + hi) / 2
                if (value(poly, lo) < 0) != (value(poly, mid) < 0):
                    hi = mid
                else:
                    lo = mid
            found.append((lo + hi) / 2)
        previous_t, previous = t, current
    return found


def curvature_numerator(x, y, t):
    """x'y'' - y'x'': its sign is the sign of curvature (with speed² > 0)."""
    dx, dy = derivative(x), derivative(y)
    ddx, ddy = derivative(dx), derivative(dy)
    return value(dx, t) * value(ddy, t) - value(dy, t) * value(ddx, t)


def speed(x, y, t):
    dx, dy = derivative(x), derivative(y)
    return math.hypot(value(dx, t), value(dy, t))


def points(x, y, samples: int = SAMPLES):
    return [(value(x, i / samples), value(y, i / samples)) for i in range(samples + 1)]


def _cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _segments_meet(p1, p2, p3, p4, tolerance):
    """True only for a genuine crossing: not parallel, and the points agree.

    Collinear or near-collinear segments share a line and their side tests flip
    on rounding, which is how a straight curve once reported fifty crossings.
    A crossing must be transverse and the two parameters must land on the same
    place to `tolerance`.
    """
    d1, d2 = _cross(p3, p4, p1), _cross(p3, p4, p2)
    d3, d4 = _cross(p1, p2, p3), _cross(p1, p2, p4)
    if (d1 > 0) == (d2 > 0) or (d3 > 0) == (d4 > 0):
        return False
    denominator = (p2[0] - p1[0]) * (p4[1] - p3[1]) - (p2[1] - p1[1]) * (p4[0] - p3[0])
    if abs(denominator) < 1e-12:
        return False  # parallel or collinear: no transverse crossing
    ua = ((p4[0] - p3[0]) * (p1[1] - p3[1]) - (p4[1] - p3[1]) * (p1[0] - p3[0])) / denominator
    ub = ((p2[0] - p1[0]) * (p1[1] - p3[1]) - (p2[1] - p1[1]) * (p1[0] - p3[0])) / denominator
    if not (0 <= ua <= 1 and 0 <= ub <= 1):
        return False
    a = (p1[0] + ua * (p2[0] - p1[0]), p1[1] + ua * (p2[1] - p1[1]))
    b = (p3[0] + ub * (p4[0] - p3[0]), p3[1] + ub * (p4[1] - p3[1]))
    return math.hypot(a[0] - b[0], a[1] - b[1]) <= tolerance


def self_crossing_pairs(x, y, samples: int = SAMPLES):
    """Genuine parameter pairs (t1 < t2) landing on the same point."""
    sampled = points(x, y, samples)
    xs = [p[0] for p in sampled]
    ys = [p[1] for p in sampled]
    size = math.hypot(max(xs) - min(xs), max(ys) - min(ys)) or 1.0
    tolerance = 1e-3 * size
    pairs = []
    for i in range(len(sampled) - 1):
        for j in range(i + 3, len(sampled) - 1):
            if i == 0 and j == len(sampled) - 2:
                continue
            if _segments_meet(sampled[i], sampled[i + 1], sampled[j], sampled[j + 1], tolerance):
                pairs.append((round(i / samples, 4), round((j + 1) / samples, 4)))
    kept = []
    for t1, t2 in pairs:
        if all(abs(t1 - a) > 3.0 / samples or abs(t2 - b) > 3.0 / samples for a, b in kept):
            kept.append((t1, t2))
    return kept


def symmetry(x, y, samples: int = 200):
    """Half-turn and mirror gaps about the curve's own midpoint, as a share of size."""
    pts = points(x, y, samples)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    size = math.hypot(max(xs) - min(xs), max(ys) - min(ys)) or 1.0
    mid = pts[len(pts) // 2]
    half = max(math.hypot(pts[i][0] + pts[-1 - i][0] - 2 * mid[0],
                          pts[i][1] + pts[-1 - i][1] - 2 * mid[1]) for i in range(len(pts)))
    mirror = max(max(abs(pts[i][0] + pts[-1 - i][0] - 2 * mid[0]),
                     abs(pts[i][1] - pts[-1 - i][1])) for i in range(len(pts)))
    return {"half": half / size, "mirror": mirror / size}


def bend(x, y, samples: int = 400):
    pts = points(x, y, samples)
    length = sum(math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
                 for i in range(len(pts) - 1))
    chord = math.hypot(pts[-1][0] - pts[0][0], pts[-1][1] - pts[0][1])
    if chord < 1e-9:
        return None  # a closed curve has no chord; "bend" is undefined, not infinite
    return length / chord


def grid_of(x, y):
    """The lcm of the coefficients' denominators: the grid a rational curve needs."""
    grid = 1
    for poly in (x, y):
        for coefficient in poly:
            denominator = Fraction(coefficient).denominator
            grid = grid * denominator // math.gcd(grid, denominator)
    return grid


def features(x, y):
    dy, dx = derivative(y), derivative(x)
    flat = roots_in_unit(dy)
    vertical = roots_in_unit(dx)
    cusps = [t for t in flat if abs(speed(x, y, t)) < 1e-9]
    sign_changes = 0
    previous = curvature_numerator(x, y, 1e-9)
    for i in range(1, SAMPLES + 1):
        current = curvature_numerator(x, y, i / SAMPLES)
        if previous and current and (previous < 0) != (current < 0):
            sign_changes += 1
        if current:
            previous = current
    gaps = symmetry(x, y)
    bend_value = bend(x, y)
    return {
        "flat_points": [round(t, 5) for t in flat],
        "vertical_points": [round(t, 5) for t in vertical],
        "cusps": [round(t, 5) for t in cusps],
        "inflections": sign_changes,
        "crossing_pairs": len(self_crossing_pairs(x, y)),
        "symmetry": {"half": round(gaps["half"], 4), "mirror": round(gaps["mirror"], 4)},
        "symmetric": min(gaps["half"], gaps["mirror"]) <= 0.005,
        "bend": None if bend_value is None else round(bend_value, 3),
        "closed": bend_value is None,
        "grid": grid_of(x, y),
    }
