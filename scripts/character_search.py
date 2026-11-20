#!/usr/bin/env python3
"""Curves with character: a search over the walk, scored on the things the collection
already values.

    .venv/bin/python scripts/character_search.py
    .venv/bin/python scripts/character_search.py --write

A curve earns "character" here the way the stored collection does:

  * **loops** — the tangential speed reverses while the turn keeps one sign;
  * **flats** — inflections, where the turn changes sign;
  * **crossings** — distinct self-intersections, counted as pairs;
  * **symmetry** — how close the figure is to its own mirror, and to its own rotation by
    120° or 90°;
  * **proportion** — the box it fits in, and how much of the plane it uses.

Everything is exact: the stations are ratios of whole numbers, and the polynomial maps
have whole-number coefficients. The *measurements* are taken on the drawn polyline,
because a loop is a property of the shape; the stations themselves stay rational.
"""

from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "workbench" / "character-curves.json"
SVG = ROOT / "workbench" / "character-curves.svg"

# triples, as (x, y, z): the walk steps by the double angle, (x²−y², 2xy, z²)
TRIPLES = [
    (3, 4, 5), (5, 12, 13), (7, 24, 25), (8, 15, 17), (20, 21, 29),
    (48, 55, 73), (56, 783, 785),   # thin: 44 and 90 stations, smooth curves
]

# maps of (X, Y), whole-number coefficients; X and Y are the walk's coordinates
MAPS = {
    "the circle": lambda X, Y: (X, Y),
    "the S": lambda X, Y: (X, Y - Y**3),
    "the loop": lambda X, Y: (X - X**3, Y),
    "double fold": lambda X, Y: (X - X**3, Y - Y**3),
    "the trefoil": lambda X, Y: (X**3 - 3 * X * Y**2, 3 * X**2 * Y - Y**3),
    "the rose": lambda X, Y: (X * (X**2 - 3 * Y**2), Y * (3 * X**2 - Y**2)),
    "the knot": lambda X, Y: (X + X * Y**2, Y + X**2 * Y),
    "the horn": lambda X, Y: (X + X * Y, Y - X**2),
    "the cross": lambda X, Y: (X * Y, X),
    "the leaf": lambda X, Y: (X * Y, Y),
    "the crest": lambda X, Y: (X, X * Y),
    "the wave": lambda X, Y: (X, Y + X**2 * Y),
    "the pinch": lambda X, Y: (X - X**3, Y + Y * X**2),
    "cubic fold": lambda X, Y: (X - X**3 + X * Y**2, Y - Y**3 + X**2 * Y),
    "the four-fold": lambda X, Y: (X * (1 - Y**2), Y * (1 - X**2)),
    "the spiral": lambda X, Y: (X * (1 + Y), Y - X**2),
    "the saddle": lambda X, Y: (X + X * Y, Y + X * Y),
    "the lens": lambda X, Y: (X - X * Y**2, Y),
    # asymmetric maps: the collection has figures that are not symmetric, and these
    # are where crossings come from
    "the shear": lambda X, Y: (X, Y + X**3),
    "the comb": lambda X, Y: (X + Y**2, Y + X**2),
    "the hook": lambda X, Y: (X + X**2, Y + X**3),
    "the twist": lambda X, Y: (X + X**2 * Y, Y - X * Y**2),
    "the whisk": lambda X, Y: (X + Y**3, Y + X**2),
    "the tail": lambda X, Y: (X + X**2 + Y**2, Y),
    "the gull": lambda X, Y: (X, Y + X - X**3),
    "the arrow": lambda X, Y: (X + Y - Y**3, Y),
}


def lap(triple):
    """The stations of one lap, exact."""
    ax, ay, z = triple
    ax, ay = max(ax, ay), min(ax, ay)
    return max(8, math.ceil(360 / math.degrees(math.atan2(ay, ax))) + 1)


