#!/usr/bin/env python3
"""Two wonkies from every wonk: divide the curve at the y = x axis.

    .venv/bin/python scripts/make_wonkies.py --write

A wonk is a radial hybrid (see scripts/hybrid_figures.py). Its polygon is cut where it
crosses the diagonal **y = x** (the 45° axis), giving the two halves — "north-west" of the
line and "south-east" of it. The cut point is on the
line between two exact stations, so the cut is a drawing value and the file says so; the
stations on either side are exact.

Writes workbench/wonkies.json; scripts/wonky_figures.mjs draws them.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import character_search as cs  # noqa: E402

CANDIDATES = ROOT / "workbench" / "hybrids.json"
DECISIONS = ROOT / "workbench" / "sandbox-curves.json"
OUT = ROOT / "workbench" / "wonkies.json"
N = 100

BLOCKS = {
    "quadratic": [(2, 1, 1)],
    "cubic": [(3, 2, 1), (3, 1, 2)],
    "quintic-central": [(10, 3, 2), (10, 2, 3)],
    "quintic-all-four": [(5, 4, 1), (10, 3, 2), (10, 2, 3), (5, 1, 4)],
    "cubic-and-quintic": [(3, 2, 1), (3, 1, 2), (5, 4, 1), (10, 3, 2), (10, 2, 3), (5, 1, 4)],
    "every-term": [(2, 1, 1), (3, 2, 1), (3, 1, 2), (5, 4, 1), (10, 3, 2), (10, 2, 3), (5, 1, 4)],
}


def power(value, n):
    out = Fraction(1)
    for _ in range(n):
        out *= value
    return out


def stations():
    out = []
    for i in range(-N + 1, N):
        u = Fraction(i, N)
        t = u / (1 - abs(u))
        out.append(((1 - t * t) / (1 + t * t), 2 * t / (1 + t * t)))
    return out


ST = stations()


def points_for(candidate):
    p, q, use, block = candidate["p"], candidate["q"], candidate["use"], candidate["block"]
    block_terms = BLOCKS.get(block, [])
    out = []
    for C, S in ST:
        x, y = power(C, p), power(S, q)
        if use == "radius":
            P = x * x + y * y
            for coefficient, ix, iy in block_terms:
                P += coefficient * power(x, ix) * power(y, iy)
            x, y = x * P, y * P
        out.append((float(x), float(y)))
    out.append((float((-1) ** p), 0.0))
    return out


def runs_at_diagonal(points):
    """every arc of the closed polygon between two crossings of y = x.

    A wonk may cross the 45° line many times, so there may be more than two pieces. Each
    piece stays on one side of the line and stops at the crossings either side of it; the
    side decides the label, NW (y > x) or SE (y < x).
    """
    closed = list(points)
    if closed[0] != closed[-1]:
        closed.append(closed[0])

    crossings = []                     # (index of the point AFTER the crossing, point)
    for i, ((x0, y0), (x1, y1)) in enumerate(zip(closed, closed[1:])):
        d0, d1 = y0 - x0, y1 - x1
        if (d0 >= 0) != (d1 >= 0):
            t = d0 / (d0 - d1) if d0 != d1 else 0.0
            crossings.append((i + 1, (x0 + (x1 - x0) * t, y0 + (y1 - y0) * t)))
    if len(crossings) < 2:
        return []

    # start the walk at the first crossing, so every piece begins and ends at a cut
    i0, start_point = crossings[0]
    rotated = [start_point] + closed[i0:] + closed[:i0] + [start_point]

    runs = []
    current = [start_point]
    for (x0, y0), (x1, y1) in zip(rotated, rotated[1:]):
        d0, d1 = y0 - x0, y1 - x1
        current.append((x1, y1))
        if (d0 >= 0) != (d1 >= 0):
            runs.append(current)
            current = [(x1, y1)]
    if len(current) > 2:
        runs.append(current)

    out = []
    for run in runs:
        if len(run) < 3:
            continue
        mid = run[len(run) // 2]
        side = "NW" if mid[1] > mid[0] else "SE"
        out.append((side, run))
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    candidates = {row["id"]: row for row in json.loads(CANDIDATES.read_text())["candidates"]}
    decisions = json.loads(DECISIONS.read_text()).get("curves", [])
    wonks = []
    for row in decisions:
        name = str(row.get("curveName") or "")
        if not name.lower().startswith("wonk-"):
            continue
        candidate = candidates.get(row["name"])
        if candidate:
            wonks.append((name, candidate))
    wonks.sort(key=lambda item: int(item[0].split("-")[1]))

    out = []
    for name, candidate in wonks:
        points = points_for(candidate)
        runs = runs_at_diagonal(points)
        counters = {"NW": 0, "SE": 0}
        for side, part in runs:
            if len(part) < 4:
                continue
            counters[side] += 1
            half = f"{side}-{counters[side]}"
            step = max(1, len(part) // 90)
            drawn = [[round(x, 6), round(y, 6)] for x, y in part[::step]]
            if drawn[-1] != [round(part[-1][0], 6), round(part[-1][1], 6)]:
                drawn.append([round(part[-1][0], 6), round(part[-1][1], 6)])
            out.append({
                "id": f"wonky-{name.split('-')[1]}-{half}",
                "parent": candidate["id"],
                "parentName": name,
                "half": half,
                "p": candidate["p"],
                "q": candidate["q"],
                "use": candidate["use"],
                "block": candidate["block"],
                "crossings": cs.crossings([(x, y) for x, y in part]),
                "formula": {
                    "plain": candidate["formula"]["plain"],
                    "internal": candidate["formula"]["internal"],
                    "middle": candidate["formula"]["middle"],
                    "use": f"the {half} half of {name}, cut at the y = x axis",
                    "search": f"{candidate['formula']['plain']} -- {half} half, cut at the y = x axis",
                },
                "points": drawn,
                "figure": f"wonky-{name.split('-')[1]}-{half}.svg",
            })

    print(f"{len(wonks)} wonks → {len(out)} wonkies")
    if args.write:
        OUT.write_text(json.dumps({
            "format": "curve-lab.wonkies/1",
            "cut": "each wonk is divided at the 45° axis y = x into two halves, NW and SE; "
                   "the cut point is a drawing value between two exact stations",
            "count": len(out),
            "wonkies": out,
        }, indent=1) + "\n")
        print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
