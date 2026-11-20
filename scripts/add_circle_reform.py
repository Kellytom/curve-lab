#!/usr/bin/env python3
"""Enter the circle-parameter reform of a stored curve as its own record.

    .venv/bin/python scripts/add_circle_reform.py            # report
    .venv/bin/python scripts/add_circle_reform.py --write    # append to the registry

The numbers come from `scripts/circle_split.py --write`, which puts the reformed
curve in `workbench/circle-split.json` under `reformed`. This script only moves that
record into `workbench/curve-registry.json`, the seed the database is built from;
then `app/scripts/add-registry-curves.mjs` upserts the curve and its set into SQLite.

The record is a path, not rows: `t = Y/(1+X)` re-stations the curve at exact rational
points of the circle, and the coordinates are no longer a polynomial in one variable.
The outline is unchanged — the reform is a re-stationing — and the note carries the
parameter and C so the link to the original curve is never guessed.

**A curated record, not a generator's output.** If `scripts/curve_registry.py` is run
again it rebuilds the registry from its own tables and loses this row; the uid it
adds is printed here so the loss would be visible rather than silent.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPLIT = ROOT / "workbench" / "circle-split.json"
REGISTRY = ROOT / "workbench" / "curve-registry.json"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    split = json.loads(SPLIT.read_text())
    reform = split.get("reformed")
    if not reform:
        print("no `reformed` row: run scripts/circle_split.py --write first")
        return 1
    record = reform["record"]
    note = record.get("note", "")
    if "t = Y/(1+X)" not in note or "C = " not in note:
        print("the record's note does not state the circle parameter and C")
        return 1

    registry = json.loads(REGISTRY.read_text())
    set_row = {
        "uid": f"set-{record['uid']}",
        "name": record["name"],
        "inner_uid": record["uid"],
        "border_uid": record["uid"],
        "rotation": 0,
        "pieces": 1,
        "perSide": 9,
        "importance": 0,
    }
    has_curve = any(row["uid"] == record["uid"] for row in registry["curves"])
    has_set = any(row["uid"] == set_row["uid"] for row in registry.get("sets", []))
    name_taken = any(row["name"] == record["name"] and row["uid"] != record["uid"]
                     for row in registry["curves"])

    print(f'{reform["way"]}: {record["uid"]} {record["name"]}')
    print(f'  from      {reform["from"]} {reform["fromName"]}')
    print(f'  parameter {reform["parameter"]}')
    print(f'  C         {reform["circularMean"]["fraction"]} ≈ '
          f'{reform["circularMean"]["decimal"]}')
    print(f'  stations  {reform["stations"]}, path points {reform["pathPoints"]}')

    if name_taken:
        print(f'a different record already owns the name {record["name"]}')
        return 1
    if has_curve and has_set:
        print("already in the registry; nothing to add")
        return 0
    if not args.write:
        print(f'would add {record["uid"]} and {set_row["uid"]} to '
              f'{REGISTRY.relative_to(ROOT)}')
        return 0

    if not has_curve:
        registry["curves"].append(record)
    if not has_set:
        registry.setdefault("sets", []).append(set_row)
    REGISTRY.write_text(json.dumps(registry, indent=2) + "\n")
    print(f'added {record["uid"]} and {set_row["uid"]}; registry now '
          f'{len(registry["curves"])} curves, {len(registry["sets"])} sets')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
