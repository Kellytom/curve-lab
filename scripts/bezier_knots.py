#!/usr/bin/env python3
"""Looped Bézier curves from integer control polygons.

    .venv/bin/python scripts/bezier_knots.py            # search
    .venv/bin/python scripts/bezier_knots.py --write    # keep the best

A different machine from everything in the registry: whole-number control
points, Bernstein basis, de Casteljau evaluation. A control polygon that doubles
back gives a curve that crosses itself, and with integers the result is exact at
every dyadic t (halves, quarters) with no square roots and no trig.

The search keeps curves that cross themselves several times and still look like
a figure — aspect between 0.4 and 2.5 — so a sliver cannot win.
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "workbench" / "bezier-knots.json"


def de_casteljau(controls, t):
    pts = [list(p) for p in controls]
    while len(pts) > 1:
        pts = [[(1 - t) * a[0] + t * b[0], (1 - t) * a[1] + t * b[1]]
               for a, b in zip(pts, pts[1:])]
    return pts[0]


def sample(controls, steps=260):
    return [de_casteljau(controls, k / steps) for k in range(steps + 1)]


def crossings(points):
    hits = 0
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
                hits += 1
    return hits


def aspect(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    w = max(xs) - min(xs)
    h = max(ys) - min(ys)
    return (h / w) if w else 0.0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=4000)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    rng = random.Random(11)
    best = []
    for _ in range(args.n):
        degree = rng.choice([4, 5, 6])
        # Distinct ends and no repeated handles: a repeated handle makes the
        # curve retrace a line, and every overlapping segment pair then counts
        # as a crossing. That produced 14 "crossings" on a plain arc.
        ends = [(0, 0), (6, 0)]
        inner = set()
        while len(inner) < degree - 1:
            inner.add((rng.randint(-3, 9), rng.randint(-5, 5)))
        controls = [ends[0]] + list(inner) + [ends[1]]
        pts = sample(controls)
        n = crossings(pts)
        if n < 2:
            continue
        a = aspect(pts)
        if not (0.4 <= a <= 2.5):
            continue
        best.append({"degree": degree, "controls": controls, "crossings": n,
                     "aspect": round(a, 3), "points": [[round(x, 4), round(y, 4)] for x, y in pts]})
    best.sort(key=lambda item: (-item["crossings"], abs(item["aspect"] - 1)))
    print(f"{len(best)} looped integer Béziers from {args.n} draws")
    for item in best[:6]:
        print(f"  degree {item['degree']} · {item['crossings']} crossings · aspect {item['aspect']} · controls {item['controls']}")

    if args.write and best:
        OUT.write_text(json.dumps({
            "format": "curve-lab.bezier-knots/1",
            "note": "whole-number control polygons, Bernstein form; exact at dyadic t",
            "curves": best[:10],
        }, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
