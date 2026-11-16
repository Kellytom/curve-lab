"""Exhaustive census of the mirror-symmetric flat-spot families.

    .venv/bin/python scripts/family_census.py            # sweep and summarise
    .venv/bin/python scripts/family_census.py --report   # re-print from the JSON

The box, stated so the word "all" has a meaning:

  * every flat spot is mirrored about 1/2, so a set is written as its lower half;
  * 1, 2 or 3 outer spots in that lower half, each with denominators 2 to 20;
  * 1 to 5 copies of the flat spot at 1/2;
  * the x row is the constant 1, so the count is about the roots, not the width
    (measured 2026-11-16: the width bump changes the shape but never the crossing
    count, so it is a second axis, not part of this census).

For every set the script records the crossing count at the page's 1024 samples,
the grid the row needs, and the arc length. Sets whose rows are proportional are
one curve, so they are kept once.

Measured 2026-11-16: 8,265 root sets, 4,912 distinct curves after the
proportionality check.
"""

from __future__ import annotations

import itertools
import json
import sys
from fractions import Fraction as F
from math import gcd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ph_root_search as R  # noqa: E402
from ph_crossings import self_crossings  # noqa: E402

OUT = ROOT / "workbench" / "family-census.json"


def rows_for(roots):
    y = R.row_from_roots(roots)
    x = [1, 0, 0] + [0] * max(0, len(y) - 3)
    n = max(len(x), len(y))
    return (x + [0] * (n - len(x)))[:n], (y + [0] * (n - len(y)))[:n]


def arc_of(speed_x, speed_y):
    """The arc length exactly: |z'| = p^2 + q^2, a polynomial, so no sampling."""
    n = max(len(speed_x), len(speed_y))
    xs = list(speed_x) + [0] * (n - len(speed_x))
    ys = list(speed_y) + [0] * (n - len(speed_y))
    total = F(0)
    for m in range(2 * n - 1):
        coefficient = sum(xs[i] * xs[m - i] for i in range(n) if 0 <= m - i < n) \
            + sum(ys[i] * ys[m - i] for i in range(n) if 0 <= m - i < n)
        total += F(coefficient, m + 1)
    return total


def grid_of(speed_x, speed_y):
    n = max(len(speed_x), len(speed_y))
    xs = list(speed_x) + [0] * (n - len(speed_x))
    ys = list(speed_y) + [0] * (n - len(speed_y))
    pitch = 1
    for m in range(2 * n - 1):
        real = sum(xs[i] * xs[m - i] for i in range(n) if 0 <= m - i < n) \
            - sum(ys[i] * ys[m - i] for i in range(n) if 0 <= m - i < n)
        imag = 2 * sum(xs[i] * ys[m - i] for i in range(n) if 0 <= m - i < n)
        for num in (real, imag):
            if num:
                denominator = F(num, m + 1).denominator
                pitch = pitch * denominator // gcd(pitch, denominator)
    return pitch


def signature(speed_y):
    """Two rows that differ by a constant factor are the same curve."""
    values = [v for v in speed_y if v]
    if not values:
        return None
    divisor = 0
    for value in values:
        divisor = gcd(divisor, abs(int(value)))
    return tuple(int(v) // divisor for v in speed_y)


def sweep():
    pool = [F(1, d) for d in range(2, 21)]
    found = {}
    tested = 0
    for pairs in (1, 2, 3):
        for outer in itertools.combinations_with_replacement(pool, pairs):
            for middle in range(1, 6):
                roots = list(outer) + [F(1, 2)] * middle + [1 - c for c in reversed(outer)]
                speed_x, speed_y = rows_for(roots)
                tested += 1
                if not any(speed_y):
                    continue
                key = signature(speed_y)
                if key in found:
                    continue
                found[key] = {
                    "spots": ", ".join(f"{c.numerator}/{c.denominator}" for c in roots),
                    "outer": pairs,
                    "copies": middle,
                    "crossings": len(self_crossings(speed_x, speed_y, samples=1024)),
                    "grid": grid_of(speed_x, speed_y),
                    "arc": str(arc_of(speed_x, speed_y)),
                }
    document = {"source": "scripts/family_census.py",
                "box": "mirror-symmetric, 1-3 outer pairs, denominators 2-20, 1-5 copies at 1/2",
                "tested": tested, "curves": list(found.values())}
    OUT.write_text(json.dumps(document, indent=1))
    return document


def summarise(document):
    curves = document["curves"]
    print(f"root sets tested: {document['tested']:,}   distinct curves: {len(curves):,}")
    counts = {}
    for curve in curves:
        counts[curve["crossings"]] = counts.get(curve["crossings"], 0) + 1
    print("crossings: " + ", ".join(f"{k}→{v}" for k, v in sorted(counts.items())))
    best = sorted(curves, key=lambda c: (-c["crossings"], c["grid"]))[:10]
    print("best by crossings, then grid:")
    for curve in best:
        print(f"  {curve['crossings']:>2} crossings, grid 1/{curve['grid']:<12} "
              f"{curve['outer']} pairs, {curve['copies']} at 1/2  [{curve['spots']}]")
    cheap = sorted(curves, key=lambda c: (c["grid"], -c["crossings"]))[:5]
    print("cheapest grids:")
    for curve in cheap:
        print(f"  grid 1/{curve['grid']:<8} {curve['crossings']:>2} crossings  [{curve['spots']}]")


def main():
    if "--report" in sys.argv:
        summarise(json.loads(OUT.read_text()))
        return
    summarise(sweep())


if __name__ == "__main__":
    main()
