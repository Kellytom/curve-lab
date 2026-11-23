#!/usr/bin/env python3
"""Search complex-coefficient polynomials for loops and knots.

    .venv/bin/python scripts/parametric_search.py            # 600 candidates
    .venv/bin/python scripts/parametric_search.py --n 2000   # a longer run
    .venv/bin/python scripts/parametric_search.py --write    # keep the winners
    .venv/bin/python scripts/parametric_search.py --cell 0,4 # does the empty cell fill?

The object is one complex polynomial in a real parameter:

    z(t) = sum (a_k + i b_k) t^k,   t in [-1, 1]

so that x = Re z and y = Im z. A real coefficient makes a graph, which cannot
loop; a coefficient with `i` turns that term a quarter turn, and sums with the
real terms loop. That is the whole trick, and it is the same one the sandbox
uses for "A + iB".

Scoring is cheap and honest about it: crossings counted on a sampled polyline,
then the winners re-counted with the router (`scripts/ph_crossings.py`) and the
exact core (`curve_lab/measure.py`) supplies grid, inflections and bend. Nothing
is published that only the fast pass has seen.

The seed is fixed, so a run is reproducible; `--n` changes the search, not luck.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab import measure  # noqa: E402
from scripts.ph_crossings import stable_crossings  # noqa: E402

OUT = ROOT / "workbench" / "parametric-candidates.json"
STEPS = 220
MAX_DEGREE = 9


def complex_rows(terms):
    """terms: [(power, real, imag)] -> x(t), y(t) coefficient rows."""
    n = max(p for p, _, _ in terms) + 1
    x = [0.0] * n
    y = [0.0] * n
    for power, a, b in terms:
        x[power] += a
        y[power] += b
    return x, y


def deriv(row):
    return [i * row[i] for i in range(1, len(row))] or [0]


def sample(x, y, steps=STEPS):
    """Walk the position polynomials directly: no speed, no scale surprises."""
    pts = []
    for k in range(steps + 1):
        t = -1 + 2 * k / steps
        pts.append((sum(c * t ** i for i, c in enumerate(x)),
                    sum(c * t ** i for i, c in enumerate(y))))
    return pts


def crossings(points):
    """All segment pairs: the loops in this family are small, so subsampling lies."""
    n = len(points)
    hits = 0
    for i in range(n - 2):
        ax, ay = points[i]
        bx, by = points[i + 1]
        for j in range(i + 2, n - 1):
            cx, cy = points[j]
            dx, dy = points[j + 1]
            den = (bx - ax) * (dy - cy) - (by - ay) * (dx - cx)
            if abs(den) < 1e-12:
                continue
            s = ((cx - ax) * (dy - cy) - (cy - ay) * (dx - cx)) / den
            u = ((cx - ax) * (by - ay) - (cy - ay) * (bx - ax)) / den
            if 0 < s < 1 and 0 < u < 1:
                hits += 1
    return hits


def signed_crossings(points):
    """Count each pair once, not once per adjacency: the number a reader means."""
    n = len(points)
    seen = set()
    for i in range(n - 2):
        ax, ay = points[i]
        bx, by = points[i + 1]
        for j in range(i + 2, n - 1):
            cx, cy = points[j]
            dx, dy = points[j + 1]
            den = (bx - ax) * (dy - cy) - (by - ay) * (dx - cx)
            if abs(den) < 1e-12:
                continue
            s = ((cx - ax) * (dy - cy) - (cy - ay) * (dx - cx)) / den
            u = ((cx - ax) * (by - ay) - (cy - ay) * (bx - ax)) / den
            if 0 < s < 1 and 0 < u < 1:
                seen.add((i, j))
    return len(seen)


def grid_of(x, y):
    try:
        return int(measure.grid(deriv(x), deriv(y)))
    except Exception:  # noqa: BLE001 - a wild candidate may not be a proper curve
        return 0


def score(candidate):
    points = sample(candidate["x"], candidate["y"])
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    spread = max(max(xs) - min(xs), max(ys) - min(ys)) or 1
    return {
        "crossings": signed_crossings(points),
        "size": round(spread, 3),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=600)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--cell", default=None,
                        help="C,I: keep only candidates with exactly C crossing pairs and I inflections")
    parser.add_argument("--family", choices=["loop", "graph"], default="loop",
                        help="loop: the turned-coefficient family; graph: y = p(t), x = t, for low crossings")
    args = parser.parse_args(argv)

    rng = random.Random(7)
    pool = []
    if args.family == "graph":
        # A graph cannot cross itself: x = t is monotone, so the crossing count is 0 by
        # construction. Inflections are the roots of p''; a degree-7 p has p'' of degree 5, so
        # four roots are reachable. This family is the honest test of a (0, I) cell.
        for _ in range(args.n):
            degree = rng.choice([5, 7, 7, 9])
            y = [0.0] * (degree + 1)
            for power in range(2, degree + 1):
                y[power] = rng.choice([-2, -1, -0.5, 0.5, 1, 2])
            pool.append({"terms": [], "x": [0.0, 1.0], "y": y, "graph": True})
    else:
        for _ in range(args.n):
            degree = rng.choice([5, 7, 7, 9])
            terms = []
            # one real low term, one turned term, and a tail: the shape that loops
            terms.append((1, rng.choice([-1, 1]), 0))
            terms.append((rng.choice([3, 5]), rng.choice([-2, -1, 1, 2]), 0))
            terms.append((rng.choice([4, 6]), rng.choice([-1, 1]), 0))
            power = rng.choice([5, 6, 7, 8, 9])
            terms.append((power, 0, rng.choice([-2, -1, 1, 2])))
            if degree == 9 and rng.random() < 0.5:
                terms.append((rng.choice([8, 9]), 0, rng.choice([-1, 1])))
            x, y = complex_rows(terms)
            pool.append({"terms": terms, "x": x, "y": y})

    for candidate in pool:
        candidate.update(score(candidate))
    kept = []

    if args.cell:
        # The empty-cell question: does a cell of (crossing pairs, inflections) fill? Scan the
        # whole pool, not only the 2+ crossing winners, and keep exact matches. The counts come
        # from the exact core, the same ones the metadata records carry.
        want_crossings, want_inflections = (int(v) for v in args.cell.split(","))
        matches = []
        for candidate in pool:
            if candidate["crossings"] != want_crossings:
                continue
            try:
                m = measure.metrics(deriv(candidate["x"]), deriv(candidate["y"]))
            except Exception:  # noqa: BLE001
                continue
            if int(m["inflection_count"]) == want_inflections:
                matches.append((candidate, m))
        matches.sort(key=lambda pair: pair[0]["size"])
        print(f"{args.n} candidates · {len(matches)} in the cell "
              f"({want_crossings} crossing pairs, {want_inflections} inflections)")
        for candidate, m in matches[:12]:
            x, y = candidate["x"], candidate["y"]
            hits = stable_crossings(deriv(x), deriv(y))
            item = {
                "terms": candidate["terms"],
                "crossings": len(hits),
                "places": len({(round(h["x"], 1), round(h["y"], 1)) for h in hits}),
                "grid": int(m["grid"]), "inflections": int(m["inflection_count"]),
                "bend": round(float(m["bend"]), 4), "exact": True,
                "x": [round(v, 6) for v in x], "y": [round(v, 6) for v in y],
            }
            kept.append(item)
            print(f"  x={item['x']} y={item['y']} → {item['crossings']} pairs, "
                  f"{item['places']} places, grid {item['grid']}, infl {item['inflections']}, "
                  f"bend {item['bend']}")
    else:
        winners = [c for c in pool if c["crossings"] >= 2]
        winners.sort(key=lambda c: (-c["crossings"], c["size"]))
        top = winners[:12]

        print(f"{args.n} candidates · {len(winners)} with 2+ crossings · "
              f"best {top[0]['crossings'] if top else 0}")

        for candidate in top:
            x, y = candidate["x"], candidate["y"]
            hits = stable_crossings(deriv(x), deriv(y))
            try:
                m = measure.metrics(deriv(x), deriv(y))
                grid = int(m["grid"])
                inflections = int(m["inflection_count"])
                bend = round(float(m["bend"]), 4)
                exact = True
            except Exception:  # noqa: BLE001
                grid, inflections, bend, exact = 0, 0, 0.0, False
            item = {
                "terms": candidate["terms"],
                "crossings": len(hits),
                "places": len({(round(h["x"], 1), round(h["y"], 1)) for h in hits}),
                "grid": grid, "inflections": inflections, "bend": bend, "exact": exact,
                "x": [round(v, 6) for v in x], "y": [round(v, 6) for v in y],
            }
            kept.append(item)
            print(f"  x={item['x']} y={item['y']} → {item['crossings']} pairs, "
                  f"{item['places']} places, grid {grid}, infl {inflections}, bend {bend}")

    if args.write:
        # History, not a snapshot: a new run goes on top and the older finds sink
        # to the bottom, so the page reads newest first and nothing is lost.
        previous = {"candidates": []}
        if OUT.exists():
            previous = json.loads(OUT.read_text(encoding="utf-8"))
        existing = previous.get("candidates", [])
        top_serial = max((item.get("serial", 0) for item in existing), default=0)
        stamp = datetime.now().isoformat(timespec="seconds")
        fresh = []
        for index, item in enumerate(kept, 1):
            fresh.append({**item, "serial": top_serial + index, "foundAt": stamp,
                          "run": args.n})
        payload = {
            "format": "curve-lab.parametric-candidates/1",
            "note": "complex-coefficient polynomials searched for crossings; newest first; starred ones pin to the top on the page",
            "seed": 7,
            "candidates": fresh + existing,
        }
        OUT.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {OUT.relative_to(ROOT)} · {len(fresh)} new, {len(payload['candidates'])} total")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
