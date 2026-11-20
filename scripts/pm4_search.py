#!/usr/bin/env python3
"""Four prime movers: a pair just under 180, a mirrored pair just over.

    .venv/bin/python scripts/pm4_search.py
    .venv/bin/python scripts/pm4_search.py --write

The operator's reading (2026-11-19): the two-PM sum is a spiral, and spirals are
not loops. A loop is a different animal — the speed rises to a maximum at the
middle of the loop and falls again while the turn keeps one sign. What can do
that is a sum in which one mover is *almost* cancelled:

    PM1  lag   0°            the carrier
    PM2  lag 180° - d        nearly opposite, so the pair beats slowly
    PM3  lag 180° + d        the mirror of PM2: above 180, not at it
    PM4  lag 360° - d        the mirror of PM1

with a radius per mover, so the near-cancellation leaves a residual that turns
once and comes back — the shape of a loop rather than a spiral.

Everything is a damped phasor sum:

    P(k) = sum_i  r_i^k · exp(i (theta_i + k phi)),   phi = arg(factor)

which is exact arithmetic in the ratios; the drawing is sampled. The search
scores crossing pairs and rejects slivers, and it reports the beat `d` and the
radii, so a find can be rebuilt.
"""

from __future__ import annotations

import argparse
import cmath
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "workbench" / "pm4-curves.json"
FACTOR = 2 + 1j
PHI = cmath.phase(FACTOR)
STEPS = 400


def curve(lags, radii, steps=STEPS):
    points = []
    for k in range(steps):
        z = 0j
        for theta, radius in zip(lags, radii):
            z += (radius ** k) * cmath.exp(1j * (math.radians(theta) + k * PHI))
        points.append((z.real, z.imag))
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
    for d in (1, 2, 3, 5, 7, 11, 15):
        for r1 in (1.0, 0.98, 0.95):
            for r2 in (0.9, 0.95, 0.99, 1.0):
                lags = [0.0, 180.0 - d, 180.0 + d, 360.0 - d]
                radii = [r1, r2, r2, r1 * 0.9]
                points = curve(lags, radii)
                n = crossings(points)
                a = aspect(points)
                if not (0.2 <= a <= 5):
                    continue
                rows.append({
                    "beat": d, "lags": lags, "radii": [round(r, 3) for r in radii],
                    "crossings": n, "aspect": round(a, 3),
                    "points": [[round(x, 5), round(y, 5)] for x, y in points],
                })

    rows.sort(key=lambda row: (-row["crossings"], abs(row["aspect"] - 1)))
    print(f"{len(rows)} four-mover sums · best {rows[0]['crossings'] if rows else 0} crossing pairs")
    for row in rows[:8]:
        print(f"  beat {row['beat']:>2}° · radii {row['radii']} → {row['crossings']} crossings · aspect {row['aspect']}")

    if args.write and rows:
        OUT.write_text(json.dumps({
            "format": "curve-lab.pm4/1",
            "note": "four-mover damped phasor sum, lags 0 / 180-d / 180+d / 360-d; sampled drawing",
            "curves": rows[:8],
        }, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
