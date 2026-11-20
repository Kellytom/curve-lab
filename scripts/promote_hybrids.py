#!/usr/bin/env python3
"""Promote the kept hybrid candidates into registry records.

    .venv/bin/python scripts/promote_hybrids.py            # report only
    .venv/bin/python scripts/promote_hybrids.py --write    # append to the registry

Reads the decisions (workbench/sandbox-curves.json, written by
app/scripts/export-sandbox.mjs) and the candidate list (workbench/hybrids.json). Every
candidate with decision "keep" and no registry row yet gets one:

    uid        the next free c-number, assigned once
    name       hybrid-<p>-<q>-<block>-<use>   (colour: hybrid-<p>-<q>-colour)
    params     p, q, block, use                the construction, so it can be rebuilt
    formula    plain and rational strings      the same object the other records carry
    grid       lcm of the exact station denominators
    note       the construction, the measures, the grid

Then app/scripts/add-registry-curves.mjs puts it in SQLite and
node scripts/curve_pngs.mjs --only <uid> draws it.

Spec: state/SPEC-hybrids-int.md, "promotion".
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "workbench" / "curve-registry.json"
DECISIONS = ROOT / "workbench" / "sandbox-curves.json"
CANDIDATES = ROOT / "workbench" / "hybrids.json"
N = 100

BLOCKS = {
    "quadratic": [(2, 1, 1)],
    "cubic": [(3, 2, 1), (3, 1, 2)],
    "quintic-central": [(10, 3, 2), (10, 2, 3)],
    "quintic-all-four": [(5, 4, 1), (10, 3, 2), (10, 2, 3), (5, 1, 4)],
    "cubic-and-quintic": [(3, 2, 1), (3, 1, 2), (5, 4, 1), (10, 3, 2), (10, 2, 3), (5, 1, 4)],
    "every-term": [(2, 1, 1), (3, 2, 1), (3, 1, 2), (5, 4, 1), (10, 3, 2), (10, 2, 3), (5, 1, 4)],
}


def power(value, n):
    out = Fraction(1)
    for _ in range(n):
        out *= value
    return out


def stations():
    out = []
    for i in range(-N + 1, N):
        u = Fraction(i, N)
        t = u / (1 - abs(u))
        out.append(((1 - t * t) / (1 + t * t), 2 * t / (1 + t * t)))
    return out


ST = stations()


def points_and_grid(p, q, use, block_name):
    pts = []
    grid = 1
    block = BLOCKS.get(block_name, [])
    for C, S in ST:
        x, y = power(C, p), power(S, q)
        if use == "radius":
            P = x * x + y * y
            for coefficient, ix, iy in block:
                P += coefficient * power(x, ix) * power(y, iy)
            x, y = x * P, y * P
        pts.append((float(x), float(y)))
        for value in (x, y):
            grid = grid * value.denominator // math.gcd(grid, value.denominator)
    return pts, grid


def name_for(p, q, block_name, use):
    return f"hybrid-{p}-{q}-{block_name}-{use}" if use == "radius" else f"hybrid-{p}-{q}-colour"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    decisions = json.loads(DECISIONS.read_text())
    kept = {row["name"]: row for row in decisions.get("curves", [])
            if row.get("decision") == "keep"}
    candidates = {row["id"]: row for row in json.loads(CANDIDATES.read_text())["candidates"]}
    registry = json.loads(REGISTRY.read_text())
    names = {row["name"] for row in registry["curves"]}
    used = {row["uid"] for row in registry["curves"]}

    print(f"{len(kept)} kept candidates")
    if not kept:
        print("nothing to promote; walk the desk and press keep first")
        return 0

    next_number = 1
    for uid in used:
        if uid.startswith("c-"):
            next_number = max(next_number, int(uid[2:]) + 1)

    added = []
    for key in sorted(kept):
        candidate = candidates.get(key)
        if candidate is None:
            print(f"  {key}: no candidate with that id; skipped")
            continue
        p, q = candidate["p"], candidate["q"]
        block_name = candidate["block"]
        use = candidate["use"]
        name = (kept[key].get("curveName") or "").strip() or name_for(p, q, block_name, use)
        importance = int(candidate.get("importance") or kept[key].get("importance") or 0)
        if name in names:
            print(f"  {key}: already in the registry as {name}")
            continue
        pts, grid = points_and_grid(p, q, use, block_name)
        uid = f"c-{next_number:04d}"
        next_number += 1
        formula = candidate["formula"]
        note = (f"{formula['plain']}; rational form {formula['rational']}; "
                f"{formula['use']}; stations at t = u/(1-|u|), u = i/{N} "
                f"({len(pts)} stations); grid 1/{grid}; "
                f"{candidate['crossings']} crossing pairs; promoted from {key}")
        record = {
            "uid": uid,
            "name": name,
            "aliases": [key],
            "speedX": [],
            "speedY": [],
            "step": 1,
            "lists": ["found", "hybrid"],
            "family": "hybrid",
            "source": "new",
            "auto_named": False,
            "family_id": "hybrid",
            "variant": f"{p}-{q}-{block_name}-{use}",
            "kind": "path",
            "starred": bool(importance),
            "candidate": False,
            "importance": importance,
            "base_uid": None,
            "params": {"p": p, "q": q, "block": block_name, "use": use,
                       "stations": len(pts), "uStep": f"1/{N}",
                       "stationRule": "t = u/(1-|u|), u = i/100"},
            # the mature field set, at rest: character offsets and framing are placeholders
            # until the operator sets them, so nothing downstream has to guess the shape.
            "rotation": 0,
            "pieces": 1,
            "borderUid": None,
            "perSide": 9,
            "borderTurn": 0,
            "offsets": 0,
            "widthPct": 0,
            "plus": 0,
            "minus": 0,
            "profile": None,
            "formula": formula,
            "conversion": {
                "algorithm": "hybrid",
                "status": "native",
                "target": "x = C(t)^p, y = S(t)^q; C = (1 - t^2)/(1 + t^2), S = 2t/(1 + t^2)",
                "formulaNext": None,
            },
            "grid": f"1/{grid}",
            "note": note,
            "path": [[round(x, 6), round(y, 6)] for x, y in pts],
        }
        added.append(record)
        names.add(name)

    for record in added:
        print(f"  would add {record['uid']} {record['name']} "
              f"({record['params']['stations']} stations, grid length "
              f"{len(record['grid'])} digits)")

    if not added:
        print("nothing new to add")
        return 0
    if not args.write:
        print("report only; --write appends")
        return 0

    for record in added:
        registry["curves"].append(record)
        registry.setdefault("sets", []).append({
            "uid": f"set-{record['uid']}",
            "name": record["name"],
            "inner_uid": record["uid"],
            "border_uid": record["uid"],
            "rotation": 0,
            "pieces": 1,
            "perSide": 9,
            "importance": importance,
        })
    REGISTRY.write_text(json.dumps(registry, indent=2) + "\n")
    print(f"added {len(added)}; registry now {len(registry['curves'])} curves, "
          f"{len(registry['sets'])} sets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
