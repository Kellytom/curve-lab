"""A foundry: whole-number maps of the walk, scored for complexity.

The walk is exact (`walker(k)` of a p-triple); a *map* sends its coordinates
(X, Y) somewhere else. This file tries a family of maps and keeps the ones that
read as curves with character: several loops, a handful of crossings, and a
figure close to its own mirror.

    .venv/bin/python scripts/curve_foundry.py            # print the ranking
    .venv/bin/python scripts/curve_foundry.py --write    # write workbench/foundry.json

The family tried here is the odd map

    x = X * (a + b X² + c Y²)
    y = Y * (d + e X² + f Y²)

because it keeps the walk's symmetry about the origin: a closed figure, not two
lobes. Coefficients are small whole numbers, so every curve is cheap to write.

Spec: state/SPEC-prime-mover-int.md, "the foundry".
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import character_search as cs  # noqa: E402

OUT = ROOT / "workbench" / "foundry.json"

TRIPLES = [(3, 4, 5), (5, 12, 13), (7, 24, 25), (20, 21, 29), (48, 55, 73), (56, 783, 785)]


def map_points(coefficients):
    a, b, c, d, e, f = coefficients
    return lambda X, Y: (
        X * (a + b * X * X + c * Y * Y),
        Y * (d + e * X * X + f * Y * Y),
    )


def measure(points):
    """The numbers that decide whether a figure is worth looking at."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    width = max(xs) - min(xs)
    height = max(ys) - min(ys)
    return {
        "loops": min(cs.reversals(points), 24),
        "crossings": cs.crossings(points),
        "mirror": round(cs.mirror_gap(points), 4),
        "aspect": round(max(width, height) / (min(width, height) or 1), 3),
        "extent": round(max(width, height), 3),
    }


def score(row):
    """Beauty, as a number: crossings are the character, symmetry is the calm.

    A curve with no crossing is a blob; a curve with forty is a smear. The band
    between is where the lace lives.
    """
    crossings = row["crossings"]
    s = 0.0
    if 4 <= crossings <= 30:
        s += min(crossings, 18) * 1.0
    elif crossings > 30:
        s += 18 - (crossings - 30) * 0.5
    s += 3.0 * max(0.0, 1 - row["mirror"] / 0.08)
    s += 2.0 * max(0.0, 1 - abs(row["aspect"] - 1.15) / 0.6)
    s += 1.5 * min(row["loops"], 6)
    if row["extent"] < 0.5:
        s -= 6
    return round(s, 3)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--top", type=int, default=20)
    args = parser.parse_args(argv)

    rows = []
    for triple in TRIPLES:
        stations = cs.walk(triple)
        lap = cs.lap(triple)
        for coefficients in itertools.product((1, 2), (0, -1, 1, -2), (0, -1, 1, -2),
                                             (1, 2), (0, -1, 1, -2), (0, -1, 1, -2)):
            name = f"x(a{coefficients[0]} b{coefficients[1]} c{coefficients[2]}) " \
                   f"y(d{coefficients[3]} e{coefficients[4]} f{coefficients[5]})"
            f = map_points(coefficients)
            drawn = [(cs.fval(f(X, Y)[0]), cs.fval(f(X, Y)[1])) for X, Y in stations]
            pts = drawn[:lap]
            if max(abs(p[0]) for p in pts) > 40 or max(abs(p[1]) for p in pts) > 40:
                continue
            row = measure(pts)
            if row["crossings"] < 3:
                continue
            row.update({
                "map": name,
                "coefficients": list(coefficients),
                "triple": ",".join(str(v) for v in triple),
                "stations": len(pts),
                "character": score(row),
                "points": [[round(x, 5), round(y, 5)] for x, y in pts],
            })
            rows.append(row)

    rows.sort(key=lambda r: -r["character"])
    best = rows[: args.top]
    for i, row in enumerate(best, 1):
        print(f"{i:2d}. {row['character']:6.2f}  {row['map']}  on {row['triple']}  "
              f"crossings {row['crossings']:2d}  loops {row['loops']}  "
              f"mirror {row['mirror']:.4f}  aspect {row['aspect']}")

    if args.write:
        OUT.write_text(json.dumps({"format": "curve-lab.foundry/1", "curves": best}, indent=1) + "\n")
        print(f"wrote {OUT.relative_to(ROOT)} with {len(best)} curves")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
