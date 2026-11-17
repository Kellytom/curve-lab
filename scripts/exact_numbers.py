"""Audit every stored curve's numbers against the exact core.

    .venv/bin/python scripts/exact_numbers.py           # report, exit 1 on a mismatch
    .venv/bin/python scripts/exact_numbers.py --write   # rewrite the wrong numbers

Where a record's numbers come from today is not one place: `found-curves.json`
carries `measured.grid` and `measured.bend`, a `curves/<slug>/curve.json`
carries `grid` and `bend`, and both were written by different scripts on
different days. This script asks `curve_lab/measure.py` — the one exact
reference — and reports any record that disagrees, so a wrong number is caught
by a command instead of by the operator noticing a curve looks different.

The numbers are compared as integers for the grid and to three places for the
bend, which is the precision the pages print. Nothing is rewritten unless
`--write` is given.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab import measure  # noqa: E402

FOUND = ROOT / "workbench" / "found-curves.json"
CURVEDIR = ROOT / "curves"


def found_rows():
    """(name, speed_x, speed_y, grid, bend, path) for every gallery curve."""
    if not FOUND.exists():
        return
    document = json.loads(FOUND.read_text())
    for curve in document.get("curves", []):
        speed_x, speed_y = measure.speeds_from_terms(curve.get("terms") or [])
        measured = curve.get("measured") or {}
        yield (
            curve.get("name", "?"),
            speed_x,
            speed_y,
            measured.get("grid"),
            measured.get("bend"),
            FOUND,
            curve,
        )


def folder_rows():
    """(name, speed_x, speed_y, grid, bend, path) for every curve folder."""
    for path in sorted(CURVEDIR.glob("*/curve.json")):
        record = json.loads(path.read_text())
        speed_x = record.get("speedX")
        speed_y = record.get("speedY")
        if not speed_x or not speed_y:
            continue
        yield (
            record.get("name", path.parent.name),
            speed_x,
            speed_y,
            record.get("grid"),
            record.get("bend"),
            path,
            record,
        )


def audit():
    """Every disagreement, as (name, what, record number, exact number, path)."""
    problems = []
    rows = list(found_rows()) + list(folder_rows())
    for name, speed_x, speed_y, stored_grid, stored_bend, path, record in rows:
        exact_grid = measure.grid(speed_x, speed_y)
        if stored_grid is not None and int(stored_grid) != exact_grid:
            problems.append((name, "grid", int(stored_grid), exact_grid, path, record))
        if stored_bend is not None:
            exact_bend = measure.bend(speed_x, speed_y)
            if abs(float(stored_bend) - exact_bend) > 0.0005:
                problems.append(
                    (name, "bend", float(stored_bend), round(exact_bend, 6), path, record)
                )
    return rows, problems


def write_fixes(problems):
    """Put the exact number into each record that disagrees."""
    touched = set()
    for name, what, was, exact, path, record in problems:
        if str(path) == str(FOUND):
            if record.get("measured") is None:
                record["measured"] = {}
            record["measured"][what] = exact
        else:
            record[what] = exact
        touched.add(path)
    for path in touched:
        if str(path) == str(FOUND):
            document = json.loads(FOUND.read_text())
            by_name = {c.get("name"): c for c in document.get("curves", [])}
            for name, what, was, exact, path2, record in problems:
                if str(path2) == str(FOUND):
                    by_name[name].setdefault("measured", {})[what] = exact
            path.write_text(json.dumps(document, indent=2) + "\n")
        else:
            data = json.loads(path.read_text())
            for name, what, was, exact, path2, record in problems:
                if path2 == path:
                    data[what] = exact
            path.write_text(json.dumps(data, indent=2) + "\n")
    return touched


def main(argv):
    rows, problems = audit()
    print(f"{len(rows)} stored curves checked against curve_lab/measure.py")
    for name, what, was, exact, path, record in problems:
        print(f"  {name:28s} {what:5s} record {was} -> exact {exact}   ({path.relative_to(ROOT)})")
    if not problems:
        print("every grid and bend agrees with the exact core")
        return 0
    if "--write" in argv:
        touched = write_fixes(problems)
        print(f"rewrote {len(problems)} number(s) in {len(touched)} file(s)")
        return 0
    print("run with --write to replace the record's number with the exact one")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
