#!/usr/bin/env python3
"""Probe: multiplying two prime-mover walks, and odd-power (S) curves.

    .venv/bin/python scripts/pm_product_probe.py
    .venv/bin/python scripts/pm_product_probe.py --write

Two ideas from the operator (2026-11-19):

1. **Multiply the movers, do not only add them.**  With unit radii the product
   is `(1+e^{i a k})(1+e^{i b k}) = 4 cos(a k/2) cos(b k/2) e^{i(a+b)k/2}`.
   When either cosine changes sign the point passes *through the origin*, so the
   figure is drawn with straight chords — a star polygon, not a curve.  Keeping
   each radius under one keeps the radius positive and the figure a curve.
   So a product find must pass a *clearance* test: the smallest distance to the
   origin, as a fraction of the largest radius.

2. **Odd powers make S curves.**  A graph `y = t - t^3` is an S and no closed
   curve; but a *parametric* odd-power pair can loop: `x = t^3 - t`,
   `y = t^5 - t^3` returns.  The test is the same: reversals, inflections,
   crossings, plus whether the figure closes or runs away.

Scores, in the operator's language: a loop reverses its tangential speed while
the turn keeps one sign.  A spiral never reverses.  A star polygon reverses
often but its radius hits zero.
"""

from __future__ import annotations

import argparse
import cmath
import json
import math
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "workbench" / "pm-product.json"
STEPS = 240


def reversals(points):
    count, last = 0, 0
    for i in range(1, len(points) - 1):
        ax, ay = points[i][0] - points[i - 1][0], points[i][1] - points[i - 1][1]
        bx, by = points[i + 1][0] - points[i][0], points[i + 1][1] - points[i][1]
        dot = ax * bx + ay * by
        if abs(dot) < 1e-12:
            continue
        sign = 1 if dot > 0 else -1
        if last and sign != last:
            count += 1
        last = sign
    return count


def inflections(points):
    count, last = 0, 0
    for i in range(1, len(points) - 1):
        ax, ay = points[i][0] - points[i - 1][0], points[i][1] - points[i - 1][1]
        bx, by = points[i + 1][0] - points[i][0], points[i + 1][1] - points[i][1]
        cross = ax * by - ay * bx
        if abs(cross) < 1e-10:
            continue
        sign = 1 if cross > 0 else -1
        if last and sign != last:
            count += 1
        last = sign
    return count


def crossings(points):
    seen = set()
    n = len(points)
    for i in range(n - 1):
        ax, ay = points[i]
        bx, by = points[i + 1]
        for j in range(i + 2, n - 1):
            cx, cy = points[j]
            dx, dy = points[j + 1]
            den = (bx - ax) * (dy - cy) - (by - ay) * (dx - cx)
            if abs(den) < 1e-12:
                continue
            s = ((cx - ax) * (dy - cy) - (cy - ay) * (dx - cx)) / den
            w = ((cx - ax) * (by - ay) - (cy - ay) * (bx - ax)) / den
            if 0 < s < 1 and 0 < w < 1:
                seen.add((round(ax + (bx - ax) * s, 1), round(ay + (by - ay) * s, 1)))
    return len(seen)


