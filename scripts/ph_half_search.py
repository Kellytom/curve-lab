"""Half powers: can a row be symmetric, and can it be a knot?

    .venv/bin/python scripts/ph_half_search.py
    .venv/bin/python scripts/ph_half_search.py --write

The root walk at step 1 gets its symmetry for free, because mirroring the roots
about 1/2 mirrors the parameter t -> 1 - t. At a fractional step the speed is a
polynomial in u = t^s, and the symmetry point of u is 1/2, which is t = 2^(-1/s):
irrational for s = 1/2, 1/3, 3/2. So exact mirror symmetry should be impossible
from rational rows. This script measures instead of asserting it:

* best mirror gap over a large random draw, at several steps
* whether any drawn row is both near-symmetric and a knot (self-crossings)

A gap under 1e-3 of the curve's size is treated as exact to drawing precision.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ph_root_search as R  # noqa: E402
from ph_crossings import pair_crossings  # noqa: E402

OUT = ROOT / "workbench" / "half-power-curves.json"
STEPS = (1.0, 0.5, 0.75, 1.5, 2.0)
SMALL = (-9, -6, -4, -3, -2, -1, 0, 1, 2, 3, 4, 6, 9)


def spine(row_x, row_y, step, samples=400):
    points = [(0.0, 0.0)]
    x = y = 0.0
    for i in range(samples):
        t = (i + 0.5) / samples
        p = sum(c * t ** (k * step) for k, c in enumerate(row_x))
        q = sum(c * t ** (k * step) for k, c in enumerate(row_y))
        x += (p * p - q * q) / samples
        y += 2 * p * q / samples
        points.append((x, y))
    return points


def look(row_x, row_y, step):
    points = spine(row_x, row_y, step)
    mirror = R.distance_to(points, R.mirror_of(points))
    turn = R.distance_to(points, R.half_turn_of(points))
    width = max(p[0] for p in points) - min(p[0] for p in points)
    height = max(p[1] for p in points) - min(p[1] for p in points)
    if width <= 0 or height <= 0:
        return None
    arc = sum(math.dist(points[i], points[i + 1]) for i in range(len(points) - 1))
    chord = math.dist(points[0], points[-1])
    return {
        "gap": min(mirror, turn), "kind": "mirror" if mirror <= turn else "half-turn",
        "self": len(pair_crossings(points, points)),
        "bend": arc / chord if chord > 1e-12 else 99.0,
        "aspect": width / height,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draws", type=int, default=1200)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    random.seed(args.seed)

    best = {step: None for step in STEPS}
    knots = []
    draws = []
    for step in STEPS:
        for _ in range(args.draws):
            length = random.choice((4, 5, 6))
            row_x = [random.choice(SMALL) for _ in range(length)]
            row_y = [random.choice(SMALL) for _ in range(length)]
            if not any(row_y):
                continue
            measured = look(row_x, row_y, step)
            if not measured or measured["aspect"] < 0.2 or measured["aspect"] > 80:
                continue
            measured.update({"step": step, "speedX": row_x, "speedY": row_y})
            draws.append(measured)
            if best[step] is None or measured["gap"] < best[step]["gap"]:
                best[step] = measured
            if measured["gap"] < 0.02 and measured["self"] >= 4:
                knots.append(measured)

    print(f"{len(draws)} usable draws\n")
    print(f"{'step':>5} {'best mirror gap':>16} {'its self-crossings':>19} {'its bend':>9}")
    for step in STEPS:
        found = best[step]
        if found:
            print(f"{step:5.2f} {found['gap']:16.5f} {found['self']:19d} {found['bend']:9.2f}")

    knots.sort(key=lambda row: (row["gap"], -row["self"]))
    print(f"\nrows that are near-symmetric AND knots (gap < 0.02, four or more self-crossings): {len(knots)}")
    for row in knots[:10]:
        print(f"  step {row['step']:4.2f} gap {row['gap']:.4f} crossings {row['self']:2d} "
              f"bend {row['bend']:5.2f} | x {row['speedX']} y {row['speedY']}")

    exact = [row for row in draws if row["gap"] < 1e-3]
    print(f"\nrows within 1e-3 of symmetric: {len(exact)} of {len(draws)}")
    for row in exact[:8]:
        print(f"  step {row['step']:4.2f} gap {row['gap']:.6f} crossings {row['self']:2d} | "
              f"x {row['speedX']} y {row['speedY']}")

    if args.write and knots:
        OUT.write_text(json.dumps({"name": "half-power-curves",
                                   "note": "written by scripts/ph_half_search.py",
                                   "curves": knots[:40]}, indent=1) + "\n")
        print(f"\n{OUT.relative_to(ROOT)}  {len(knots[:40])} curves")


if __name__ == "__main__":
    main()
