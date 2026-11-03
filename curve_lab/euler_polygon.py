"""C curve → exact p-triple Euler polygon → rational rails → cubic drawing.

The p-triple spine is the solved plan route:

1. resample the target C curve at equal arc length;
2. rotate it so the first chord is east;
3. choose a primitive triangle angle with `for_angle`;
4. quantize each chord's heading change to whole triangle turns;
5. build a rational `Spiral` with equal rational chords;
6. take the exact rational miter rails from `ribbon.rails`;
7. draw the cubic seam from `spans.spans`.

The polygon and the rails are exact.  The target curve and the cubic drawing
are approximations; the report carries the p-triple angle, the chord count,
the polygon error and the cubic error.  A cusp/loop is not handled here: split
the target before calling.
"""

from __future__ import annotations

import math
from fractions import Fraction

from . import spine

# spine.load() adds pythagorean-spiral to sys.path
SPINE = spine.load()
from pythagorean_spiral import Dir, Spiral, ribbon, spans as span_module  # noqa: E402
from pythagorean_spiral.triples import for_angle  # noqa: E402


def _dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def resample(points, n):
    """n+1 points at equal chord/arc fractions along the sampled polyline."""
    if len(points) < 2:
        raise ValueError("need at least two points")
    cum = [0.0]
    for a, b in zip(points, points[1:]):
        cum.append(cum[-1] + _dist(a, b))
    total = cum[-1] or 1.0
    out = []
    j = 0
    for i in range(n + 1):
        target = total * i / n
        while j < len(cum) - 2 and cum[j + 1] < target:
            j += 1
        seg = cum[j + 1] - cum[j]
        t = 0.0 if seg <= 1e-15 else (target - cum[j]) / seg
        out.append((points[j][0] + t * (points[j + 1][0] - points[j][0]),
                    points[j][1] + t * (points[j + 1][1] - points[j][1])))
    return out


def _rotate_translate(points):
    """Put the first chord east and the first point at the origin."""
    dx = points[1][0] - points[0][0]
    dy = points[1][1] - points[0][1]
    a = math.atan2(dy, dx)
    c, s = math.cos(-a), math.sin(-a)
    x0, y0 = points[0]
    return [((x - x0) * c - (y - y0) * s,
             (x - x0) * s + (y - y0) * c) for x, y in points]


def _nearest_to_polyline(p, poly):
    best = float("inf")
    for a, b in zip(poly, poly[1:]):
        vx, vy = b[0] - a[0], b[1] - a[1]
        ll = vx * vx + vy * vy
        t = 0.0 if ll <= 1e-15 else max(0.0, min(1.0,
              ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / ll))
        best = min(best, math.hypot(p[0] - (a[0] + t * vx),
                                    p[1] - (a[1] + t * vy)))
    return best


def cubic_points(span_list, per=12):
    out = []
    for sp in span_list:
        for i in range(per):
            t = i / per
            mt = 1 - t
            out.append((mt ** 3 * sp["p0"][0] + 3 * mt * mt * t * sp["c1"][0]
                        + 3 * mt * t * t * sp["c2"][0] + t ** 3 * sp["p3"][0],
                        mt ** 3 * sp["p0"][1] + 3 * mt * mt * t * sp["c1"][1]
                        + 3 * mt * t * t * sp["c2"][1] + t ** 3 * sp["p3"][1]))
    out.append((span_list[-1]["p3"][0], span_list[-1]["p3"][1]))
    return out


def convert(points, n=160, max_angle=0.6, width_factor=0.08):
    """Convert one smooth C-curve section to a p-triple Euler section.

    `points` must be a smooth section; split at a cusp/loop first.
    """
    target = _rotate_translate(resample(points, n))
    triangle = for_angle(max_angle)
    alpha = triangle.radians
    arc = sum(_dist(a, b) for a, b in zip(target, target[1:]))
    chord = Fraction(arc / n).limit_denominator(1_000_000)
    chain = Spiral(triangle, chord, heading=Dir.east())
    headings = [math.atan2(b[1] - a[1], b[0] - a[0])
                for a, b in zip(target, target[1:])]
    turns = []
    for i, h in enumerate(headings):
        if i == 0:
            k = 0
        else:
            k = int(round((h - headings[i - 1]) / alpha))
        turns.append(k)
        chain.walk(k)
    chain_points = [(float(x), float(y)) for x, y in chain.nodes]

    size = max(math.hypot(x, y) for x, y in target) or 1.0
    width = Fraction(str(round(width_factor * size, 6)))
    left, right = ribbon.rails(chain.nodes, width, taper=0)
    left = [(float(x), float(y)) for x, y in left]
    right = [(float(x), float(y)) for x, y in right]

    cubic = cubic_points(span_module.spans(chain))
    poly_err = [_dist(a, b) for a, b in zip(target, chain_points)]
    cubic_err = [_nearest_to_polyline(p, target) for p in cubic]
    return {
        "target": target,
        "polygon": chain_points,
        "left": left,
        "right": right,
        "cubic": cubic,
        "triangle": triangle,
        "alpha_deg": math.degrees(alpha),
        "chords": n,
        "chord": float(chord),
        "width": float(width),
        "turns": turns,
        "poly_max": max(poly_err),
        "poly_rms": math.sqrt(sum(e * e for e in poly_err) / len(poly_err)),
        "cubic_max": max(cubic_err),
        "cubic_rms": math.sqrt(sum(e * e for e in cubic_err) / len(cubic_err)),
        "size": size,
    }
