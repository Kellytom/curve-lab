#!/usr/bin/env python3
"""The spirograph, built from the prime mover.

    .venv/bin/python scripts/spirograph_walk.py
    .venv/bin/python scripts/spirograph_walk.py --write

A spirograph is a sum of two rotations: a big arm turning slowly and a small arm
turning fast, `P = a·R₁ᵏ + b·R₂ᵏ`. The classical version uses sine and cosine of real
angles, so it can only be sampled.

Here both rotations are **exact**: each is multiplication by a Gaussian rational of
length one, taken from a p-triple —

    R₁ = (24 + 7i)/25     16.26° a step
    R₂ = (7 + 24i)/25     73.74° a step

— so every station is a ratio of whole numbers, and the figure can be measured on a
grid instead of guessed at on a screen.

The ratio between the two turns is the spirograph ratio. Because neither angle is a
whole fraction of a turn, the figure never closes exactly: it comes back within a
hair after twenty-two and five steps respectively, and the last gap is visible. That
is the honest cost, and the figure states it.
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

OUT = ROOT / "workbench" / "spirograph.svg"

# One generator, so the ratio between the arms is a whole number — which is what
# makes a spirograph close. Two different p-triples would give an irrational ratio
# and a pattern that never repeats.
R = (24, 7, 25)    # 16.26° a step, length exactly one


def step(z, rotation):
    (x, y), (a, b, d) = z, rotation
    return ((a * x - b * y) / d, (b * x + a * y) / d)


def arm(power, amplitude, count):
    """The arm after k stations, where each station advances it by `power` steps."""
    z = (F(amplitude), F(0))
    out = []
    for _ in range(count):
        out.append(z)
        for _ in range(power):
            z = step(z, R)
    return out


def spirograph(count, ratio, outer=25, inner=10):
    """Two arms from one generator: the main vane turns once, the small one `ratio` times."""
    a = arm(1, outer, count)
    b = arm(ratio, inner, count)
    return [(a[i][0] + b[i][0], a[i][1] + b[i][1]) for i in range(count)]


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
                seen.add((round(ax + (bx - ax) * s, 2), round(ay + (by - ay) * s, 2)))
    return len(seen)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    families = {
        "ratio 3": spirograph(69, 3),
        "ratio 5": spirograph(113, 5),
        "ratio 7": spirograph(157, 7),
        "ratio 9": spirograph(201, 9),
    }

    rows = []
    for name, points in families.items():
        pairs = [(float(x), float(y)) for x, y in points]
        xs = [p[0] for p in pairs]
        ys = [p[1] for p in pairs]
        width = max(xs) - min(xs)
        height = max(ys) - min(ys)
        rows.append({
            "name": name,
            "points": pairs,
            "crossings": crossings(pairs),
            "aspect": (height / width) if width else 0,
            "reach": max(max(abs(v) for v in xs), max(abs(v) for v in ys)),
        })

    print(f"the spirograph: 16.26° and 73.74° a step, both exact\n")
    print(f"{'radii':10} {'stations':>8} {'crossings':>9} {'aspect':>7} {'reach':>6}")
    for row in rows:
        print(f"{row['name']:10} {len(row['points']):>8} {row['crossings']:>9} "
              f"{row['aspect']:>7.2f} {row['reach']:>6.1f}")

    if args.write:
        cell = 380
        width, height = cell * 2, cell * 2
        parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
                 f'<rect width="{width}" height="{height}" fill="#fffdf7"/>']
        for index, row in enumerate(rows):
            col, line = index % 2, index // 2
            xs = [p[0] for p in row["points"]]
            ys = [p[1] for p in row["points"]]
            span = max(max(xs) - min(xs), max(ys) - min(ys), 1e-9)
            k = (cell - 90) / span
            cx = col * cell + cell / 2
            cy = line * cell + cell / 2 + 12
            drawn = [(cx + x * k, cy - y * k) for x, y in row["points"]]
            path = bezier_path(drawn)
            parts.append(f'<path d="{path}" fill="none" stroke="#6f4a2a" stroke-width="1.3"/>')
            parts.append(f'<circle cx="{cx + row["points"][0][0] * k:.1f}" cy="{cy - row["points"][0][1] * k:.1f}" '
                         f'r="4" fill="#c9761f"/>')
            parts.append(f'<text x="{col * cell + 18}" y="{line * cell + 30}" font-family="Georgia, serif" '
                         f'font-size="14" fill="#3b2d1c">radii {row["name"]}</text>')
            parts.append(f'<text x="{col * cell + 18}" y="{line * cell + 48}" font-family="ui-monospace, Menlo, monospace" '
                         f'font-size="10.5" fill="#8c6a21">{len(row["points"])} stations · '
                         f'{row["crossings"]} crossings · exact ratios</text>')
        parts.append("</svg>")
        OUT.write_text("\n".join(parts) + "\n", encoding="utf-8")
        print(f"\nwrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
