#!/usr/bin/env python3
"""Deep probe: does the multi-mover family give loops, or only dense spirals?

    .venv/bin/python scripts/pm_deep_search.py
    .venv/bin/python scripts/pm_deep_search.py --write

The operator's definition of a loop, made into a test: **the tangential speed
reverses twice while the curvature keeps one sign.** A spiral never reverses its
tangential speed; a dense braid has many reversals and many curvature flips.

So each sampled curve is scored on three things, in this order:

  reversals  how many times the motion goes backwards along its own tangent
  inflections  sign changes of the curvature (fewer is better: a loop tolerates none)
  crossings  distinct intersection points, de-duplicated

The movers: N damped phasors, each a rotation by a fraction of a turn and a
radius per step. Lags are written as `p/q` so a find can be named the way the
`lace-*` family is named. Exactness is stated: q in {1,2,3,4,6} is a rational
rotation, everything else is sampled.
"""

from __future__ import annotations

import argparse
import cmath
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "workbench" / "pm-deep.json"
FACTOR = 2 + 1j
PHI = cmath.phase(FACTOR)
STEPS = 320
EXACT_DENOMINATORS = {1, 2, 3, 4, 6}


def sample(lags, radii, steps=STEPS):
    pts = []
    for k in range(steps):
        z = 0j
        for lag, radius in zip(lags, radii):
            z += (radius ** k) * cmath.exp(1j * (lag * 2 * math.pi + k * PHI))
        pts.append((z.real, z.imag))
    return pts


def reversals(points):
    """How often the motion goes backwards along its own tangent."""
    count = 0
    last = 0
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
    count = 0
    last = 0
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


def aspect(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    w = max(xs) - min(xs)
    h = max(ys) - min(ys)
    return (h / w) if w else 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    rows = []
    # lags as fractions of a turn: mirrored pairs about half, plus the carrier
    for q in (2, 3, 4, 6, 9, 12):
        for p in (1, 2):
            if p * 2 >= q:
                continue
            beat = p / q
            for r_pair in ((1.0, 0.9), (0.99, 1.0), (1.0, 0.75), (0.95, 0.999)):
                for radii in (
                    [1.0, r_pair[0], r_pair[1], 0.9],
                    [1.0, r_pair[0], r_pair[1]],
                    [r_pair[0], r_pair[1]],
                ):
                    n = len(radii)
                    lags = [0.0, 0.5 - beat, 0.5 + beat, 1.0 - beat][:n]
                    if n == 3:
                        lags = [0.0, 0.5 - beat, 0.5 + beat]
                    points = sample(lags, radii)
                    a = aspect(points)
                    if not (0.2 <= a <= 5):
                        continue
                    rows.append({
                        "lags": [round(v, 4) for v in lags],
                        "fractions": [f"0", f"{p}/{q} under", f"{p}/{q} over", "1"][:n],
                        "radii": radii,
                        "crossings": crossings(points),
                        "reversals": reversals(points),
                        "inflections": inflections(points),
                        "aspect": round(a, 3),
                        "exact": q in EXACT_DENOMINATORS,
                        "points": [[round(x, 5), round(y, 5)] for x, y in points],
                    })

    # a loop: reversals present, few inflections, sane aspect
    loops = [row for row in rows if row["reversals"] >= 2 and row["inflections"] <= 2]
    loops.sort(key=lambda row: (-row["crossings"], row["reversals"], row["inflections"]))
    print(f"{len(rows)} sums · {len(loops)} pass the loop test (2+ reversals, ≤2 inflections)")
    for row in loops[:10]:
        print(f"  lags {row['fractions']} radii {row['radii']} → {row['crossings']} crossings, "
              f"{row['reversals']} reversals, {row['inflections']} inflections, aspect {row['aspect']}, exact {row['exact']}")
    dense = sorted(rows, key=lambda row: -row["crossings"])[:5]
    print("densest (likely braids, not loops):")
    for row in dense:
        print(f"  lags {row['fractions']} → {row['crossings']} crossings, {row['reversals']} reversals, {row['inflections']} inflections")

    if args.write:
        OUT.write_text(json.dumps({
            "format": "curve-lab.pm-deep/1",
            "note": "multi-mover damped phasor sums; lags as fractions of a turn; loop test = 2+ tangential reversals with <=2 inflections",
            "loops": loops[:10],
            "densest": dense,
        }, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
