#!/usr/bin/env python3
"""Curves from the prime-mover walk.

    .venv/bin/python scripts/walk_curves.py
    .venv/bin/python scripts/walk_curves.py --write

The walk is the orbit of the triangle's apex under the rotation
`(527 + 336i)/625`: twelve points on the circle of radius 25, exactly. This script
feeds those points through polynomials and scores what comes out.

Everything is a ratio of whole numbers. The drawing converts to a float to place a
point; the data never does.
"""

from __future__ import annotations

import argparse
import math
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def bezier_path(points):
    """A cubic Bézier chain through the points (Catmull-Rom, tension 1/2).

    The stations are the data; this is how the line between them is drawn, and the
    figure says the line is approximate.
    """
    if len(points) < 2:
        return ""
    pts = [points[0]] + list(points) + [points[-1]]
    parts = [f"M {pts[1][0]:.2f},{pts[1][1]:.2f}"]
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        parts.append(f"C {c1[0]:.2f},{c1[1]:.2f} {c2[0]:.2f},{c2[1]:.2f} {p2[0]:.2f},{p2[1]:.2f}")
    return " ".join(parts)

OUT = ROOT / "workbench" / "walk-curves.svg"

# The finer walk: one triangle's own turn, 16.26°, so a full circuit needs about
# twenty-two stations instead of twelve. Same construction, more stations.
APEX = (25, 0)
ROTATION = (24, 7, 25)


def walk(count=22):
    x, y, d = APEX[0], APEX[1], 1
    out = []
    for k in range(count):
        out.append((F(x, d), F(y, d)))
        nx, ny, nd = ROTATION[0] * x - ROTATION[1] * y, ROTATION[1] * x + ROTATION[0] * y, ROTATION[2] * d
        g = math.gcd(math.gcd(abs(nx), abs(ny)), nd) or 1
        x, y, d = nx // g, ny // g, nd // g
    return out


def curves():
    """Each preset is a polynomial map of (X, Y); the walk is the input."""
    return {
        "circle": lambda X, Y: (X, Y),
        "the S": lambda X, Y: (X, Y - Y**3),
        "the loop": lambda X, Y: (X - X**3, Y),
        "the leaf": lambda X, Y: (X * Y, Y),
        "the crest": lambda X, Y: (X, X * Y),
        "double fold": lambda X, Y: (X - X**3, Y - Y**3),
        "pinch": lambda X, Y: (X * Y, X * Y * Y),
        "cross": lambda X, Y: (X * Y, X),
        "wave": lambda X, Y: (X, Y * (1 - X**2)),
    }


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
                seen.add((round(ax + (bx - ax) * s, 3), round(ay + (by - ay) * s, 3)))
    return len(seen)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    points = walk(22)
    radius = 25
    print(f"the walk: {len(points)} points, each on radius {radius}, exact")
    print(f"  first  {points[0][0]} , {points[0][1]}")
    print(f"  last   {points[-1][0]} , {points[-1][1]}")
    print()

    rows = []
    for name, map_points in curves().items():
        moved = [map_points(X / radius, Y / radius) for X, Y in points]
        pairs = [(float(u), float(v)) for u, v in moved]
        xs = [p[0] for p in pairs]
        ys = [p[1] for p in pairs]
        width = max(xs) - min(xs)
        height = max(ys) - min(ys)
        rows.append({
            "name": name,
            "points": pairs,
            "crossings": crossings(pairs),
            "aspect": (height / width) if width else 0,
            "reach": max(max(abs(x) for x in xs), max(abs(y) for y in ys)),
        })

    rows.sort(key=lambda row: (-row["crossings"], abs(row["aspect"] - 1)))
    print(f"{'curve':14} {'crossings':>9} {'aspect':>7} {'reach':>6}")
    for row in rows:
        print(f"{row['name']:14} {row['crossings']:>9} {row['aspect']:>7.2f} {row['reach']:>6.2f}")

    if args.write:
        cell = 300
        cols = 3
        lines = math.ceil(len(rows) / cols)
        width, height = cols * cell, lines * cell
        parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
                 f'<rect width="{width}" height="{height}" fill="#fffdf7"/>']
        for index, row in enumerate(rows):
            col, line = index % cols, index // cols
            xs = [p[0] for p in row["points"]]
            ys = [p[1] for p in row["points"]]
            span = max(max(xs) - min(xs), max(ys) - min(ys), 1e-9)
            k = (cell - 70) / span
            ox = col * cell + 35 - min(xs) * k + (cell - 70 - (max(xs) - min(xs)) * k) / 2
            oy = line * cell + 45 + (cell - 80 - (max(ys) - min(ys)) * k) / 2 + max(ys) * k
            drawn = [(x * k + ox, oy - y * k) for x, y in row["points"]]
            path = bezier_path(drawn)
            parts.append(f'<path d="{path}" fill="none" stroke="#6f4a2a" stroke-width="1.6"/>')
            for x, y in row["points"]:
                parts.append(f'<circle cx="{x * k + ox:.1f}" cy="{oy - y * k:.1f}" r="2.6" fill="#c9761f"/>')
            parts.append(f'<text x="{col * cell + 14}" y="{line * cell + 26}" font-family="Georgia, serif" '
                         f'font-size="13" fill="#3b2d1c">{row["name"]}</text>')
            parts.append(f'<text x="{col * cell + 14}" y="{line * cell + 42}" font-family="ui-monospace, Menlo, monospace" '
                         f'font-size="10" fill="#8c6a21">crossings {row["crossings"]} · aspect {row["aspect"]:.2f}</text>')
        parts.append("</svg>")
        OUT.write_text("\n".join(parts) + "\n", encoding="utf-8")
        print(f"\nwrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
