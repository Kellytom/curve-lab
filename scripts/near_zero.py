#!/usr/bin/env python3
"""Curves that pass near the origin without touching it.

    .venv/bin/python scripts/near_zero.py            # report
    .venv/bin/python scripts/near_zero.py --write    # keep the list

"Near zero" here means the *position*: how close the stroke comes to (0, 0)
without ever reaching it. That is a different question from the speed near zero
(a near-cusp), which `CurveMetric.closest` already holds.

The measure is simple and honest: sample the curve, take the smallest |C(t)|, and
keep the parameter where it happens. A curve whose smallest distance is small but
not zero, with the closest approach away from the ends, is a **graze** — the
shape that nearly touches its own centre and turns away.

Then the wobble: a small rational rotation or offset moves that closest point
without changing the rows' grid, which is how a dead-centre graze becomes an
off-centre swirl.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

OUT = ROOT / "workbench" / "near-zero.json"
STEPS = 400


def position(u, v, steps=STEPS):
    x = y = 0.0
    points = [(0.0, 0.0, 0.0)]
    for k in range(steps):
        t = (k + 0.5) / steps
        ux = sum(c * t ** i for i, c in enumerate(u))
        vy = sum(c * t ** i for i, c in enumerate(v))
        x += (ux * ux - vy * vy) / steps
        y += (2 * ux * vy) / steps
        points.append((x, y, (k + 1) / steps))
    return points


def analyse(record):
    u = record.get("speedX") or [0]
    v = record.get("speedY") or [0]
    if not any(u) and not any(v):
        return None
    points = position(u, v)
    # Every curve here starts at the origin, so the raw nearest point is always
    # its start. Centre the drawing on its own bounding box first — the operator's
    # "off centre" — and then ask how near the stroke passes the middle.
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    cx = (min(xs) + max(xs)) / 2
    cy = (min(ys) + max(ys)) / 2
    points = [(x - cx, y - cy, t) for x, y, t in points]
    size = max(max(abs(x), abs(y)) for x, y, _ in points) or 1
    inner = [p for p in points if 0.08 < p[2] < 0.92]
    best = min(inner, key=lambda p: math.hypot(p[0], p[1])) if inner else (0, 0, 0)
    distance = math.hypot(best[0], best[1])
    return {
        "uid": record["uid"],
        "name": record["name"],
        "distance": round(distance, 6),
        "share": round(distance / size, 4),      # relative to the curve's own size
        "t": round(best[2], 4),
        "interior": True,
        "size": round(size, 3),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    registry = json.loads((ROOT / "workbench" / "curve-registry.json").read_text(encoding="utf-8"))["curves"]
    rows = [row for row in (analyse(record) for record in registry) if row]
    grazes = [row for row in rows if row["distance"] > 0 and row["interior"]]
    grazes.sort(key=lambda row: row["distance"])

    print(f"{len(rows)} curves · {len(grazes)} graze the origin with an interior closest point")
    for row in grazes[:8]:
        print(f"  {row['name']:28s} closest {row['distance']:9.4f} at t {row['t']:.3f} "
              f"({row['share']:.4f} of its size)")

    if args.write:
        OUT.write_text(json.dumps({
            "format": "curve-lab.near-zero/1",
            "note": "distance from the curve to the origin, and where it happens; sampled",
            "curves": grazes,
        }, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
