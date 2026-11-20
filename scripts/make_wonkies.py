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


def drawn_side(t, candidate):
    """sign of the drawn point's distance from y = x: sign(P·(y − x))."""
    px, py = point_at(t, candidate)
    d = py - px
    return 1 if d > 0 else (-1 if d < 0 else 0)


def cuts_of(candidate, steps=8000):
    """every parameter where the drawn point crosses y = x, solved and bisected.

    The drawn point is (C^p·P, S^q·P), so it is on y = x where P·(S^q − C^p) = 0: both the
    solved diagonal roots and the places the curve passes the origin. Each sign change of that
    product is bracketed on the parameter and bisected; nothing is taken from the polygon.
    """
    def value(t):
        px, py = point_at(t, candidate)
        return py - px

    roots = []
    previous_t = previous_v = None
    for i in range(-steps, steps + 1):
        u = i / steps
        t = u / (1 - abs(u)) if abs(u) < 1 else 1e9 * (1 if u > 0 else -1)
        v = value(t)
        if previous_v is not None and (previous_v < 0) != (v < 0):
            lo, hi, flo = previous_t, t, previous_v
            for _ in range(70):
                mid = (lo + hi) / 2
                fm = value(mid)
                if (flo < 0) == (fm < 0):
                    lo, flo = mid, fm
                else:
                    hi = mid
            roots.append((lo + hi) / 2)
        previous_t, previous_v = t, v
    return roots


def t_of_station(k):
    """station k (list order) sits at u = (k − (N−1))/N, t = u/(1−|u|)."""
    u = (k - (N - 1)) / N
    if abs(u) >= 1:                       # the closing limit point sits at t = ∞
        u = 0.999999 * (1 if u > 0 else -1)
    return u / (1 - abs(u))


def runs_at_diagonal(points, roots, candidate):
    """cut the polygon where the solved crossings fall, and return the arcs between them.

    Each crossing is inserted into the segment it belongs to, so every piece is a contiguous
    run of the drawn polygon: no chords across the figure, and no station from the other side
    of the line.
    """
    ts = [t_of_station(k) for k in range(len(points))]
    # nodes: (t, point, is_cut)
    nodes = [(ts[i], points[i], False) for i in range(len(points))]
    for root in roots:
        # find the segment whose t range contains the root
        index = None
        for i in range(len(ts) - 1):
            if (ts[i] - root) * (ts[i + 1] - root) <= 0:
                index = i
                break
        if index is None:
            continue
        nodes.append((root, point_at(root, candidate), True))
    nodes.sort(key=lambda node: node[0])

    cuts = [i for i, node in enumerate(nodes) if node[2]]
    if len(cuts) < 2:
        return []

    pieces = []
    for k, start in enumerate(cuts):
        end = cuts[(k + 1) % len(cuts)]
        if end > start:
            arc = [nodes[i][1] for i in range(start, end + 1)]
            cut_ts = [nodes[start][0], nodes[end][0]]
        else:                      # wrap round the end of the parameter
            arc = [nodes[i][1] for i in range(start, len(nodes))] + \
                  [nodes[i][1] for i in range(0, end + 1)]
            cut_ts = [nodes[start][0], nodes[end][0]]
        if len(arc) < 3:
            continue
        mid = arc[len(arc) // 2]
        side = "NW" if mid[1] > mid[0] else "SE"
        pieces.append((side, arc, cut_ts))
    return pieces


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
        roots = cuts_of(candidate)
        runs = runs_at_diagonal(points, roots, candidate)
        counters = {"NW": 0, "SE": 0}
        for side, part, cut_ts in runs:
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
                "kind": "piece",
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
            "cuts": [{"t": round(t, 6),
                      "x": round(point_at(t, candidate)[0], 4),
                      "y": round(point_at(t, candidate)[1], 4)} for t in cut_ts],
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
