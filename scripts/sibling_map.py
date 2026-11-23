#!/usr/bin/env python3
"""The sibling map: a nearby recipe at the ceiling for every over-ceiling curve.

    .venv/bin/python scripts/sibling_map.py            # sweep, rank, write
    .venv/bin/python scripts/sibling_map.py --uid c-0055

Every stored family curve is a PH curve with u fixed (mostly [1, 0, …] or
1 − 2t + 2t²) and v a PRODUCT OF LINEAR ROOTS: mirrored pairs (r, 1 − r)
and a repeated stack at 1/2. The name encodes the roots. So a sibling at the
degree ceiling is found without guessing recipes, by reading the curve back:

    1. factor v numerically and rationalise its roots (r, 1 − r, 1/2 repeated);
    2. rebuild a v-row from a SUBSET of those roots — the same construction
       with a shorter stack, the mirrored pairs kept entire (a pair is one
       idea, half a pair is not);
    3. score the candidate against the original with the exact station miss
       (reduction/speed_fit.py), in curve units;
    4. keep the best candidate whose speed degree ≤ 5 (position 11, rails 9).

The output says, per curve, either a sibling recipe with its miss in curve
units, or that no recipe in this family reaches the ceiling — never a
percentage. Existing stored curves whose rows match a candidate exactly are
named as in-catalogue siblings.
"""

from __future__ import annotations

import json
import math
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402

from curve_lab.datafile import FORMATS  # noqa: E402
from curve_lab.measure import to_fraction  # noqa: E402
from reduction import speed_fit  # noqa: E402

OUT = ROOT / "workbench" / "sibling-map.json"
CEILING_SPEED = 5          # speed degree; position 11, rails 9
DENOMINATORS = (2, 3, 4, 5, 6, 8, 10, 12, 16)  # where the family's roots live
TOLERANCE = Fraction(1, 50)  # a root this close to a small fraction is that fraction


def trim(row):
    row = list(row)
    while row and row[-1] == 0:
        row.pop()
    return row


def speed_degree(row):
    return len(trim(row)) - 1


def rationalise(root):
    """The small-denominator fraction nearest a real root, or None."""
    best = None
    for d in DENOMINATORS:
        n = round(root * d)
        if n <= 0 or n >= d:  # the family's roots live strictly inside (0, 1)
            continue
        candidate = Fraction(int(n), d)
        if best is None or abs(root - float(candidate)) < abs(root - float(best)):
            best = candidate
    if best is None or abs(root - float(best)) > float(TOLERANCE):
        return None
    return best


def factor_row(v):
    """v as a root multiset: [(root, count)], or None when it is not a
    product of real rational roots."""
    coeffs = [float(c) for c in v]
    while coeffs and coeffs[-1] == 0:
        coeffs.pop()
    roots = np.roots(coeffs[::-1]) if len(coeffs) > 1 else []
    out = []
    for r in roots:
        # repeated roots come back from the numerical factorisation as small
        # complex pairs; the family's roots are real, so snap them
        if abs(r.imag) > 0.02:
            return None
        q = rationalise(r.real)
        if q is None:
            return None
        out.append(q)
    return out


