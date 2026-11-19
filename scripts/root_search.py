#!/usr/bin/env python3
"""The recipe that worked: a mirrored root pair, then a stack at one half.

    .venv/bin/python scripts/root_search.py
    .venv/bin/python scripts/root_search.py --write

`lace-1of9-3` is the curve the operator remembers: roots at 1/9 and 8/9 (a
mirror pair about 1/2), and three roots at 1/2 — and it is also the curve that
passes within 2.4% of its own centre without touching it (`state/HANDOFF-int.md`,
2026-11-19). This script builds that family on purpose and ranks it.

The construction, all in `Fraction` so the rows stay whole:

    v(t) = (t - p/q)(t - (q-p)/q) · (t - 1/2)^m      the y speed
    u(t) = 1 - 2t + 2t^2                            the x speed (the known good one)

and the pair is mirrored: every root r has a partner 1 - r, which is what keeps
the curve symmetric about t = 1/2.

Ranking: crossing pairs first (the knot measure), then inflections, then the
cheapest grid. A curve is reported with all four numbers, and the grid is exact.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab import measure  # noqa: E402
from scripts.ph_crossings import stable_crossings  # noqa: E402

OUT = ROOT / "workbench" / "root-candidates.json"


def poly_from_roots(roots):
    """(t - r) for each root, as exact integer coefficients (cleared)."""
    coeffs = [Fraction(1)]
    for root in roots:
        nxt = [Fraction(0)] * (len(coeffs) + 1)
        for i, c in enumerate(coeffs):
            # ascending powers: (t - r) maps a_i t^i to a_i t^(i+1) - r a_i t^i
            nxt[i + 1] += c
            nxt[i] -= c * root
        coeffs = nxt
    scale = 1
    for c in coeffs:
        scale = scale * c.denominator // _gcd(scale, c.denominator)
    return [int(c * scale) for c in coeffs]


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return abs(a) or 1


def candidate(p, q, m):
    roots = [Fraction(p, q), Fraction(q - p, q)] + [Fraction(1, 2)] * m
    v = poly_from_roots(roots)
    u = [1, -2, 2]                      # the x speed that pairs with these rows
    n = len(v)
    v += [0] * (len(u) - n) if len(u) > n else []
    u += [0] * (len(v) - len(u)) if len(v) > len(u) else []
    return u, v


def describe(u, v):
    try:
        m = measure.metrics(u, v)
    except Exception as error:  # noqa: BLE001
        return {"error": str(error)[:100]}
    hits = stable_crossings(u, v)
    return {
        "grid": int(m["grid"]),
        "bend": round(float(m["bend"]), 4),
        "inflections": int(m["inflection_count"]),
        "crossings": len(hits),
        "places": len({(round(h["x"], 1), round(h["y"], 1)) for h in hits}),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    rows = []
    for q in range(5, 13):
        for p in range(1, (q // 2) + 1):
            if _gcd(p, q) != 1:
                continue
            for m in (1, 3, 5):
                u, v = candidate(p, q, m)
                facts = describe(u, v)
                if "error" in facts:
                    continue
                rows.append({
                    "name": f"pair-{p}of{q}-mid{m}",
                    "p": p, "q": q, "mid": m,
                    "u": u, "v": v, **facts,
                    "grace": round(_closest_grace(u, v), 4),
                })

    rows.sort(key=lambda r: (-r["crossings"], -r["inflections"], r["grid"]))
    print(f"{len(rows)} candidates · best {rows[0]['crossings']} pairs at grid {rows[0]['grid']}")
    for row in rows[:10]:
        print(f"  {row['name']:22s} {row['crossings']:2d} pairs · {row['places']:2d} places · "
              f"inflections {row['inflections']} · grid {row['grid']:>12,} · grace {row['grace']}")

    if args.write:
        OUT.write_text(json.dumps({
            "format": "curve-lab.root-candidates/1",
            "note": "mirrored root pair + stack at 1/2; crossing pairs, inflections and the exact grid",
            "candidates": rows,
        }, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


def _closest_grace(u, v, steps=300):
    """How near the centred drawing passes its own middle."""
    import math
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
    size = max(max(abs(a), abs(b)) for a, b, _ in pts) or 1
    inner = [(a - cx, b - cy) for a, b, t in pts if 0.08 < t < 0.92]
    return min(math.hypot(a, b) for a, b in inner) / size if inner else 9


if __name__ == "__main__":
    raise SystemExit(main())