def walk(triple, steps=None):
    """The walk, exact, on **both** circles, interleaved.

    The apex walks radius z at angles φ, φ+t, φ+2t, …; the foot walks the longer
    leg's circle at 0, t, 2t, … — one triangle turn behind. Merged by angle, the two
    sets interleave and **double the stations**, each pair half a turn apart.

    For a thin triple the two radii differ by a quarter of one per cent, so the pair is
    invisible and the drawing is simply twice as fine. For 7-24-25 the difference is
    four per cent, and the pair is better drawn as two curves than one.
    """
    ax, ay, z = triple
    ax, ay = max(ax, ay), min(ax, ay)
    turn = math.degrees(math.atan2(ay, ax))
    if steps is None:
        laps = 2 if turn < 10 else 1
        steps = max(8, math.ceil(laps * 360 / turn) + 1)

    # one unit-circle point, turned by the triangle's own angle each station
    u = (F(1), F(0))
    step = (F(ax, z), F(ay, z))
    apexes, feet = [], []
    for _ in range(steps):
        # both on the unit circle: the apex at radius 1, the foot at ax/z — 0.9988 for
        # the thin triple, 0.96 for 7-24-25
        apexes.append((u[0], u[1]))
        feet.append((F(ax, z) * u[0], F(ax, z) * u[1]))
        u = (u[0] * step[0] - u[1] * step[1], u[0] * step[1] + u[1] * step[0])

    # Merge only when the circles are within one per cent of each other. Beyond that
    # the pen would jump between radii and the curve would wobble; the two circles are
    # then drawn as two curves.
    if ax / z >= 0.99:
        merged = apexes + feet
        merged.sort(key=lambda p: math.atan2(fval(p[1]), fval(p[0])))
        return merged
    return apexes


