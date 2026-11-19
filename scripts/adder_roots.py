#!/usr/bin/env python3
"""The root families, in the visual adder and with the imaginary component.

    .venv/bin/python scripts/adder_roots.py

Three curves from the recipe the operator remembers — a mirrored root pair and a
stack at 1/2 — are taken apart term by term. Each term is now a *pair*: the x
term and the y term at the same power, which together draw a small arc. The sum
of the arcs is the curve.

Then the imaginary component: `A + iB`, where multiplying B's speed by i turns it
a quarter turn. That is the operation that can make a sum loop, and it is shown
beside the plain sum.

Writes into `workbench/sandbox-parametric.json` under `rootAdders`, leaving the
existing combination search alone.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.root_search import candidate  # noqa: E402
from scripts.ph_crossings import stable_crossings  # noqa: E402

OUT = ROOT / "workbench" / "sandbox-parametric.json"
STEPS = 121
FAMILIES = [(1, 8, 3), (1, 9, 3), (2, 5, 1)]


def positions(u, v):
    """Integrate the speed rows: x(t), y(t) as coefficient rows, ascending."""
    x = [0] + [Fraction(c, k + 1) for k, c in enumerate(u)]
    y = [0] + [Fraction(c, k + 1) for k, c in enumerate(v)]
    return x, y


def sample_row(row):
    return [sum(float(c) * t ** k for k, c in enumerate(row))
            for t in (i / (STEPS - 1) for i in range(STEPS))]


def terms(x, y):
    """One pair per power, as (x points, y points)."""
    out = []
    n = max(len(x), len(y))
    for k in range(n):
        a = x[k] if k < len(x) else 0
        b = y[k] if k < len(y) else 0
        if a == 0 and b == 0:
            continue
        ts = [i / (STEPS - 1) for i in range(STEPS)]
        out.append({
            "power": k,
            "x": round(float(a), 6),
            "y": round(float(b), 6),
            "points": [[round(float(a) * t ** k, 6), round(float(b) * t ** k, 6)] for t in ts],
        })
    return out


def curve_points(x, y):
    ts = [i / (STEPS - 1) for i in range(STEPS)]
    return [[round(sum(float(c) * t ** k for k, c in enumerate(x)), 5),
             round(sum(float(c) * t ** k for k, c in enumerate(y)), 5)] for t in ts]


def main() -> int:
    payload = json.loads(OUT.read_text(encoding="utf-8"))
    adders = []
    for p, q, m in FAMILIES:
        u, v = candidate(p, q, m)
        x, y = positions(u, v)
        adders.append({
            "name": f"pair {p}/{q} · {m} at 1/2",
            "note": "a mirrored root pair and a stack at one half: the recipe",
            "u": u, "v": v,
            "terms": terms(x, y),
            "sum": curve_points(x, y),
            "crossings": len(stable_crossings(u, v)),
        })

    # A + iB: the quarter-turned sum of two of them, which is where loops come from
    pairs = []
    for a, b in ((0, 1), (1, 2), (0, 2)):
        ua, va = adders[a]["u"], adders[a]["v"]
        ub, vb = adders[b]["u"], adders[b]["v"]
        n = max(len(ua), len(ub), len(va), len(vb))
        pad = lambda row: list(row) + [0] * (n - len(row))  # noqa: E731
        ua, va, ub, vb = pad(ua), pad(va), pad(ub), pad(vb)
        plain = ([p + q for p, q in zip(ua, ub)], [p + q for p, q in zip(va, vb)])
        turned = ([p - q for p, q in zip(ua, vb)], [p + q for p, q in zip(va, ub)])
        for label, (u, v) in (("A + B", plain), ("A + iB", turned)):
            x, y = positions(u, v)
            pairs.append({
                "a": adders[a]["name"], "b": adders[b]["name"], "op": label,
                "points": curve_points(x, y),
                "crossings": len(stable_crossings(u, v)),
            })

    payload["rootAdders"] = adders
    payload["rootPairs"] = pairs
    OUT.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {len(adders)} root adders and {len(pairs)} sums into {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
