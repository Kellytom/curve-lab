#!/usr/bin/env python3
"""Add the next batch of classical named curves as records.

    .venv/bin/python scripts/add_classical.py
    cd app && PATH="$HOME/node24/bin:$PATH" node scripts/add-registry-curves.mjs

The equations are the generators' own (`scripts/generators.py`, NAMED). Each curve is stored
as a sampled path, like every other named curve that has no speed pair; the note says so.
The list is chosen from `state/GAPS-int.md`: the six whose shapes are most recognisable and
whose equations are already proven exact or rational.
"""

import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import generators as G  # noqa: E402

REGISTRY = ROOT / "workbench" / "curve-registry.json"
SAMPLES = 400
BATCH = ["astroid", "cardioid", "deltoid", "nephroid", "trifolium", "quadrifolium"]


def points_of(spec):
    data = G.named_data(spec)
    ctrls = data.get("ctrl")
    if not ctrls:
        return []
    pts = []
    for ctrl in ctrls:
        deg = len(ctrl) - 1
        for i in range(SAMPLES + 1):
            s = Fraction(i, SAMPLES)
            w = sum(Fraction(p[2]) * G.bern_n(j, deg, s) for j, p in enumerate(ctrl))
            if w == 0:
                continue
            x, y = G.homog_point(ctrl, s)
            pts.append((float(x), float(y)))
    return pts


def main():
    registry = json.loads(REGISTRY.read_text())
    have = {row["uid"] for row in registry["curves"]}
    names = {row["name"].lower() for row in registry["curves"]}
    sets = registry.setdefault("sets", [])
    used = [int(s["uid"].split("-")[1]) for s in sets if s["uid"].startswith("s-")]
    next_set = (max(used) + 1) if used else 1
    next_uid = 402
    added = 0

    for key in BATCH:
        spec = next((s for s in G.NAMED if s["key"] == key), None)
        if spec is None:
            print(f"  {key}: not in NAMED")
            continue
        if key.lower() in names:
            print(f"  {key}: already a record")
            continue
        pts = points_of(spec)
        if len(pts) < 10:
            print(f"  {key}: no drawable branch")
            continue
        while f"c-{next_uid:04d}" in have:
            next_uid += 1
        uid = f"c-{next_uid:04d}"
        next_uid += 1
        registry["curves"].append({
            "uid": uid,
            "name": key,
            "aliases": [],
            "path": [[round(x, 6), round(y, 6)] for x, y in pts],
            "kind": "polyline",
            "family": key,
            "source": "named",
            "lists": ["new"],
            "starred": False,
            "candidate": False,
            "importance": 0,
            "transform": {"degrees": 0, "matrix": [["1", "0"], ["0", "1"]], "exact": True},
            "note": (f"{key} — {spec.get('eq', '')}", f"{spec.get('tail', '')}")[0] +
                    (f" · {spec.get('tail', '')}" if spec.get("tail") else ""),
        })
        sets.append({"uid": f"s-{next_set:04d}", "name": f"{key}-set", "inner_uid": uid,
                     "border_uid": uid, "rotation": 0, "pieces": 1, "per_side": 9,
                     "importance": 0})
        next_set += 1
        have.add(uid)
        added += 1
        print(f"  {uid}  {key}  {len(pts)} stations")

    if added:
        REGISTRY.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n")
    print(f"{added} curve(s) added; {len(registry['curves'])} in the registry")


if __name__ == "__main__":
    main()
