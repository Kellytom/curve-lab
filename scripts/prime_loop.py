#!/usr/bin/env python3
"""The prime-mover loop: i from the end of the negatives to the end of the positives.

    .venv/bin/python scripts/prime_loop.py
    .venv/bin/python scripts/prime_loop.py --steps 6 --write

The operator's definition (2026-11-19):

    set up a loop i, i = the end of the negatives (around −360 degrees) as a
    rational fraction. go to i = the end of the positives as a rational fraction.
    that is the loop, and the curves come out of that loop.

So the loop is the **parameter**, and it is written as a fraction of a turn:

    i = −a/b  …  0  …  +a/b        (default −1/1 … 0 … +1/1, i.e. −360° … +360°)

At each station the pen is a rational point. The step is the p-triple
`(x+iy)/z`, a unit complex number, so the radius never changes and the station is
exact: `(3+4i)/5` gives `3/5 + 4/5i`, `−7/25 + 24/25i`, `−117/125 + 44/125i`, …

The negative half is the mirror of the positive half — the same denominators, the
sign of the imaginary part flipped. The two **ends** (`i = −a/b` and `i = +a/b`)
are joined by a chord: that chord is the loop's seam, and it is the only straight
line in the figure that is not a step.

**The curves come out of the loop.** A branch at a station is the exact
perpendicular of the incoming step, `(−y, x)`, scaled by a rational — so the
branch endpoint is a rational point as well, and a branch can be cut off and used
as a stem. This is the whole method: one loop, and stems leaving it at stations.
"""

from __future__ import annotations

import argparse
import math
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "workbench" / "prime-loop.svg"


def multiply(a, b):
    (p, q), (r, s) = a, b
    return (p * r - q * s, p * s + q * r)


def power(step, n: int):
    z = (F(1), F(0))
    for _ in range(abs(n)):
        z = multiply(z, step)
    return z if n >= 0 else (z[0], -z[1])


def num(value: F) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def point_text(point) -> str:
    x, y = point
    if y == 0:
        return num(x)
    return f"{num(x)}{' + ' if y > 0 else ' − '}{num(abs(y))}i"


def perpendicular(point, length: F):
    """The exact branch direction: the radius turned a quarter turn, scaled."""
    x, y = point
    return (-y * length, x * length)


def loop(triple, steps: int):
    x, y, z = triple
    step = (F(x, z), F(y, z))
    return [power(step, k) for k in range(-steps, steps + 1)]


