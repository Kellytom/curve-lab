#!/usr/bin/env python3
"""Set a record's plate turn, for a uid range, and say exactly what moved.

    python scripts/set_turns.py c-0273:c-0328=-90 c-0333:c-0337=-45

The registry is the record the plate writer reads; the transform is the turn the desk stores.
The matrix is written as the maths rotation R(d) (counter-clockwise in model coordinates),
which is how the existing 45-degree rows are stored.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "workbench" / "curve-registry.json"

ROOT2 = "√2/2"


def matrix_for(degrees):
    d = int(degrees)
    if d % 360 == 0:
        return ([["1", "0"], ["0", "1"]], True)
    if d % 360 == -90 or d % 360 == 90 or d % 360 == 270:
        if d % 360 == -90:
            return ([["0", "1"], ["-1", "0"]], True)
        if d % 360 == 90:
            return ([["0", "-1"], ["1", "0"]], True)
        return ([["0", "1"], ["-1", "0"]], True)
    if d % 360 in (45, -45, 135, -135, 225, -225, 315, -315):
        # the four diagonals
        s = ROOT2
        if d % 360 == 45:
            return ([[s, f"-{s}"], [s, s]], False)
        if d % 360 == -45:
            return ([[s, s], [f"-{s}", s]], False)
        if d % 360 in (135, -225):
            return ([[f"-{s}", f"-{s}"], [s, f"-{s}"]], False)
        return ([[s, f"-{s}"], [f"-{s}", f"-{s}"]], False)
    raise SystemExit(f"no exact matrix is written for {d} degrees")


def main(argv):
    if not argv:
        raise SystemExit(__doc__)
    plan = []
    for spec in argv:
        rng, degrees = spec.split("=")
        start, end = rng.split(":")
        plan.append((start, end, int(degrees)))

    registry = json.loads(REGISTRY.read_text())
    changed = []
    for row in registry["curves"]:
        uid = row.get("uid", "")
        for start, end, degrees in plan:
            if start <= uid <= end:
                matrix, exact = matrix_for(degrees)
                if row.get("transform", {}).get("degrees") == degrees:
                    continue
                row["transform"] = {"degrees": degrees, "matrix": matrix, "exact": exact}
                changed.append((uid, degrees))
                break
    if not changed:
        print("nothing to change")
        return
    REGISTRY.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n")
    print(f"{len(changed)} curve(s) turned:")
    for uid, degrees in changed:
        print(f"  {uid}  {degrees}°")


if __name__ == "__main__":
    main(sys.argv[1:])