def fval(value, scale=2**40):
    """A Fraction as a float, safely: the division happens in integers at a fixed
    scale, so a 600-digit denominator cannot overflow the conversion."""
    n, d = value.numerator, value.denominator
    if not d:
        return 0.0
    return (n * scale // d) / scale


def reversals(points):
    count, last = 0, 0
    for i in range(1, len(points) - 1):
        ax, ay = points[i][0] - points[i - 1][0], points[i][1] - points[i - 1][1]
        bx, by = points[i + 1][0] - points[i][0], points[i + 1][1] - points[i][1]
        dot = ax * bx + ay * by
        if abs(dot) < 1e-15:
            continue
        sign = 1 if dot > 0 else -1
        if last and sign != last:
            count += 1
        last = sign
    return count


def inflections(points):
    count, last = 0, 0
    for i in range(1, len(points) - 1):
        ax, ay = points[i][0] - points[i - 1][0], points[i][1] - points[i - 1][1]
        bx, by = points[i + 1][0] - points[i][0], points[i + 1][1] - points[i][1]
        cross = ax * by - ay * bx
        if abs(cross) < 1e-15:
            continue
        sign = 1 if cross > 0 else -1
        if last and sign != last:
            count += 1
        last = sign
    return count


def crossings(points):
    seen = set()
    n = len(points)
    for i in range(n - 1):
        ax, ay = points[i]
        bx, by = points[i + 1]
        for j in range(i + 2, n - 1):
            cx, cy = points[j]
            dx, dy = points[j + 1]
            if i == 0 and j == n - 2:
                continue
            den = (bx - ax) * (dy - cy) - (by - ay) * (dx - cx)
            if abs(den) < 1e-15:
                continue
            s = ((cx - ax) * (dy - cy) - (cy - ay) * (dx - cx)) / den
            w = ((cx - ax) * (by - ay) - (cy - ay) * (bx - ax)) / den
            if 0 < s < 1 and 0 < w < 1:
                seen.add((round(ax + (bx - ax) * s, 2), round(ay + (by - ay) * s, 2)))
    return len(seen)


def mirror_gap(points):
    """Mean distance from each point to the nearest point of the mirrored figure."""
    mirrored = [(x, -y) for x, y in points]
    total = 0.0
    for x, y in points:
        total += min(math.hypot(x - mx, y - my) for mx, my in mirrored)
    return total / len(points)


def rotation_gap(points, turns):
    angle = 2 * math.pi / turns
    total = 0.0
    for x, y in points:
        best = min(
            math.hypot(x - (px * math.cos(angle * k) - py * math.sin(angle * k)),
                       y - (px * math.sin(angle * k) + py * math.cos(angle * k)))
            for px, py in points for k in range(1, turns)
        )
        total += best
    return total / len(points)


def score(row, extent):
    """Character, as a number: loops and flats first, then crossings and symmetry."""
    s = 3.0 * min(row["loops"], 2)
    s += 1.2 * min(row["flats"], 3)
    s += 0.6 * min(row["crossings"], 12)
    s += 2.0 * max(0.0, 1 - row["mirror"] / 0.05)      # symmetric figures
    s += 1.5 * max(0.0, 1 - row["rotation"] / 0.05)    # three- or four-fold
    s += 2.0 * max(0.0, 1 - row["smoothness"] / 25)    # many small turns, not few big chords
    if extent < 0.2:
        s -= 4                                          # a dot is not a curve
    if row["crossings"] > 40:
        s -= 3                                          # a smear is not a curve
    return round(s, 3)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    rows = []
    for triple in TRIPLES:
        stations = walk(triple)
        for name, map_points in MAPS.items():
            # the figure is drawn over every station; the *measurements* are taken on
            # one lap, because a second lap retraces the first and would count the same
            # crossings twice
            drawn = [(fval(map_points(X, Y)[0]), fval(map_points(X, Y)[1])) for X, Y in stations]
            pts = drawn[:lap(triple)]
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            width = max(xs) - min(xs)
            height = max(ys) - min(ys)
            if not width or not height:
                continue
            turns = []
            for i in range(1, len(pts) - 1):
                ax, ay = pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]
                bx, by = pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]
                a1, a2 = math.atan2(ay, ax), math.atan2(by, bx)
                d = abs((a2 - a1 + math.pi) % (2 * math.pi) - math.pi)
                turns.append(d)
            smoothness = round(math.degrees(sum(turns) / len(turns)), 2) if turns else 180
            row = {
                "triple": f"{triple[0]},{triple[1]},{triple[2]}",
                "smoothness": smoothness,
                "map": name,
                "stations": len(pts),
                "loops": reversals(pts),
                "flats": inflections(pts),
                "crossings": crossings(pts),
                "mirror": round(mirror_gap(pts), 4),
                "rotation": round(min(rotation_gap(pts, 3), rotation_gap(pts, 4)), 4),
                "aspect": round(height / width, 3),
                "extent": round(max(width, height), 3),
                "points": [(round(x, 4), round(y, 4)) for x, y in drawn],
            }
            row["character"] = score(row, row["extent"])
            rows.append(row)

    # ties are broken towards the finely sampled walks: more stations, smoother curve
    rows.sort(key=lambda r: (-r["character"], -r["stations"]))
    print(f"{len(rows)} curves scored; the twelve with most character:\n")
    print(f"{'score':>6} {'stn':>4} {'smooth':>6} {'loops':>5} {'flats':>5} {'cross':>5} {'mirror':>7} {'aspect':>6}  triple       map")
    for row in rows[:12]:
        print(f"{row['character']:>6} {row['stations']:>4} {row['smoothness']:>6} {row['loops']:>5} "
              f"{row['flats']:>5} {row['crossings']:>5} {row['mirror']:>7} {row['aspect']:>6}  "
              f"{row['triple']:12} {row['map']}")

    if args.write:
        OUT.write_text(json.dumps({
            "format": "curve-lab.character/1",
            "note": "the walk under whole-number polynomial maps; scored on loops, flats, crossings, symmetry",
            "curves": rows[:48],
        }, indent=1) + "\n", encoding="utf-8")

        picks = rows[:9]
        cell = 320
        lines = 3
        width, height = cell * 3, cell * lines
        parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
                 f'<rect width="{width}" height="{height}" fill="#fffdf7"/>']
        for index, row in enumerate(picks):
            col, line = index % 3, index // 3
            xs = [p[0] for p in row["points"]]
            ys = [p[1] for p in row["points"]]
            span = max(max(xs) - min(xs), max(ys) - min(ys), 1e-9)
            k = (cell - 84) / span
            ox = col * cell + cell / 2 - (max(xs) + min(xs)) / 2 * k
            oy = line * cell + cell / 2 + 14 - (max(ys) + min(ys)) / 2 * k
            path = "".join(f"{'L' if i else 'M'}{x * k + ox:.1f},{oy - y * k:.1f}"
                           for i, (x, y) in enumerate(row["points"]))
            parts.append(f'<path d="{path}" fill="none" stroke="#6f4a2a" stroke-width="1.7"/>')
            parts.append(f'<text x="{col * cell + 14}" y="{line * cell + 26}" font-family="Georgia, serif" '
                         f'font-size="13" fill="#3b2d1c">{row["map"]}</text>')
            parts.append(f'<text x="{col * cell + 14}" y="{line * cell + 42}" font-family="ui-monospace, Menlo, monospace" '
                         f'font-size="9.5" fill="#8c6a21">{row["triple"]} · {row["loops"]}L '
                         f'{row["flats"]}F {row["crossings"]}X · score {row["character"]}</text>')
        parts.append("</svg>")
        SVG.write_text("\n".join(parts) + "\n", encoding="utf-8")
        print(f"\nwrote {OUT.relative_to(ROOT)} and {SVG.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
