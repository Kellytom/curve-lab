"""Find curves like a set of examples: symmetric, knot-like, many meetings.

    .venv/bin/python scripts/ph_similar.py
    .venv/bin/python scripts/ph_similar.py --write

The examples are the six the operator keeps: wave3, bud, wave5, the cusp copy and
the two padded repeats of wave3. What they share is not a root pattern but a
descriptor: each is exactly symmetric about a vertical axis, and each crosses a
rotated copy of itself many times, which is what makes the lace.

So the search is on the descriptor, not on the rows:

    symmetry        worst distance to the curve's own vertical mirror, / size
    crossings 180   meetings with the curve rotated 180 about its centroid
    crossings 90    the same at 90
    inflections    how many times the curvature changes sign
    aspect          width over height

A curve is "like them" when its symmetry is under one per cent and its crossing
count is high. The best are appended to workbench/found-curves.json with --write,
which the sandbox gallery already reads.
"""

from __future__ import annotations

import argparse
import math
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ph_quintic_metrics as metrics  # noqa: E402
from ph_crossings import pair_crossings, spine  # noqa: E402

EXAMPLES = {
    "wave3": ([1, 0, 0, 0, 0, 0], [-5, 46, -108, 72, 0, 0]),
    "bud": ([0.5, 0, 0, 0, 0, 0], [-5, 46, -108, 72, 0, 0]),
    "wave5": ([1, 0, 0, 0, 0, 0], [-10, 137, -675, 1530, -1620, 648]),
    "hersheys": ([1, 0, 0, 0, 0, 0], [-3, 30, -120, 240, -240, 96]),
}

SMALL = (-6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6)


def points_of(speed_x, speed_y, samples=500):
    _, x, y = spine(speed_x, speed_y, samples)
    return np.column_stack((x, y))


def symmetry(points):
    """Worst distance to the curve's own vertical mirror, as a fraction of size."""
    centre = (points[:, 0].min() + points[:, 0].max()) / 2
    mirrored = points.copy()
    mirrored[:, 0] = 2 * centre - mirrored[:, 0]
    size = max(np.ptp(points[:, 0]), np.ptp(points[:, 1])) or 1e-9

    def near(point, cloud):
        return float(np.sqrt(((cloud - point) ** 2).sum(1)).min())

    return max(max(near(p, points) for p in mirrored),
               max(near(p, mirrored) for p in points)) / size


def rotate(points, degrees):
    centre = points.mean(0)
    angle = math.radians(degrees)
    cos, sin = math.cos(angle), math.sin(angle)
    shifted = points - centre
    turned = np.column_stack((shifted[:, 0] * cos - shifted[:, 1] * sin,
                              shifted[:, 0] * sin + shifted[:, 1] * cos))
    return turned + centre


def descriptor(speed_x, speed_y):
    points = points_of(speed_x, speed_y)
    measured = metrics.metrics(speed_x, speed_y)
    turn = 0.0
    return {
        "symmetry": symmetry(points),
        "cross180": len(pair_crossings([tuple(p) for p in points],
                                       [tuple(p) for p in rotate(points, 180)])),
        "cross90": len(pair_crossings([tuple(p) for p in points],
                                      [tuple(p) for p in rotate(points, 90)])),
        "inflections": measured["inflection_count"],
        "bend": round(measured["bend"], 3),
        "pitch": measured["pitch"],
        "aspect": float(np.ptp(points[:, 0]) / max(np.ptp(points[:, 1]), 1e-9)),
    }


def score(described, target):
    """How far a curve is from the examples, as one number."""
    return (abs(described["symmetry"] - target["symmetry"]) * 50
            + abs(described["cross180"] - target["cross180"]) / 10
            + abs(described["cross90"] - target["cross90"]) / 10
            + abs(described["inflections"] - target["inflections"]) / 2
            + abs(math.log(max(described["aspect"], 1e-6) / max(target["aspect"], 1e-6))))


def row_from_roots(roots):
    """The coefficients of the product of (t - r), lowest power first, as integers."""
    from fractions import Fraction
    coefficients = [Fraction(1)]
    for root in roots:
        wider = [Fraction(0)] * (len(coefficients) + 1)
        for power, value in enumerate(coefficients):
            wider[power] += -root * value
            wider[power + 1] += value
        coefficients = wider
    scale = 1
    for value in coefficients:
        scale = scale * value.denominator // math.gcd(scale, value.denominator)
    return [int(value * scale) for value in coefficients]


