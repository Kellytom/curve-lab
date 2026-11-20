#!/usr/bin/env python3
"""The flipped transform on a chosen p-triple: transform, flip, transform, flip.

    .venv/bin/python scripts/flip_demo.py
    .venv/bin/python scripts/flip_demo.py --triple 7,24,25
    .venv/bin/python scripts/flip_demo.py --triple 48,55,73 --steps 24 --write

The rule settled on 2026-11-19:

  * the **transform** of a triple (x, y, z) divides by its hypotenuse — a
    rotation by `atan2(y, x)` that keeps the radius;
  * the **flip** is that transform turned a quarter turn, `(y, −x, z)` — a
    rotation by `−atan2(x, y)`, which also keeps the radius;
  * chained, the pair advances the point by `atan2(y, x) − atan2(x, y)`, which is
    `90° − 2·atan2(x, y)`.

Because the two slopes `y/x` and `x/y` are reciprocals, the two turns add to
exactly 90°, so the point stays on the circle of radius `z` for ever and the
chain never closes.

The pair step is the dial. A triple near 45° gives a very slow carousel:

    (7, 24, 25)      pair 57.48°     6.3 pairs a turn
    (48, 55, 73)     pair  7.78°    46.3 pairs a turn   ← about 8° a pair
    (65, 72, 97)     pair  5.85°    61.5 pairs a turn
    (119, 120, 169)  pair  0.48°   750.8 pairs a turn
"""

from __future__ import annotations

import argparse
import math
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "workbench" / "flip-transform.svg"


def multiply(z, w):
    (a, b), (c, d) = z, w
    return (a * c - b * d, a * d + b * c)


def text_of(value: F) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def point_text(point) -> str:
    x, y = point
    if x.denominator == 1 and y.denominator == 1:
        return f"({x}, {y})"
    return f"({text_of(x)}, {text_of(y)})"


def chain(triple, steps: int):
    x, y, z = triple
    transform = (F(x, z), F(y, z))
    flip = (F(y, z), F(-x, z))
    points = [(F(z), F(0))]
    for k in range(steps):
        points.append(multiply(points[-1], transform if k % 2 == 0 else flip))
    return points


def turns(triple):
    x, y, z = triple
    alpha = math.degrees(math.atan2(y, x))
    beta = math.degrees(math.atan2(x, y))
    return alpha, beta, alpha - beta


