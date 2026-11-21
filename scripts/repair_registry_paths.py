#!/usr/bin/env python3
"""Repair the registry's path records that were rounded into a staircase.

    .venv/bin/python scripts/repair_registry_paths.py          # report
    .venv/bin/python scripts/repair_registry_paths.py --write  # repair

The finder stores a sampled outline at six decimals. The registry copied it with
`round(px, 2)`, which is coarser than the step between samples on a curve of size 1-3:
the outline became a run of axis-aligned steps. `c-0143` (y = x^2 as a t^2 cover) is the
plain case — it draws as a staircase, not a parabola.

The registry keeps the 2-decimal rounding for *identity* (two paths merge only when every
rounded sample agrees). It must not keep it for the drawing. This script matches each
polyline record to its source by that identity and writes the source outline back at six
decimals. Nothing else in a record changes.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "workbench" / "curve-registry.json"
BACKUP = ROOT / "state" / "backups" / "curve-registry.before-paths.json"
SOURCES = (ROOT / "workbench" / "finder.json", ROOT / "workbench" / "real-curves.json")


def shape(path):
    return tuple((round(float(x), 2), round(float(y), 2)) for x, y in path)


def source_paths():
    """every sampled outline in the finder data, by its rounded shape."""
    out = {}
    for file in SOURCES:
        if not file.exists():
            continue
        data = json.loads(file.read_text(encoding="utf-8"))
        for item in data.get("curves", []):
            path = item.get("path")
            if not path or item.get("speedX") or item.get("speedY"):
                continue
            out.setdefault(shape(path), (item.get("name") or item.get("id"), path))
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    by_shape = source_paths()
    changed, missed = [], []
    for record in registry["curves"]:
        if record.get("kind") != "polyline" or not record.get("path"):
            continue
        found = by_shape.get(shape(record["path"]))
        if not found or len(found[1]) != len(record["path"]):
            missed.append(record["uid"])
            continue
        name, source = found
        worst = max((max(abs(float(a[0]) - float(b[0])), abs(float(a[1]) - float(b[1])))
                     for a, b in zip(record["path"], source)), default=0.0)
        if worst <= 1e-6:
            continue
        changed.append((record["uid"], record["name"], worst))
        record["path"] = [[round(float(x), 6), round(float(y), 6)] for x, y in source]

    print(f"{len(changed)} path records to repair, {len(missed)} without a source match")
    for uid, name, worst in changed[:12]:
        print(f"  {uid} {name[:42]:42} worst stored miss {worst:.4f}")
    if missed:
        print("  no match:", ", ".join(missed[:8]))
    if not args.write or not changed:
        return 0

    BACKUP.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(REGISTRY, BACKUP)
    REGISTRY.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    print(f"registry written; previous copy at {BACKUP.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
