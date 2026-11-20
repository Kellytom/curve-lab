#!/usr/bin/env python3
"""Walking one circle's whole-number points: the grid stays the grid.

    .venv/bin/python scripts/circle_grid_walk.py
    .venv/bin/python scripts/circle_grid_walk.py --radius 1105 --step 7 --write

The mistake the operator caught (2026-11-19): chaining the *turn* — multiplying
by (48+55i)/73 and then by (55−48i)/73 — keeps the angle exact but divides every
position by 73, so stations land on grid 1/73^k. That is why the denominator
grew. The direction was right; the **sequence of events** was wrong.

Staying on the grid means choosing the circle first. A circle of radius r has a
whole number of integer points on it, and every one is an exact station:

    r =  625 (5⁴)        36 points      gaps  4.35° – 16.26°   max chord inset 6.28
    r = 1105 (5·13·17)  108 points      gaps  0.43° –  8.37°   max chord inset 2.95
    r = 5525            180 points      gaps  0.43° –  5.45°   max chord inset 6.25

The count does not follow the radius: it follows the prime factors that are 1
mod 4. 325 has more points than 625 for that reason.

Walking the points in order, or stepping by k points at a time (k coprime to the
count), keeps every station a whole-number point on the same circle for ever.
Between two stations the pen cuts a chord, so the drawing is **slightly inset**
and comes back out to the circle at each station — exactly the behaviour the
operator described. The inset is the sagitta, measured here rather than guessed.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "workbench" / "circle-grid-walk.svg"


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


def walk(points, step: int):
    count = len(points)
    order = []
    index = 0
    for _ in range(count):
        order.append(points[index])
        index = (index + step) % count
    return order


def adjacent(radius: int):
    """The circle's own points in order: spacing in degrees and the chord inset."""
    points = circle_points(radius)
    gaps = []
    for i in range(len(points)):
        x0, y0 = points[i]
        x1, y1 = points[(i + 1) % len(points)]
        angle = (math.degrees(math.atan2(y1, x1) - math.atan2(y0, x0))) % 360
        gaps.append(angle)
    return sorted(g for g in gaps if g > 0), inset(radius, points)


def inset(radius: int, points) -> float:
    """The deepest a chord between two neighbouring stations goes inside."""
    worst = 0.0
    for i in range(len(points)):
        x0, y0 = points[i]
        x1, y1 = points[(i + 1) % len(points)]
        chord = math.hypot(x1 - x0, y1 - y0)
        worst = max(worst, radius - math.sqrt(max(0.0, radius * radius - chord * chord / 4)))
    return worst


def report(radius: int, step: int):
    points = circle_points(radius)
    order = walk(points, step)
    assert all(x * x + y * y == radius * radius for x, y in order), "a station left the circle"
    adjacent_gaps, adjacent_inset = adjacent(radius)
    walk_gaps = sorted(
        (math.degrees(math.atan2(order[(i + 1) % len(order)][1], order[(i + 1) % len(order)][0])
         - math.atan2(order[i][1], order[i][0]))) % 360
        for i in range(len(order))
    )
    walk_gaps = [g for g in walk_gaps if g > 0]
    return order, adjacent_gaps, adjacent_inset, walk_gaps


