"""Find curves by a count rather than by eye.

    .venv/bin/python scripts/ph_find.py --inflections
    .venv/bin/python scripts/ph_find.py --crossings
    .venv/bin/python scripts/ph_find.py --both --curves 4000

Two counts are cheap and mean something:

* inflections — roots of p q' - q p' inside (0, 1). The ceiling for a speed of
  degree k is 2k - 1, so a curve near the ceiling is using its top powers.
* crossings — where a curve meets its own flip across the origin. That is the
  double-knot pair the sandbox draws in grey.

Both are reported with the rows, so a result can be pasted straight in. The
search is random over small integers with a fixed seed, so a run can be repeated.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

try:                                   # numpy is only a fast screen
    import numpy as np
except ImportError:                    # the test runner has no numpy
    np = None

import ph_quintic_metrics as metrics  # noqa: E402
from ph_crossings import pair_crossings, spine  # noqa: E402


def fast_inflections(speed_x, speed_y) -> int:
    """Roots of the Wronskian in (0, 1), by polynomial roots rather than by
    sampling. Used only to screen candidates; the ones that are reported are
    measured again exactly with `metrics.inflections`."""
    if np is None:
        return len(metrics.inflections(speed_x, speed_y))
    # numpy reads coefficients highest power first; the rows are written lowest
    # power first, so both are reversed here
    p = np.array(speed_x[::-1], dtype=float)
    q = np.array(speed_y[::-1], dtype=float)
    wronskian = np.polysub(np.polymul(p, np.polyder(q)), np.polymul(q, np.polyder(p)))
    if not np.any(wronskian):
        return 0
    roots = np.roots(wronskian)
    real = roots[np.abs(roots.imag) < 1e-7].real
    return int(np.sum((real > 1e-6) & (real < 1 - 1e-6)))

SMALL = (-4, -3, -2, -1, 1, 2, 3, 4)
WIDE = (-6, -4, -3, -2, -1, 0, 1, 2, 3, 4, 6)


def random_rows(length: int) -> tuple[list, list]:
    return ([random.choice(SMALL)] + [random.choice(WIDE) for _ in range(length - 1)],
            [random.choice(WIDE) for _ in range(length)])


def flipped_across(points):
    """The pair the sandbox draws: the same curve mirrored in x."""
    return [(-x, y) for x, y in points]


def crossings_with_flip(speed_x, speed_y, samples: int = 500) -> int:
    _, x, y = spine(speed_x, speed_y, samples)
    points = list(zip(x, y))
    return len(pair_crossings(points, flipped_across(points)))


def search_inflections(curves: int, lengths=(4, 5, 6)) -> list:
    best = []
    for _ in range(curves):
        speed_x, speed_y = random_rows(random.choice(lengths))
        count = fast_inflections(speed_x, speed_y)
        if not count:
            continue
        measured = metrics.metrics(speed_x, speed_y)
        if measured["inflection_count"] != count:
            continue                     # the exact count disagrees; drop it
        share = count / measured["inflection_max"]
        best.append((share, count, measured["inflection_max"], speed_x, speed_y))
    best.sort(reverse=True)
    return best


def search_crossings(curves: int, lengths=(3, 4, 5)) -> list:
    best = []
    for _ in range(curves):
        speed_x, speed_y = random_rows(random.choice(lengths))
        count = crossings_with_flip(speed_x, speed_y)
        if count < 4:
            continue
        # verify at a finer sample count before it is offered
        if crossings_with_flip(speed_x, speed_y, samples=1200) != count:
            continue
        measured = metrics.metrics(speed_x, speed_y)
        best.append((count, speed_x, speed_y, measured))
    best.sort(key=lambda item: -item[0])
    return best


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inflections", action="store_true")
    parser.add_argument("--crossings", action="store_true")
    parser.add_argument("--both", action="store_true")
    parser.add_argument("--curves", type=int, default=2500)
    parser.add_argument("--seed", type=int, default=11)
    args = parser.parse_args()
    if not (args.inflections or args.crossings or args.both):
        parser.print_help()
        return
    random.seed(args.seed)

    if args.inflections or args.both:
        found = search_inflections(args.curves)
        print(f"\nmost inflections for its degree ({len(found)} with any)")
        for share, count, ceiling, speed_x, speed_y in found[:6]:
            print(f"  {count} of {ceiling}  x {speed_x}  y {speed_y}")
        if found:
            share, count, ceiling, speed_x, speed_y = found[0]
            print("  json:", json.dumps({"name": f"inflect-{count}", "speedX": speed_x,
                                         "speedY": speed_y}))

    if args.crossings or args.both:
        found = search_crossings(args.curves)
        print(f"\nmost crossings with its own flip ({len(found)} with four or more)")
        for count, speed_x, speed_y, measured in found[:6]:
            print(f"  {count} crossings  x {speed_x}  y {speed_y}"
                  f"  bend {measured['bend']:.3f}  pitch {measured['pitch']}")
        if found:
            count, speed_x, speed_y, measured = found[0]
            print("  json:", json.dumps({"name": f"knot-{count}", "speedX": speed_x,
                                         "speedY": speed_y}))


if __name__ == "__main__":
    main()
