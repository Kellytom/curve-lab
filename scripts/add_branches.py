#!/usr/bin/env python3
"""Store a sampled named curve's branches separately, so a plate draws them as separate strokes.

    .venv/bin/python scripts/add_branches.py

A record whose path is several branches joined end to start cannot be drawn as one polyline:
the join becomes a chord across the shape. The path stays (for compatibility); `branches` is the
honest form, and the plate writer prefers it.
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


def branches_of(spec):
    data = G.named_data(spec)
    ctrls = data.get("ctrl")
    if not ctrls:
        return []
    out = []
    for ctrl in ctrls:
        deg = len(ctrl) - 1
        pts = []
        for i in range(SAMPLES + 1):
            s = Fraction(i, SAMPLES)
            w = sum(Fraction(p[2]) * G.bern_n(j, deg, s) for j, p in enumerate(ctrl))
            if w == 0:
                continue
            x, y = G.homog_point(ctrl, s)
            pts.append([round(float(x), 6), round(float(y), 6)])
        if len(pts) > 2:
            out.append(pts)
    return out


def main():
    registry = json.loads(REGISTRY.read_text())
    by_key = {s["key"]: s for s in G.NAMED}
    changed = 0
    for record in registry["curves"]:
        spec = by_key.get(record["name"])
        if spec is None:
            continue
        branches = branches_of(spec)
        if len(branches) < 2:
            continue
        record["branches"] = branches
        changed += 1
    if changed:
        REGISTRY.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n")
    print(f"{changed} record(s) now carry their branches separately")


if __name__ == "__main__":
    main()
