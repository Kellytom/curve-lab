#!/usr/bin/env python3
"""Add Tschirnhausen and three variations as records.

    .venv/bin/python scripts/add_tschirnhausen.py
    cd app && PATH="$HOME/node24/bin:$PATH" node scripts/add-registry-curves.mjs

The curve is y² = x²(x + 3), parametrised x = t² − 3, y = t(t² − 3). It is rational (both rows
are polynomials in t), but its node sits at t = ±√3, which is irrational, so the crossing point
has no integer parameter. It is stored as a sampled polyline, exactly like the other named
curves that have no speed pair: the equation is exact, the drawing between stations is not.

Four records: the curve, a half-size copy, a 45° copy and its mirror. The 45° copy carries √2
in every station, so it is sampled by construction and says so.
"""

import json
import math
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "workbench" / "curve-registry.json"
SAMPLES = 400
LO, HI = -2.4, 2.4


def base_points():
    pts = []
    for i in range(SAMPLES + 1):
        t = LO + (HI - LO) * i / SAMPLES
        pts.append((t * t - 3, t * (t * t - 3)))
    return pts


def turn(points, degrees):
    a = degrees * math.pi / 180
    c, s = math.cos(a), math.sin(a)
    return [(x * c - y * s, x * s + y * c) for x, y in points]


def rounded(points):
    return [[round(x, 6), round(y, 6)] for x, y in points]


def main():
    base = base_points()
    variants = [
        dict(uid="c-0398", name="tschirnhausen", points=base,
             note="the Tschirnhausen cubic · x = t² − 3, y = t(t² − 3) · the node is at "
                  "t = ±√3, so its crossing point has no rational parameter"),
        dict(uid="c-0399", name="tschirnhausen-half", points=[(x / 2, y / 2) for x, y in base],
             note="the Tschirnhausen cubic at half size · same equation, every station halved"),
        dict(uid="c-0400", name="tschirnhausen-rot45", points=turn(base, 45),
             note="the Tschirnhausen cubic turned 45° · sampled: the turn carries √2, so the "
                  "stations are not exact"),
        dict(uid="c-0401", name="tschirnhausen-mirror", points=[(-x, y) for x, y in base],
             note="the Tschirnhausen cubic mirrored across x = 0 · a file MIRROR_CURVE action "
                  "reproduces it from the base record"),
    ]

    registry = json.loads(REGISTRY.read_text())
    have = {row["uid"] for row in registry["curves"]}
    added = 0
    for variant in variants:
        if variant["uid"] in have:
            print(f"  {variant['uid']} already present, left alone")
            continue
        registry["curves"].append({
            "uid": variant["uid"],
            "name": variant["name"],
            "aliases": [],
            "path": rounded(variant["points"]),
            "kind": "polyline",
            "family": "tschirnhausen",
            "source": "named",
            "lists": ["new"],
            "starred": False,
            "candidate": False,
            "importance": 0,
            "transform": {"degrees": 0, "matrix": [["1", "0"], ["0", "1"]], "exact": True},
            "note": variant["note"],
        })
        added += 1
    if added:
        REGISTRY.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n")
    print(f"{added} Tschirnhausen record(s) added; {len(registry['curves'])} curves in the registry")


if __name__ == "__main__":
    main()
