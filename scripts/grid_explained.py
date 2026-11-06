"""Grid explained: a denominator is a ruler, not a size.

    .venv/bin/python scripts/grid_explained.py
    open workbench/grid-explained.html

The page answers one question in plain diagrams: if a triangle chain gives
exact position and angle at every node, why do the reports talk about a huge
grid? Because three different quantities were being called "the grid":

1. the drawing's extent, in chords;
2. the exact ruler (the denominator) needed to write the nodes as integers;
3. the placement lattice a drawing is snapped to.

Only (2) is large, and only at unit spacing. The page draws (1) and (2) and
states (3) with its measured snap error.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from curve_lab import spine as SL  # noqa: E402
import plant_forms as PF  # noqa: E402

INK, BLUE, RED, GOLD, GREEN = "#2e2413", "#1f5fa8", "#a23b2a", "#c9a441", "#2f6f4f"
MUTED, PAPER, GRID = "#7b6c4e", "#fffdf7", "#e4dcc6"
W, H = 900, 430


def _fit(pts, w=W, h=H, pad=42):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    s = min((w - 2 * pad) / (x1 - x0 or 1), (h - 2 * pad - 18) / (y1 - y0 or 1))
    ox = (w - (x1 - x0) * s) / 2
    oy = (h - 18 - (y1 - y0) * s) / 2
    return lambda p: (ox + (p[0] - x0) * s, h - oy - 14 - (p[1] - y0) * s)


def _svg(curves, dots=(), labels=(), title="", note="", w=W, h=H):
    pts = [p for pts, *_ in curves for p in pts]
    put = _fit(pts, w, h)
    out = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">',
           f'<rect width="{w}" height="{h}" fill="{PAPER}" stroke="{GRID}"/>']
    for pts, colour, width, dash in curves:
        d = " ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}" for p in pts)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        out.append(f'<path d="M {d}" fill="none" stroke="{colour}" '
                   f'stroke-width="{width}" stroke-linejoin="round" '
                   f'stroke-linecap="round"{da}/>')
    for p, colour in dots:
        q = put(p)
        out.append(f'<circle cx="{q[0]:.1f}" cy="{q[1]:.1f}" r="3" fill="{colour}"/>')
    for p, text in labels:
        q = put(p)
        out.append(f'<text x="{q[0]:.1f}" y="{q[1]-9:.1f}" '
                   f'font-family="ui-monospace,Menlo,monospace" font-size="11" '
                   f'fill="{INK}">{text}</text>')
    out.append(f'<text x="12" y="20" font-family="Georgia,serif" font-size="13" '
               f'fill="{INK}">{title}</text>')
    out.append(f'<text x="12" y="{h-10}" font-family="ui-monospace,Menlo,monospace" '
               f'font-size="10" fill="{MUTED}">{note}</text>')
    out.append("</svg>")
    return "".join(out)


def _chain(pkg, tri, turns, chord=1.0):
    ch = pkg.Spiral(tri, chord)
    ch.extend(turns)
    return ch


def main() -> int:
    pkg = SL.load()
    tri = pkg.Triple(3, 4, 5)
    thin = pkg.thinnest(3125)

    # --- panel 1: position and angle at every node ------------------------
    ch = _chain(pkg, tri, [1] * 6)
    pts = ch.floats()
    arrows = []
    for (x, y), heading in ch.knots():
        arrows.append([(float(x), float(y)),
                       (float(x) + 0.32 * float(heading.re),
                        float(y) + 0.32 * float(heading.im))])
    node = ch.nodes[3]
    num = (node[0].numerator, node[0].denominator,
           node[1].numerator, node[1].denominator)
    p1 = _svg(
        [(pts, INK, 2.0, None)] + [(a, GREEN, 1.2, None) for a in arrows],
        dots=[(p, GOLD) for p in pts],
        labels=[(pts[3], "node 3 = (52/25, 39/25)")],
        title="1 · Every node has an exact position and an exact heading",
        note="3-4-5 chain, six turns; gold = nodes, green = heading; "
             "the fraction is exact, not a measurement")

    # --- panel 2: the denominator is the ruler ----------------------------
    ruler = []
    ticks = []
    for i in range(26):
        x = i / 25.0
        ruler.append(([(x, 0.0), (x, 0.06 if i % 5 else 0.12)], MUTED, 1.0, None))
    ruler.append(([(0.0, 0.0), (1.0, 0.0)], INK, 1.6, None))
    for j in range(21):
        y = j / 25.0
        ruler.append(([(0.0, y), (0.06 if j % 5 else 0.12, y)], MUTED, 1.0, None))
    ruler.append(([(0.0, 0.0), (0.0, 0.8)], INK, 1.6, None))
    px, py = float(node[0]) % 1.0, float(node[1]) % 1.0
    ruler.append(([(px, 0.0), (px, py)], RED, 1.0, "4 3"))
    ruler.append(([(0.0, py), (px, py)], RED, 1.0, "4 3"))
    p2 = _svg(
        ruler,
        dots=[((px, py), RED)],
        labels=[((px, py), "52 ticks x, 39 ticks y of a 1/25 ruler")],
        title="2 · The denominator is the ruler, not the size of the drawing",
        note="one unit divided into 25 ticks; the node is at 52/25 and 39/25 "
             "— the ruler is fine, the drawing is small", w=560, h=300)

    # --- panel 3: one arc, two groupings ---------------------------------
    a = _chain(pkg, thin, [1] * 62, 1.0)
    b = _chain(pkg, thin, [2] * 31, 2.0)
    p3 = _svg(
        [(a.floats(), INK, 1.8, None),
         (b.floats(), BLUE, 1.4, "6 4")],
        dots=[(p, GOLD) for p in a.floats()] + [(p, BLUE) for p in b.floats()],
        title="3 · One 90° arc, two groupings: 62 single turns, 31 double turns",
        note="same angle and same arc; 1× turn = gold nodes, 2× turn = blue; "
             "the exact ruler is set by the number of turns, not the steps")

    # --- panel 4: the box, not the path ----------------------------------
    c270 = _chain(pkg, thin, [1] * 186, 1.0)
    bx = _bbox(c270)
    box = [(bx["x0"], bx["y0"]), (bx["x1"], bx["y0"]),
           (bx["x1"], bx["y1"]), (bx["x0"], bx["y1"]), (bx["x0"], bx["y0"])]
    p4 = _svg(
        [(box, MUTED, 1.2, "5 4"), (c270.floats(), INK, 1.6, None)],
        dots=[((bx["x1"], bx["y1"]), RED), ((bx["x0"] + (bx["x1"]-bx["x0"])/2, bx["y1"]), RED)],
        labels=[((bx["x1"], bx["y1"]), "vertical at 90°: x stops"),
                ((bx["x0"] + (bx["x1"]-bx["x0"])/2, bx["y1"]), "horizontal at 180°: y stops")],
        title="4 · The grid is the box, not the path",
        note="270° of the same chain: box 79 × 79, path 186 chords; after the "
             "turning points the spiral curls inside the box")

    # --- the numbers ------------------------------------------------------
    snapa = _snap(a)
    p1_den = 5 ** 6
    p3_den = 3121 ** 62

    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Grid explained — the denominator is a ruler</title>
<style>
body{{margin:0;background:#f6f1e4;color:{INK};font:16px/1.55 Georgia,serif}}
main{{max-width:1000px;margin:0 auto;padding:34px 22px 70px}}
h1{{font-size:30px;margin:0 0 6px}}
.lead{{color:#8c6a21;margin:0 0 18px;font-size:18px}}
h2{{font:600 12px/1.2 ui-monospace,Menlo,monospace;letter-spacing:.10em;text-transform:uppercase;color:{MUTED};margin:30px 0 8px}}
.panel{{background:{PAPER};border:1px solid #d8ccae;padding:16px 18px;margin:0 0 18px}}
.art{{background:{PAPER};border:1px solid #d8ccae;padding:8px;margin:0 0 8px}}
.art svg{{display:block;width:100%;height:auto}}
p{{margin:0 0 10px}}
.big{{font-size:18px}}
table{{border-collapse:collapse;width:100%;font:12px/1.5 ui-monospace,Menlo,monospace;margin:8px 0 0}}
td,th{{border-bottom:1px solid #d8ccae;padding:6px 8px;text-align:left}}
th{{color:{MUTED};font-weight:600}}
code{{font:12px ui-monospace,Menlo,monospace}}
.note{{font:11px/1.6 ui-monospace,Menlo,monospace;color:{MUTED}}}
</style></head><body><main>
<h1>Grid explained</h1>
<p class="lead">A denominator is a ruler, not the size of the drawing. String a
few triangles together and you know exactly where you are and which way you
face.</p>

<div class="panel">
<p class="big"><strong>The short answer: yes.</strong> Each triangle step turns
the heading by the same exact angle — cosine {tri.b}/{tri.c}, sine
{tri.a}/{tri.c} — and each step adds an exact vector. Position and heading at
every node are exact, with no accumulated error. The denominator is only how
that exact fraction is written down.</p>
</div>

<h2>1 · Position and angle, without a denominator in sight</h2>
<div class="art">{p1}</div>
<div class="panel">
<p>Gold dots are nodes; green ticks are the heading there. The node marked is
at <code>(52/25, 39/25)</code> after three turns. It is not “about 2.08”; it is
exactly 52 twenty-fifths and 39 twenty-fifths. A chain of these gives the same
exactness at every node, which is what you asked for.</p>
</div>

<h2>2 · What the denominator actually is</h2>
<div class="art">{p2}</div>
<div class="panel">
<p>One unit is divided into 25 ticks. The node sits 52 ticks along and 39 ticks
up. The denominator <strong>25</strong> is the number of ticks per unit; it
does not make the drawing 25 units long. A 217-digit denominator is the same
idea with a finer ruler: 217 digits of ticks, on a drawing that is still tens
of chords across.</p>
<p>So when a report says “a very large grid”, it should say which ruler it
means. The drawing is small; the ruler is fine.</p>
</div>

<h2>3 · Grouping the turns changes the step count, not the angle</h2>
<div class="art">{p3}</div>
<div class="panel">
<p>Both chains sweep the same 90°. The 1× chain needs 62 turns; the 2× chain
needs 31 steps with two turns each. The exact ruler is fixed by the number of
turns, 62, so both have denominator 3121<sup>62</sup>. Grouping saves steps;
it does not change the exactness or the ruler.</p>
</div>

<h2>4 · The grid is the box, not the path</h2>
<div class="art">{p4}</div>
<div class="panel">
<p>The box only grows while the curve is going out. At <strong>90°</strong> the
tangent is vertical, so x stops increasing; at <strong>180°</strong> the tangent
is horizontal, so y stops. After that the spiral curls inside the box. For this
270° chain the box is <strong>79 × 79</strong>, while the path is
<strong>186 chords</strong> long. The grid needs the box, not the path.</p>
<p>For a full 360° the box is still 79 × 79; the path is 248 chords. A circle
of radius R needs a 2R × 2R box and a 2πR path, so the box is about 1/π of the
path. That is the factor the “large grid” phrasing was missing.</p>
</div>

<h2>The three numbers, kept apart</h2>
<div class="panel">
<table>
<tr><th>drawing extent</th><td>box {_bbox(a)['w']:.0f} × {_bbox(a)['h']:.0f} for the
90° arc (path {len(a.turns)} chords); the 270° box is 79 × 79 with a 186-chord
path</td></tr>
<tr><th>exact ruler</th><td>the denominator that makes every node an integer —
3121<sup>62</sup>, 217 digits; a representation cost, not a drawing size</td></tr>
<tr><th>placement grid</th><td>the 3125 lattice a drawing is snapped to;
measured worst error {snapa:.1e} of a chord</td></tr>
</table>
</div>

<div class="panel">
<p><strong>What this means for the reports.</strong> “Needs a very large grid”
is accurate only for the exact ruler at unit spacing. It is misleading for the
drawing (a 79 × 79 box for a 270° volute) and for the placement grid (3125,
error {snapa:.1e}). Say “the exact denominator is 217 digits” or “the box is
79 × 79”, not one phrase for both.</p>
<p><strong>And the LAC.</strong> A chain that turns by the same angle every
step is a circular arc. An LAC turns by growing multiples (0, 1, 2, …), so its
ruler grows faster — c<sup>n(n+1)/2</sup> — but the position and angle at each
node are still exact. That is the case where “large” is earned.</p>
<p class="note">Re-derive: <code>python scripts/grid_explained.py</code> ·
<code>python -m unittest tests.test_grid_explained</code></p>
</div>
</main></body></html>
'''
    out = ROOT / "workbench" / "grid-explained.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    return 0


def _snap(chain):
    pts = chain.floats()
    snapped = [(round(x * 3125) / 3125, round(y * 3125) / 3125) for x, y in pts]
    return max(math.dist(a, b) for a, b in zip(pts, snapped))


def _extent(chain):
    pts = chain.floats()
    return max(math.hypot(x, y) for x, y in pts)


def _bbox(chain):
    pts = chain.floats()
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return {"x0": min(xs), "x1": max(xs), "y0": min(ys), "y1": max(ys),
            "w": max(xs) - min(xs), "h": max(ys) - min(ys)}


if __name__ == "__main__":
    raise SystemExit(main())
