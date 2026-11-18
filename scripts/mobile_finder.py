"""The mobile: a big vane carrying smaller ones, and a pencil on the last.

    .venv/bin/python scripts/mobile_finder.py

A vane is a rotation. Rather than sines, each rotation is the rational
parametrisation of the circle,

    R(s) = ((1 - s^2)/(1 + s^2), 2s/(1 + s^2))

so a vane turned at `k` times the base rate is `R(k t)`. The pencil's path is a
sum of vanes with falling amplitudes,

    z(t) = A0 R(t) + A1 R(k1 t) + A2 R(k2 t) + ...

which is a rational curve: every point is an exact fraction, and the big vane
sets where the curve goes while the small ones make the arcs and loops on top of
it. That is the mobile in the operator's picture, with no trigonometry.
"""

from __future__ import annotations

import json
import math
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab.datafile import FORMATS  # noqa: E402
from finder_store import save_family  # noqa: E402
from curve_lab.features import self_crossing_pairs  # noqa: E402

OUT = ROOT / "workbench" / "finder.json"
SAMPLES = 600
SPAN = (-3.0, 3.0)   # the base vane needs a full turn: t = tan(theta/2)
RAIL_SHARE = 0.010


def circle_point(s: Fraction):
    denominator = 1 + s * s
    return ((1 - s * s) / denominator, (2 * s) / denominator)


def mobile(t, vanes):
    """Sum of vanes: (amplitude, rate) pairs, each a rational rotation."""
    x = Fraction(0)
    y = Fraction(0)
    for amplitude, rate in vanes:
        px, py = circle_point(rate * t)
        x += amplitude * px
        y += amplitude * py
    return x, y


def sample(vanes, samples=SAMPLES):
    lo, hi = SPAN
    points = []
    for i in range(samples + 1):
        t = Fraction(int(lo * 1000), 1000) + (Fraction(int(hi * 1000), 1000) - Fraction(int(lo * 1000), 1000)) * Fraction(i, samples)
        x, y = mobile(t, vanes)
        points.append([round(float(x), 6), round(float(y), 6)])
    return points


def rails(points, share=RAIL_SHARE):
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


def crossings(points):
    """Segment crossings on the sampled path, collinear pairs refused."""
    def cross(o, a, b):
        return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
    hits = 0
    n = len(points)
    for i in range(n - 1):
        for j in range(i + 3, n - 1):
            p1, p2, p3, p4 = points[i], points[i+1], points[j], points[j+1]
            d1, d2 = cross(p3, p4, p1), cross(p3, p4, p2)
            d3, d4 = cross(p1, p2, p3), cross(p1, p2, p4)
            if (d1 > 0) != (d2 > 0) and (d3 > 0) != (d4 > 0):
                hits += 1
    return hits


def main():
    configs = (
        ("two vanes, 1:1/2", [(Fraction(1), 1), (Fraction(1, 2), 2)]),
        ("two vanes, 1:1/3", [(Fraction(1), 1), (Fraction(1, 3), 3)]),
        ("three vanes, 1:1/2:1/4", [(Fraction(1), 1), (Fraction(1, 2), 2), (Fraction(1, 4), 4)]),
        ("three vanes, big small", [(Fraction(3), 1), (Fraction(1, 4), 5), (Fraction(1, 8), 7)]),
    )
    curves = []
    for name, vanes in configs:
        points = sample(vanes)
        hits = crossings(points)
        curves.append({
            "name": name,
            "vanes": [[str(a), r] for a, r in vanes],
            "definition": {"family": "mobile", "vanes": [[str(a), r] for a, r in vanes]},
            "degree": None,
            "proper": True,
            "path": points,
            "rails": rails(points),
            "peak": None,
            "features": {"crossing_pairs": hits, "tangent_45": [], "tangent_-45": []},
            "flags": [f"{hits} crossings on the sample"],
        })
        print(f"{name:26} sampled crossings {hits}")
    save_family("mobile", curves, note="Mobiles: sums of rational vanes.")
    print(f"wrote {OUT.relative_to(ROOT)} with {len(curves)} curves")
    return 0


if __name__ == "__main__":
    sys.exit(main())
