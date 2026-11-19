#!/usr/bin/env python3
"""Symmetry by parity over t in [-1, 1], not by mirrored roots.

    .venv/bin/python scripts/parity_search.py
    .venv/bin/python scripts/parity_search.py --write

A different machine from the `lace-*` family. If the x speed `u` holds only
even powers and the y speed `v` only odd powers, then

    x'(t) = u^2 - v^2   is even  ->  x is odd
    y'(t) = 2 u v       is odd   ->  y is even

so `x(-t) = -x(t)` and `y(-t) = y(t)`: the curve is mirror-symmetric about the
horizontal axis, for every coefficient choice, with no root pairing at all. Swap
the parities and the mirror is vertical. That is the mechanism the project has
not swept, and t in [-1, 1] is where it pays.

The grid is still exact: whole coefficients in, `measure.grid` out.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab import measure  # noqa: E402
from scripts.ph_crossings import self_crossings, stable_crossings  # noqa: E402

OUT = ROOT / "workbench" / "parity-curves.json"


def grace(u, v, steps=300):
    x = y = 0.0
    pts = []
    for k in range(steps):
        t = (k + 0.5) / steps
        ux = sum(c * t ** i for i, c in enumerate(u))
        vy = sum(c * t ** i for i, c in enumerate(v))
        x += (ux * ux - vy * vy) / steps
        y += (2 * ux * vy) / steps
        pts.append((x, y, (k + 1) / steps))
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    cx = (min(xs) + max(xs)) / 2
    cy = (min(ys) + max(ys)) / 2
    size = max(max(xs) - min(xs), max(ys) - min(ys)) or 1
    inner = [(a - cx, b - cy) for a, b, t in pts if 0.08 < t < 0.92]
    return min(math.hypot(a, b) for a, b in inner) / size if inner else 9


def mirror_gap(u, v, steps=200):
    """How far the sampled curve is from its own horizontal mirror."""
    x = y = 0.0
    pts = []
    for k in range(steps + 1):
        t = -1 + 2 * k / steps
        ux = sum(c * t ** i for i, c in enumerate(u))
        vy = sum(c * t ** i for i, c in enumerate(v))
        x += (ux * ux - vy * vy) * (2 / steps)
        y += (2 * ux * vy) * (2 / steps)
        pts.append((x, y))
    n = len(pts)
    worst = 0.0
    size = max(max(abs(a) for a, _ in pts), max(abs(b) for _, b in pts)) or 1
    for i in range(n):
        rx, ry = pts[i]
        mx, my = pts[n - 1 - i]          # t -> -t
        worst = max(worst, math.hypot(rx - mx, -(ry - my)) / size)
    return round(worst, 4)


def normalised(u, v):
    factor = 0
    for value in list(u) + list(v):
        factor = math.gcd(factor, abs(int(value)))
    factor = factor or 1
    return tuple(x // factor for x in u), tuple(y // factor for y in v)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    registry = json.loads((ROOT / "workbench" / "curve-registry.json").read_text(encoding="utf-8"))["curves"]
    known = {normalised(c["speedX"], c["speedY"]) for c in registry if c.get("speedX")}

    rows = []
    seen = set()
    # u even, v odd: x odd, y even -> mirror about the horizontal axis.
    for a0 in (1, 2):
        for a2 in (-1, 0, 1):
            for a4 in (-1, 0, 1):
                u = [a0, 0, a2, 0, a4]
                for b1 in (-2, -1, 1, 2):
                    for b3 in (-2, -1, 0, 1, 2):
                        for b5 in (-2, -1, 0, 1, 2):
                            v = [0, b1, 0, b3, 0, b5]
                            key = normalised(u, v)
                            if key in seen:
                                continue
                            seen.add(key)
                            hits = self_crossings(u, v, samples=400)
                            if len(hits) < 2:
                                continue
                            rows.append({
                                "u": u, "v": v, "crossings": len(hits),
                                "grace": round(grace(u, v), 4),
                                "mirror": mirror_gap(u, v),
                                "known": key in known,
                            })

    rows.sort(key=lambda row: (-row["crossings"], row["grace"]))
    fresh = [row for row in rows if not row["known"]]
    print(f"{len(rows)} with 2+ crossings · {len(fresh)} not in the registry")
    for row in fresh[:10]:
        print(f"  u={row['u']} v={row['v']} → {row['crossings']} pairs · "
              f"grace {row['grace']:.4f} · mirror {row['mirror']:.4f} · grid {measure.grid(row['u'], row['v']):,}")

    if not fresh:
        print("nothing new in this parity sweep")
        return 0

    for row in fresh[:10]:
        row["crossings"] = len(stable_crossings(row["u"], row["v"]))
        row["grid"] = int(measure.grid(row["u"], row["v"]))
        row["inflections"] = int(measure.metrics(row["u"], row["v"])["inflection_count"])

    if args.write:
        OUT.write_text(json.dumps({
            "format": "curve-lab.parity-curves/1",
            "note": "symmetry by parity over t in [-1,1]: u even, v odd, so x is odd and y even",
            "curves": fresh[:10],
        }, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