def row_from_roots(roots):
    """Integer v-row from rational linear roots, the family's normal form."""
    poly = [Fraction(1)]
    for r in roots:
        poly = _mul(poly, [-r, Fraction(1)])
    factor = 1
    for c in poly:
        factor = factor * c.denominator // math.gcd(factor, c.denominator)
    ints = [int(c * factor) for c in poly]
    common = 0
    for c in ints:
        common = math.gcd(common, abs(c))
    return [c // (common or 1) for c in ints]


def _mul(a, b):
    out = [Fraction(0)] * (len(a) + len(b) - 1)
    for i, ca in enumerate(a):
        for j, cb in enumerate(b):
            out[i + j] += ca * cb
    return out


def pairs_of(roots):
    """Group the roots: mirrored pairs (r, 1 − r) whole, the 1/2 stack as a
    count. Returns (pair_roots, stack_count) — halves never travel alone."""
    half = [r for r in roots if r == Fraction(1, 2)]
    rest = [r for r in roots if r != Fraction(1, 2)]
    pairs = []
    while rest:
        r = rest.pop(0)
        mirror = 1 - r
        if mirror in rest:
            rest.remove(mirror)
            pairs.append((r, mirror))
        else:
            return None  # an unpaired root: not this family's construction
    return pairs, len(half)


def candidates_from(roots):
    """The sibling candidates: pairs kept whole, the stack shortened by
    0, 1, 2 … roots, down to the ceiling."""
    grouped = pairs_of(roots)
    if grouped is None:
        return []
    pairs, stack = grouped
    flat = [r for pair in pairs for r in pair]
    out = []
    for keep in range(stack, -1, -1):
        row = row_from_roots(flat + [Fraction(1, 2)] * keep)
        if len(row) - 1 <= CEILING_SPEED:
            out.append((flat + [Fraction(1, 2)] * keep, keep))
    return out


def name_of(roots):
    parts = []
    i = 0
    while i < len(roots):
        r = roots[i]
        if r == Fraction(1, 2) and i == len(roots) - 1:
            parts.append("mid")
            i += 1
            continue
        if i + 1 < len(roots) and roots[i + 1] == 1 - r:
            parts.append(f"1of{int(1 / r)}" if r.numerator == 1 else f"{r.numerator}of{r.denominator}")
            i += 2
        else:
            parts.append(str(r))
            i += 1
    return "-".join(parts)


def rows_of(record):
    return ([to_fraction(v) for v in record["speedX"]],
            [to_fraction(v) for v in record["speedY"]])


def main(argv):
    registry = json.load(open(ROOT / "workbench" / "curve-registry.json"))
    only = None
    if "--uid" in argv:
        only = argv[argv.index("--uid") + 1]
    by_rows = {}
    for record in registry["curves"]:
        if record.get("speedX"):
            u, v = rows_of(record)
            by_rows[(tuple(map(str, trim(u))), tuple(map(str, trim(v))))] = record

    rows = []
    for record in registry["curves"]:
        if not record.get("speedX") or (only and record["uid"] != only):
            continue
        u, v = rows_of(record)
        speed = max(speed_degree(u), speed_degree(v))
        if speed <= CEILING_SPEED:
            continue
        entry = {"uid": record["uid"], "name": record["name"],
                 "speed_degree": speed, "position_degree": 2 * speed + 1,
                 "rails": 2 * speed - 1}
        if speed_degree(u) > CEILING_SPEED:
            entry["verdict"] = "u itself is over the ceiling — not this family's sibling"
            rows.append(entry)
            continue
        factored = factor_row(v)
        if factored is None:
            entry["verdict"] = "v does not factor into rational roots — no recipe found"
            rows.append(entry)
            continue
        best = None
        x, y = speed_fit.position_of_rows(u, [Fraction(c) for c in v])
        for roots, keep in candidates_from(factored):
            row = row_from_roots(roots)
            cx, cy = speed_fit.position_of_rows(u, [Fraction(c) for c in row])
            miss = speed_fit.station_miss(x, y, cx, cy)
            if best is None or miss < best[0]:
                existing = by_rows.get((tuple(map(str, trim(u))),
                                        tuple(map(str, trim(row)))))
                best = (miss, roots, row, existing["name"] if existing else None)
        if best is None:
            entry["verdict"] = "no candidate reaches the ceiling"
        else:
            miss, roots, row, sibling = best
            entry.update({
                "sibling_roots": name_of(roots),
                "sibling_v": [str(c) for c in row],
                "sibling_speed_degree": speed_degree(row),
                "sibling_position_degree": 2 * speed_degree(row) + 1,
                "miss_units": round(miss, 6),
                "in_catalogue": sibling,
                "verdict": ("an in-catalogue sibling exists" if sibling else
                            "a sibling recipe is found by shortening the stack"),
            })
        rows.append(entry)

    rows.sort(key=lambda e: (e.get("miss_units") is None, e.get("miss_units", 0)))
    out = ROOT / "workbench" / "sibling-map.json"
    out.write_text(json.dumps({"format": FORMATS["sibling-map.json"], "curves": rows},
                              indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    for entry in rows:
        detail = (f"miss {entry['miss_units']:12.4f} units · {entry.get('sibling_roots', '')}"
                  if "miss_units" in entry else entry.get("verdict", ""))
        print(f"{entry['uid']} {entry['name'][:26]:26s} speed {entry['speed_degree']:2d}  {detail}")
    print(f"\nwrote {out.relative_to(ROOT)} with {len(rows)} curves")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
