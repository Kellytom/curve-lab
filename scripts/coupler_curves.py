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
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab.crossings import crossing_pairs  # noqa: E402

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
        # A full turn matters more than rational points: walking a slope from
        # -6 to 6 covers only a short arc, and the curve retraced it, inventing
        # crossings. cos/sin for now; the rational walk can follow.
        t = 2 * math.pi * k / steps
        bx, by = r2 * math.cos(t), r2 * math.sin(t)
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
    """Crossing pairs, once per segment pair; the grid counter in curve_lab.crossings.

    The double loop here cost 260k pair tests per 720-station trace, so a 729-linkage
    sweep was 190M tests. The counter is identical (tests/test_crossings.py compares it with
    the plain loop) and fast enough to widen the sweep.
    """
    return crossing_pairs(points)


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
    parser.add_argument("--wide", action="store_true",
                        help="wider link ratios and coupler fractions (about four minutes)")
    parser.add_argument("--random", type=int, default=0,
                        help="N random continuous linkages instead of the grid (a few hundred a second)")
    parser.add_argument("--min-crossings", type=int, default=2,
                        help="keep curves with at least this many crossing pairs (a coupler curve has at most 3 double points, so 4 is impossible)")
    args = parser.parse_args(argv)

    if args.random:
        # The grid is integers and a few fractions; the classic three-node couplers need their own
        # ratios, so search the continuous space instead. The fast counter makes it cheap.
        import random
        rng = random.Random(20261124)
        found = []
        for _ in range(args.random):
            r2 = round(rng.uniform(0.3, 4.0), 3)
            r3 = round(rng.uniform(0.6, 7.0), 3)
            r4 = round(rng.uniform(0.3, 6.0), 3)
            ground = round(rng.uniform(0.6, 7.0), 3)
            a = round(rng.uniform(-2.0, 3.0), 3)
            b = round(rng.uniform(-2.0, 2.0), 3)
            # Only a Grashof linkage with the crank shortest can turn a full circle; without that
            # the trace is a partial arc and no coupler curve is drawn. Every classic multi-node
            # coupler is Grashof, so the filter is the search, not a heuristic.
            links = sorted((r2, r3, r4, ground))
            if links[0] + links[3] > links[1] + links[2]:
                continue
            if r2 != links[0]:
                continue
            pts = trace(r2, r3, r4, ground, a, b)
            if len(pts) < 700:
                continue
            n = crossings(pts)
            if n >= args.min_crossings:
                found.append({"r2": r2, "r3": r3, "r4": r4, "d": ground,
                              "a": a, "b": b, "crossings": n,
                              "mirror": symmetry_gap(pts), "points": pts})
        found.sort(key=lambda item: (-item["crossings"], item["mirror"]))
        print(f"{len(found)} of {args.random} random couplers with {args.min_crossings}+ crossings")
        for item in found[:8]:
            print(f"  r2 {item['r2']} r3 {item['r3']} r4 {item['r4']} ground {item['d']} "
                  f"a {item['a']} b {item['b']} -> {item['crossings']} crossings · "
                  f"mirror {item['mirror']}")
        return 0
    if args.wide:
        r2s, r3s, r4s, grounds = (1, 2, 3, 4), (2, 3, 4, 5, 6), (1, 2, 3, 4, 5), (2, 3, 4, 5, 6)
        a_s = (0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0)
        b_s = (0.2, 0.4, 0.6, 0.8, 1.0, 1.2)
    else:
        r2s, r3s, r4s, grounds = (1, 2, 3), (3, 4, 5), (2, 3, 4), (3, 4, 5)
        a_s, b_s = (0.5, 1.0, 1.5), (0.3, 0.6, 0.9)

    found = []
    for r2 in r2s:
        for r3 in r3s:
            for r4 in r4s:
                for ground in grounds:
                    for a in a_s:
                        for b in b_s:
                            pts = trace(r2, r3, r4, ground, a, b)
                            if len(pts) < 8:
                                continue
                            n = crossings(pts)
                            if n >= args.min_crossings:
                                found.append({
                                    "r2": r2, "r3": r3, "r4": r4, "d": ground,
                                    "a": a, "b": b, "crossings": n,
                                    "mirror": symmetry_gap(pts),
                                    "points": [[round(x, 4), round(y, 4)] for x, y in pts],
                                })
    found.sort(key=lambda item: (-item["crossings"], item["mirror"]))
    print(f"{len(found)} coupler curves with {args.min_crossings}+ crossings")
    for item in found[:8]:
        print(f"  r2 {item['r2']} r3 {item['r3']} r4 {item['r4']} ground {item['d']} "
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
