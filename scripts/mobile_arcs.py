"""Mobile arcs: a piece of the mobile with exact ends you can chain.

    .venv/bin/python scripts/mobile_arcs.py

The mobile is periodic, so it has no ends — but any piece between two rational
parameters does. On the arc, at `t = t1` and `t = t2`:

    exact position      rational coordinates, from integer polynomials
    exact tangent       from the exact derivative, reported as an angle
    a printable corner  the turn between two arcs, which is what a chain needs

Nothing here samples to decide anything: the endpoints and tangents are
computed from the polynomials and then rounded only for the caption.
"""

from __future__ import annotations

import json
import math
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from finder_store import save_family  # noqa: E402
from mobile_exact import evaluate, mobile  # noqa: E402

SAMPLES = 480
SPAN_PAIRS = ((Fraction(0), Fraction(1, 2)),
              (Fraction(-1, 2), Fraction(1, 2)),
              (Fraction(0), Fraction(1)),
              (Fraction(-1), Fraction(1)))

VANES = ((1, 1, "3-4-5"), (Fraction(1, 2), 2, "5-12-13"))


def deriv(poly):
    return [poly[i] * i for i in range(1, len(poly))] or [Fraction(0)]


def point_and_tangent(num_re, num_im, den, t):
    """Exact point and tangent of a rational curve."""
    numerator_x, numerator_y = evaluate(num_re, t), evaluate(num_im, t)
    d = evaluate(den, t)
    dx_num = evaluate(deriv(num_re), t) * d - numerator_x * evaluate(deriv(den), t)
    dy_num = evaluate(deriv(num_im), t) * d - numerator_y * evaluate(deriv(den), t)
    return ((numerator_x / d, numerator_y / d), (dx_num / (d * d), dy_num / (d * d)))


def angle_of(vector):
    return math.degrees(math.atan2(float(vector[1]), float(vector[0])))


def arc_points(num_re, num_im, den, t1, t2, samples=SAMPLES):
    out = []
    for i in range(samples + 1):
        t = t1 + (t2 - t1) * Fraction(i, samples)
        x, y = point_and_tangent(num_re, num_im, den, t)[0]
        out.append([round(float(x), 6), round(float(y), 6)])
    return out


def rails(points, share=0.010):
    xs = [p[0] for p in points]; ys = [p[1] for p in points]
    size = math.hypot(max(xs) - min(xs), max(ys) - min(ys)) or 1.0
    d = share * size
    left, right = [], []
    for i, (px, py) in enumerate(points):
        a = points[max(0, i - 1)]; b = points[min(len(points) - 1, i + 1)]
        vx, vy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(vx, vy) or 1.0
        nx, ny = -vy / length, vx / length
        left.append([round(px + d * nx, 6), round(py + d * ny, 6)])
        right.append([round(px - d * nx, 6), round(py - d * ny, 6)])
    return [left, right]


def main():
    num_re, num_im, den = mobile(VANES)
    curves = []
    for t1, t2 in SPAN_PAIRS:
        points = arc_points(num_re, num_im, den, t1, t2)
        start, start_tangent = point_and_tangent(num_re, num_im, den, t1)
        end, end_tangent = point_and_tangent(num_re, num_im, den, t2)
        start_angle, end_angle = angle_of(start_tangent), angle_of(end_tangent)
        # the turn a chain sees when this arc is joined to its own mirror
        corner = end_angle - start_angle
        while corner > 180:
            corner -= 360
        while corner < -180:
            corner += 360
        name = f"arc {t1} to {t2}"
        curves.append({
            "name": name,
            "definition": {"family": "mobile-arcs", "vanes": [[str(a), r, tilt] for a, r, tilt in VANES],
                           "t1": str(t1), "t2": str(t2)},
            "degree": max(len(num_re), len(den)) - 1,
            "proper": True,
            "path": points,
            "rails": rails(points),
            "peak": None,
            "features": {"crossing_pairs": 0, "tangent_45": [], "tangent_-45": []},
            "flags": [f"start ({start[0]}, {start[1]}) tangent {start_angle:+.1f}°",
                      f"end ({end[0]}, {end[1]}) tangent {end_angle:+.1f}°",
                      f"turn across the arc {corner:+.1f}°"],
        })
        print(f"{name:18} start {str(start[0])[:12]},{str(start[1])[:12]} "
              f"({start_angle:+.1f}°)  end {str(end[0])[:12]},{str(end[1])[:12]} "
              f"({end_angle:+.1f}°)  turn {corner:+.1f}°")
    save_family("mobile-arcs", curves,
                note="Arcs of the mobile: exact endpoints and tangents, chainable.")
    print("saved to workbench/finder.json (family: mobile-arcs)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
