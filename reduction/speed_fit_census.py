#!/usr/bin/env python3
"""The speed-space census: every over-ceiling curve, fitted to speed 5.

    .venv/bin/python reduction/speed_fit_census.py

Writes workbench/speed-fit-census.json: for each curve whose speed degree is
above 5 (position above 11, rails above 9), the best speed-5 re-fit, its
station miss in curve units, and the curve's own size — so the miss can be
read against the curve it misses.

The verdict is by the unit count, per curve; the census does not decide.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab.measure import curve_polynomials, to_fraction
from reduction import speed_fit


def size_of(x, y, count=241):
    xs, ys = [], []
    for k in range(count):
        t = k / (count - 1)
        xs.append(sum(float(c) * t ** i for i, c in enumerate(x)))
        ys.append(sum(float(c) * t ** i for i, c in enumerate(y)))
    return ((max(xs) - min(xs)) ** 2 + (max(ys) - min(ys)) ** 2) ** 0.5


def main():
    registry = json.load(open(ROOT / "workbench" / "curve-registry.json"))
    rows = []
    for record in registry["curves"]:
        if not record.get("speedX"):
            continue
        u = [to_fraction(v) for v in record["speedX"]]
        v = [to_fraction(v) for v in record["speedY"]]
        speed = max(
            (len([c for c in u if c]) - 1) if any(u) else 0,
            (len([c for c in v if c]) - 1) if any(v) else 0,
        )
        if speed <= 5:
            continue
        x, y = curve_polynomials(u, v)
        fu, fv, report = speed_fit.reffit(x, y, 5, start=(u, v))
        rows.append({
            "uid": record["uid"],
            "name": record["name"],
            "speed_degree": speed,
            "position_degree": 2 * speed + 1,
            "rail_degree": 2 * speed - 1,
            "size": round(size_of(x, y), 4),
            "max_miss": round(report["max_miss"], 4),
            "miss_share": round(report["max_miss"] / size_of(x, y), 6) if size_of(x, y) else None,
        })
    rows.sort(key=lambda r: r["max_miss"])
    out = ROOT / "workbench" / "speed-fit-census.json"
    out.write_text(json.dumps({
        "format": "curve-lab.speed-fit-census/1",
        "curves": rows,
    }, indent=1))
    print(f"{len(rows)} over-ceiling curves → {out}")
    for r in rows[:8]:
        print(f"  {r['uid']} {r['name'][:26]:26s} speed {r['speed_degree']:2d} "
              f"miss {r['max_miss']:12.4f} units of {r['size']:.1f}")
    print("  ...")
    for r in rows[-3:]:
        print(f"  {r['uid']} {r['name'][:26]:26s} speed {r['speed_degree']:2d} "
              f"miss {r['max_miss']:12.4f} units of {r['size']:.1f}")


if __name__ == "__main__":
    main()
