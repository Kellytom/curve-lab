"""The drawings for Fig. 9: the three named database curves, and the quadratic example.

    .venv/bin/python scripts/circle_plots.py --write     # workbench/circle-plots.json

Every point written here is an **exact rational** evaluated in `Fraction` and only then
converted to a float for drawing: the stations are exact, the line between them is a
cubic Bézier chain drawn by `app/src/lib/plot-figure.js`, and the figure says so.

The three curves are the ones the operator named:

    c-0028  lace-2-eight-3     u = 1 − 2t + 2t²,  v = the stored row
    c-0029  lace-balloon-3
    c-0060  lace-arch-x-1

For each: speed `x' = u² − v²`, `y' = 2uv`, integrated exactly, sampled at `t = k/N`.
The fourth panel is the operator's equation: the original `x² + 2xy + y² = 1` (two lines),
the circle taken out `2xy = 1` (a hyperbola), and the twelve exact stations of the walk.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from circle_split import (  # noqa: E402
    exact_stations, padd, peval, pintegral, pmul, psub, trim,
)

OUT = ROOT / "workbench" / "circle-plots.json"
SAMPLES = 240
TRIPLE = (3, 4, 5)
NAMED = [("c-0028", "lace-2-eight-3"), ("c-0029", "lace-balloon-3"), ("c-0060", "lace-arch-x-1")]



def poly_text(coefficients, variable="t"):
    """A polynomial as a reader can check it: 1 − 2t + 2t², exact parts only."""
    terms = []
    for power, coefficient in enumerate(coefficients):
        coefficient = Fraction(coefficient)
        if coefficient == 0:
            continue
        sign = "−" if coefficient < 0 else ("+" if terms else "")
        size = abs(coefficient)
        body = "" if size == 1 and power else str(size)
        if power == 0:
            term = body or "1"
        elif power == 1:
            term = f"{body}{variable}"
        elif power <= 9:
            term = f"{body}{variable}{str(power).translate(str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹"))}"
        else:
            term = f"{body}{variable}^{power}"
        if sign == "−":
            terms.append(f"−{term}")
        elif sign == "+":
            terms.append(f"+ {term}")
        else:
            terms.append(term)
    return " ".join(terms) if terms else "0"


def row_text(row):
    return "[" + ", ".join("0" if c == 0 else str(c) for c in row) + "]"


def lace_panel(uid, name, registry, stations):
    """Two panels: the curve stationed by the circle, and the circle's remainder."""
    record = next(r for r in registry["curves"] if r["uid"] == uid)
    u = trim(record["speedX"])
    v = trim(record["speedY"])
    speed_x = trim(psub(pmul(u, u), pmul(v, v)))
    speed_y = trim([Fraction(2) * c for c in pmul(u, v)])
    position_x = pintegral(speed_x)
    position_y = pintegral(speed_y)
    def at(t):
        return peval(position_x, t), peval(position_y, t)

    points = []
    for k in range(SAMPLES + 1):
        x, y = at(Fraction(k, SAMPLES))
        points.append([round(float(x), 6), round(float(y), 6)])

    # P(t) = x(t)² + y(t)², its mean C, and the remainder R = P − C
    squared = padd(pmul(position_x, position_x), pmul(position_y, position_y))
    mean = sum(c / Fraction(i + 1) for i, c in enumerate(squared))
    remainder = trim(psub(squared, [mean]))

    curve_xs = [p[0] for p in points]
    curve_ys = [p[1] for p in points]

    # the circle-parameter stations: t = Y/(1+X), kept to the curve's own interval
    marks = []
    for X, Y in stations:
        if X == -1:
            continue
        t = Y / (1 + X)
        if not (0 <= t <= 1):
            continue
        x, y = at(t)
        marks.append([round(float(x), 6), round(float(y), 6)])

    formulas = [
        f"stored rows   u = {poly_text(u)}   v = {poly_text(v)}",
        f"the speed     x′ = u² − v²,  y′ = 2uv   (degrees {len(speed_x) - 1} and {len(speed_y) - 1})",
        f"stations      t = Y / (1 + X), from the walk; the dots are those stations",
        "circle out    x̃ = x·(P − C)/P,  ỹ = y·(P − C)/P   (the same direction, a new radius)",
    ]
    curve_panel = {
        "key": f"{uid}-curve",
        "formulas": formulas,
        "title": f"{uid} · {name} — stationed by the circle",
        "equation": "the circle parameter, and the curve it stations",
        "legend": [
            {"label": f"{name} — the stored curve", "colour": "#c9b79a"},
            {"label": "the walk's stations on it", "colour": "#c9761f"},
        ],
        "paths": [{"name": name, "colour": "#c9b79a", "points": points}],
        "stations": marks,
        "bounds": [min(curve_xs), max(curve_xs), min(curve_ys), max(curve_ys)],
        "samples": SAMPLES,
    }

    # the dimensionless form, bounded in (-1, 1): 0 where the circle carries the curve,
    # +1 far outside it, -1 far inside. R/C alone is unbounded and one endpoint squashes
    # the rest of the panel.
    spread = []
    for k in range(SAMPLES + 1):
        t = Fraction(k, SAMPLES)
        q = peval(squared, t)
        spread.append(float((q - mean) / (q + mean)))
    remainder_points = [[round(k / SAMPLES, 6), round(value, 6)]
                        for k, value in enumerate(spread)]
    remainder_panel = {
        "key": f"{uid}-remainder",
        "formulas": [
            f"original      P(t) = x(t)² + y(t)²   (degree {len(squared) - 1})",
            f"the circle    C = ∫₀¹ P dt = {mean.numerator}/{mean.denominator} ≈ {float(mean):.4f}",
            f"taken out     (P(t) − C) / (P(t) + C)",
            f"equivalently  P(t) = C (1 + q) / (1 − q), with q the plotted value",
            "so the curve  cannot change shape: only its distance from the origin moves",
        ],
        "title": f"{uid} · {name} — the circle taken out",
        "equation": f"the circle taken out; 0 means the circle carries the curve",
        "legend": [{"label": "(P − C)/(P + C) — the circle taken out", "colour": "#a8341f"}],
        "paths": [{"name": f"{name} remainder", "colour": "#a8341f",
                   "points": remainder_points}],
        "stations": [],
        "bounds": [0.0, 1.0, min(spread), max(spread)],
        "samples": SAMPLES,
    }
    return [curve_panel, remainder_panel]


