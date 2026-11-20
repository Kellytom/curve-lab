#!/usr/bin/env python3
"""A double wonky: a wonky mirrored across the x axis.

    .venv/bin/python scripts/make_doubles.py --write

The wonky is open at the x axis (it was cut there). Mirroring it in that axis closes it into
a symmetric figure: the half, then the same half with y negated, walked back. The join is
exact at the two ends — those points sit on the axis, where y = 0 and −y = 0.

Writes workbench/doubles.json; scripts/double_figures.mjs draws them.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import character_search as cs  # noqa: E402

WONKIES = ROOT / "workbench" / "wonkies.json"
OUT = ROOT / "workbench" / "doubles.json"


def double(points):
    """the half, then its mirror in the x axis, walked back."""
    mirrored = [(x, -y) for x, y in reversed(points)]
    # the join: drop the duplicated end points (both sit on the axis)
    return points + mirrored[1:-1]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    wonkies = json.loads(WONKIES.read_text())["wonkies"]
    out = []
    for row in wonkies:
        points = [(x, y) for x, y in row["points"]]
        both = double(points)
        step = max(1, len(both) // 120)
        drawn = [[round(x, 6), round(y, 6)] for x, y in both[::step]]
        if drawn[-1] != [round(both[-1][0], 6), round(both[-1][1], 6)]:
            drawn.append([round(both[-1][0], 6), round(both[-1][1], 6)])
        out.append({
            "id": f"double-{row['id'].removeprefix('wonky-')}",
            "parent": row["id"],
            "parentName": row["parentName"],
            "half": row["half"],
            "p": row["p"], "q": row["q"], "use": row["use"], "block": row["block"],
            "crossings": cs.crossings(both),
            "formula": {
                "plain": row["formula"]["plain"],
                "internal": row["formula"]["internal"],
                "middle": row["formula"]["middle"],
                "use": f"{row['parentName']}, its {row['half']} half mirrored across the x axis",
                "search": f"{row['formula']['plain']} mirrored across the x axis",
            },
            "points": drawn,
            "figure": f"double-{row['id'].removeprefix('wonky-')}.svg",
        })

    print(f"{len(wonkies)} wonkies → {len(out)} doubles")
    if args.write:
        OUT.write_text(json.dumps({
            "format": "curve-lab.doubles/1",
            "rule": "a wonky mirrored across the x axis: the half, then the same half with y "
                    "negated, walked back; the join points sit on the axis, where the mirror "
                    "is the point itself",
            "count": len(out),
            "doubles": out,
        }, indent=1) + "\n")
        print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
