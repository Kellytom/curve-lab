"""Every two-outer-pair family, measured: the list behind the page's section.

    .venv/bin/python scripts/related_families.py            # pairs (7 spots)
    .venv/bin/python scripts/related_families.py --three    # triples (9 spots)

A family is one outer flat spot or more, each with its mirror, plus three copies
at 1/2. The search used to test a handful of pairs by hand. This walks every pair
over denominators 2 to 20, counts the self-crossings at the same 1024 samples the
page uses, and prints them ranked by crossings and then by grid.

Measured 2026-11-16: 171 pairs, 119 with three crossings or more; 1/15 + 1/12 is
the cheapest nine (grid 1/182). Triples: 1,140 sets, up to fifteen crossings at
1/3 + 1/7 + 1/11, whose grid is 1/19,399,380.
"""

from __future__ import annotations

import itertools
import sys
from fractions import Fraction as F
from math import gcd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ph_root_search as R  # noqa: E402
from ph_crossings import self_crossings  # noqa: E402


def rows_for(roots):
    y = R.row_from_roots(roots)
    x = [1, 0, 0] + [0] * max(0, len(y) - 3)
    n = max(len(x), len(y))
    return (x + [0] * (n - len(x)))[:n], (y + [0] * (n - len(y)))[:n]


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


def measure(outer):
    roots = list(outer) + [F(1, 2)] * 3 + [1 - c for c in reversed(outer)]
    x, y = rows_for(roots)
    if not any(y):
        return None
    return {"outer": [str(c) for c in outer],
            "crossings": len(self_crossings(x, y, samples=1024)),
            "grid": grid_of(x, y)}


def main():
    three = "--three" in sys.argv
    pool = [F(1, d) for d in range(2, 21)]
    sets = []
    for combo in itertools.combinations_with_replacement(pool, 3 if three else 2):
        measured = measure(combo)
        if measured:
            sets.append(measured)
    sets.sort(key=lambda row: (-row["crossings"], row["grid"]))
    print(f"{len(sets)} sets; {sum(1 for s in sets if s['crossings'] >= 3)} with 3+ crossings")
    for row in sets[:20]:
        print(f"  {' + '.join(row['outer'])}: {row['crossings']:>2} crossings, grid 1/{row['grid']}")


if __name__ == "__main__":
    main()