def figure(radius: int, step: int) -> str:
    order, gaps, dip, walk_gaps = report(radius, step)
    width, height = 940, 820
    cx, cy = 470, 390
    scale = 268 / radius

    def px(p):
        return (cx + p[0] * scale, cy - p[1] * scale)

    title = (f"Fig. 3 · Walking one circle's whole-number points · radius {radius} · "
             f"{len(order)} stations · step {step}")
    subtitle = (f"every station satisfies x² + y² = {radius}² exactly · gap {gaps[0]:.2f}°–{gaps[-1]:.2f}° · "
                f"deepest chord inset {dip:.2f} · no denominator anywhere")

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
        f'<rect width="{width}" height="{height}" fill="#fffdf7"/>',
        f'<text x="34" y="38" font-family="Georgia,serif" font-size="18" fill="#3b2d1c">{title}</text>',
        f'<text x="34" y="62" font-family="ui-monospace,Menlo,monospace" font-size="11.5" fill="#8c6a21">{subtitle}</text>',
        f'<circle cx="{cx}" cy="{cy}" r="{radius*scale:.2f}" fill="none" stroke="#c9a441" stroke-width="1.4" stroke-dasharray="6 5"/>',
        f'<line x1="{px((-radius,0))[0]:.1f}" y1="{cy}" x2="{px((radius,0))[0]:.1f}" y2="{cy}" stroke="#e3d7bd"/>',
        f'<line x1="{cx}" y1="{px((0,-radius))[1]:.1f}" x2="{cx}" y2="{px((0,radius))[1]:.1f}" stroke="#e3d7bd"/>',
    ]

    path = " ".join(f"{px(p)[0]:.1f},{px(p)[1]:.1f}" for p in order + [order[0]])
    parts.append(f'<polyline points="{path}" fill="none" stroke="#6f4a2a" stroke-width="1.5" stroke-linejoin="round"/>')

    for index, point in enumerate(order):
        X, Y = px(point)
        parts.append(f'<circle cx="{X:.2f}" cy="{Y:.2f}" r="3" fill="#c9761f"/>')
        if index % max(1, len(order) // 12) == 0:
            parts.append(f'<text x="{X:.1f}" y="{Y-10:.1f}" font-family="ui-monospace,Menlo,monospace" '
                         f'font-size="10.5" fill="#8c5a1a" text-anchor="middle">{point[0]}, {point[1]}</text>')

    # one chord drawn heavy, with its inset marked, so the "slightly inset" is visible
    x0, y0 = order[0]
    x1, y1 = order[1]
    (a0, b0), (a1, b1) = px((x0, y0)), px((x1, y1))
    parts.append(f'<line x1="{a0:.1f}" y1="{b0:.1f}" x2="{a1:.1f}" y2="{b1:.1f}" stroke="#a8341f" stroke-width="2.6"/>')
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    length = math.hypot(mx, my) or 1
    tipx, tipy = mx * radius / length, my * radius / length
    parts.append(f'<line x1="{px((mx,my))[0]:.1f}" y1="{px((mx,my))[1]:.1f}" '
                 f'x2="{px((tipx,tipy))[0]:.1f}" y2="{px((tipx,tipy))[1]:.1f}" '
                 f'stroke="#a8341f" stroke-width="1.2" stroke-dasharray="3 3"/>')
    parts.append(f'<text x="{px((tipx,tipy))[0]+8:.1f}" y="{px((tipx,tipy))[1]:.1f}" '
                 f'font-family="ui-monospace,Menlo,monospace" font-size="11" fill="#a8341f">inset</text>')

    parts.append(f'<rect x="0" y="{height-104}" width="{width}" height="104" fill="#f7f1e3"/>')
    legend = [
        ("#c9761f", f"{len(order)} whole-number stations, each with x² + y² = {radius}²"),
        ("#6f4a2a", f"walk step {step}: from station i to station i+{step}, wrapping at {len(order)}"),
        ("#a8341f", f"the chord dips {dip:.2f} inside the circle, then comes back out at the next station"),
    ]
    for index, (colour, text) in enumerate(legend):
        y_ = height - 72 + index * 22
        parts.append(f'<line x1="38" y1="{y_-4}" x2="66" y2="{y_-4}" stroke="{colour}" stroke-width="3.4"/>')
        parts.append(f'<text x="78" y="{y_}" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="#3b2d1c">{text}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--radius", type=int, default=625)
    parser.add_argument("--step", type=int, default=1)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    for radius in (625, 1105, 1625, 5525):
        points = circle_points(radius)
        print(f"radius {radius:5} → {len(points):3} whole-number points")

    order, gaps, dip, walk_gaps = report(args.radius, args.step)
    print(f"\nradius {args.radius}: {len(order)} stations, all exact on the circle")
    print(f"neighbour spacing {gaps[0]:.3f}° to {gaps[-1]:.3f}° · deepest neighbour inset {dip:.3f}")
    print(f"walk step {args.step} turns {walk_gaps[0]:.2f}° to {walk_gaps[-1]:.2f}° a station")
    print(f"first stations: {order[:6]} … last {order[-1]}")

    if args.write:
        OUT.write_text(figure(args.radius, args.step) + "\n", encoding="utf-8")
        print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
