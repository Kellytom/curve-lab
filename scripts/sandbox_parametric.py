#!/usr/bin/env python3
"""The parametric adder: existing curves added, turned and mirrored.

    .venv/bin/python scripts/sandbox_parametric.py

A graph `y = f(x)` can never loop; a parametric curve can. So this works on the
rows that are already parametric — the speed pairs `(u, v)` — and uses the three
tricks the project has settled:

- **adding** two curves: sum their speed rows, term by term (exact);
- **the quarter turn** `i`: `(u, v) -> (-v, u)`, which is what an imaginary
  component means here;
- **the mirror** `-v`: (kept in the pool, not in every sum).

It searches the pool for sums that cross themselves most, then writes the best
six to `workbench/sandbox-parametric.json` for the page. Sampling is stated; the
crossing counts are re-checked with the router's own routine for the six that
are published.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.ph_crossings import stable_crossings  # noqa: E402

REGISTRY = ROOT / "workbench" / "curve-registry.json"
OUT = ROOT / "workbench" / "sandbox-parametric.json"
STEPS = 160
POOL = [
    "c-0262",   # loop-8-11-mid-1, the cheap knot
    "c-0253",   # loop-12-13-15-mid-1
    "c-0028",   # lace-1of8-3
    "c-0062",   # lace-1of10-1of3-1
    "c-0014",   # wave-coarse
    "c-0003",   # swan
    "c-0091",   # loop t=1/2,3/4 (starred)
    "c-0094",   # cross+45deg (starred)
    "c-0101",   # cross 2/5-4/5 (starred)
    "c-0134",   # mobile, starred
]


def rows(record):
    n = max(len(record.get("speedX") or []), len(record.get("speedY") or []))
    u = list(record.get("speedX") or []) + [0] * (n - len(record.get("speedX") or []))
    v = list(record.get("speedY") or []) + [0] * (n - len(record.get("speedY") or []))
    return u, v


def add(a, b):
    n = max(len(a[0]), len(b[0]))
    ua = a[0] + [0] * (n - len(a[0]))
    va = a[1] + [0] * (n - len(a[1]))
    ub = b[0] + [0] * (n - len(b[0]))
    vb = b[1] + [0] * (n - len(b[1]))
    return [x + y for x, y in zip(ua, ub)], [x + y for x, y in zip(va, vb)]


def quarter(u, v):
    """Multiplying the speed by i turns the curve by 90 degrees."""
    return [-a for a in v], list(u)


def points(u, v, steps=STEPS):
    x = y = 0.0
    out = [(0.0, 0.0)]
    for k in range(steps):
        t = (k + 0.5) / steps
        ux = sum(c * t ** i for i, c in enumerate(u))
        vy = sum(c * t ** i for i, c in enumerate(v))
        x += (ux * ux - vy * vy) / steps
        y += (2 * ux * vy) / steps
        out.append((x, y))
    return out


def crossings(points, limit=400):
    """A quick sampled count: enough to rank, not to publish."""
    n = len(points)
    hits = 0
    for i in range(0, n - 2, 2):
        a, b = points[i], points[i + 1]
        for j in range(i + 4, n - 2, 2):
            c, d = points[j], points[j + 1]
            den = (b[0] - a[0]) * (d[1] - c[1]) - (b[1] - a[1]) * (d[0] - c[0])
            if abs(den) < 1e-12:
                continue
            s = ((c[0] - a[0]) * (d[1] - c[1]) - (c[1] - a[1]) * (d[0] - c[0])) / den
            t = ((c[0] - a[0]) * (b[1] - a[1]) - (c[1] - a[1]) * (b[0] - a[0])) / den
            if 0 < s < 1 and 0 < t < 1:
                hits += 1
                if hits >= limit:
                    return hits
    return hits


def main() -> int:
    registry = {c["uid"]: c for c in json.loads(REGISTRY.read_text(encoding="utf-8"))["curves"]}
    pool = [registry[uid] for uid in POOL if uid in registry]
    found = []

    for i in range(len(pool)):
        for j in range(i + 1, len(pool)):
            a, b = rows(pool[i]), rows(pool[j])
            for label, (u, v) in (
                ("A + B", add(a, b)),
                ("A + iB", add(a, quarter(*b))),
            ):
                pts = points(u, v)
                scored = crossings([list(p) for p in pts])
                if scored >= 4:
                    found.append({
                        "a": pool[i]["uid"], "b": pool[j]["uid"], "op": label,
                        "aName": pool[i]["name"], "bName": pool[j]["name"],
                        "quick": scored, "points": pts, "u": u, "v": v,
                    })

    found.sort(key=lambda item: -item["quick"])
    best = found[:6]
    for item in best:
        hits = stable_crossings(item["u"], item["v"])
        item["crossings"] = len(hits)
        item["places"] = len({(round(h["x"], 1), round(h["y"], 1)) for h in hits})
        del item["u"], item["v"]

    print(f"pool {len(pool)} · pairs {len(pool) * (len(pool) - 1) // 2} · candidate sums {len(found)}")
    for item in best:
        print(f"  {item['aName']} {item['op']} {item['bName']}: {item['crossings']} pairs, {item['places']} places")

    payload = {
        "format": "curve-lab.sandbox-parametric/1",
        "note": "parametric sums of stored curves, sampled; crossings re-checked with the router",
        "steps": STEPS,
        "combinations": [{
            "a": item["a"], "b": item["b"], "op": item["op"],
            "aName": item["aName"], "bName": item["bName"],
            "crossings": item["crossings"], "places": item["places"],
            "points": [[round(x, 5), round(y, 5)] for x, y in item["points"]],
        } for item in best],
    }
    OUT.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
