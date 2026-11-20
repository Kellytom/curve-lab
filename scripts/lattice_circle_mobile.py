#!/usr/bin/env python3
"""A mobile on the integer lattice: both arms walk exact lattice circles.

    .venv/bin/python scripts/lattice_circle_mobile.py
    .venv/bin/python scripts/lattice_circle_mobile.py --write

Why not the eight-point compass? Because it is too coarse to be a spirograph:
every compass walk closes in eight steps with seven or eight stations and no
crossing at all (measured: 42 closed walks, 0 crossing pairs). A spirograph
needs many stations per lap.

The finer exact compass is the **integer points on a circle**. For radius r the
points with x² + y² = r² are exact integers by definition — no rounding, no
trigonometry. Their count grows with the number of prime factors of r that are 1
mod 4:

    r = 5      12 points
    r = 13     12 points
    r = 25     20 points
    r = 65     16 points
    r = 1105   64 points

So the mobile is the classical sum of two arms, with each arm stepping through
the lattice points of its own circle:

    P_k = A[k mod n_A] + B[(k·ratio) mod n_B]

`ratio` is the spirograph ratio. Every station is the sum of two integer points,
so it is an integer point; the curve closes because each arm is periodic; and it
can be cut at any station because every station is on the lattice.

The cost, stated: the integer points on a circle are **not evenly spaced in
angle**, so the pen speeds up and slows down where the points crowd. That wobble
is the lattice's own character — the price of having every station exact.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "workbench" / "lattice-mobile.json"


def circle_points(radius: int):
    """Every integer point on x² + y² = radius², in order of angle."""
    points = []
    r2 = radius * radius
    for x in range(-radius, radius + 1):
        y2 = r2 - x * x
        y = math.isqrt(y2)
        if y * y != y2:
            continue
        points.append((x, y))
        if y:
            points.append((x, -y))
    points.sort(key=lambda p: math.atan2(p[1], p[0]))
    return points


def mobile(radius_a, radius_b, ratio, steps):
    a = circle_points(radius_a)
    b = circle_points(radius_b)
    points = []
    for k in range(steps):
        ax, ay = a[k % len(a)]
        bx, by = b[(k * ratio) % len(b)]
        points.append((ax + bx, ay + by))
    return points


def crossings(points):
    seen = set()
    n = len(points)
    for i in range(n - 1):
        ax, ay = points[i]
        bx, by = points[i + 1]
        for j in range(i + 2, n - 1):
            cx, cy = points[j]
            dx, dy = points[j + 1]
            if i == 0 and j == n - 2 and points[0] == points[-1]:
                continue
            den = (bx - ax) * (dy - cy) - (by - ay) * (dx - cx)
            if den == 0:
                continue
            s = ((cx - ax) * (dy - cy) - (cy - ay) * (dx - cx)) / den
            w = ((cx - ax) * (by - ay) - (cy - ay) * (bx - ax)) / den
            if 0 < s < 1 and 0 < w < 1:
                seen.add((round(ax + (bx - ax) * s, 3), round(ay + (by - ay) * s, 3)))
    return len(seen)


def aspect(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    w = max(xs) - min(xs)
    h = max(ys) - min(ys)
    return round(h / w, 3) if w else 0.0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    radii = (5, 13, 17, 25, 65)
    rows = []
    for radius_a in radii:
        for radius_b in radii:
            if radius_a == radius_b:
                continue
            n_a = len(circle_points(radius_a))
            n_b = len(circle_points(radius_b))
            for ratio in (1, 2, 3, 4, 5, 7):
                if math.gcd(ratio, n_b) != 1:
                    continue
                steps = math.lcm(n_a, n_b)
                points = mobile(radius_a, radius_b, ratio, steps)
                rows.append(
                    {
                        "radiusA": radius_a,
                        "radiusB": radius_b,
                        "ratio": f"{ratio}/1",
                        "pointsA": n_a,
                        "pointsB": n_b,
                        "steps": steps,
                        "crossings": crossings(points),
                        "aspect": aspect(points),
                        "convex": len(set(points)) == len(points),
                        "points": points,
                    }
                )

    # symmetric figures are the classical ones; the interest is in the rest, but
    # an aspect near 1 keeps a plate readable
    keep = [r for r in rows if 0.5 <= r["aspect"] <= 2.0 and r["crossings"] >= 1]
    keep.sort(key=lambda r: (-r["crossings"], abs(r["aspect"] - 1)))
    print(f"{len(rows)} mobiles · {len(keep)} with at least one crossing and a readable aspect")
    for row in keep[:12]:
        print(
            f"  radii {row['radiusA']}:{row['radiusB']} ratio {row['ratio']} · "
            f"{row['pointsA']}+{row['pointsB']} points · {row['steps']} steps · "
            f"{row['crossings']} crossings · aspect {row['aspect']}"
        )

    if args.write:
        OUT.write_text(
            json.dumps(
                {
                    "format": "curve-lab.lattice-mobile/1",
                    "note": "two arms walking integer points on circles of radius r; every station an integer point; ratio is the spirograph ratio",
                    "curves": keep[:16],
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
