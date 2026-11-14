"""Do fractional exponents give balanced curves from mirrored roots?

    .venv/bin/python scripts/ph_step_search.py
    .venv/bin/python scripts/ph_step_search.py --write

With exponent step s the speed is a polynomial in u = t^s, so mirrored roots
(r and 1 - r) make the speed symmetric about u = 1/2. That is a symmetry of the
*curve* only if the map t -> (1 - t^s)^(1/s) is the reflection the figure has,
so this script measures it: the worst distance from the curve to its own mirror
and to its own half turn, as a share of its size.

It also counts what makes a knot: self-crossings, and meetings with the copy
that makes the lace. Rows are built exactly from roots and measured numerically,
because a fractional exponent has no closed form to read the numbers off.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ph_root_search as roots_module  # noqa: E402
from ph_crossings import pair_crossings  # noqa: E402

OUT = ROOT / "workbench" / "step-curves.json"

STEPS = (1.0, 0.75, 2 / 3, 0.5, 1 / 3, 0.25)
PAIRS = (Fraction(1, 6), Fraction(1, 8), Fraction(1, 9), Fraction(1, 10), Fraction(1, 12))
MIDDLES = (1, 3, 5)
BOWS = (0, 2, -2)


def spine(x_row, y_row, step, samples=700):
    """The curve, sampled: z(t) = integral of (p^2 - q^2, 2 p q) with p, q in t^step."""
    points = [(0.0, 0.0)]
    x = y = 0.0
    for i in range(samples):
        t = (i + 0.5) / samples
        p = sum(coefficient * t ** (k * step) for k, coefficient in enumerate(x_row))
        q = sum(coefficient * t ** (k * step) for k, coefficient in enumerate(y_row))
        x += (p * p - q * q) / samples
        y += 2 * p * q / samples
        points.append((x, y))
    return points


def distance_to(points, other):
    size = max(max(x for x, _ in points) - min(x for x, _ in points),
               max(y for _, y in points) - min(y for _, y in points)) or 1e-9

    def nearest(point, cloud):
        return min(((px - point[0]) ** 2 + (py - point[1]) ** 2) ** 0.5 for px, py in cloud)

    return max(max(nearest(p, other) for p in points),
               max(nearest(p, points) for p in other)) / size


def measure(x_row, y_row, step):
    points = spine(x_row, y_row, step)
    mirror = distance_to(points, roots_module.mirror_of(points))
    turn = distance_to(points, roots_module.half_turn_of(points))
    if mirror <= 1e-4:
        kind, partner = "mirror", roots_module.rotate(points, 180)
    elif turn <= 1e-4:
        kind, partner = "half-turn", roots_module.mirror_of(points)
    else:
        kind, partner = None, None
    width = max(x for x, _ in points) - min(x for x, _ in points)
    height = max(y for _, y in points) - min(y for _, y in points)
    # arc and chord from the sample
    arc = sum(((points[i + 1][0] - points[i][0]) ** 2 + (points[i + 1][1] - points[i][1]) ** 2) ** 0.5
              for i in range(len(points) - 1))
    chord = ((points[-1][0]) ** 2 + (points[-1][1]) ** 2) ** 0.5
    return {
        "symmetryKind": kind,
        "symmetry": round(min(mirror, turn), 9),
        "self": len(pair_crossings(points, points)),
        "meets": len(pair_crossings(points, partner)) if partner else 0,
        "bend": round(arc / chord, 3) if chord > 1e-12 else None,
        "aspect": round(width / height, 3) if height > 1e-12 else None,
    }


def row_from_roots(spots):
    """Integer row from mirrored roots, via the shared exact construction."""
    return roots_module.row_from_roots(spots)


def candidates():
    for pair in PAIRS:
        for middle in MIDDLES:
            spots = [pair, Fraction(1, 2)] * 0 + [pair] + [Fraction(1, 2)] * middle + [1 - pair]
            y_row = row_from_roots(spots)
            for bow in BOWS:
                x_row = [1, bow, -bow]
                for step in STEPS:
                    yield spots, y_row, x_row, bow, step


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write workbench/step-curves.json")
    parser.add_argument("--top", type=int, default=12)
    args = parser.parse_args()

    found = []
    for spots, y_row, x_row, bow, step in candidates():
        measured = measure(x_row, y_row, step)
        if measured["symmetryKind"] is None:
            continue
        found.append({"roots": ",".join(str(spot) for spot in spots), "bow": bow, "step": step,
                      **measured, "speedX": x_row, "speedY": y_row})

    found.sort(key=lambda row: (-row["self"], -row["meets"], row["bend"] or 99))
    print(f"{len(found)} balanced curves over {len(STEPS)} steps")
    print(f"{'roots':34s} {'step':>5s} {'bow':>4s} {'kind':9s} {'self':>4s} {'meets':>5s} {'bend':>6s} {'aspect':>6s}")
    for row in found[:args.top]:
        print(f"{row['roots'][:34]:34s} {row['step']:5.2f} {row['bow']:4} {row['symmetryKind']:9s} "
              f"{row['self']:4d} {row['meets']:5d} {str(row['bend']):>6s} {str(row['aspect']):>6s}")

    if args.write:
        OUT.write_text(json.dumps({"name": "step-curves",
                                   "note": "written by scripts/ph_step_search.py",
                                   "curves": found[:40]}, indent=1) + "\n")
        print(f"\n{OUT.relative_to(ROOT)}  {len(found[:40])} curves")


if __name__ == "__main__":
    main()
