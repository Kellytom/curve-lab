"""Recompute every stored curve's self-crossings, and say what disagrees.

    .venv/bin/python scripts/crossing_audit.py            # report
    .venv/bin/python scripts/crossing_audit.py --write    # put the count in the records
    .venv/bin/python scripts/crossing_audit.py --samples 4000

What the number means, and what it does not. A *crossing pair* is two parameters
`t1 < t2` where the stroke passes through the same place; a triple point three
parameters meet at gives three pairs, not one. That is the number the galleries
sort by and the page prints, and it is scale-free: it does not depend on how
large the curve is drawn. It is **not** the number of distinct places the stroke
meets itself — three passes through one point count as three pairs. When the two
numbers are wanted, say "crossing pairs" for this one and "meeting points" for
the other; do not call both "crossings".

Measured 2026-11-16: `lace-1of10-1of5-3` holds 4 in its record and has 5 pairs
(three passes meet at one place, which is 3 of the 5). Fourteen folder records
and forty-two found records held a number no version of the router produces at
1024 samples, so they are the ones this script rewrites.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from ph_crossings import self_crossings  # noqa: E402

FOUND = ROOT / "workbench" / "found-curves.json"
MOVED = ROOT / "workbench" / "moved-curves.json"
CURVES = ROOT / "curves"
SAMPLES = 1024


def terms_to_rows(terms):
    length = max(int(term["power"]) for term in terms) + 1
    speed_x = [0.0] * length
    speed_y = [0.0] * length
    for term in terms:
        speed_x[int(term["power"])] = float(term["x"])
        speed_y[int(term["power"])] = float(term["y"])
    return speed_x, speed_y


def pairs(speed_x, speed_y, samples=SAMPLES):
    return len(self_crossings(speed_x, speed_y, samples=samples))


def audit(samples=SAMPLES):
    """(name, stored, measured, path) for every record that disagrees."""
    problems = []
    for path in sorted(CURVES.glob("*/curve.json")):
        record = json.loads(path.read_text())
        measured = pairs(record["speedX"], record["speedY"], samples)
        if record.get("crossings") != measured:
            problems.append((record["name"], record.get("crossings"), measured, path))
    for path in (FOUND, MOVED):
        if not path.exists():
            continue
        document = json.loads(path.read_text())
        for curve in document.get("curves", []):
            speed_x, speed_y = terms_to_rows(curve["terms"])
            measured = pairs(speed_x, speed_y, samples)
            if curve.get("measured", {}).get("self") != measured:
                problems.append((curve["name"], curve.get("measured", {}).get("self"), measured, path))
    return problems


def write(problems):
    """Set the measured count on each record that disagrees."""
    by_path = {}
    for name, was, measured, path in problems:
        by_path.setdefault(path, []).append((name, measured))
    for path, fixes in by_path.items():
        document = json.loads(path.read_text())
        if path.parent.parent.name == "curves" or path.name == "curve.json":
            record = document
            record["crossings"] = fixes[0][1]
            path.write_text(json.dumps(record, indent=1) + "\n")
            continue
        by_name = {name: measured for name, measured in fixes}
        for curve in document.get("curves", []):
            if curve.get("name") in by_name:
                curve.setdefault("measured", {})["self"] = by_name[curve["name"]]
        path.write_text(json.dumps(document, indent=1) + "\n")
    return len(by_path)


def main(argv):
    samples = SAMPLES
    if "--samples" in argv:
        samples = int(argv[argv.index("--samples") + 1])
    problems = audit(samples)
    print(f"{len(problems)} records disagree at {samples} samples")
    for name, was, measured, path in problems:
        print(f"  {name:30s} record {was} -> {measured}   ({path.relative_to(ROOT)})")
    if not problems:
        return 0
    if "--write" in argv:
        touched = write(problems)
        print(f"rewrote {len(problems)} counts in {touched} file(s)")
        return 0
    print("run with --write to put the measured count in the records")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