def shape(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    w = max(xs) - min(xs)
    h = max(ys) - min(ys)
    reach = max(math.hypot(x, y) for x, y in points)
    near = min(math.hypot(x, y) for x, y in points)
    return {
        "aspect": round(h / w, 3) if w else 0,
        "reach": round(reach, 4),
        "clearance": round(near / reach, 4) if reach else 0,
    }


def product_curve(rate_a, rate_b, radius_a, radius_b, steps=STEPS):
    """rate as a fraction of a turn per step: (p, q)."""
    pa, qa = rate_a
    pb, qb = rate_b
    angle_a = 2 * math.pi * pa / qa
    angle_b = 2 * math.pi * pb / qb
    points = []
    for k in range(steps):
        z = (1 + radius_a * cmath.exp(1j * angle_a * k)) * (
            1 + radius_b * cmath.exp(1j * angle_b * k)
        )
        points.append((z.real, z.imag))
    return points


def odd_power_curve(degrees, steps=STEPS, span=1.4):
    """x and y each a sum of odd powers of t over [-span, span]."""
    points = []
    for i in range(steps):
        t = -span + 2 * span * i / (steps - 1)
        x = sum(c * t**n for n, c in degrees["x"])
        y = sum(c * t**n for n, c in degrees["y"])
        points.append((x, y))
    return points


def score(points):
    return {
        "crossings": crossings(points),
        "reversals": reversals(points),
        "inflections": inflections(points),
        **shape(points),
        "points": [[round(x, 5), round(y, 5)] for x, y in points],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    # Rates as fractions of a turn per step. Ninth and eighth are the operator's
    # own examples; a third and a quarter are the exact rotations.
    rates = [(1, 12), (1, 9), (1, 8), (1, 6), (1, 4), (2, 9), (3, 9), (4, 9), (3, 8)]
    radii = (0.35, 0.5, 0.65, 0.8, 0.9)

    products = []
    for rate_a, rate_b in product(rates, rates):
        if rate_a == rate_b:
            continue
        for radius_a, radius_b in product(radii, radii):
            points = product_curve(rate_a, rate_b, radius_a, radius_b)
            row = score(points)
            if row["clearance"] < 0.15 or not (0.4 <= row["aspect"] <= 2.5):
                continue
            if row["reversals"] < 2 or row["inflections"] > 3:
                continue
            if not (2 <= row["crossings"] <= 60):
                continue
            row.update(
                family="product",
                rate_a=f"{rate_a[0]}/{rate_a[1]}",
                rate_b=f"{rate_b[0]}/{rate_b[1]}",
                radius_a=radius_a,
                radius_b=radius_b,
            )
            products.append(row)

    products.sort(key=lambda r: (r["reversals"] < 4, -r["crossings"], r["inflections"]))
    print(f"product sums kept: {len(products)}")
    for row in products[:10]:
        print(
            f"  {row['rate_a']} x {row['rate_b']} radii {row['radius_a']}/{row['radius_b']}"
            f" -> {row['crossings']} crossings, {row['reversals']} reversals,"
            f" {row['inflections']} inflections, aspect {row['aspect']},"
            f" clearance {row['clearance']}"
        )

    # Odd powers, both as a graph and as a parametric pair.
    odd_x = (1, 3, 5)
    odd_y = (1, 3, 5)
    powers = []
    for cx in product((-1.0, 0.0, 1.0), repeat=3):
        for cy in product((-1.0, 0.0, 1.0), repeat=3):
            if not any(cx) or not any(cy):
                continue
            degrees = {"x": list(zip(odd_x, cx)), "y": list(zip(odd_y, cy))}
            points = odd_power_curve(degrees)
            row = score(points)
            if not (0.4 <= row["aspect"] <= 2.5):
                continue
            row.update(family="odd-power", coefficients={"x": cx, "y": cy})
            powers.append(row)

    powers.sort(key=lambda r: (-r["inflections"], -r["reversals"]))
    print(f"odd-power pairs kept: {len(powers)}")
    for row in powers[:10]:
        print(
            f"  x {row['coefficients']['x']} y {row['coefficients']['y']}"
            f" -> {row['crossings']} crossings, {row['reversals']} reversals,"
            f" {row['inflections']} inflections, aspect {row['aspect']}"
        )

    if args.write:
        OUT.write_text(
            json.dumps(
                {
                    "format": "curve-lab.pm-product/1",
                    "note": "products of two mover walks (radii under 1 keep the radius positive) and odd-power parametric pairs; loop test = 2+ tangential reversals",
                    "products": products[:12],
                    "odd_powers": powers[:6],
                },
                indent=1,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
