"""Modulated width — the former Stage IV width study, given its real name.

    .venv/bin/python scripts/modulated_width.py
    open workbench/modulated-width.html

This is **not** a parallel offset. The two rails are not equidistant; the width
is a function along the spine:

    w(u) = w0 (1 + a * 64 u^3 (1-u)^3)

so the width, its slope and its curvature all meet the plain stroke at both
ends.  The three cards show plain, widening and narrowing; the source page has
the ten measured plates.
"""

from __future__ import annotations

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INK = "#2e2413"
BLUE = "#1f5fa8"
RED = "#b23a2b"
GOLD = "#c9a441"
MUTED = "#7b6c4e"
PAPER = "#fffdf7"
GRID = "#e4dcc6"
FILL = "#f8efd7"


def cubic(p0, c1, c2, p3, n=220):
    out = []
    for i in range(n + 1):
        t = i / n
        mt = 1 - t
        out.append((mt ** 3 * p0[0] + 3 * mt * mt * t * c1[0]
                    + 3 * mt * t * t * c2[0] + t ** 3 * p3[0],
                    mt ** 3 * p0[1] + 3 * mt * mt * t * c1[1]
                    + 3 * mt * t * t * c2[1] + t ** 3 * p3[1]))
    return out


def width_law(u, a, w0=1.0):
    return w0 * (1.0 + a * 64.0 * u ** 3 * (1 - u) ** 3)


def rails(points, a, w0=1.0):
    left, right = [], []
    n = len(points) - 1
    for i, p in enumerate(points):
        u = i / n
        w = width_law(u, a, w0)
        aa = points[max(0, i - 1)]
        b = points[min(n, i + 1)]
        dx, dy = b[0] - aa[0], b[1] - aa[1]
        length = math.hypot(dx, dy) or 1e-12
        nx, ny = -dy / length, dx / length
        left.append((p[0] + 0.5 * w * nx, p[1] + 0.5 * w * ny))
        right.append((p[0] - 0.5 * w * nx, p[1] - 0.5 * w * ny))
    return left, right


def figure(a, w0=1.0, w=420, h=240):
    spine = cubic((0, 0), (3.2, 2.6), (6.8, -2.6), (10, 0), 240)
    left, right = rails(spine, a, w0)
    pts = spine + left + right
    x0, y0 = min(p[0] for p in pts), min(p[1] for p in pts)
    x1, y1 = max(p[0] for p in pts), max(p[1] for p in pts)
    dx, dy = (x1 - x0) or 1, (y1 - y0) or 1
    pad = 0.1
    x0, x1 = x0 - pad * dx, x1 + pad * dx
    y0, y1 = y0 - pad * dy, y1 + pad * dy
    k = min((w - 18) / (x1 - x0), (h - 18) / (y1 - y0))
    ox, oy = (w - (x1 - x0) * k) / 2, (h - (y1 - y0) * k) / 2

    def put(p):
        return ox + (p[0] - x0) * k, h - (oy + (p[1] - y0) * k)

    fill = ("M " + " L ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}" for p in left)
            + " L " + " L ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}"
                                 for p in reversed(right)) + " Z")
    body = [
        f'<path d="{fill}" fill="{FILL}" stroke="none"/>',
        '<path d="M ' + " L ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}" for p in left)
        + f'" fill="none" stroke="{BLUE}" stroke-width="1.2"/>',
        '<path d="M ' + " L ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}" for p in right)
        + f'" fill="none" stroke="{RED}" stroke-width="1.2"/>',
        '<path d="M ' + " L ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}" for p in spine)
        + f'" fill="none" stroke="{INK}" stroke-width="1.8"/>',
    ]
    return (f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">'
            f'<rect width="{w}" height="{h}" fill="{PAPER}" stroke="{GRID}"/>'
            + "".join(body) + "</svg>")


def main():
    cards = [
        ("Plain", 0.0, "constant width · the baseline"),
        ("Widening", 0.75, "the middle swells; the ends return to plain"),
        ("Narrowing", -0.45, "the middle thins; the ends return to plain"),
    ]
    rows = "".join(
        f'<section class="card"><div class="art">{figure(a)}</div>'
        f'<h3>{name}</h3><p>{note}</p></section>'
        for name, a, note in cards)
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Modulated width — variable width, not a parallel offset</title>
<style>
body{{margin:0;background:#f6f1e4;color:{INK};font:16px/1.55 Georgia,serif}}
main{{max-width:1080px;margin:0 auto;padding:34px 22px 70px}}
h1{{font-size:28px;margin:0 0 4px}}
.lead{{color:#8c6a21;margin:0 0 18px}}
.panel{{background:{PAPER};border:1px solid #d8ccae;padding:16px 18px;margin:0 0 18px}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}}
.card{{background:{PAPER};border:1px solid #d8ccae;padding:10px}}
.art{{margin:0 0 8px}}
svg{{display:block;width:100%;height:auto}}
h3{{font:600 13px/1.3 Georgia,serif;margin:0 0 3px}}
.card p{{font:11px/1.4 ui-monospace,Menlo,monospace;color:{MUTED};margin:0}}
code{{font:12px ui-monospace,Menlo,monospace}}
a{{color:#8c6a21}}
</style></head><body><main>
<h1>Modulated width</h1>
<p class="lead">Formerly called Stage IV. The width changes along the spine;
the rails are <strong>not equidistant</strong>, so this is not a parallel offset.</p>
<div class="panel">
<p><strong>The law.</strong> <code>w(u) = w0 (1 + a · 64 u³ (1−u)³)</code>.
The cubic bump has a triple root at both ends, so the width, its slope and its
curvature all meet the plain stroke with no step. The three cards show plain,
widening and narrowing. The full measured set is the old
<a href="http://localhost:8001/stage-four.html">Stage IV source page</a>
(10 plates); serve it from <code>../ornaments</code> on port 8001.</p>
<p><strong>Why it is a separate track.</strong> A parallel offset keeps the two
rails a constant distance apart; here the width is a function. The 2× offset
rule does not apply. This is an advanced width-modulation target, not a side
issue and not a failure; it is simply outside the parallel-offset grade.</p>
<p>For comparison: <a href="stem-library-offset.html">parallel offsets</a> ·
<a href="plant-forms.html">plant-form endings</a>.</p>
</div>
<div class="grid">{rows}</div>
</main></body></html>
'''
    out = ROOT / "workbench" / "modulated-width.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
