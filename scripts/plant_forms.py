"""Plant-form proof: endings, lattice growth marks and branches.

    .venv/bin/python scripts/plant_forms.py
    open workbench/plant-forms.html

The proof uses one stalk with two rails, a cone terminal at the top, pyramid
growth marks at the integer-grid crossings, and three branches whose length
falls with height. The detail cards show each ending separately.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab import plant as P  # noqa: E402

INK = "#2e2413"
BLUE = "#1f5fa8"
RED = "#b23a2b"
GOLD = "#c9a441"
MUTED = "#7b6c4e"
PAPER = "#fffdf7"
GRID = "#e4dcc6"
LEAF = "#2f6f4f"
FILL = "#f8efd7"


def cubic(p0, c1, c2, p3, n=240):
    pts = []
    for i in range(n + 1):
        t = i / n
        mt = 1 - t
        pts.append((mt ** 3 * p0[0] + 3 * mt * mt * t * c1[0]
                    + 3 * mt * t * t * c2[0] + t ** 3 * p3[0],
                    mt ** 3 * p0[1] + 3 * mt * mt * t * c1[1]
                    + 3 * mt * t * t * c2[1] + t ** 3 * p3[1]))
    return pts


def normal_offsets(points, d):
    out_p, out_m = [], []
    n = len(points) - 1
    for i, p in enumerate(points):
        a = points[max(0, i - 1)]
        b = points[min(n, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        l = math.hypot(dx, dy) or 1e-12
        nx, ny = -dy / l, dx / l
        out_p.append((p[0] + d * nx, p[1] + d * ny))
        out_m.append((p[0] - d * nx, p[1] - d * ny))
    return out_p, out_m


def add_ending(items, kind, point, tangent, w):
    if kind == "cone":
        c = P.cone_terminal(point, tangent, w)
        items.append((c["left"], INK, 1.8, None))
        items.append((c["right"], INK, 1.8, None))
    elif kind == "seagrass":
        for pts in P.seagrass(point, tangent, w):
            items.append((pts, LEAF, 1.2, None))
    elif kind == "flower":
        pts = P.flower(point, tangent, w)
        items.append((pts + [pts[0]], GOLD, 1.4, None, FILL))

    # a small collar at the rail ends
    T, N = P.frame(tangent)
    a = (point[0] + w * N[0], point[1] + w * N[1])
    b = (point[0] - w * N[0], point[1] - w * N[1])
    items.append(([a, b], INK, 1.1, None))


def branch_ending(kind, point, tangent, w):
    items = []
    add_ending(items, kind, point, tangent, w)
    return items


def stalk_items(points, w, grid=True, marks=True, branches=True,
                top="cone"):
    items = []
    plus, minus = normal_offsets(points, w)
    hits = [h for h in P.lattice_hits(points, 1.0) if 1.0 <= h["value"] <= 7.0]
    if grid:
        x0 = math.floor(min(p[0] for p in points)) - 1
        x1 = math.ceil(max(p[0] for p in points)) + 1
        y0 = math.floor(min(p[1] for p in points)) - 1
        y1 = math.ceil(max(p[1] for p in points)) + 1
        for x in range(x0, x1 + 1):
            items.append(([(x, y0), (x, y1)], GRID, 0.5, None))
        for y in range(y0, y1 + 1):
            items.append(([(x0, y), (x1, y)], GRID, 0.5, None))

    items.append((plus, BLUE, 1.1, None))
    items.append((minus, RED, 1.1, None))
    items.append((points, INK, 2.2, None))

    if marks:
        for h in hits:
            i = h["index"]
            T, N = P.frame(h["tangent"])
            tri = P.pyramid(plus[i], h["tangent"], N, (0.11, 0.26))
            items.append((tri + [tri[0]], GOLD, 0.8, None, GOLD))
            tri = P.pyramid(minus[i], h["tangent"], (-N[0], -N[1]),
                            (0.11, 0.26))
            items.append((tri + [tri[0]], GOLD, 0.8, None, GOLD))

    if top:
        add_ending(items, top, points[-1],
                   (points[-1][0] - points[-2][0],
                    points[-1][1] - points[-2][1]), w)

    if branches:
        chosen = [h for h in hits if h["value"] in (2.0, 4.0, 6.0)]
        sizes = [2.4, 1.8, 1.3]           # lower bigger than upper
        kinds = ["flower", "seagrass", "cone"]
        sides = [1, -1, 1]
        for h, length, kind, side in zip(chosen, sizes, kinds, sides):
            br = P.branch(h["point"], h["tangent"], side, length)
            bp, bm = normal_offsets(br, 0.42 * w)
            items.append((bp, BLUE, 0.8, None))
            items.append((bm, RED, 0.8, None))
            items.append((br, INK, 1.4, None))
            tip = br[-1]
            tan = (br[-1][0] - br[-2][0], br[-1][1] - br[-2][1])
            items += branch_ending(kind, tip, tan, 0.45 * w)
    return items


def figure(items, w=980, h=620, pad=0.06):
    pts = [p for it in items for p in it[0]]
    x0, y0, x1, y1 = min(p[0] for p in pts), min(p[1] for p in pts), \
        max(p[0] for p in pts), max(p[1] for p in pts)
    dx, dy = (x1 - x0) or 1, (y1 - y0) or 1
    x0, x1 = x0 - pad * dx, x1 + pad * dx
    y0, y1 = y0 - pad * dy, y1 + pad * dy
    k = min((w - 20) / (x1 - x0), (h - 20) / (y1 - y0))
    ox, oy = (w - (x1 - x0) * k) / 2, (h - (y1 - y0) * k) / 2

    def put(p):
        return ox + (p[0] - x0) * k, h - (oy + (p[1] - y0) * k)

    body = []
    for item in items:
        pts, colour, width, dash = item[0], item[1], item[2], item[3]
        fill = item[4] if len(item) > 4 else "none"
        d = " ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}" for p in pts)
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        body.append(f'<path d="M {d}" fill="{fill}" stroke="{colour}" '
                    f'stroke-width="{width}" stroke-linejoin="round" '
                    f'stroke-linecap="round"{dash_attr}/>')
    return (f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">'
            f'<rect width="{w}" height="{h}" fill="{PAPER}" stroke="{GRID}"/>'
            + "".join(body) + "</svg>")


def short_stalk(ending):
    pts = cubic((0, 0), (0.1, 0.8), (-0.1, 1.6), (0.0, 2.4), 120)
    return stalk_items(pts, 0.42, grid=False, marks=False, branches=False,
                       top=ending)


def mark_stalk():
    pts = cubic((0, 0), (0.4, 1.1), (-0.2, 2.0), (0.3, 3.0), 160)
    return stalk_items(pts, 0.40, grid=True, marks=True, branches=False,
                       top=None)


def branch_stalk():
    pts = cubic((0, 0), (0.3, 1.5), (-0.1, 3.0), (0.2, 4.5), 200)
    # branch points at y=1.5, 2.8, 4.0; lower bigger
    hits = {round(h["value"], 1): h for h in P.lattice_hits(pts, 0.5)}
    items = stalk_items(pts, 0.36, grid=False, marks=True, branches=False,
                        top="cone")
    for level, length, kind, side in ((1.5, 1.9, "flower", 1),
                                      (3.0, 1.4, "seagrass", -1),
                                      (4.0, 0.9, "cone", 1)):
        h = hits.get(level)
        if not h:
            continue
        br = P.branch(h["point"], h["tangent"], side, length)
        bp, bm = normal_offsets(br, 0.34 * 0.36)
        items.append((bp, BLUE, 0.8, None))
        items.append((bm, RED, 0.8, None))
        items.append((br, INK, 1.3, None))
        tan = (br[-1][0] - br[-2][0], br[-1][1] - br[-2][1])
        items += branch_ending(kind, br[-1], tan, 0.36)
    return items


def main():
    stalk = cubic((0.0, 0.0), (1.1, 3.0), (2.8, 5.8), (3.4, 8.0), 280)
    main_items = stalk_items(stalk, 0.44, grid=True, marks=True,
                             branches=True, top="cone")
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Plant forms — endings, lattice marks, branches</title>
<style>
body{{margin:0;background:#f6f1e4;color:{INK};font:16px/1.55 Georgia,serif}}
main{{max-width:1120px;margin:0 auto;padding:34px 22px 70px}}
h1{{font-size:28px;margin:0 0 4px}}
.lead{{color:#8c6a21;margin:0 0 18px}}
h2{{font:600 12px/1.2 ui-monospace,Menlo,monospace;letter-spacing:.10em;
text-transform:uppercase;color:{MUTED};margin:30px 0 8px}}
.panel{{background:{PAPER};border:1px solid #d8ccae;padding:16px 18px;margin:0 0 18px}}
.art{{background:{PAPER};border:1px solid #d8ccae;padding:8px;margin:0 0 8px}}
svg{{display:block;width:100%;height:auto}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}}
.card{{background:{PAPER};border:1px solid #d8ccae;padding:10px}}
.card h3{{font:600 12px/1.35 Georgia,serif;margin:0 0 3px}}
.card p{{font:10px/1.4 ui-monospace,Menlo,monospace;color:{MUTED};margin:0}}
.legend{{display:flex;gap:16px;flex-wrap:wrap;font:11px ui-monospace,Menlo,monospace;
color:{MUTED};margin:6px 0 0}}
.sw{{display:inline-block;width:20px;height:0;border-top:3px solid {INK};margin-right:5px;vertical-align:middle}}
.sw.b{{border-top:2px solid {BLUE}}}.sw.r{{border-top:2px solid {RED}}}
.sw.g{{border-top:2px solid {GOLD}}}
code{{font:12px ui-monospace,Menlo,monospace}}
</style></head><body><main>
<h1>Plant forms</h1>
<p class="lead">One stalk, two rails, an ending, marks at the integer lattice,
and branches that get smaller upward.</p>
<div class="panel">
<p><strong>The sequence.</strong> The stalk is offset at ±d; the rails are 2d
apart. Every stalk ends in a flower, a seagrass/leaf ending, or — if there is
no flower or head — a <strong>cone terminal</strong>: two arcs of radius
<strong>2 × offset</strong>, one from each rail, meeting at the centreline.
The <strong>growth mark</strong> is a small pyramid on each rail at an
integer-lattice crossing. Branches leave selected marks; the lower branch is
longer than the upper, and each branch gets its own ending. No bare tip.</p>
<p>The grid is the integer lattice in model space. The stalk crosses the
horizontal integer lines at the marked points; the pyramid’s base sits on the
rail and its apex points outward.</p>
</div>
<div class="art">{figure(main_items)}</div>
<div class="legend">
<span><i class="sw"></i> stalk</span>
<span><i class="sw b"></i> +d rail</span>
<span><i class="sw r"></i> −d rail</span>
<span><i class="sw g"></i> growth mark / flower</span>
</div>
<h2>Endings</h2>
<div class="grid">
<section class="card"><div class="art">{figure(short_stalk("cone"), 360, 260)}</div>
<h3>Cone terminal</h3><p>two arcs · R = 2 × offset · meet at the centreline</p></section>
<section class="card"><div class="art">{figure(short_stalk("seagrass"), 360, 260)}</div>
<h3>Seagrass</h3><p>three tapered blades · no bare tip</p></section>
<section class="card"><div class="art">{figure(short_stalk("flower"), 360, 260)}</div>
<h3>Flower</h3><p>a rosette head · the flower sits beyond the stalk tip</p></section>
</div>
<h2>Growth marks</h2>
<div class="grid" style="grid-template-columns:1fr 1fr">
<section class="card"><div class="art">{figure(mark_stalk(), 540, 400)}</div>
<h3>Integer-lattice hits</h3><p>pyramids on both rails · base on the rail, apex outward</p></section>
<section class="card"><div class="art">{figure(branch_stalk(), 540, 400)}</div>
<h3>Branches</h3><p>lower branch bigger than upper · each branch gets an ending</p></section>
</div>
</main></body></html>
'''
    out = ROOT / "workbench" / "plant-forms.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
