#!/usr/bin/env python3
"""The wobble that follows the circle: one picture, three variants.

    .venv/bin/python scripts/wobble_show.py

The operator's idea: the wobble is not a permanent offset. It **rotates** as the
parameter advances — the perturbation vector walks the unit circle while the
curve is drawn. So at t = 0 the stroke leans one way, at t = 1/2 it leans the
other, and the offset is a wave along the stroke rather than a shift of it.

Kept rational, as the project requires: the unit circle is walked by a slope
`s`, not an angle —

    circle(s) = ((1 - s^2)/(1 + s^2), 2s/(1 + s^2))

so `s = 1/2` is the 3-4-5 point (3/5, 4/5), and a whole turn is s from -inf to
+inf. The drawing below sweeps s over the ranges the operator named, -1..1 and
0..1, and states the share the wobble takes of the curve's own size.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.ph_crossings import spine  # noqa: E402

OUT = ROOT / "workbench" / "wobble.html"
SUBJECT = "c-0003"          # swan, a clean stroke that shows a wobble well
SHARE = 0.06                # the wobble's size, as a share of the curve's size


def circle(s):
    den = 1 + s * s
    return (1 - s * s) / den, 2 * s / den


def wobbled(points, low, high):
    """Offset each station along its normal and tangent by a rotating pair."""
    out = []
    n = len(points)
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    size = max(max(xs) - min(xs), max(ys) - min(ys)) or 1
    amplitude = SHARE * size
    for i, (x, y) in enumerate(points):
        t = i / (n - 1)
        s = low + (high - low) * t
        cs, sn = circle(s)
        a = points[max(0, i - 1)]
        b = points[min(n - 1, i + 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        length = math.hypot(tx, ty) or 1
        tx, ty = tx / length, ty / length
        nx, ny = -ty, tx
        out.append((x + amplitude * (cs * nx + sn * tx),
                    y + amplitude * (cs * ny + sn * ty)))
    return out


def svg_for(points, title, size=340, pad=26):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    span = max(x1 - x0, y1 - y0) or 1
    k = (size - 2 * pad) / span
    def sx(x): return pad + (x - x0) * k + ((size - 2 * pad) - (x1 - x0) * k) / 2
    def sy(y): return size - pad - (y - y0) * k - ((size - 2 * pad) - (y1 - y0) * k) / 2
    d = "".join(f"{'L' if i else 'M'}{sx(x):.1f},{sy(y):.1f}" for i, (x, y) in enumerate(points))
    return (f'<figure><svg viewBox="0 0 {size} {size}"><rect width="{size}" height="{size}" fill="#fffdf7"/>'
            f'<path d="{d}" fill="none" stroke="#141414" stroke-width="1.6" stroke-linejoin="round"/></svg>'
            f"<figcaption>{title}</figcaption></figure>")


def main() -> int:
    registry = {c["uid"]: c for c in json.loads(
        (ROOT / "workbench" / "curve-registry.json").read_text(encoding="utf-8"))["curves"]}
    record = registry[SUBJECT]
    _, x, y = spine(record["speedX"], record["speedY"], 500)
    points = list(zip(x, y))

    panels = [
        svg_for(points, f"{record['name']} — the stroke as it is"),
        svg_for(wobbled(points, 0.0, 1.0), "wobble slope 0 → 1 (a quarter of the circle)"),
        svg_for(wobbled(points, -1.0, 1.0), "wobble slope −1 → 1 (half the circle)"),
    ]

    html = f"""<!doctype html>
<html lang="en" data-theme="light"><head><meta charset="utf-8">
<title>The wobble that follows the circle: draft A</title>
<link rel="stylesheet" href="/vendor/pico.min.css">
<link rel="stylesheet" href="/vendor/curve-lab-theme.css">
<link rel="stylesheet" href="/vendor/app-shell.css">
<style>
body{{padding:18px;background:#f6f1e4}}
.row{{display:flex;flex-wrap:wrap;gap:18px;align-items:flex-start}}
figure{{margin:0;background:#fffdf7;border:1px solid #d8ccae}}
svg{{display:block;width:340px;height:340px}}
figcaption{{font:11px/1.5 ui-monospace,Menlo,monospace;color:#7b6c4e;padding:6px 8px;border-top:1px solid #e2d8bf}}
p{{color:#7b6c4e;max-width:80ch}}
</style></head><body>
<div class="draft-a" style="position:fixed;right:.75rem;bottom:.75rem;z-index:9999;background:#1b1b1b;color:#fff;font:12px/1.4 system-ui,sans-serif;padding:.35rem .6rem;border-radius:.25rem;opacity:.9">draft A</div>
<h1>Wobble that follows the unit circle</h1>
<p>The offset is not a constant shift: at every station the stroke is pushed by
the unit-circle point at a slope that walks from {0} to {1}. The circle is walked
by slope, not angle, so the points are rational — slope 1/2 is the 3-4-5 point.
The wobble is {int(SHARE * 100)}% of the curve's size.</p>
<div class="row">{''.join(panels)}</div>
</body></html>
"""
    OUT.write_text(html, encoding="utf-8")
    # and the same three panels as data, for /sandbox
    panels_json = {
        "format": "curve-lab.wobble/1",
        "note": "the swan stroke, then the unit-circle wobble at slope 0-1 and -1..1; rational circle points",
        "subject": record["name"],
        "share": SHARE,
        "panels": [
            {"title": f"{record['name']} — the stroke as it is", "points": [[round(a, 4), round(b, 4)] for a, b in points]},
            {"title": "wobble slope 0 → 1 (a quarter of the circle)", "points": [[round(a, 4), round(b, 4)] for a, b in wobbled(points, 0.0, 1.0)]},
            {"title": "wobble slope −1 → 1 (half the circle)", "points": [[round(a, 4), round(b, 4)] for a, b in wobbled(points, -1.0, 1.0)]},
        ],
    }
    (ROOT / "workbench" / "wobble.json").write_text(json.dumps(panels_json, indent=1) + "\n", encoding="utf-8")
    print("wrote workbench/wobble.json")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
