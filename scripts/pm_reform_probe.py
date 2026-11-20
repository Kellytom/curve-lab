#!/usr/bin/env python3
"""The prime mover's table, and the circle taken out of a curve built on it.

    .venv/bin/python scripts/pm_reform_probe.py --write     # workbench/pm-reform.json

The stations are **the driver table** — `k`, `a`, `b`, `denominator` for both
directions, the same rule as `driverRows()` in
`app/src/scripts/prime-mover-driver.js`: step by `(ax + i·ay)/z`, reduce nothing,
keep the denominator as a power of the hypotenuse.

A whole-number map sends `(X, Y)` to `(x, y)`. `P = x² + y²`, `C` is its mean over
the stations, and the reformed point is `z·(P − C)/P`. The stations stay exact;
only the line drawn between them is sampled, and the figure says so.
"""

from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "workbench" / "pm-reform.json"
TRIPLE = (3, 4, 5)
STEPS = 10
SAMPLES = 1440


def driver_table(triple, steps):
    """The engine's table: both directions, one row per station."""
    ax, ay, z = triple
    rows = [(0, Fraction(1), Fraction(0))]
    for k in range(1, steps + 1):
        X, Y = rows[-1][1], rows[-1][2]
        rows.append((k, X * Fraction(ax, z) - Y * Fraction(ay, z),
                     X * Fraction(ay, z) + Y * Fraction(ax, z)))
    negative = [(-k, X, -Y) for k, X, Y in rows[1:]][::-1]
    return negative + rows


def lens(X, Y):
    return X * (1 - Y * Y), Y


def text(value):
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    rows = driver_table(TRIPLE, STEPS)
    stations = [(X, Y) for _, X, Y in rows]
    base = [lens(X, Y) for X, Y in stations]
    P = [x * x + y * y for x, y in base]
    C = sum(P) / len(P)
    reformed = [(x * (1 - C / p), y * (1 - C / p)) for (x, y), p in zip(base, P)]

    def sampled(map_fn, n=SAMPLES):
        points = []
        for i in range(n + 1):
            angle = 2 * math.pi * i / n
            points.append(map_fn(math.cos(angle), math.sin(angle)))
        return [[round(x, 6), round(y, 6)] for x, y in points]

    dense = sampled(lens)
    dense_reformed = [[round(x * (1 - float(C) / (x * x + y * y)), 6),
                       round(y * (1 - float(C) / (x * x + y * y)), 6)]
                      for x, y in dense]

    def bounds(points):
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        return [min(xs), max(xs), min(ys), max(ys)]

    exact = [{"k": k, "X": text(X), "Y": text(Y), "Xdecimal": round(float(X), 9),
              "Ydecimal": round(float(Y), 9)} for k, X, Y in rows]

    panels = [
        {
            "key": "pm-lens",
            "title": "the prime mover's table, sent through the lens map",
            "equation": "x = X(1 − Y²),  y = Y   on the (3,4,5) table",
            "formulas": [
                f"table        {len(rows)} stations, 10 steps each way, closing gap 8.7°",
                "map          x = X(1 − Y²),  y = Y",
                "stations     exact ratios a/z^k from the driver table",
            ],
            "legend": [
                {"label": "the lens — a closed lens, 0 crossing pairs", "colour": "#6f4a2a"},
                {"label": "the table's stations", "colour": "#c9761f"},
            ],
            "paths": [{"name": "the lens", "colour": "#6f4a2a", "points": dense}],
            "stations": [[round(float(X), 9), round(float(Y), 9)] for X, Y in base],
            "bounds": bounds(dense),
            "samples": SAMPLES,
        },
        {
            "key": "pm-lens-reformed",
            "title": "the same curve with the circle taken out",
            "equation": "z̃ = z·(P − C)/P,  P = x² + y²",
            "formulas": [
                f"C = mean of P = {C.numerator}/{C.denominator} ≈ {float(C):.4f}",
                "the reform passes through the origin where P = C",
                "the stations are exact; the line between them is sampled",
            ],
            "legend": [
                {"label": "the reformed lens — a new figure", "colour": "#a8341f"},
                {"label": "the stations, carried through the reform", "colour": "#c9761f"},
            ],
            "paths": [{"name": "the reformed lens", "colour": "#a8341f", "points": dense_reformed}],
            "stations": [[round(float(x), 9), round(float(y), 9)] for x, y in reformed],
            "bounds": bounds(dense_reformed),
            "samples": SAMPLES,
        },
    ]
    document = {
        "format": "curve-lab.pm-reform/1",
        "triple": ",".join(str(v) for v in TRIPLE),
        "steps": STEPS,
        "map": "x = X(1 − Y²), y = Y",
        "C": f"{C.numerator}/{C.denominator}",
        "Cdecimal": round(float(C), 6),
        "stations": exact,
        "panels": panels,
    }
    print(f"table {document['triple']}, {len(rows)} stations, C = {document['C']} ≈ {document['Cdecimal']}")
    for panel in panels:
        print(f"  {panel['key']:18} {len(panel['paths'][0]['points'])} points, "
              f"{len(panel['stations'])} stations")
    if args.write:
        OUT.write_text(json.dumps(document, indent=1, ensure_ascii=True) + "\n")
        print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
