#!/usr/bin/env python3
"""Fitting on a 5ⁿ grid: what a bigger grid buys, and what it costs.

    .venv/bin/python scripts/grid625_demo.py
    .venv/bin/python scripts/grid625_demo.py --grids 125,625,3125,15625 --draw 3125 --write

The operator's question (2026-11-19): "i am seeking numbers way higher than 625
for numerators and denominators. how can we just fit on a 625 grid scale please"
— then "or 3125 etc".

**Why the numbers grew.** A turn divides by its hypotenuse, so the denominator is
multiplied by it every step. With `(3+4i)/5` that is `5, 25, 125, 625, 3125, …`.

**The rule.** A station fits on grid `g` exactly when its reduced denominator
divides `g`. So a grid is a **budget of steps**, not a limit on the curve:

| grid | 5ⁿ | steps of (3+4i)/5 | steps of (7+24i)/25 | stations on the circle |
|---|---|---|---|---|
| 125 | 5³ | 3 | 1 | 28 |
| 625 | 5⁴ | 4 | 2 | 36 |
| 3125 | 5⁵ | 5 | 2 | 44 |
| 15625 | 5⁶ | 6 | 3 | 52 |

Every extra factor of 5 in the grid buys **one more step** and **eight more
stations** — and no coordinate ever exceeds the grid.

**The way to fit for ever.** Choose the circle first and step between its
whole-number points. The circle of radius 3125 carries 44 of them, each a whole
number no larger than 3125; read at unit radius they are `x/3125 + y/3125 i`. The
walk never leaves the grid because it does not turn — it steps between points
that are already on it.
"""

from __future__ import annotations

import argparse
import math
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "workbench" / "grid-625-demo.svg"


def circle_points(radius: int):
    points = []
    r2 = radius * radius
    for x in range(-radius, radius + 1):
        y2 = r2 - x * x
        y = math.isqrt(y2)
        if y * y != y2:
            continue
        points.append((x, y))
        if y:
            points.append((x, -y))
    points.sort(key=lambda p: math.atan2(p[1], p[0]))
    return points


def reduced(point, grid: int):
    """The station at unit radius, in lowest terms, and the denominator it needs."""
    x, y = F(point[0], grid), F(point[1], grid)
    den = x.denominator * y.denominator // math.gcd(x.denominator, y.denominator)
    return x, y, den


def reduction_counts(points, grid: int):
    counts = {}
    for point in points:
        _, _, den = reduced(point, grid)
        counts[den] = counts.get(den, 0) + 1
    return dict(sorted(counts.items()))


def step_budget(hypotenuse: int, grid: int) -> int:
    """How many steps of a turn by this hypotenuse stay on the grid."""
    power, steps = 1, 0
    while power * hypotenuse <= grid:
        power *= hypotenuse
        steps += 1
    return steps


def denominator_chain(hypotenuse: int, grid: int, steps: int = 8):
    rows = [(0, 1, True)]
    den = 1
    for k in range(1, steps + 1):
        den *= hypotenuse
        rows.append((k, den, den <= grid and grid % den == 0))
    return rows