def figure(triple, points) -> str:
    x, y, z = triple
    alpha, beta, pair = turns(triple)
    width, height = 940, 800
    cx, cy = 470, 380
    scale = 270 / z  # 73 units → 270 px
    def px(p, q):
        return (cx + float(p) * scale, cy - float(q) * scale)

    title = (f"Fig. 2 · The flipped transform, doubled slowly · triple ({x}, {y}, {z}) · "
             f"{pair:.2f}° a pair")
    subtitle = (f"transform +{alpha:.4f}° · flip −{beta:.4f}° · one pair advances {pair:.4f}°, "
                f"{360/pair:.1f} pairs a turn · every station on radius {z}")

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
        f'<rect width="{width}" height="{height}" fill="#fffdf7"/>',
        f'<text x="34" y="38" font-family="Georgia,serif" font-size="18" fill="#3b2d1c">{title}</text>',
        f'<text x="34" y="62" font-family="ui-monospace,Menlo,monospace" font-size="11" fill="#8c6a21">{subtitle}</text>',
    ]

    for v in range(-80, 81, 10):
        xa, ya = px(v, -80)
        xb, yb = px(v, 80)
        parts.append(f'<line x1="{xa:.1f}" y1="{ya:.1f}" x2="{xb:.1f}" y2="{yb:.1f}" stroke="#f3ecdd"/>')
        xa, ya = px(-80, v)
        xb, yb = px(80, v)
        parts.append(f'<line x1="{xa:.1f}" y1="{ya:.1f}" x2="{xb:.1f}" y2="{yb:.1f}" stroke="#f3ecdd"/>')
    parts.append(f'<line x1="{px(-80,0)[0]:.1f}" y1="{cy}" x2="{px(80,0)[0]:.1f}" y2="{cy}" stroke="#b9a98a" stroke-width="1.3"/>')
    parts.append(f'<line x1="{cx}" y1="{px(0,-80)[1]:.1f}" x2="{cx}" y2="{px(0,80)[1]:.1f}" stroke="#b9a98a" stroke-width="1.3"/>')
    parts.append(f'<text x="{px(80,0)[0]:.1f}" y="{cy+18}" font-family="ui-monospace,Menlo,monospace" font-size="11" fill="#9b8a6b" text-anchor="end">x</text>')
    parts.append(f'<text x="{cx+8}" y="{px(0,80)[1]-4:.1f}" font-family="ui-monospace,Menlo,monospace" font-size="11" fill="#9b8a6b">y</text>')

    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{z*scale:.1f}" fill="none" stroke="#c9a441" stroke-width="1.3" stroke-dasharray="6 5"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="2.6" fill="#3b2d1c"/>')
    parts.append(f'<text x="{cx-9}" y="{cy+15}" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="#3b2d1c" text-anchor="end">O</text>')

    # radii to the first three stations, then the steps themselves
    for point in points[:3]:
        X, Y = px(*point)
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{X:.1f}" y2="{Y:.1f}" stroke="#ded0ae" stroke-width="1"/>')
    for index in range(1, min(4, len(points))):
        (x0, y0), (x1, y1) = points[index - 1], points[index]
        colour = "#a8341f" if index % 2 == 1 else "#2f6fa8"
        parts.append(f'<line x1="{px(x0,y0)[0]:.1f}" y1="{px(x0,y0)[1]:.1f}" x2="{px(x1,y1)[0]:.1f}" y2="{px(x1,y1)[1]:.1f}" stroke="{colour}" stroke-width="2.2"/>')

    # every station of the chain, so the slow drift is visible as a dotted ring
    for index, point in enumerate(points):
        X, Y = px(*point)
        if index < 4:
            colour = "#a8341f" if index % 2 == 0 else "#2f6fa8"
            parts.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="4.6" fill="{colour}" stroke="#fffdf7" stroke-width="1.2"/>')
            dy = 18 if index == 0 else -10
            parts.append(f'<text x="{X:.1f}" y="{Y+dy:.1f}" font-family="ui-monospace,Menlo,monospace" '
                         f'font-size="11" fill="{colour}" text-anchor="middle">P{index}</text>')
        else:
            parts.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="2.4" fill="#8c6a21" opacity="0.75"/>')

    # coordinates inside the figure but off the drawing, so nothing collides
    panel = [
        "P0 " + point_text(points[0]),
        "P1 " + point_text(points[1]),
        "P2 " + point_text(points[2]),
        "P3 " + point_text(points[3]),
    ]
    for index, line in enumerate(panel):
        parts.append(f'<text x="60" y="{height-330+index*19}" font-family="ui-monospace,Menlo,monospace" '
                     f'font-size="11.5" fill="#5a4a32">{line}</text>')

    # one pair step, drawn as an arc between P0 and P2
    start = math.degrees(math.atan2(float(points[0][1]), float(points[0][0])))
    end = math.degrees(math.atan2(float(points[2][1]), float(points[2][0])))
    path = []
    for i in range(33):
        a = math.radians(start + (end - start) * i / 32)
        path.append(f"{cx + 120*math.cos(a):.1f},{cy - 120*math.sin(a):.1f}")
    middle = math.radians((start + end) / 2)
    parts.append(f'<polyline points="{" ".join(path)}" fill="none" stroke="#4b7f3a" stroke-width="1.8"/>')
    parts.append(f'<text x="{cx + 250*math.cos(middle):.1f}" y="{cy - 215*math.sin(middle):.1f}" '
                 f'font-family="ui-monospace,Menlo,monospace" font-size="12.5" fill="#4b7f3a" text-anchor="middle">'
                 f'one pair = {pair:.2f}°</text>')

    parts.append(f'<rect x="0" y="{height-124}" width="{width}" height="124" fill="#f7f1e3"/>')
    legend = [
        ("#a8341f", f"transform ({x},{y},{z}) = ({x}+{y}i)/{z} — turns +{alpha:.4f}°, radius kept"),
        ("#2f6fa8", f"flip ({y},−{x},{z}) = ({y}−{x}i)/{z} — the transform quarter-turned, turns −{beta:.4f}°"),
        ("#4b7f3a", f"one transform and one flip advance the point {pair:.4f}° — {360/pair:.1f} pairs a turn"),
        ("#c9a441", f"radius {z} — the chain never leaves it and never closes"),
    ]
    for index, (colour, text) in enumerate(legend):
        y_ = height - 94 + index * 24
        parts.append(f'<line x1="38" y1="{y_-4}" x2="66" y2="{y_-4}" stroke="{colour}" stroke-width="3.4"/>')
        parts.append(f'<text x="78" y="{y_}" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="#3b2d1c">{text}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--triple", default="48,55,73", help="x,y,z of a p-triple")
    parser.add_argument("--steps", type=int, default=88)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    triple = tuple(int(part) for part in args.triple.split(","))
    if len(triple) != 3 or triple[0] ** 2 + triple[1] ** 2 != triple[2] ** 2:
        raise SystemExit(f"{args.triple} is not a p-triple")
    x, y, z = triple

    points = chain(triple, args.steps)
    alpha, beta, pair = turns(triple)
    print(f"triple ({x},{y},{z})  transform +{alpha:.4f}°  flip −{beta:.4f}°  pair {pair:.4f}°  "
          f"{360/pair:.2f} pairs a turn")
    print("\nstation  exact fraction (no decimals — a decimal is only a sample)")
    for index, (p, q) in enumerate(points[:8]):
        assert p * p + q * q == z * z, "a station left the circle"
        print(f"P{index:<6} {point_text((p, q))}")
    print(f"\nall {len(points)} stations verified on radius {z}")

    if args.write:
        OUT.write_text(figure(triple, points) + "\n", encoding="utf-8")
        print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
