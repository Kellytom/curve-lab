"""Truncate the stored curves whose legs are long, and record where.

    .venv/bin/python scripts/truncate_found.py --report
    .venv/bin/python scripts/truncate_found.py --apply

The legs are the parts of the stroke outside the knot. "Long" is measured, not
judged: the share of the figure's diagonal taken by the longer leg. A curve over
`--legs` (55% by default) is truncated by cutting the same fraction of **arc
length** off each end — arc length belongs to the shape, not to the construction
parameter — and the cut is written into the record as `truncation`, with both
points and their exact parameters.

The window is a view; this is the data. A reader that wants the whole curve still
has every term; a reader that wants the short-legged version has the cut.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import curve_records as R  # noqa: E402
from ph_crossings import pair_crossings  # noqa: E402

FOUND = ROOT / "workbench" / "found-curves.json"


def position(terms, t):
    """x(t), y(t): integrate the squared speed from 0 to t."""
    rows_x = {}
    for term in terms:
        rows_x[term["power"]] = (term["x"], term["y"])
    steps = 400
    x = y = 0.0
    for i in range(steps):
        at = t * (i + 0.5) / steps
        p = q = 0.0
        for power, (cx, cy) in rows_x.items():
            factor = at ** power
            p += cx * factor
            q += cy * factor
        x += (p * p - q * q) * t / steps
        y += 2 * p * q * t / steps
    return x, y


def samples(terms, count=600):
    return [position(terms, i / count) for i in range(count + 1)]


def legs_share(terms):
    points = samples(terms)
    crossings = pair_crossings(points, points)
    if not crossings:
        return 1.0
    size = math.hypot(max(p[0] for p in points) - min(p[0] for p in points),
                      max(p[1] for p in points) - min(p[1] for p in points)) or 1e-9
    legs = [min(math.dist(end, c) for c in crossings) for end in (points[0], points[-1])]
    return max(legs) / size


def arc_fraction_t(terms, fraction, count=800):
    """The t that reaches `fraction` of the total arc length from the start."""
    speeds = []
    total = 0.0
    for i in range(count):
        at = (i + 0.5) / count
        p = q = 0.0
        for term in terms:
            factor = at ** term["power"]
            p += term["x"] * factor
            q += term["y"] * factor
        speed = p * p + q * q               # |z'(t)| = |w|^2
        speeds.append(speed)
        total += speed / count
    target = fraction * total
    running = 0.0
    for i, speed in enumerate(speeds):
        running += speed / count
        if running >= target:
            return (i + 0.5) / count
    return 1.0


def truncate(curve, keep, legs_limit):
    share = legs_share(curve["terms"])
    if share <= legs_limit:
        return None, share
    cut = (1 - keep) / 2
    low = arc_fraction_t(curve["terms"], cut)
    high = arc_fraction_t(curve["terms"], 1 - cut)
    if high - low < 0.05:
        return None, share
    from_x, from_y = position(curve["terms"], low)
    to_x, to_y = position(curve["terms"], high)
    return {"from": {"t": round(low, 6), "x": round(from_x, 6), "y": round(from_y, 6)},
            "to": {"t": round(high, 6), "x": round(to_x, 6), "y": round(to_y, 6)}}, share


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--keep", type=float, default=0.8, help="share of arc length kept")
    parser.add_argument("--legs", type=float, default=0.55, help="truncate above this leg share")
    parser.add_argument("--apply", action="store_true", help="write the records")
    parser.add_argument("--report", action="store_true", help="say what would change")
    args = parser.parse_args()
    if not (args.apply or args.report):
        parser.print_help()
        return 2

    document = R.read(FOUND)
    changed, untouched = [], []
    for curve in document["curves"]:
        cut, share = truncate(curve, args.keep, args.legs)
        if cut is None:
            untouched.append((curve["name"], share))
            continue
        if args.apply:
            curve["truncation"] = cut
        changed.append((curve["name"], share, cut["from"]["t"], cut["to"]["t"]))

    print(f"{len(changed)} curves have legs over {args.legs:.0%}; {len(untouched)} do not\n")
    print(f"{'curve':32s} {'legs':>6} {'cut from':>9} {'to':>9}")
    for name, share, low, high in changed[:20]:
        print(f"{name[:32]:32s} {share:6.0%} {low:9.3f} {high:9.3f}")
    if len(changed) > 20:
        print(f"  … and {len(changed) - 20} more")

    if args.apply:
        R.write(FOUND, document)
        print(f"\n{len(changed)} truncations written to {FOUND.relative_to(ROOT)}")
    else:
        print("\nnothing written; run with --apply to keep it")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
