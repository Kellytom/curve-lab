"""Search small integer speed pairs for curves worth looking at.

    .venv/bin/python scripts/ph_finder.py            # search, rank, write finder.json
    .venv/bin/python scripts/ph_finder.py --top 12   # how many to keep

A curve is the integral of a squared complex speed: x = ∫(u² − v²), y = ∫2uv,
with u and v small integer polynomials. That is the construction the original
finds came from, and unlike a graph of y = f(x) it can loop.

What counts as interesting, in the order the project cares:
  crossing pairs   the stroke meets itself (loops and knots)
  symmetric        mirror or half turn, within 0.5% of the size
  flat points      y' = 0 with the speed nonzero (a horizontal tangent)
  coarse grid      the lcm of the coefficients' denominators

The top few are written to workbench/finder.json with their character rails —
two offset curves, the same idea as a book plate — so the page shows width, not
just a line.
"""

from __future__ import annotations

import itertools
import json
import math
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import numpy as np  # noqa: E402

from curve_lab.datafile import FORMATS  # noqa: E402
from curve_lab.features import features  # noqa: E402
from ph_crossings import stable_crossings  # noqa: E402

OUT = ROOT / "workbench" / "finder.json"
COEFFICIENTS = (-2, -1, 0, 1, 2)
DEGREE = 2          # u and v as a + b t + c t^2
RAIL_SHARE = 0.015   # rail distance as a share of the curve's size
SAMPLES = 240


def integrate(poly):
    return [Fraction(0)] + [Fraction(c, i + 1) for i, c in enumerate(poly)]


def poly_mul(a, b):
    out = [Fraction(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def poly_sub(a, b):
    n = max(len(a), len(b))
    a = list(a) + [Fraction(0)] * (n - len(a))
    b = list(b) + [Fraction(0)] * (n - len(b))
    return [x - y for x, y in zip(a, b)]


def speed_to_curve(u, v):
    u2, v2 = poly_mul(u, u), poly_mul(v, v)
    x = integrate(poly_sub(u2, v2))
    y = integrate([2 * c for c in poly_mul(u, v)])
    return x, y


def evaluate(poly, t):
    total = 0.0
    for c in reversed(poly):
        total = total * t + float(c)
    return total


def derivative(poly):
    return [poly[i] * i for i in range(1, len(poly))] or [Fraction(0)]


def path_of(x, y, steps=SAMPLES):
    return [[round(evaluate(x, i / steps), 6), round(evaluate(y, i / steps), 6)]
            for i in range(steps + 1)]


def rails_of(x, y, share=RAIL_SHARE, steps=SAMPLES):
    """Two offset curves at ±share of the size, along the normal."""
    pts = path_of(x, y, steps)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    size = math.hypot(max(xs) - min(xs), max(ys) - min(ys)) or 1.0
    d = share * size
    dx, dy = derivative(x), derivative(y)
    left, right = [], []
    for i, (px, py) in enumerate(pts):
        t = i / steps
        vx, vy = evaluate(dx, t), evaluate(dy, t)
        length = math.hypot(vx, vy) or 1.0
        nx, ny = -vy / length, vx / length
        left.append([round(px + d * nx, 6), round(py + d * ny, 6)])
        right.append([round(px - d * nx, 6), round(py - d * ny, 6)])
    return left, right


def turning(u, v, samples=120):
    """Total turn of the tangent, in degrees, along t in [0, 1]."""
    def w(t):
        uu = evaluate(u, t); vv = evaluate(v, t)
        return (uu * uu - vv * vv, 2 * uu * vv)

    total = 0.0
    previous = None
    for i in range(samples + 1):
        x, y = w(i / samples)
        angle = math.atan2(y, x)
        if previous is not None:
            step = angle - previous
            while step > math.pi:
                step -= 2 * math.pi
            while step < -math.pi:
                step += 2 * math.pi
            total += abs(step)
        previous = angle
    return math.degrees(total)


def name_of(u, v):
    def text(poly):
        return "(" + ", ".join(str(c) for c in poly) + ")"
    return f"u{text(u)} v{text(v)}"


def search(limit=12):
    found = []
    seen = set()
    ranges = [COEFFICIENTS] * (2 * (DEGREE + 1))
    for values in itertools.product(*ranges):
        u = [Fraction(values[i]) for i in range(DEGREE + 1)]
        v = [Fraction(values[DEGREE + 1 + i]) for i in range(DEGREE + 1)]
        if not any(u) or not any(v):
            continue
        # one representative per pair: drop the sign-flipped copy
        key = tuple(sorted((tuple(u), tuple(v)), key=lambda p: tuple(-x for x in p)))
        if key in seen:
            continue
        seen.add(key)
        # A loop needs the heading to turn past half a circle. This is cheap and
        # throws away most candidates before the expensive crossing scan.
        if turning(u, v) < 200:
            continue
        hits = stable_crossings([float(c) for c in u], [float(c) for c in v])
        if len(hits) < 2:
            continue
        x, y = speed_to_curve(u, v)
        measured = features(x, y)
        if measured["crossing_pairs"] < 2:
            continue
        found.append({"name": name_of(u, v), "u": u, "v": v, "x": x, "y": y,
                      "hits": len(hits), "features": measured})
    found.sort(key=lambda item: (-item["features"]["crossing_pairs"],
                                 not item["features"]["symmetric"],
                                 item["features"]["grid"]))
    return found[:limit]


def main(argv):
    top = 12
    if "--top" in argv:
        top = int(argv[argv.index("--top") + 1])
    best = search(top)
    curves = []
    for item in best:
        left, right = rails_of(item["x"], item["y"])
        curves.append({
            "name": item["name"],
            "u": [str(c) for c in item["u"]],
            "v": [str(c) for c in item["v"]],
            "degree": max(len(item["x"]), len(item["y"])) - 1,
            "proper": True,
            "path": path_of(item["x"], item["y"]),
            "rails": [left, right],
            "features": item["features"],
            "flags": (["symmetric"] if item["features"]["symmetric"] else [])
                     + (["loops"] if item["features"]["crossing_pairs"] >= 2 else []),
            "peak": None,
        })
        f = item["features"]
        print(f'{item["name"]:28} crossings {f["crossing_pairs"]:2}  grid {f["grid"]:5}  '
              f'{"symmetric" if f["symmetric"] else "":10} flats {len(f["flat_points"])}')
    OUT.write_text(json.dumps({
        "format": FORMATS["finder.json"],
        "note": "Interesting integer speed pairs: crossing pairs first, then symmetry, then grid.",
        "curves": curves,
    }, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} with {len(curves)} curves")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
