#!/usr/bin/env python3
"""Mirror a hybrid across the y axis into a double, and check the ends line up.

    .venv/bin/python scripts/make_mirror_doubles.py --write

The rule is the wonk page's, with the y axis instead of y = x:

    cut the curve where it crosses x = 0,
    keep one half,
    mirror it (x → −x), walk it back,
    the join closes when the half's ends sit on x = 0.

Every double records `closed` and `endGap`, so a join that does not meet is named rather
than drawn and hoped for. Writes workbench/mirror-doubles.json; the figures are drawn by
scripts/wonky_figures.mjs with the same builder.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HYBRIDS = ROOT / "workbench" / "hybrids.json"
DECISIONS = ROOT / "data" / "sandbox-curves.json"
OUT = ROOT / "workbench" / "mirror-doubles.json"
FIG = ROOT / "app" / "public" / "hybrid-figures"
SIZE = 440


def split_at_y_axis(points):
    """the arcs between the crossings of x = 0, the longest one kept.

    Crossings are inserted into the polygon segment they fall on, so each arc starts and ends
    exactly on the axis — which is what makes the mirror close.
    """
    nodes = [(0, points[0], False)]
    for index, (a, b) in enumerate(zip(points, points[1:]), start=1):
        nodes.append((index, b, False))
        if (a[0] >= 0) != (b[0] >= 0):
            t = a[0] / (a[0] - b[0]) if a[0] != b[0] else 0.0
            crossing = (0.0, a[1] + (b[1] - a[1]) * t)
            nodes.append((index - 0.5, crossing, True))
    nodes.sort(key=lambda node: node[0])
    cuts = [i for i, node in enumerate(nodes) if node[2]]
    if len(cuts) < 2:
        return [], 0.0
    arcs = []
    for k, start in enumerate(cuts):
        end = cuts[(k + 1) % len(cuts)]
        arc = [nodes[i][1] for i in range(start, end + 1)] if end > start else \
              [nodes[i][1] for i in range(start, len(nodes))] + \
              [nodes[i][1] for i in range(0, end + 1)]
        if len(arc) > 2:
            arcs.append(arc)
    arcs.sort(key=lambda arc: -sum(math.dist(p, q) for p, q in zip(arc, arc[1:])))
    return arcs[0] if arcs else [], 0.0


def double_of(points):
    half, _ = split_at_y_axis(points)
    if len(half) < 3:
        return None
    mirrored = [(-x, y) for x, y in reversed(half)]
    double = half + mirrored[1:]
    gap = math.dist(double[0], double[-1])
    return {"points": double, "closed": gap < 1e-6, "endGap": round(gap, 6)}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--only", default="", help="comma-separated hybrid ids")
    args = parser.parse_args(argv)

    hybrids = {row["id"]: row for row in json.loads(HYBRIDS.read_text())["candidates"]}
    decisions = json.loads(DECISIONS.read_text()).get("rows", []) if DECISIONS.exists() else []
    wanted = {row["name"] for row in decisions if row.get("decision") == "saved"} if not args.only else set(args.only.split(","))

    out = []
    for key in sorted(wanted):
        candidate = hybrids.get(key)
        if candidate is None or not candidate.get("points"):
            continue
        built = double_of([tuple(p) for p in candidate["points"]])
        if built is None:
            continue
        out.append({
            "id": f"mirror-{key}",
            "parent": key,
            "kind": "double",
            "mirror": "y axis",
            "closed": built["closed"],
            "endGap": built["endGap"],
            "p": candidate.get("p"), "q": candidate.get("q"),
            "use": candidate.get("use"), "block": candidate.get("block"),
            "formula": candidate.get("formula", {}),
            "points": [[round(x, 6), round(y, 6)] for x, y in built["points"]],
            "figure": f"mirror-{key}.svg",
        })

    closed = sum(1 for row in out if row["closed"])
    print(f"{len(out)} mirror doubles, {closed} closed, {len(out) - closed} with a gap")
    for row in out:
        if not row["closed"]:
            print(f"  {row['id']}: ends do not meet (gap {row['endGap']})")
    if args.write:
        OUT.write_text(json.dumps({
            "format": "curve-lab.mirror-doubles/1",
            "rule": "the hybrid is cut where it crosses x = 0, one half is kept and mirrored "
                    "across the y axis, and the ends are checked: closed means the gap is 0",
            "count": len(out), "doubles": out,
        }, indent=1) + "\n")
        print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