def quadratic_panel(stations):
    lines = []
    for sign in (1, -1):
        # x² + 2xy + y² = 1  ->  y = ±1 − x
        lines.append({"name": f"y = {sign:+d} − x", "colour": "#2f6fa8",
                      "points": [[-3.2, sign - (-3.2)], [3.2, sign - 3.2]]})
    branches = []
    for sign in (1, -1):
        branch = []
        for k in range(1, 240):
            x = Fraction(sign * k, 60)          # |x| from 1/60 to 4
            y = 1 / (2 * x)
            if abs(y) <= 3.2:
                branch.append([round(float(x), 6), round(float(y), 6)])
        if branch:
            branches.append({"name": f"2xy = 1, branch {sign:+d}", "colour": "#a8341f",
                             "points": branch})
    walk = [[round(float(X), 6), round(float(Y), 6)] for X, Y in stations]
    return {
        "key": "quadratic",
        "title": "the operator's equation, and the circle taken out",
        "equation": "x² + 2xy + y² = 1   →   take x² + y² out   →   2xy = 1",
        "legend": [
            {"label": "x² + 2xy + y² = 1 — two lines", "colour": "#2f6fa8"},
            {"label": "2xy = 1 — the circle removed", "colour": "#a8341f"},
            {"label": "the walk's stations", "colour": "#c9761f"},
        ],
        "paths": lines + branches,
        "stations": walk,
        "bounds": [-3.2, 3.2, -3.2, 3.2],
        "samples": None,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    registry = json.loads((ROOT / "workbench" / "curve-registry.json").read_text())
    stations = exact_stations(TRIPLE, 12)
    panels = []
    for uid, name in NAMED:
        panels.extend(lace_panel(uid, name, registry, stations))
    panels.append(quadratic_panel(stations))

    document = {"format": "curve-lab.circle-plots/1", "panels": panels}
    for panel in panels:
        print(f'{panel["key"]:10}  {panel["title"][:44]:44}  '
              f'{len(panel["paths"])} paths, {len(panel["stations"])} stations')
    if args.write:
        OUT.write_text(json.dumps(document, indent=1) + "\n")
        print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
