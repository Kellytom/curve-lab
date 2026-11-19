#!/usr/bin/env python3
"""Chebyshev Lissajous curves: a different machine entirely.

    .venv/bin/python scripts/chebyshev_curves.py
    .venv/bin/python scripts/chebyshev_curves.py --write

Not the PH speed-pair recipe and not the root family. Take the Chebyshev
polynomials, which have whole coefficients by construction,

    T0 = 1,  T1 = t,  T(n+1) = 2t T(n) - T(n-1)

and use one as x and another as y:

    x(t) = Tm(t),  y(t) = Tn(t),  t in [-1, 1]

This is the polynomial Lissajous figure: it closes, it crosses itself many
times, and both rows are integers, so the grid is exact and often small. The
shapes are the "string art" family — loops at the ends, a lattice of crossings
in the middle — which is visibly unlike anything in the registry.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab import measure  # noqa: E402
from scripts.ph_crossings import self_crossings, stable_crossings  # noqa: E402

OUT = ROOT / "workbench" / "chebyshev-curves.json"


def chebyshev(n):
    """T_n, ascending powers, integer coefficients."""
    a, b = [1], [0, 1]
    if n == 0:
        return a
    if n == 1:
        return b
    for _ in range(2, n + 1):
        doubled = [0] + [2 * c for c in b]          # 2t * T(n-1)
        length = max(len(doubled), len(a))
        doubled += [0] * (length - len(doubled))
        a += [0] * (length - len(a))
        a = [x - y for x, y in zip(doubled, a)]
        a, b = b, a
    return b


def deriv(row):
    return [i * row[i] for i in range(1, len(row))] or [0]


def sample(row_x, row_y, steps=600):
    pts = []
    for k in range(steps + 1):
        t = -1 + 2 * k / steps
        pts.append((sum(c * t ** i for i, c in enumerate(row_x)),
                    sum(c * t ** i for i, c in enumerate(row_y))))
    return pts


def aspect(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    w = max(xs) - min(xs)
    h = max(ys) - min(ys)
    return (h / w) if w else 0.0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    rows = []
    for m in range(2, 13):
        for n in range(2, 13):
            if m == n:
                continue
            x, y = chebyshev(m), chebyshev(n)
            hits = self_crossings(deriv(x), deriv(y), samples=600)
            if len(hits) < 4:
                continue
            pts = sample(x, y)
            rows.append({
                "m": m, "n": n, "x": x, "y": y,
                "crossings": len(hits), "aspect": round(aspect(pts), 3),
                "grid": int(measure.grid(deriv(x), deriv(y))),
                "inflections": int(measure.metrics(deriv(x), deriv(y))["inflection_count"]),
            })

    rows.sort(key=lambda row: (-row["crossings"], row["grid"]))
    print(f"{len(rows)} Chebyshev Lissajous curves with 4+ crossings")
    for row in rows[:10]:
        print(f"  T{row['m']} x, T{row['n']} y → {row['crossings']:2d} pairs · grid {row['grid']:>9,} · "
              f"aspect {row['aspect']:.2f} · inflections {row['inflections']}")

    if args.write and rows:
        for row in rows[:10]:
            row["crossings"] = len(stable_crossings(deriv(row["x"]), deriv(row["y"])))
        OUT.write_text(json.dumps({
            "format": "curve-lab.chebyshev/1",
            "note": "x = Tm(t), y = Tn(t); whole coefficients, exact grid; sampled drawings",
            "curves": rows[:10],
        }, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
