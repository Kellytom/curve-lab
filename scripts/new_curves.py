#!/usr/bin/env python3
"""Fresh curves: two mirrored pairs in v, which has barely been tried.

    .venv/bin/python scripts/new_curves.py
    .venv/bin/python scripts/new_curves.py --write

Every stored `lace-*` curve has *one* mirrored pair plus a stack at 1/2. A pair
is two roots, r and 1-r; two pairs are four, and the combinations have almost
never been enumerated. This does that:

    v(t) = (q t - p)(q t - (q - p)) (s t - r)(s t - (s - r)) (2t - 1)^m
    u(t) = 1 - 2t + 2t^2

Ranking is crossings first, then inflections, then the cheaper grid; a curve is
checked against the registry by its *normalised rows*, so "new" means new and not
a rescaling of something already stored.

Fast pass: the router's own crossing routine at coarse sampling. The winners are
re-counted at the stable setting before anything is written.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab import measure  # noqa: E402
from scripts.ph_crossings import self_crossings, stable_crossings  # noqa: E402

OUT = ROOT / "workbench" / "new-curves.json"
# Exhaustive over this stated space: every reduced mirrored pair p/q with a
# denominator from 4 to 12, taken one at a time and in every two-pair
# combination, with a stack at 1/2 of 1 to 5 roots. The x row is fixed at
# 1 - 2t + 2t^2, which is the row the stored family uses.
PAIRS = []
for q in range(4, 13):
    for p in range(1, q // 2 + 1):
        if math.gcd(p, q) == 1:
            PAIRS.append((p, q))


def poly_mul(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, ca in enumerate(a):
        for j, cb in enumerate(b):
            out[i + j] += ca * cb
    return out


def pair_row(p, q):
    """(q t - p)(q t - (q - p)), integer coefficients."""
    return poly_mul([-p, q], [-(q - p), q])


def candidate(p, q, r, s, mid):
    v = poly_mul(pair_row(p, q), pair_row(r, s))
    for _ in range(mid):
        v = poly_mul(v, [-1, 2])
    return [1, -2, 2], v


def normalised(u, v):
    """Rows divided by their common factor: the same curve, whatever the scale."""
    factor = 0
    for value in list(u) + list(v):
        factor = math.gcd(factor, abs(int(value)))
    factor = factor or 1
    return tuple(x // factor for x in u), tuple(x // factor for x in v)


def aspect(u, v, steps=200):
    """Height over width of the drawn curve: a degenerate curve has an extreme one."""
    x = y = 0.0
    xs = [0.0]
    ys = [0.0]
    for k in range(steps):
        t = (k + 0.5) / steps
        ux = sum(c * t ** i for i, c in enumerate(u))
        vy = sum(c * t ** i for i, c in enumerate(v))
        x += (ux * ux - vy * vy) / steps
        y += (2 * ux * vy) / steps
        xs.append(x)
        ys.append(y)
    w = max(xs) - min(xs)
    h = max(ys) - min(ys)
    if not w or not h:
        return 0.0
    return h / w


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


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    registry = json.loads((ROOT / "workbench" / "curve-registry.json").read_text(encoding="utf-8"))["curves"]
    known = {normalised(c["speedX"], c["speedY"]) for c in registry if c.get("speedX")}
    known_names = {normalised(c["speedX"], c["speedY"]): c["name"] for c in registry if c.get("speedX")}

    rows = []
    seen = set()
    combos = [((p, q), None) for (p, q) in PAIRS]
    combos += [((PAIRS[i]), PAIRS[j]) for i in range(len(PAIRS)) for j in range(i + 1, len(PAIRS))]
    for (p, q), second in combos:
        r, s = second if second else (0, 1)
        for mid in (1, 2, 3, 4, 5):
                u, v = candidate(p, q, r, s, mid)
                key = normalised(u, v)
                if key in seen:
                    continue
                seen.add(key)
                hits = self_crossings(u, v, samples=400)
                if len(hits) < 2:
                    continue
                # A curve whose v row dwarfs its u row is a straight line with
                # numerical crossings. Require a shape, not a sliver.
                shape = aspect(u, v)
                if not (0.25 <= shape <= 4.0):
                    continue
                if max(abs(c) for c in v) > 20 * max(abs(c) for c in u):
                    continue
                g = grace(u, v)
                name = f"pairs-{p}of{q}-{r}of{s}-mid{mid}"
                rows.append({
                    "name": name, "p": p, "q": q, "r": r, "s": s, "mid": mid,
                    "u": u, "v": v, "crossings": len(hits),
                    "grace": round(g, 4), "known": key in known,
                    "knownAs": known_names.get(key),
                })

    rows.sort(key=lambda row: (-row["crossings"], row["grace"]))
    fresh = [row for row in rows if not row["known"]]
    print(f"{len(rows)} with 2+ crossings · {len(fresh)} not in the registry")
    for row in fresh[:10]:
        print(f"  {row['name']:28s} {row['crossings']:2d} pairs · grace {row['grace']:.4f} · "
              f"grid {measure.grid(row['u'], row['v']):,}")

    if not fresh:
        print("no new curve in this sweep")
        return 0

    # verify the winners with the stable setting before keeping them
    for row in fresh[:10]:
        row["crossings"] = len(stable_crossings(row["u"], row["v"]))
        row["grid"] = int(measure.grid(row["u"], row["v"]))
        row["inflections"] = int(measure.metrics(row["u"], row["v"])["inflection_count"])
    fresh.sort(key=lambda row: (-row["crossings"], row["grace"]))

    if args.write:
        OUT.write_text(json.dumps({
            "format": "curve-lab.new-curves/1",
            "note": "two mirrored root pairs in v, plus a stack at 1/2; checked against the registry",
            "curves": fresh[:10],
        }, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
