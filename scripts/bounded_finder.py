"""Bounded rational curves: equal degrees, leading pair from a p-triple.

    .venv/bin/python scripts/bounded_finder.py

    z(t) = ( A(t) + i B(t) ) / (1 + t^2),   deg A = deg B = 2

Numerator and denominator have the same degree, so `t -> +-inf` lands on the
same finite point `(a2, b2)` and the curve is **closed at infinity**: it passes
through that point once and comes back. When `(a2, b2)` is taken from a
Pythagorean triple, that point is rational on a circle, which is the bound in
exact form — nothing can run away, and no square root appears anywhere.

The middle coefficients are free. They decide where the curve wanders between
the two passes through the closing point, and therefore whether it loops.
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

OUT = ROOT / "workbench" / "finder.json"
SAMPLES = 700
T_MAX = 40.0
RAIL_SHARE = 0.010


def value(t, a, b, c):
    """(a t^2 + b t + c) / (1 + t^2)"""
    return (a * t * t + b * t + c) / (1 + t * t)


def point(t, spec):
    if "polar" in spec:
        a, b = spec["polar"]
        c = (1 - t * t) / (1 + t * t)
        s = 2 * t / (1 + t * t)
        r = a + b * c
        return (r * c, r * s)
    return (value(t, spec["ax"], spec["bx"], spec["cx"]),
            value(t, spec["ay"], spec["by"], spec["cy"]))


def sample(spec, samples=SAMPLES):
    # uniform in angle, so the closing point is approached at a sane density:
    # t = tan(u), u in (-pi/2, pi/2)
    points = []
    for i in range(samples + 1):
        u = -math.pi / 2 + math.pi * (i / samples)
        t = math.tan(u * 0.999)
        points.append([round(point(t, spec)[0], 6), round(point(t, spec)[1], 6)])
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


# (ax, ay) is the leading pair: a Pythagorean triple, so the closing point is a
# rational point of a circle. The rest is free.
SPECS = {
    "3-4-5, gentle": dict(ax=3, ay=4, bx=0, by=1, cx=1, cy=0),
    "3-4-5, crossed": dict(ax=3, ay=4, bx=2, by=-2, cx=-2, cy=1),
    "5-12-13, gentle": dict(ax=5, ay=12, bx=0, by=2, cx=2, cy=0),
    "5-12-13, crossed": dict(ax=5, ay=12, bx=6, by=-4, cx=-4, cy=2),
    "8-15-17, crossed": dict(ax=8, ay=15, bx=10, by=-6, cx=-6, cy=3),
    "3-4-5, tight": dict(ax=3, ay=4, bx=5, by=-5, cx=-5, cy=2),
    # Limaçons: a circle of radius k about a centre one unit away. k > 1 gives
    # the inner loop; k = 1 is the cardioid (a cusp, not a crossing).
    # Polar limaçons: r = a + b cos(theta), rational in t = tan(theta/2),
    # degree 4 over degree 4 — bounded, and b > a puts a loop through the origin.
    "limacon 1+2cos": dict(polar=(1, 2)),
    "limacon 1+3cos": dict(polar=(1, 3)),
    "limacon 2+3cos": dict(polar=(2, 3)),
    "limacon 1+2cos (5x)": dict(polar=(1, 2)),
}


def main():
    curves = []
    for name, spec in SPECS.items():
        points = sample(spec)
        hits = crossings(points)
        curves.append({
            "name": name,
            "spec": {k: str(v) for k, v in spec.items()},
            "definition": {"family": "bounded", "spec": {k: str(v) for k, v in spec.items()}},
            "degree": 2,
            "proper": True,
            "path": points,
            "rails": rails(points),
            "peak": None,
            "features": {"crossing_pairs": hits, "tangent_45": [], "tangent_-45": []},
            "flags": ([f"r = {spec['polar'][0]} + {spec['polar'][1]} cos θ"] if "polar" in spec
                      else [f"closed at ({spec['ax']}, {spec['ay']})"]) + [f"{hits} sampled crossings"],
        })
        where = (f"r = {spec['polar'][0]} + {spec['polar'][1]} cos theta" if "polar" in spec
                 else f"closing point ({spec['ax']}, {spec['ay']})")
        print(f"{name:18} {where:26} sampled crossings {hits}")
    save_family("bounded", curves, note="Bounded rational curves closing on a p-triple point.")
    print(f"wrote {OUT.relative_to(ROOT)} with {len(curves)} curves")
    return 0


if __name__ == "__main__":
    sys.exit(main())
