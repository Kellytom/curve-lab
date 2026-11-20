#!/usr/bin/env python3
"""Promote every saved desk row into a registry record.

    .venv/bin/python scripts/promote_saved.py            # report
    .venv/bin/python scripts/promote_saved.py --write    # append to the registry

A "saved" row in `data/sandbox-curves.json` becomes a record with everything the row
carries: the name, the stars as `importance`, the kind (hybrid / piece / double), the parent,
the cut points, the ends, the formulas, the note, and the drawn path.

The geometry comes from `workbench/hybrids.json`, `wonkies.json` and `doubles.json` by id, so
a record cannot be made for a curve that is no longer in the data.

Then: `app/scripts/add-registry-curves.mjs` puts it in SQLite and
`node scripts/curve_pngs.mjs --only <uid>` draws it.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "workbench" / "curve-registry.json"
DECISIONS = ROOT / "data" / "sandbox-curves.json"
SOURCES = [ROOT / "workbench" / name for name in ("hybrids.json", "wonkies.json", "doubles.json")]
TARGET = "x = C(t)^p, y = S(t)^q; C = (1 - t^2)/(1 + t^2), S = 2t/(1 + t^2)"


def safe_name(name):
    """a name is a path component: no slash, no spaces, lower case, hyphenated."""
    name = re.sub(r"(\d+)\s*/\s*(\d+)", r"\1of\2", name)
    name = name.lower().replace("_", "-").replace(" ", "-")
    name = re.sub(r"[^a-z0-9.-]+", "-", name).strip("-")
    return re.sub(r"-+", "-", name)


def geometry():
    """every candidate on the pages, by id."""
    out = {}
    for path in SOURCES:
        if not path.exists():
            continue
        data = json.loads(path.read_text())
        for key in ("candidates", "wonkies", "doubles"):
            for row in data.get(key, []):
                out[row["id"]] = row
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    decisions = json.loads(DECISIONS.read_text()).get("rows", [])
    by_id = geometry()
    registry = json.loads(REGISTRY.read_text())
    names = {row["name"] for row in registry["curves"]}
    next_number = 1
    for row in registry["curves"]:
        if row["uid"].startswith("c-"):
            next_number = max(next_number, int(row["uid"][2:]) + 1)

    added, skipped = [], []
    for row in sorted(decisions, key=lambda item: item["name"]):
        if row.get("decision") != "saved":
            continue
        candidate = by_id.get(row["name"])
        if candidate is None:
            skipped.append((row["name"], "no geometry with that id"))
            continue
        chosen = safe_name((row.get("curveName") or "").strip() or row["name"])
        if chosen in names:
            skipped.append((row["name"], f"name {chosen} already in the registry"))
            continue
        kind = candidate.get("kind") or ("double" if row["name"].startswith("double-") else "hybrid")
        formula = candidate.get("formula") or {}
        construction = row.get("construction") or {}
        note = (construction.get("note") or formula.get("use") or formula.get("plain") or "")[:900]
        record = {
            "uid": f"c-{next_number:04d}",
            "name": chosen,
            "aliases": [row["name"]],
            "speedX": [],
            "speedY": [],
            "step": 1,
            "lists": ["found", "hybrid", kind],
            "family": "hybrid",
            "source": "new",
            "auto_named": False,
            "family_id": "hybrid",
            "variant": chosen,
            "kind": "path",
            "starred": bool(row.get("importance")),
            "candidate": False,
            "importance": int(row.get("importance") or 0),
            "base_uid": None,
            "rotation": 0, "pieces": 1, "borderUid": None, "perSide": 9, "borderTurn": 0,
            "offsets": 0, "widthPct": 0, "plus": 0, "minus": 0, "profile": None,
            "params": {
                "kind": kind,
                "parent": candidate.get("parent") or None,
                "parentName": candidate.get("parentName") or None,
                "half": candidate.get("half") or None,
                "p": candidate.get("p"), "q": candidate.get("q"),
                "use": candidate.get("use"), "block": candidate.get("block"),
                "cuts": construction.get("cuts") or candidate.get("cuts") or [],
                "ends": construction.get("ends")
                        or [candidate["points"][0], candidate["points"][-1]],
                "crossings": candidate.get("crossings"),
            },
            "formula": formula,
            "transform": {"degrees": 0, "matrix": [[1, 0], [0, 1]], "exact": True},
            "conversion": {"algorithm": kind, "status": "native", "target": TARGET,
                           "formulaNext": None},
            "note": note,
            "path": [[round(x, 6), round(y, 6)] for x, y in candidate.get("points", [])],
        }
        added.append(record)
        names.add(chosen)
        next_number += 1

    print(f"{len(added)} to add, {len(skipped)} skipped")
    for name, why in skipped[:10]:
        print(f"  {name}: {why}")
    if not args.write or not added:
        return 0

    for record in added:
        registry["curves"].append(record)
        registry.setdefault("sets", []).append({
            "uid": f"set-{record['uid']}", "name": record["name"],
            "inner_uid": record["uid"], "border_uid": record["uid"],
            "rotation": 0, "pieces": 1, "perSide": 9,
            "importance": record["importance"],
        })
    REGISTRY.write_text(json.dumps(registry, indent=2) + "\n")
    print(f"registry now {len(registry['curves'])} curves, {len(registry['sets'])} sets")
    print("first uids:", ", ".join(r["uid"] for r in added[:6]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
