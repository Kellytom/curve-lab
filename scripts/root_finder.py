"""Search mirrored-root curves — the construction the original finds came from.

    .venv/bin/python scripts/root_finder.py            # search, rank, write finder.json

A curve is built the way the sandbox builds one:

    y'(t) = (t - 1/2)^m · (t - p) · (t - (1 - p))      a flat spot at the middle,
                                                       and a mirrored pair
    x'(t) = (t - 1/2)^j                                the x row's own roots

multiply out, integrate, and clear the denominators to integers. Mirrored roots
are what make the curve symmetric; the multiplicities are what make the long
flat middle and the smooth legs.

Every candidate is measured with curve_lab.features: crossing pairs, flats,
inflections, symmetry, bend and the grid. The interesting ones are written to
workbench/finder.json with character rails, so the page shows width.
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
from curve_lab.features import features  # noqa: E402

OUT = ROOT / "workbench" / "finder.json"
RAIL_SHARE = 0.015
SAMPLES = 240
KEEP = 12

PAIRS = (Fraction(1, 10), Fraction(1, 8), Fraction(1, 5), Fraction(1, 4),
         Fraction(1, 3), Fraction(3, 8), Fraction(2, 5))


def mul(a, b):
    out = [Fraction(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def linear(root):
    """t - root, as coefficients."""
    return [-root, Fraction(1)]


def integrate(poly):
    return [Fraction(0)] + [Fraction(c, i + 1) for i, c in enumerate(poly)]


def integerise(poly):
    """Scale a polynomial to integer coefficients; return (poly, factor)."""
    factor = 1
    for c in poly:
        factor = factor * c.denominator // math.gcd(factor, c.denominator)
    return [c * factor for c in poly], factor


def build(pair, middle_multiplicity, x_multiplicity, pair_multiplicity=1,
          x_pair=None, x_pair_multiplicity=1):
    y_speed = [Fraction(1)]
    for _ in range(middle_multiplicity):
        y_speed = mul(y_speed, linear(Fraction(1, 2)))
    for _ in range(pair_multiplicity):
        y_speed = mul(y_speed, linear(pair))
        y_speed = mul(y_speed, linear(1 - pair))
    x_speed = [Fraction(1)]
    for _ in range(x_multiplicity):
        x_speed = mul(x_speed, linear(Fraction(1, 2)))
    if x_pair is not None:
        for _ in range(x_pair_multiplicity):
            x_speed = mul(x_speed, linear(x_pair))
            x_speed = mul(x_speed, linear(1 - x_pair))

    y = integrate(y_speed)
    x = integrate(x_speed)
    # same scale on both rows: the shape survives, the numbers go whole
    y_int, factor = integerise(y)
    x_int = [c * factor for c in x]
    if any(c.denominator != 1 for c in x_int):
        common = 1
        for c in x_int:
            common = common * c.denominator // math.gcd(common, c.denominator)
        y_int = [c * common for c in y_int]
        x_int = [c * common for c in x_int]
    return x_int, y_int


def evaluate(poly, t):
    total = 0.0
    for c in reversed(poly):
        total = total * t + float(c)
    return total


def derivative(poly):
    return [poly[i] * i for i in range(1, len(poly))] or [Fraction(0)]


def path(x, y, steps=SAMPLES):
    return [[round(evaluate(x, i / steps), 6), round(evaluate(y, i / steps), 6)]
            for i in range(steps + 1)]


def rails(x, y, share=RAIL_SHARE):
    pts = path(x, y)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    size = math.hypot(max(xs) - min(xs), max(ys) - min(ys)) or 1.0
    d = share * size
    dx, dy = derivative(x), derivative(y)
    left, right = [], []
    for i, (px, py) in enumerate(pts):
        t = i / len(pts)
        vx, vy = evaluate(dx, t), evaluate(dy, t)
        length = math.hypot(vx, vy) or 1.0
        nx, ny = -vy / length, vx / length
        left.append([round(px + d * nx, 6), round(py + d * ny, 6)])
        right.append([round(px - d * nx, 6), round(py - d * ny, 6)])
    return [left, right]


def name_of(pair, middle_multiplicity, x_multiplicity, pair_multiplicity, x_pair):
    y_span = f"{pair.numerator}/{pair.denominator}"
    x_span = "-" if x_pair is None else f"{x_pair.numerator}/{x_pair.denominator}"
    return (f"y' {y_span}×{pair_multiplicity} mid {middle_multiplicity} "
            f"· x' {x_span} mid {x_multiplicity}")


def turning(x_speed, y_speed, samples=120):
    total, previous = 0.0, None
    for i in range(samples + 1):
        t = i / samples
        vx, vy = evaluate(x_speed, t), evaluate(y_speed, t)
        angle = math.atan2(vy, vx)
        if previous is not None:
            step = angle - previous
            while step > math.pi:
                step -= 2 * math.pi
            while step < -math.pi:
                step += 2 * math.pi
            total += abs(step)
        previous = angle
    return math.degrees(total)


def search():
    found = []
    for pair in PAIRS:
        for mid_y in range(0, 3):
            for pm_y in (1, 2):
                for x_pair in PAIRS:
                    for mid_x in range(0, 3):
                        x, y = build(pair, mid_y, mid_x, pm_y, x_pair, 1)
                        xs = derivative(x)
                        ys = derivative(y)
                        if turning(xs, ys) < 180:
                            continue  # cannot close a loop without turning past half a circle
                        measured = features(x, y)
                        if measured["crossing_pairs"] < 1:
                            continue
                        found.append({
                            "name": name_of(pair, mid_y, mid_x, pm_y, x_pair),
                            "x": [str(c) for c in x],
                            "y": [str(c) for c in y],
                            "degree": max(len(x), len(y)) - 1,
                            "proper": True,
                            "path": path(x, y),
                            "rails": rails(x, y),
                            "features": measured,
                            "peak": None,
                            "flags": (["symmetric"] if measured["symmetric"] else [])
                                     + (["loops"] if measured["crossing_pairs"] >= 1 else []),
                        })
    found.sort(key=lambda item: (-item["features"]["crossing_pairs"],
                                 not item["features"]["symmetric"],
                                 item["features"]["grid"]))
    return found[:KEEP]


def main():
    best = search()
    OUT.write_text(json.dumps({
        "format": FORMATS["finder.json"],
        "note": "Mirrored-root curves: crossing pairs first, then symmetry, then grid.",
        "curves": best,
    }, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    for item in best:
        f = item["features"]
        print(f'{item["name"]:34} cross {f["crossing_pairs"]:2}  grid {f["grid"]:5}  '
              f'{"symmetric" if f["symmetric"] else "":10} flats {len(f["flat_points"])}')
    print(f"wrote {OUT.relative_to(ROOT)} with {len(best)} curves")
    return 0


if __name__ == "__main__":
    sys.exit(main())
