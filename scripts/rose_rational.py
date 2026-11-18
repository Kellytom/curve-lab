"""A polar rose with no trigonometry: integer polynomials top and bottom.

    .venv/bin/python scripts/rose_rational.py

Write c = cos(theta) and s = sin(theta) through the rational circle

    c = (1 - t^2)/(1 + t^2),   s = 2t/(1 + t^2)

and cos(k theta) by Chebyshev, T_k(c). Since T_k is a polynomial, every rose

    r = a + b T_k(c),   x = r c,   y = r s

is rational in t. Clearing the denominators gives integer polynomials with the
same degree top and bottom, so the curve is bounded, exact, and on the grid — no
cos, no sin, no irrational number anywhere.

    v = 1 + t^2,  u = 1 - t^2
    P_0 = 1,  P_1 = u,  P_{k+1} = 2u P_k - v^2 P_{k-1}      (v^k T_k(u/v))
    N   = a v^k + b P_k
    x = N u / v^(k+1),   y = 2 N t / v^(k+1)
"""

from __future__ import annotations

import json
import math
import sys
from fractions import Fraction
from math import gcd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from finder_store import save_family  # noqa: E402

SAMPLES = 720
RAIL_SHARE = 0.010


# -- polynomials over Q, as [c0, c1, ...] ------------------------------------

def mul(a, b):
    out = [Fraction(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def scale(a, k):
    return [c * k for c in a]


def add(a, b):
    n = max(len(a), len(b))
    a = list(a) + [Fraction(0)] * (n - len(a))
    b = list(b) + [Fraction(0)] * (n - len(b))
    return [x + y for x, y in zip(a, b)]


def poly(k):
    """v^k T_k(u/v), degree 2k, integer coefficients for integer k."""
    u = [Fraction(1), Fraction(0), Fraction(-1)]      # 1 - t^2
    v = [Fraction(1), Fraction(0), Fraction(1)]       # 1 + t^2
    if k == 0:
        return [Fraction(1)]
    p_prev, p = [Fraction(1)], u
    for _ in range(1, k):
        p_prev, p = p, add(scale(mul(u, p), 2), scale(mul(mul(v, v), p_prev), -1))
    return p


def numerator(a, b, k):
    """a v^k + b P_k, degree 2k."""
    v = [Fraction(1), Fraction(0), Fraction(1)]
    vk = [Fraction(1)]
    for _ in range(k):
        vk = mul(vk, v)
    return add(scale(vk, Fraction(a)), scale(poly(k), Fraction(b)))


def rose(a, b, k):
    """(Nx, Ny, D) with x = Nx/D, y = Ny/D, D = v^(k+1)."""
    n = numerator(a, b, k)
    u = [Fraction(1), Fraction(0), Fraction(-1)]
    two_t = [Fraction(0), Fraction(2)]
    v = [Fraction(1), Fraction(0), Fraction(1)]
    d = [Fraction(1)]
    for _ in range(k + 1):
        d = mul(d, v)
    return mul(n, u), mul(n, two_t), d


def evaluate(p, t):
    total = Fraction(0)
    for c in reversed(p):
        total = total * t + c
    return total


def point(nx, ny, d, t):
    return evaluate(nx, t) / evaluate(d, t), evaluate(ny, t) / evaluate(d, t)


def grid_of(values):
    g = 1
    for v in values:
        denominator = Fraction(v).denominator
        g = g * denominator // gcd(g, denominator)
    return g


def sampled(nx, ny, d, samples=SAMPLES):
    """t = tan(u/2) sampled on a rational ramp; every point is an exact fraction,
    converted to floats only for drawing."""
    out = []
    for i in range(samples + 1):
        t = Fraction(-samples + 2 * i, samples)          # -1 .. 1
        x, y = point(nx, ny, d, t)
        out.append([round(float(x), 6), round(float(y), 6)])
    return out


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


SHAPES = (
    ("rose k=2, a=1 b=1", 1, 1, 2),
    ("rose k=2, a=1 b=-1", 1, -1, 2),
    ("rose k=3, a=1 b=1", 1, 1, 3),
    ("rose k=4, a=1 b=1", 1, 1, 4),
)


def main():
    curves = []
    for name, a, b, k in SHAPES:
        nx, ny, d = rose(a, b, k)
        # exactness check: the coefficients are integers and the degree matches
        integer = all(c.denominator == 1 for c in nx + ny + d)
        degrees = (len(nx) - 1, len(ny) - 1, len(d) - 1)
        pts = sampled(nx, ny, d)
        example = point(nx, ny, d, Fraction(1, 2))
        print(f"{name:22} degrees {degrees} integer coefficients {integer} "
              f"point at t=1/2 {example[0]} {example[1]}")
        curves.append({
            "name": name,
            "definition": {"family": "roses-rational", "a": str(a), "b": str(b), "k": k},
            "degree": degrees[0],
            "proper": True,
            "path": pts,
            "rails": rails(pts),
            "peak": None,
            "features": {"crossing_pairs": 0, "tangent_45": [], "tangent_-45": []},
            "flags": [f"integer polynomials, degrees {degrees}",
                      "exact rational: no cos, no sin"],
        })
    save_family("roses-rational", curves,
                note="Polar roses as ratios of integer polynomials (no trigonometry).")
    print("saved to workbench/finder.json (family: roses-rational)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
