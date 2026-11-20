#!/usr/bin/env python3
"""Reserve the conversion slot on every registry record.

    .venv/bin/python scripts/reserve_conversion.py            # report
    .venv/bin/python scripts/reserve_conversion.py --write

The collection has several algorithms — polynomial speed rows, sampled paths, the prime
mover's walk, the hybrid rational curve. They will be re-expressed in the rational form
eventually, so every record carries the space now:

    conversion: {
      algorithm,     what the curve is today (rows, path, prime-mover, hybrid)
      status,        native | pending | converted
      target,        the form they are heading to
      formulaNext    null until the improved formula exists
    }

A null is a deliberate placeholder, not missing data: it says the question was asked and
the answer is not written yet. Nothing else in the record changes.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "workbench" / "curve-registry.json"
TARGET = "x = C(t)^p, y = S(t)^q; C = (1 - t^2)/(1 + t^2), S = 2t/(1 + t^2)"

# A finished hybrid is usually turned 45° or 90° for the page. The matrix is the record of
# that turn: 90° is a quarter turn and exact (0, −1, 1, 0); 45° is display only, because
# cos 45° = √2/2 is irrational and no exact integer matrix can express it.
IDENTITY = {"degrees": 0, "matrix": [[1, 0], [0, 1]], "exact": True}
TURNS = {
    0: {"degrees": 0, "matrix": [[1, 0], [0, 1]], "exact": True},
    90: {"degrees": 90, "matrix": [[0, -1], [1, 0]], "exact": True},
    180: {"degrees": 180, "matrix": [[-1, 0], [0, -1]], "exact": True},
    270: {"degrees": 270, "matrix": [[0, 1], [-1, 0]], "exact": True},
    45: {"degrees": 45, "matrix": [["√2/2", "-√2/2"], ["√2/2", "√2/2"]], "exact": False},
}


def algorithm_of(record):
    family = (record.get("family") or record.get("family_id") or "").lower()
    if family == "hybrid":
        return "hybrid"
    if family in ("walker", "lens", "four-fold"):
        return "prime-mover"
    kind = record.get("kind")
    if kind == "path":
        return "path"
    return "rows"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    registry = json.loads(REGISTRY.read_text())
    added = 0
    for record in registry["curves"]:
        if "conversion" in record:
            continue
        algorithm = algorithm_of(record)
        record["transform"] = dict(IDENTITY)
        record["conversion"] = {
            "algorithm": algorithm,
            "status": "native" if algorithm == "hybrid" else "pending",
            "target": TARGET,
            "formulaNext": None,
        }
        added += 1

    missing = [row["uid"] for row in registry["curves"] if "transform" not in row]
    for record in registry["curves"]:
        if "transform" not in record:
            record["transform"] = dict(IDENTITY)

    print(f"{added} records gained the conversion slot; "
          f"{len(registry['curves'])} records in all")
    if not args.write:
        print("report only; --write appends the placeholder to every record")
        return 0
    REGISTRY.write_text(json.dumps(registry, indent=2) + "\n")
    print("written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