def figure(triple, steps: int, end_fraction: str) -> str:
    x, y, z = triple
    points = loop(triple, steps)
    width, height = 940, 840
    cx, cy, radius = 470, 400, 250

    def px(point):
        return (cx + float(point[0]) * radius, cy - float(point[1]) * radius)

    start, finish = points[0], points[-1]
    title = (f"Fig. 4 · The prime-mover loop · i = −{end_fraction} … +{end_fraction} of a turn · "
             f"step ({x}+{y}i)/{z}")
    subtitle = (f"{len(points)} stations, each an integer or a rational fraction · "
                f"the two ends are joined by the seam · branches leave the loop")

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
        f'<rect width="{width}" height="{height}" fill="#fffdf7"/>',
        f'<text x="34" y="38" font-family="Georgia,serif" font-size="18" fill="#3b2d1c">{title}</text>',
        f'<text x="34" y="62" font-family="ui-monospace,Menlo,monospace" font-size="11.5" fill="#8c6a21">{subtitle}</text>',
        f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="#efe4c9" stroke-width="1"/>',
        f'<line x1="{cx-radius}" y1="{cy}" x2="{cx+radius}" y2="{cy}" stroke="#efe4c9"/>',
        f'<line x1="{cx}" y1="{cy-radius}" x2="{cx}" y2="{cy+radius}" stroke="#efe4c9"/>',
    ]

    # the walk, negative half then positive half, then the seam that closes it
    path = " ".join(f"{px(p)[0]:.1f},{px(p)[1]:.1f}" for p in points)
    parts.append(f'<polyline points="{path}" fill="none" stroke="#6f4a2a" stroke-width="2"/>')
    parts.append(f'<line x1="{px(points[0])[0]:.1f}" y1="{px(points[0])[1]:.1f}" '
                 f'x2="{px(points[-1])[0]:.1f}" y2="{px(points[-1])[1]:.1f}" '
                 f'stroke="#a8341f" stroke-width="2" stroke-dasharray="7 5"/>')

    # branches: the exact perpendicular at every station, scaled by 1/6
    for index, point in enumerate(points):
        if index in (0, len(points) - 1):
            continue
        bx, by = perpendicular(point, F(1, 6) if index % 2 else F(-1, 6))
        (x0, y0), (x1, y1) = px(point), px((point[0] + bx, point[1] + by))
        parts.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" '
                     f'stroke="#4b7f3a" stroke-width="1.4"/>')
        parts.append(f'<circle cx="{x1:.1f}" cy="{y1:.1f}" r="2.4" fill="#4b7f3a"/>')

    for index, point in enumerate(points):
        X, Y = px(point)
        ends = index in (0, len(points) - 1)
        centre = index == (len(points) - 1) // 2
        colour = "#a8341f" if ends else ("#2f6fa8" if centre else "#c9761f")
        parts.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{4.6 if ends else 3.0}" fill="{colour}"/>')

    # labels for the three stations that define the loop: whole numbers written whole
    middle = (len(points) - 1) // 2
    def fraction_text(text: str) -> str:
        top, _, bottom = text.partition("/")
        return top if (not bottom or bottom == "1") else f"{top}/{bottom}"
    end_text = fraction_text(end_fraction)
    labels = {0: f"i = −{end_text}", middle: "i = 0", len(points) - 1: f"i = +{end_text}"}
    for index, label in labels.items():
        X, Y = px(points[index])
        parts.append(f'<text x="{X:.1f}" y="{Y+20:.1f}" font-family="ui-monospace,Menlo,monospace" '
                     f'font-size="11.5" fill="#3b2d1c" text-anchor="middle">{label}</text>')

    # a few exact stations, written as fractions
    for index in (1, 2, middle + 1, len(points) - 2):
        X, Y = px(points[index])
        parts.append(f'<text x="{X+8:.1f}" y="{Y-8:.1f}" font-family="ui-monospace,Menlo,monospace" '
                     f'font-size="10.5" fill="#8c5a1a">{point_text(points[index])}</text>')

    parts.append(f'<rect x="0" y="{height-124}" width="{width}" height="124" fill="#f7f1e3"/>')
    legend = [
        ("#6f4a2a", f"the loop: i runs −{end_fraction} → +{end_fraction} of a turn, one station a step"),
        ("#a8341f", f"the seam: the two ends joined, {point_text(points[0])} to {point_text(points[-1])}"),
        ("#4b7f3a", "branches: the exact perpendicular at a station, scaled by a fraction of the radius"),
        ("#2f6fa8", "i = 0 — the middle of the loop, where the positives and negatives cross over"),
    ]
    for index, (colour, text) in enumerate(legend):
        y_ = height - 96 + index * 23
        parts.append(f'<line x1="38" y1="{y_-4}" x2="66" y2="{y_-4}" stroke="{colour}" stroke-width="3.4"/>')
        parts.append(f'<text x="78" y="{y_}" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="#3b2d1c">{text}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--triple", default="3,4,5")
    parser.add_argument("--steps", type=int, default=6, help="stations either side of i = 0")
    parser.add_argument("--end", default="1", help="the end of the loop: an integer or a fraction of a turn")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    triple = tuple(int(part) for part in args.triple.split(","))
    if triple[0] ** 2 + triple[1] ** 2 != triple[2] ** 2:
        raise SystemExit(f"{args.triple} is not a p-triple")
    points = loop(triple, args.steps)

    print(f"loop: i = −{args.end} … +{args.end} of a turn · step ({triple[0]}+{triple[1]}i)/{triple[2]}")
    print(f"{len(points)} stations, each an exact fraction, all on radius 1\n")
    for index, point in enumerate(points):
        i = F(index - args.steps, args.steps)
        assert point[0] ** 2 + point[1] ** 2 == 1, "a station left the circle"
        bx, by = perpendicular(point, F(1, 6))
        print(f"i = {num(i):>5}   z = {point_text(point):28}  branch end {point_text((point[0]+bx, point[1]+by))}")
    print(f"\nseam: {point_text(points[0])} → {point_text(points[-1])}")

    if args.write:
        OUT.write_text(figure(triple, args.steps, args.end) + "\n", encoding="utf-8")
        print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
