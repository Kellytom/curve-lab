#!/usr/bin/env python3
"""Add the new looped integer Béziers (and one mobile) to the registry.

    .venv/bin/python scripts/add_found_curves.py            # report
    .venv/bin/python scripts/add_found_curves.py --write

The registry is the seed the database is built from, so a curve enters the
collection here first: a record with the same shape as the others (speed rows in
the power basis, lists, family, a name), then `app/scripts/add-registry-curves.mjs`
upserts it into SQLite.

The named curves are the ones the operator called good: the looped integer
Béziers from `scripts/bezier_knots.py`, starred and important, plus the symmetric
mobile at k = 3/1.

**These are curated finds, not a generator's output.** If `scripts/curve_registry.py`
is ever run again it will rebuild the registry from its own tables and lose these
rows; the docstring there says so, and this script prints the uids it adds so the
loss is visible rather than silent.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "workbench" / "curve-registry.json"
BEZIERS = ROOT / "workbench" / "bezier-knots.json"
MOBILES = ROOT / "workbench" / "mobile-curves.json"

SEED = 0x8db86b7d79643feb      # the same owner mark the other records carry


def binom(n, k):
    return math.comb(n, k)


def bernstein_to_power(controls):
    """Control points -> power-basis coefficients, per axis."""
    n = len(controls) - 1
    x = [0] * (n + 1)
    y = [0] * (n + 1)
    for i, (cx, cy) in enumerate(controls):
        row = [((-1) ** (i - k)) * binom(n, i) * binom(i, k) for k in range(i + 1)]
        for k, value in enumerate(row):
            x[k] += value * cx
            y[k] += value * cy
    return x, y


def derivative(row):
    return [i * row[i] for i in range(1, len(row))] or [0]


def bezier_speeds(controls):
    x, y = bernstein_to_power(controls)
    return derivative(x), derivative(y)


def fade(row, length=8):
    row = list(row)
    return row + [0] * (length - len(row)) if len(row) < length else row


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    existing = {record["uid"] for record in registry["curves"]}
    next_number = max(int(uid.split("-")[1]) for uid in existing) + 1

    beziers = json.loads(BEZIERS.read_text(encoding="utf-8"))["curves"][:6]
    mobiles = json.loads(MOBILES.read_text(encoding="utf-8"))["curves"]

    wanted = []
    for index, curve in enumerate(beziers, 1):
        speed_x, speed_y = bezier_speeds(curve["controls"])
        wanted.append({
            "name": f"bezier-loop-{index}",
            "family": "bezier",
            "variant": f"deg{curve['degree']}",
            "speedX": fade(speed_x),
            "speedY": fade(speed_y),
            "importance": 9,
            "note": f"integer control polygon {curve['controls']}; {curve['crossings']} crossings",
        })
    best_mobile = max(mobiles, key=lambda row: row["crossings"])
    wanted.append({
        "name": "mobile-k3-equal",
        "family": "mobile-k3",
        "variant": f"k{best_mobile['p']}of{best_mobile['q']}",
        "speedX": [],
        "speedY": [],
        "points": best_mobile["points"],
        "importance": 8,
        "note": f"mobile, k = {best_mobile['p']}/{best_mobile['q']}, equal radii; mirror {best_mobile['mirror']}",
    })

    rows = []
    for item in wanted:
        uid = f"c-{next_number:04d}"
        next_number += 1
        record = {
            "uid": uid,
            "name": item["name"],
            "aliases": [],
            "speedX": item["speedX"],
            "speedY": item["speedY"],
            "step": 1,
            "lists": ["found", item["family"]],
            "family": item["family"],
            "source": "new",
            "auto_named": False,
            "family_id": item["family"],
            "variant": item["variant"],
            "owner": f"{SEED:x}",
            "kind": "rows" if item["speedX"] else "path",
            "starred": True,
            "candidate": False,
            "importance": item["importance"],
            "base_uid": None,
            "note": item["note"],
        }
        if item.get("points"):
            record["path"] = item["points"]
        rows.append(record)
        print(f"{uid} {record['name']} · {item['note']}")

    if not args.write:
        print(f"{len(rows)} would be added")
        return 0

    registry["curves"].extend(rows)
    for record in rows:
        registry["sets"].append({
            "uid": f"set-{record['uid']}",
            "name": record["name"],
            "inner_uid": record["uid"],
            "border_uid": record["uid"],
            "rotation": 0,
            "pieces": 1,
            "perSide": 9,
            "importance": record["importance"],
        })
    REGISTRY.write_text(json.dumps(registry, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {REGISTRY.relative_to(ROOT)}: {len(registry['curves'])} curves, {len(registry['sets'])} sets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
