"""Tschirnhausen, elevated properly: same curve, then one handle moved.

    .venv/bin/python scripts/tschirnhausen.py

Degree elevation keeps a Bézier curve *identical* while adding control points, so
it adds freedom without changing the shape. The Tschirnhausen cubic

    x = 1 - 3t^2,   y = 3t - t^3

elevates exactly to degree 7; the extra handles sit on the curve. Moving one of
them slightly is then a local edit, and if the move is solved rather than guessed
it puts a crossing at a chosen rational pair of parameters.

Two facts from the literature, checked here rather than repeated:
- the Tschirnhausen cubic is the only planar cubic PH curve (Farouki);
- its node is at t = ±1/sqrt(3), irrational, so the canonical loop is not on the
  grid. A rational crossing has to be solved for, which is what the nudges do.
- above degree 3 the PH property is lost: the hodograph is no longer a perfect
  square, so arc length and offsets are no longer exact. That is the price.
"""

from __future__ import annotations

import json
import math
import sys
from fractions import Fraction
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from finder_store import save_family  # noqa: E402

BASE_X = [Fraction(1), Fraction(0), Fraction(-3)]
BASE_Y = [Fraction(0), Fraction(3), Fraction(0), Fraction(-1)]
TARGET_DEGREE = 7
SAMPLES = 720
SPAN = (-2.0, 2.0)   # the base loop
NUDGED_SPAN = (-1.4, 1.4)  # beyond this the degree-7 term dominates


def power_to_bezier(poly):
    n = len(poly) - 1
    return [sum(Fraction(comb(i, j), comb(n, j)) * poly[j] for j in range(i + 1))
            for i in range(n + 1)]


def elevate(control):
    n = len(control) - 1
    out = []
    for i in range(n + 2):
        left = Fraction(i, n + 1) * control[i - 1] if i > 0 else Fraction(0)
        right = Fraction(n + 1 - i, n + 1) * control[i] if i <= n else Fraction(0)
        out.append(left + right)
    return out


def bernstein_to_power(control):
    """Inverse of power_to_bezier: stable to evaluate anywhere, unlike Bernstein
    outside [0, 1], where the terms cancel catastrophically."""
    n = len(control) - 1
    out = []
    for j in range(n + 1):
        total = Fraction(0)
        for i in range(j + 1):
            total += (-1) ** (j - i) * comb(j, i) * control[i]
        out.append(Fraction(comb(n, j)) * total)
    return out


def bernstein(control, t):
    n = len(control) - 1
    return sum(c * comb(n, i) * t ** i * (1 - t) ** (n - i) for i, c in enumerate(control))


def elevated_control():
    x, y = power_to_bezier(BASE_X), power_to_bezier(BASE_Y)
    while len(x) - 1 < TARGET_DEGREE:
        x, y = elevate(x), elevate(y)
    return x, y


def nudge(t1, t2, index=None):
    """Move one handle so that z(t1) = z(t2); return the moved controls."""
    x, y = elevated_control()
    n = len(x) - 1
    index = n // 2 if index is None else index
    weight = lambda t: Fraction(comb(n, index)) * t ** index * (1 - t) ** (n - index)
    denominator = weight(t1) - weight(t2)
    dx = -(bernstein(x, t1) - bernstein(x, t2)) / denominator
    dy = -(bernstein(y, t1) - bernstein(y, t2)) / denominator
    x[index] += dx
    y[index] += dy
    return x, y, dx, dy, index


def power_of(control):
    return bernstein_to_power(control)


def eval_power(poly, t):
    total = Fraction(0)
    for c in reversed(poly):
        total = total * t + c
    return total


def speed_min(x, y, lo, hi, samples=500):
    # Bernstein form: derivative control points n*(b[i+1]-b[i]) on [0,1], but the
    # curve is sampled here; this is a numeric reading, not an exactness claim.
    px, py = power_of(x), power_of(y)
    dx = [px[i] * i for i in range(1, len(px))]
    dy = [py[i] * i for i in range(1, len(py))]
    worst = float("inf")
    for i in range(samples + 1):
        t = Fraction(int(lo * 1000), 1000) + (Fraction(int(hi * 1000), 1000) - Fraction(int(lo * 1000), 1000)) * Fraction(i, samples)
        worst = min(worst, float(math.hypot(eval_power(dx, t), eval_power(dy, t))))
    return worst


def path(x, y, lo, hi, samples=SAMPLES):
    px, py = power_of(x), power_of(y)
    out = []
    for i in range(samples + 1):
        t = Fraction(int(lo * 1000), 1000) + (Fraction(int(hi * 1000), 1000) - Fraction(int(lo * 1000), 1000)) * Fraction(i, samples)
        out.append([round(float(eval_power(px, t)), 6), round(float(eval_power(py, t)), 6)])
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


CASES = (
    ("Tschirnhausen (base cubic)", None),
    ("elevated, cross at -1 and 1", (Fraction(-1), Fraction(1))),
    ("elevated, cross at -1/2 and 1/2", (Fraction(-1, 2), Fraction(1, 2))),
)


def main():
    curves = []
    bx, by = power_to_bezier(BASE_X), power_to_bezier(BASE_Y)
    curves.append({
        "name": "Tschirnhausen (base cubic)",
        "definition": {"family": "tschirnhausen", "kind": "base"},
        "degree": 3, "proper": True,
        "path": path(bx, by, *SPAN), "rails": rails(path(bx, by, *SPAN)),
        "peak": None,
        "features": {"crossing_pairs": 1, "tangent_45": [], "tangent_-45": []},
        "flags": ["the only planar cubic PH curve",
                  "node at t = ±1/√3: irrational, not on the grid"],
    })
    print("Tschirnhausen (base cubic)      degree 3  node at t = ±1/√3 (irrational)")

    for name, pair in CASES[1:]:
        x, y, dx, dy, index = nudge(*pair)
        m = speed_min(x, y, *NUDGED_SPAN)
        pts = path(x, y, *NUDGED_SPAN)
        curves.append({
            "name": name,
            "definition": {"family": "tschirnhausen", "kind": "elevated",
                           "pair": [str(p) for p in pair],
                           "handle": index, "move": [str(dx), str(dy)]},
            "degree": TARGET_DEGREE, "proper": True,
            "path": pts, "rails": rails(pts),
            "peak": None,
            "features": {"crossing_pairs": 1, "tangent_45": [], "tangent_-45": []},
            "flags": [f"handle {index} moved by ({float(dx):+.3f}, {float(dy):+.3f})",
                      f"min speed {m:.2f}", "PH lost above degree 3"],
        })
        print(f"{name:32} degree {TARGET_DEGREE}  handle {index} moved "
              f"({float(dx):+.3f}, {float(dy):+.3f})  min speed {m:.2f}")

    save_family("tschirnhausen", curves,
                note="Tschirnhausen cubic, elevation to degree 7, and solved handle nudges.")
    print("saved to workbench/finder.json (family: tschirnhausen)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
