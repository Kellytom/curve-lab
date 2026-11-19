#!/usr/bin/env python3
"""The mobile: two vanes turning at different rates.

    .venv/bin/python scripts/mobile_search.py
    .venv/bin/python scripts/mobile_search.py --write

A mobile's main vane swings while the smaller parts twirl. As a curve that is two
rotations composed:

    P(t) = r1 (cos t, sin t) + r2 (cos k t, sin k t),   k = p/q rational

which is the classical epicycloid/hypotrochoid family: guaranteed to loop, and
rational in the ratios. Sampled here, cos and sin of a real angle, which the
project allows for exploration but never claims as exact.

The search keeps curves that cross themselves and are reasonably square, and it
reports the ratios in the field's terms (`k = p/q`) so a find can be rebuilt.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "workbench" / "mobile-curves.json"
STEPS = 900


def trace(r1, r2, p, q):
    points = []
    for k in range(STEPS + 1):
        t = 2 * math.pi * k / STEPS
        points.append((r1 * math.cos(t) + r2 * math.cos(p * t / q),
                       r1 * math.sin(t) + r2 * math.sin(p * t / q)))
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
            den = (bx - ax) * (dy - cy) - (by - ay) * (dx - cx)
            if abs(den) < 1e-12:
                continue
            s = ((cx - ax) * (dy - cy) - (cy - ay) * (dx - cx)) / den
            w = ((cx - ax) * (by - ay) - (cy - ay) * (bx - ax)) / den
            if 0 < s < 1 and 0 < w < 1:
                seen.add((round(ax + (bx - ax) * s, 2), round(ay + (by - ay) * s, 2)))
    return len(seen)


def aspect(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    w = max(xs) - min(xs)
    h = max(ys) - min(ys)
    return (h / w) if w else 0


def symmetry(points):
    xs = [p[0] for p in points]
    cx = (min(xs) + max(xs)) / 2
    size = max(max(xs) - min(xs), max(p[1] for p in points) - min(p[1] for p in points)) or 1
    step = max(1, len(points) // 120)
    total = 0.0
    count = 0
    for i in range(0, len(points), step):
        px, py = 2 * cx - points[i][0], points[i][1]
        best = min((px - qx) ** 2 + (py - qy) ** 2 for qx, qy in points[::step])
        total += math.sqrt(best)
        count += 1
    return round(total / count / size, 3)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    rows = []
    for p, q in ((3, 2), (5, 2), (5, 3), (7, 3), (7, 4), (8, 3), (9, 4), (11, 5), (2, 1), (3, 1)):
        for r1, r2 in ((1, 0.5), (1, 0.8), (1, 1.0), (2, 1)):
            if math.gcd(p, q) != 1:
                continue
            pts = trace(r1, r2, p, q)
            rows.append({
                "p": p, "q": q, "r1": r1, "r2": r2,
                "crossings": crossings(pts),
                "aspect": round(aspect(pts), 3),
                "mirror": symmetry(pts),
                "points": [[round(x, 4), round(y, 4)] for x, y in pts],
            })

    rows.sort(key=lambda row: (-row["crossings"], abs(row["aspect"] - 1)))
    print(f"{len(rows)} mobiles")
    for row in rows[:8]:
        print(f"  k = {row['p']}/{row['q']} · r {row['r1']}:{row['r2']} → {row['crossings']} crossings · "
              f"aspect {row['aspect']} · mirror {row['mirror']}")

    if args.write:
        OUT.write_text(json.dumps({
            "format": "curve-lab.mobile-curves/1",
            "note": "P(t) = r1 (cos t, sin t) + r2 (cos kt, sin kt), k = p/q; sampled, not exact",
            "curves": rows[:8],
        }, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
