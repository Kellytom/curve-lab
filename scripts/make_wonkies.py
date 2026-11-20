#!/usr/bin/env python3
"""Two wonkies from every wonk: divide the curve at the x axis.

    .venv/bin/python scripts/make_wonkies.py --write

A wonk is a radial hybrid (see scripts/hybrid_figures.py). Its polygon is cut where it
crosses the x axis, giving an **upper** half and a **lower** half. The cut point is on the
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


def split_at_x_axis(points):
    """upper and lower halves, cut where the polygon crosses y = 0."""
    upper, lower = [], []
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if (y0 >= 0) == (y1 >= 0):
            (upper if y0 >= 0 else lower).append((x1, y1))
            continue
        # the crossing, on the drawn line between two exact stations
        t = y0 / (y0 - y1) if y0 != y1 else 0.0
        cx = x0 + (x1 - x0) * t
        upper.append((cx, 0.0))
        if not upper or upper[-1] != (cx, 0.0):
            upper.append((cx, 0.0))
        lower.append((cx, 0.0))
        (upper if y1 >= 0 else lower).append((x1, y1))
    return upper, lower


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
        upper, lower = split_at_x_axis(points)
        for half, part in (("upper", upper), ("lower", lower)):
            if len(part) < 4:
                continue
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
                    "use": f"the {half} half of {name}, cut at the x axis",
                    "search": f"{candidate['formula']['plain']} -- {half} half, cut at the x axis",
                },
                "points": drawn,
                "figure": f"wonky-{name.split('-')[1]}-{half}.svg",
            })

    print(f"{len(wonks)} wonks → {len(out)} wonkies")
    if args.write:
        OUT.write_text(json.dumps({
            "format": "curve-lab.wonkies/1",
            "cut": "each wonk is divided at the x axis into an upper and a lower half; the cut "
                   "point is a drawing value between two exact stations",
            "count": len(out),
            "wonkies": out,
        }, indent=1) + "\n")
        print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
