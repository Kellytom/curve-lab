"""The lace family, reconstructed exactly: one mirrored pair, one middle count.

    .venv/bin/python scripts/lace_finder.py            # sweep, rank, write finder.json

The stored finds are PH curves: x' = u² - v², y' = 2uv, with

    u(t) = 1 - 2t + 2t²                                   fixed, the operator's row
    v(t) = (t - p)(t - (1 - p))(t - 1/2)^m                the lever

and v scaled to integers. Checked against `lace-1of8-3`: p = 1/8, m = 3 gives
exactly [-7, 106, -532, 1208, -1280, 512], the stored row.

So the simplest change that makes a different curve is p — one number — or m,
the middle count. The crossing count comes from the same router the records
were audited with (`scripts/ph_crossings.py`), not from a new instrument.
"""

from __future__ import annotations

import json
import math
import sys
from fractions import Fraction
from math import gcd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import numpy as np  # noqa: E402

from curve_lab.datafile import FORMATS  # noqa: E402
from ph_crossings import spine, stable_crossings  # noqa: E402

OUT = ROOT / "workbench" / "finder.json"
U_ROW = (Fraction(1), Fraction(-2), Fraction(2))
PAIRS = (Fraction(1, 12), Fraction(1, 10), Fraction(1, 8), Fraction(1, 6),
         Fraction(1, 5), Fraction(1, 4), Fraction(1, 3), Fraction(3, 8), Fraction(2, 5))
MIDDLES = (0, 1, 2, 3, 4)
KEEP = 12
SAMPLES = 240
RAIL_SHARE = 0.015


def mul(a, b):
    out = [Fraction(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def linear(root):
    return [-Fraction(root), Fraction(1)]


def v_row(pair, middle):
    poly = [Fraction(1)]
    poly = mul(poly, linear(pair))
    poly = mul(poly, linear(1 - pair))
    for _ in range(middle):
        poly = mul(poly, linear(Fraction(1, 2)))
    factor = 1
    for c in poly:
        factor = factor * c.denominator // gcd(factor, c.denominator)
    ints = [int(c * factor) for c in poly]
    common = 0
    for c in ints:
        common = gcd(common, abs(c))
    return [c // (common or 1) for c in ints]


def path_of(u, v, steps=SAMPLES):
    # The router's own integration, so the drawing and the count agree.
    t, x, y = spine([float(c) for c in u], [float(c) for c in v], samples=steps)
    return [[round(float(a), 6), round(float(b), 6)] for a, b in zip(x, y)]


def rails_of(points, share=RAIL_SHARE):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    size = math.hypot(max(xs) - min(xs), max(ys) - min(ys)) or 1.0
    d = share * size
    left, right = [], []
    for i, (px, py) in enumerate(points):
        a = points[max(0, i - 1)]
        b = points[min(len(points) - 1, i + 1)]
        vx, vy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(vx, vy) or 1.0
        nx, ny = -vy / length, vx / length
        left.append([round(px + d * nx, 6), round(py + d * ny, 6)])
        right.append([round(px - d * nx, 6), round(py - d * ny, 6)])
    return [left, right]


def main():
    found = []
    for pair in PAIRS:
        for middle in MIDDLES:
            v = v_row(pair, middle)
            hits = stable_crossings([float(c) for c in U_ROW], [float(c) for c in v])
            if len(hits) < 2:
                continue
            points = path_of(U_ROW, v)
            found.append({
                "name": f"p={pair.numerator}/{pair.denominator} · middle {middle}",
                "u": [str(c) for c in U_ROW],
                "v": [str(c) for c in v],
                "degree": max(len(v) * 2, len(U_ROW) * 2),
                "proper": True,
                "path": points,
                "rails": rails_of(points),
                "crossings": len(hits),
                "features": {"crossing_pairs": len(hits), "grid": 0},
                "peak": None,
                "flags": [f"{len(hits)} crossings"],
            })
    found.sort(key=lambda item: -item["crossings"])
    best = found[:KEEP]
    OUT.write_text(json.dumps({
        "format": FORMATS["finder.json"],
        "note": "Lace family: u fixed, v from one mirrored pair and a middle count.",
        "curves": best,
    }, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    for item in best:
        print(f'{item["name"]:24} crossings {item["crossings"]:3}  v={item["v"][:6]}')
    print(f"wrote {OUT.relative_to(ROOT)} with {len(best)} curves")
    return 0


if __name__ == "__main__":
    sys.exit(main())
