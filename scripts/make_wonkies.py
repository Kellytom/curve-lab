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
from diagonal_crossings import crossings_via_sin2 as diagonal_crossings  # noqa: E402

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


def point_at(t, candidate):
    """the drawn point at parameter t, exactly as the curve is drawn (radial scale included)."""
    C = (1 - t * t) / (1 + t * t)
    S = 2 * t / (1 + t * t)
    x, y = C ** candidate["p"], S ** candidate["q"]
    if candidate["use"] == "radius":
        P = x * x + y * y
        for coefficient, ix, iy in BLOCKS.get(candidate["block"], []):
            P += coefficient * (x ** ix) * (y ** iy)
        x, y = x * P, y * P
    return (x, y)


def runs_at_diagonal(points, roots, candidate):
    """the arcs between the solved crossings of y = x.

    The crossings come from the equation (scripts/diagonal_crossings.py), not from walking the
    polygon: their number is the number of pieces. Each arc runs from one crossing to the next
    and stops there.
    """
    if len(roots) < 2:
        return []
    # where each root falls in the sampled polygon: t → u = t/(1+|t|) → station index
    marks = []
    for root in roots:
        u = root / (1 + abs(root))
        index = min(len(points) - 2, max(0, int(round((u + 1) * N))))
        marks.append((index, point_at(root, candidate)))
    marks.sort()
    indices = [index for index, _ in marks]
    if len(set(indices)) < 2:
        return []

    closed = list(points)
    if closed[0] != closed[-1]:
        closed.append(closed[0])

    out = []
    for k, (start, start_point) in enumerate(marks):
        end, end_point = marks[(k + 1) % len(marks)]
        middle = closed[start + 1:end] if end > start else closed[start + 1:] + closed[:end]
        # the arc ends exactly on the line: the solved crossing point, then the stations
        arc = [start_point] + middle + [end_point]
        if len(arc) < 3:
            continue
        mid = arc[len(arc) // 2]
        side = "NW" if mid[1] > mid[0] else "SE"
        out.append((side, arc))
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
        runs = runs_at_diagonal(points, diagonal_crossings(candidate["p"], candidate["q"]), candidate)
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
