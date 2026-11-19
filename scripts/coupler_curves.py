#!/usr/bin/env python3
"""Coupler curves: what a four-bar linkage draws.

    .venv/bin/python scripts/coupler_curves.py
    .venv/bin/python scripts/coupler_curves.py --write

A four-bar linkage is two fixed pivots, a crank, a coupler and a rocker. A point
on the coupler traces a plane curve — a **coupler curve** — and these are the
classic source of symmetric curves with many nodes: the same object a mechanism
designer or a century of kinematics text would call by that name. This is the
industrial relative of our folded-at-the-middle family, so it is worth trying
before the search comes back.

The construction, per crank angle theta:

    B = O2 + r2 (cos t, sin t)
    C = the intersection of the circles (B, r3) and (O4, r4)
    P = B + a (C - B) + b perp(C - B)

Sampled, not exact — cos and sin of a general angle are irrational, which the
project's own rule forbids claiming as exact. A rational parameterisation
`t = tan(theta/2)` exists and can follow if the family pays.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "workbench" / "coupler-curves.json"


def circle_hit(bx, by, r3, ox, oy, r4, previous=None):
    dx, dy = ox - bx, oy - by
    d = math.hypot(dx, dy)
    if d == 0 or d > r3 + r4 or d < abs(r3 - r4):
        return None
    a = (r3 * r3 - r4 * r4 + d * d) / (2 * d)
    h = math.sqrt(max(0.0, r3 * r3 - a * a))
    mx, my = bx + a * dx / d, by + a * dy / d
    rx, ry = -dy / d, dx / d
    first = (mx + h * rx, my + h * ry)
    second = (mx - h * rx, my - h * ry)
    if previous is None:
        return first
    # Keep the branch: a jump between them zigzags and invents crossings.
    return first if math.hypot(first[0] - previous[0], first[1] - previous[1]) <= \
        math.hypot(second[0] - previous[0], second[1] - previous[1]) else second


def crank_point(slope):
    """A point of the unit circle from a rational slope t = tan(theta/2).

    cos = (1 - t^2)/(1 + t^2), sin = 2t/(1 + t^2): exact rationals, and with
    t = 1/2 the point is (3/5, 4/5) -- the 3-4-5 triple. This is the shape the
    project will keep when the cos/sin are torn out: slopes and lattice points,
    multiplied by 5^n to stay whole.
    """
    p, q = slope
    den = q * q + p * p
    return (q * q - p * p) / den, (2 * p * q) / den


def trace(r2, r3, r4, ground, a, b, steps=720):
    points = []
    previous = None
    for k in range(steps + 1):
        # Walk the crank by slope, not by angle: t from -6 to 6 and back through
        # infinity, which covers the whole turn.
        u = -6 + 12 * k / steps
        p, q = abs(u), 1
        bx, by = crank_point((p, q))
        bx, by = r2 * bx, r2 * by
        hit = circle_hit(bx, by, r3, ground, 0.0, r4, previous)
        if hit is None:
            return []
        previous = hit
        cx, cy = hit
        ux, uy = cx - bx, cy - by
        px = bx + a * ux - b * uy
        py = by + a * uy + b * ux
        points.append((px, py))
    return points


def crossings(points):
    n = len(points)
    if n < 8:
        return 0
    hits = 0
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
                hits += 1
    return hits


def symmetry_gap(points):
    """Distance from the curve to its own mirror across the vertical axis."""
    if not points:
        return 9
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    cx = (min(xs) + max(xs)) / 2
    size = max(max(xs) - min(xs), max(ys) - min(ys)) or 1
    mirrored = [(2 * cx - x, y) for x, y in points]
    step = max(1, len(points) // 90)
    total = 0.0
    for i in range(0, len(points), step):
        px, py = mirrored[i]
        best = min((px - qx) ** 2 + (py - qy) ** 2 for qx, qy in points[::step])
        total += math.sqrt(best)
    return round(total / len(range(0, len(points), step)) / size, 4)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    found = []
    for r2 in (1, 2, 3):
        for r3 in (3, 4, 5):
            for r4 in (2, 3, 4):
                for ground in (3, 4, 5):
                    for a in (0.5, 1.0, 1.5):
                        for b in (0.3, 0.6, 0.9):
                            pts = trace(r2, r3, r4, ground, a, b)
                            if len(pts) < 8:
                                continue
                            n = crossings(pts)
                            if n >= 4:
                                found.append({
                                    "r2": r2, "r3": r3, "r4": r4, "ground": ground,
                                    "a": a, "b": b, "crossings": n,
                                    "mirror": symmetry_gap(pts),
                                    "points": [[round(x, 4), round(y, 4)] for x, y in pts],
                                })
    found.sort(key=lambda item: (-item["crossings"], item["mirror"]))
    print(f"{len(found)} coupler curves with 4+ crossings")
    for item in found[:8]:
        print(f"  r2 {item['r2']} r3 {item['r3']} r4 {item['r4']} ground {item['ground']} "
              f"a {item['a']} b {item['b']} → {item['crossings']} crossings · mirror {item['mirror']}")

    if args.write and found:
        OUT.write_text(json.dumps({
            "format": "curve-lab.coupler-curves/1",
            "note": "four-bar coupler curves, sampled (cos/sin of a general angle); crossings counted on the polyline",
            "curves": found[:20],
        }, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