def symmetric_families():
    """Every root set placed symmetrically about t = 1/2.

    This is how the examples were found: a root at r and one at 1 - r, with an
    optional root at 1/2 between them. A polynomial with roots symmetric about
    1/2 satisfies q(1 - t) = +/- q(t), and that is what makes the curve exactly
    symmetric about its own vertical axis.
    """
    from fractions import Fraction
    halves = (Fraction(1, 8), Fraction(1, 6), Fraction(1, 5), Fraction(1, 4),
              Fraction(1, 3), Fraction(2, 5), Fraction(3, 8))
    for count in (1, 2, 3):
        for picked in _combinations(halves, count):
            for middle in (False, True):
                for multiplicity in ((1, 1), (2, 1), (1, 2), (2, 2)):
                    roots = []
                    for r, times in zip(picked, multiplicity):
                        roots.extend([r] * times)
                        roots.extend([1 - r] * times)
                    if middle:
                        roots.append(Fraction(1, 2))
                    roots.sort()
                    yield list(picked), middle, multiplicity, row_from_roots(roots)


def _combinations(items, count):
    if count == 1:
        return [(item,) for item in items]
    if count == 2:
        return [(items[i], items[j]) for i in range(len(items)) for j in range(i + 1, len(items))]
    return [(items[i], items[j], items[k]) for i in range(len(items))
            for j in range(i + 1, len(items)) for k in range(j + 1, len(items))]


def search(curves=3000, seed=13):
    random.seed(seed)
    print("the examples")
    targets = {}
    for name, (speed_x, speed_y) in EXAMPLES.items():
        targets[name] = descriptor(speed_x, speed_y)
        d = targets[name]
        print(f"  {name:10s} symmetry {d['symmetry']:.4f}  cross180 {d['cross180']:3d}"
              f"  cross90 {d['cross90']:3d}  inflections {d['inflections']}  bend {d['bend']}")
    reference = targets["wave3"]

    best = []
    seen = set()
    for picked, middle, multiplicity, speed_y in symmetric_families():
        if len(speed_y) > 8 or not any(speed_y):
            continue
        key = tuple(speed_y)
        if key in seen:
            continue
        seen.add(key)
        for scale in (1, 0.5):
            speed_x = [scale] + [0] * (len(speed_y) - 1)
            described = descriptor(speed_x, speed_y)
            if described["symmetry"] > 0.01:
                continue                   # not symmetric after all: skip it
            best.append((score(described, reference), speed_x, speed_y, described))
    best.sort(key=lambda row: row[0])
    print(f"\n{len(best)} symmetric curves from symmetric roots; the closest six")
    for value, speed_x, speed_y, described in best[:6]:
        print(f"  distance {value:6.3f}  cross180 {described['cross180']:3d}"
              f"  cross90 {described['cross90']:3d}  inflections {described['inflections']}"
              f"  aspect {described['aspect']:4.2f}")
        print(f"     x {speed_x}  y {speed_y}")
    return best


def write(best, limit=6):
    import json
    path = ROOT / "workbench" / "found-curves.json"
    document = json.loads(path.read_text()) if path.exists() else {"curves": []}
    known = {(tuple(c["speedX"]), tuple(c["speedY"])) for c in document["curves"]}
    added = 0
    for value, speed_x, speed_y, described in best[:limit]:
        key = (tuple(float(v) for v in speed_x), tuple(float(v) for v in speed_y))
        if key in known:
            continue
        document["curves"].append({
            "name": f"like-wave-{described['cross180']}-{added + 1}",
            "speedX": [float(v) for v in speed_x],
            "speedY": [float(v) for v in speed_y],
            "bend": described["bend"],
            "pitch": described["pitch"],
            "inflections": described["inflections"],
            "from": "found",
        })
        added += 1
    path.write_text(json.dumps(document, indent=1) + "\n")
    print(f"\n{path.relative_to(ROOT)}  {added} new, {len(document['curves'])} in all")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--curves", type=int, default=3000)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    best = search(args.curves, args.seed)
    if args.write and best:
        write(best)


if __name__ == "__main__":
    main()