def figure(grids, drawn: int) -> str:
    points = circle_points(drawn)
    width, height = 1000, 880
    title = f"Fig. 5 · Fitting on a 5ⁿ grid · drawn on {drawn}"
    subtitle = (f"a turn multiplies the denominator by its hypotenuse · a circle carries whole-number stations · "
                f"no coordinate above {drawn}")

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
        f'<rect width="{width}" height="{height}" fill="#fffdf7"/>',
        f'<text x="34" y="38" font-family="Georgia,serif" font-size="18" fill="#3b2d1c">{title}</text>',
        f'<text x="34" y="62" font-family="ui-monospace,Menlo,monospace" font-size="11.5" fill="#8c6a21">{subtitle}</text>',
        f'<text x="46" y="112" font-family="Georgia,serif" font-size="14" fill="#3b2d1c">the grid is a budget of steps</text>',
    ]

    headers = ["grid", "5ⁿ", "(3,4,5) steps", "(7,24,25) steps", "stations"]
    columns = [46, 150, 210, 340, 470]
    for text, x in zip(headers, columns):
        parts.append(f'<text x="{x}" y="140" font-family="ui-monospace,Menlo,monospace" font-size="11.5" fill="#8c6a21">{text}</text>')
    for index, grid in enumerate(grids):
        y = 168 + index * 30
        count = len(circle_points(grid))
        power = round(math.log(grid, 5)) if abs(math.log(grid, 5) - round(math.log(grid, 5))) < 1e-9 else ""
        values = [str(grid), f"5^{power}" if power != "" else "—", str(step_budget(5, grid)),
                  str(step_budget(25, grid)), str(count)]
        chosen = grid == drawn
        for text, x in zip(values, columns):
            parts.append(f'<text x="{x}" y="{y}" font-family="ui-monospace,Menlo,monospace" font-size="12.5" '
                         f'fill="{"#a8341f" if chosen else "#3b2d1c"}">{text}</text>')

    note_y = 168 + len(grids) * 30 + 24
    parts.append(f'<text x="46" y="{note_y}" font-family="ui-monospace,Menlo,monospace" font-size="11.5" fill="#3b2d1c">'
                 f'each factor of 5 buys one more step and eight more stations.</text>')

    # the drawn circle
    cx, cy, radius = 720, 450, 270

    def px(point):
        return (cx + point[0] / drawn * radius, cy - point[1] / drawn * radius)

    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="#c9a441" stroke-width="1.4" stroke-dasharray="6 5"/>')
    parts.append(f'<line x1="{cx-radius}" y1="{cy}" x2="{cx+radius}" y2="{cy}" stroke="#efe4c9"/>')
    parts.append(f'<line x1="{cx}" y1="{cy-radius}" x2="{cx}" y2="{cy+radius}" stroke="#efe4c9"/>')
    for point in points:
        X, Y = px(point)
        parts.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="3.1" fill="#c9761f"/>')

    labelled = [(0, drawn), (points[1]), (points[len(points) // 4]), (points[len(points) // 2])]
    for point in labelled:
        X, Y = px(point)
        fx, fy, den = reduced(point, drawn)
        name = f"{point[0]}, {point[1]}" if point[0] else f"0, {point[1]}"
        name += f" = {fx} + {fy}i" if fy > 0 else f" = {fx} − {abs(fy)}i"
        anchor = "start" if point[0] >= 0 else "end"
        dx = 10 if point[0] >= 0 else -10
        parts.append(f'<text x="{X+dx:.1f}" y="{Y-8:.1f}" font-family="ui-monospace,Menlo,monospace" '
                     f'font-size="11" fill="#8c5a1a" text-anchor="{anchor}">{name}</text>')

    parts.append(f'<text x="{cx}" y="{cy+radius+28}" font-family="ui-monospace,Menlo,monospace" font-size="12" '
                 f'fill="#3b2d1c" text-anchor="middle">radius {drawn} · {len(points)} whole-number stations'
                 f' · largest coordinate {max(max(abs(a), abs(b)) for a, b in points)}</text>')

    parts.append(f'<rect x="0" y="{height-120}" width="{width}" height="120" fill="#f7f1e3"/>')
    legend = [
        ("#a8341f", f"a turn divides by its hypotenuse: 5, 25, 125, … so a grid stops the chain after a few steps"),
        ("#c9a441", f"a circle is not a turn: {len(points)} stations, every coordinate a whole number ≤ {drawn}"),
        ("#3b2d1c", f"at unit radius each station reduces: "
                     + ", ".join(f"{d}: {c}" for d, c in reduction_counts(points, drawn).items())
                     + f" stations by denominator"),
    ]
    for index, (colour, text) in enumerate(legend):
        y_ = height - 88 + index * 24
        parts.append(f'<line x1="38" y1="{y_-4}" x2="66" y2="{y_-4}" stroke="{colour}" stroke-width="3.4"/>')
        parts.append(f'<text x="78" y="{y_}" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="#3b2d1c">{text}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grids", default="125,625,3125,15625")
    parser.add_argument("--draw", type=int, default=3125)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    grids = [int(part) for part in args.grids.split(",") if part.strip()]

    print(f"{'grid':>8} {'steps (3,4,5)':>14} {'steps (7,24,25)':>17} {'stations':>9} {'largest':>8}")
    for grid in grids:
        points = circle_points(grid)
        largest = max(max(abs(x), abs(y)) for x, y in points) if points else 0
        print(f"{grid:>8} {step_budget(5, grid):>14} {step_budget(25, grid):>17} {len(points):>9} {largest:>8}")

    print(f"\nstep (3+4i)/5 on grid {args.draw}:")
    for k, den, ok in denominator_chain(5, args.draw, 6):
        print(f"  step {k}: denominator {den:>9}  {'fits' if ok else 'over the grid'}")

    points = circle_points(args.draw)
    assert all(x * x + y * y == args.draw * args.draw for x, y in points)
    print(f"\ncircle radius {args.draw}: {len(points)} stations, every coordinate ≤ {args.draw}")
    print("  reduced denominators, and how many stations need each:")
    for den, count in reduction_counts(points, args.draw).items():
        print(f"    denominator {den:>6}: {count} stations")
    print("  (the turn chain is a different matter: it is always in lowest terms, so its")
    print("   denominator is exactly 5^k and cannot be reduced — see LTMemory.)")

    if args.write:
        OUT.write_text(figure(grids, args.draw) + "\n", encoding="utf-8")
        print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
