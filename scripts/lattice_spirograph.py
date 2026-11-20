#!/usr/bin/env python3
"""The lattice spirograph: two vanes, every station an integer point.

    .venv/bin/python scripts/lattice_spirograph.py
    .venv/bin/python scripts/lattice_spirograph.py --write

The operator's reading (2026-11-19): chain the prime movers, then treat the
secondary movers like the main vane and the small vanes of a mobile. That is a
spirograph — two rotations added — with a spirograph ratio between the rates.
The difference asked for: **every station must be an integer lattice point**, so
the curve can be cut at a station and a branch added there.

That last requirement decides the arithmetic. A rotation that maps the lattice
to itself and keeps the radius fixed is one of the eight compass directions:

    E (1,0)  NE (1,1)  N (0,1)  NW (-1,1)  W (-1,0)  SW (-1,-1)  S (0,-1)  SE (1,-1)

So the spirograph's two rotating arms become two **compass walks**, and the pen
takes, at station k, the step that is their sum:

    step_k = compass(8·k·α) + compass(8·k·β),      α, β in turns per step

Every station is then the sum of integer steps: integer by construction, with no
rounding of a position anywhere. The two rates are written in eighths of a turn,
because eighths are the only turns the compass can express exactly — 45° is the
finest exact rotation the square lattice has.

The two rates do two different jobs, which is why there are two:

    α + β   the direction the pen travels      (evenly spaced moves)
    α − β   the beat between the vanes          (the spirograph figure)

Closure is exact and testable: the walk closes when the steps over one period sum
to zero. A closed walk can be cut anywhere without moving a station.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "workbench" / "lattice-spirograph.json"

# The compass, in eighths of a turn, starting east and turning anticlockwise.
COMPASS = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]


def direction(k: int, rate_eighths: int) -> int:
    return (k * rate_eighths) % 8


def walk(rate_a: int, rate_b: int, steps: int):
    """A lattice walk: station k is the sum of the first k step vectors."""
    points = [(0, 0)]
    x = y = 0
    for k in range(steps):
        ax, ay = COMPASS[direction(k, rate_a)]
        bx, by = COMPASS[direction(k, rate_b)]
        x += ax + bx
        y += ay + by
        points.append((x, y))
    return points


def closes(points) -> bool:
    return points[-1] == points[0]


def crossings(points) -> int:
    """Crossing pairs of the lattice polyline, on exact integer segments."""
    seen = set()
    n = len(points)
    for i in range(n - 1):
        ax, ay = points[i]
        bx, by = points[i + 1]
        for j in range(i + 2, n - 1):
            cx, cy = points[j]
            dx, dy = points[j + 1]
            if (i, j) == (0, n - 2) and points[0] == points[-1]:
                continue  # the closing vertex is the start, not a crossing
            den = (bx - ax) * (dy - cy) - (by - ay) * (dx - cx)
            if den == 0:
                continue
            s = ((cx - ax) * (dy - cy) - (cy - ay) * (dx - cx)) / den
            w = ((cx - ax) * (by - ay) - (cy - ay) * (bx - ax)) / den
            if 0 < s < 1 and 0 < w < 1:
                px = ax + (bx - ax) * s
                py = ay + (by - ay) * s
                seen.add((round(px, 4), round(py, 4)))
    return len(seen)


def stations(points) -> int:
    return len(set(points))


def aspect(points) -> float:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    w = max(xs) - min(xs)
    h = max(ys) - min(ys)
    return round(h / w, 3) if w else 0.0


def period(rate_a: int, rate_b: int) -> int:
    """The step count after which both vane directions repeat."""
    for n in range(1, 65):
        if (n * rate_a) % 8 == 0 and (n * rate_b) % 8 == 0:
            return n
    return 8


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    rows = []
    for rate_a in range(1, 9):
        for rate_b in range(1, 9):
            for laps in (1, 2, 3):
                steps = period(rate_a, rate_b) * laps
                points = walk(rate_a, rate_b, steps)
                if not closes(points):
                    continue
                xs = [p[0] for p in points]
                ys = [p[1] for p in points]
                width = max(xs) - min(xs)
                height = max(ys) - min(ys)
                if min(width, height) < 3:
                    continue
                rows.append(
                    {
                        "rateA": f"{rate_a}/8",
                        "rateB": f"{rate_b}/8",
                        "steps": steps,
                        "stations": stations(points),
                        "crossings": crossings(points),
                        "aspect": aspect(points),
                        "width": width,
                        "height": height,
                        "points": points,
                    }
                )

    rows.sort(key=lambda r: (-r["crossings"], -r["stations"]))
    closed = len(rows)
    print(f"{closed} closed lattice walks · {sum(r['crossings'] for r in rows)} crossing pairs in all")
    for row in rows[:12]:
        print(
            f"  {row['rateA']} + {row['rateB']} · {row['steps']} steps · "
            f"{row['stations']} stations · {row['crossings']} crossings · "
            f"{row['width']}x{row['height']}"
        )

    if args.write:
        OUT.write_text(
            json.dumps(
                {
                    "format": "curve-lab.lattice-spirograph/1",
                    "note": "two compass walks summed; stations are integers by construction; rates in eighths of a turn",
                    "curves": rows[:24],
                },
                indent=1,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
