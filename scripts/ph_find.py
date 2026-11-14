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
FOUND = ROOT / "workbench" / "found-curves.json"
sys.path.insert(0, str(ROOT / "scripts"))

import numpy as np  # noqa: E402

import ph_quintic_metrics as metrics  # noqa: E402
from ph_crossings import pair_crossings, spine  # noqa: E402


def fast_inflections(speed_x, speed_y) -> int:
    """Roots of the Wronskian in (0, 1), by polynomial roots rather than by
    sampling. Used only to screen candidates; the ones that are reported are
    measured again exactly with `metrics.inflections`."""
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


def total_turn(speed_x, speed_y) -> float:
    """How far the tangent swings from start to end, in degrees.

    The tangent is w squared, so its angle is twice the angle of w: the turn is
    twice the change in direction of the speed.
    """
    def angle(row, t):
        value = sum(c * t ** k for k, c in enumerate(row))
        return value
    p0, q0 = angle(speed_x, 0.0), angle(speed_y, 0.0)
    p1, q1 = angle(speed_x, 1.0), angle(speed_y, 1.0)
    start = math.atan2(q0, p0)
    end = math.atan2(q1, p1)
    return abs(math.degrees(2 * (end - start)))


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


def search_crossings(curves: int, lengths=(3, 4, 5), max_turn: float = 400.0,
                     min_crossings: int = 4) -> list:
    best = []
    for _ in range(curves):
        speed_x, speed_y = random_rows(random.choice(lengths))
        if max_turn < 400.0 and total_turn(speed_x, speed_y) > max_turn:
            continue
        count = crossings_with_flip(speed_x, speed_y)
        if count < min_crossings:
            continue
        # verify at a finer sample count before it is offered
        if crossings_with_flip(speed_x, speed_y, samples=1200) != count:
            continue
        measured = metrics.metrics(speed_x, speed_y)
        best.append((count, speed_x, speed_y, measured))
    best.sort(key=lambda item: -item[0])
    return best


def record(name, speed_x, speed_y, measured):
    """One entry in the shape the gallery reads."""
    return {
        "name": name,
        "speedX": [float(v) for v in speed_x],
        "speedY": [float(v) for v in speed_y],
        "bend": round(measured["bend"], 3),
        "pitch": measured["pitch"],
        "inflections": measured["inflection_count"],
        "from": "found",
    }


def write_found(entries):
    """Append to workbench/found-curves.json, skipping rows already there."""
    if FOUND.exists():
        try:
            document = json.loads(FOUND.read_text())
        except json.JSONDecodeError:
            document = {"name": "found-curves", "curves": []}
    else:
        document = {"name": "found-curves", "curves": []}
    known = {(tuple(c["speedX"]), tuple(c["speedY"])) for c in document["curves"]}
    added = 0
    for entry in entries:
        key = (tuple(entry["speedX"]), tuple(entry["speedY"]))
        if key in known:
            continue
        known.add(key)
        document["curves"].append(entry)
        added += 1
    document["note"] = ("written by scripts/ph_find.py --write; the gallery reads "
                        "this file as a second seed source")
    FOUND.write_text(json.dumps(document, indent=1) + "\n")
    print(f"{FOUND.relative_to(ROOT)}  {added} new, {len(document['curves'])} in all")
    return document


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inflections", action="store_true")
    parser.add_argument("--crossings", action="store_true")
    parser.add_argument("--both", action="store_true")
    parser.add_argument("--curves", type=int, default=2500)
    parser.add_argument("--min-crossings", type=int, default=4)
    parser.add_argument("--max-turn", type=float, default=400.0,
                        help="keep only curves whose tangent turns no more than this")
    parser.add_argument("--seed", type=int, default=11)
    parser.add_argument("--write", action="store_true",
                        help="append the finds to workbench/found-curves.json")
    args = parser.parse_args()
    if not (args.inflections or args.crossings or args.both):
        parser.print_help()
        return
    random.seed(args.seed)

    collected = []

    if args.inflections or args.both:
        found = search_inflections(args.curves)
        print(f"\nmost inflections for its degree ({len(found)} with any)")
        for share, count, ceiling, speed_x, speed_y in found[:6]:
            print(f"  {count} of {ceiling}  x {speed_x}  y {speed_y}")
        if found:
            for share, count, ceiling, speed_x, speed_y in found[:3]:
                measured = metrics.metrics(speed_x, speed_y)
                collected.append(record(f"found-inflect-{count}", speed_x, speed_y, measured))
            share, count, ceiling, speed_x, speed_y = found[0]
            print("  json:", json.dumps({"name": f"inflect-{count}", "speedX": speed_x,
                                         "speedY": speed_y}))

    if args.crossings or args.both:
        found = search_crossings(args.curves, max_turn=args.max_turn,
                                 min_crossings=args.min_crossings)
        print(f"\nmost crossings with its own flip ({len(found)} with four or more)")
        for count, speed_x, speed_y, measured in found[:8]:
            print(f"  {count} crossings  turn {total_turn(speed_x, speed_y):5.1f}"
                  f"  x {speed_x}  y {speed_y}"
                  f"  bend {measured['bend']:.3f}  pitch {measured['pitch']}")
        if found:
            for count, speed_x, speed_y, measured in found[:3]:
                collected.append(record(f"found-knot-{count}", speed_x, speed_y, measured))
            count, speed_x, speed_y, measured = found[0]
            print("  json:", json.dumps({"name": f"knot-{count}", "speedX": speed_x,
                                         "speedY": speed_y}))

    if args.write and collected:
        write_found(collected)


if __name__ == "__main__":
    main()
