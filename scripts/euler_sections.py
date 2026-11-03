"""Euler sections from the C curves: p-triple polygon + rational rails + cubic seam.

    .venv/bin/python scripts/euler_sections.py
    open workbench/euler-sections.html

Each card shows one smooth section of a C curve.  Grey is the target, ink is
the exact p-triple Euler polygon, blue/red are the exact rational miter rails,
and gold-dash is the cubic seam.  Cusps/loops are split before conversion.
"""

from __future__ import annotations

import math
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab.euler_polygon import convert  # noqa: E402

sys.path.insert(0, str(ROOT / "scripts"))
import generators as G  # noqa: E402

INK = "#2e2413"
GREY = "#9c8f75"
BLUE = "#1f5fa8"
RED = "#b23a2b"
GOLD = "#c9a441"
MUTED = "#7b6c4e"
PAPER = "#fffdf7"
GRID = "#e4dcc6"


def sample(fn, t0, t1, n=360):
    return [fn(t0 + (t1 - t0) * i / n) for i in range(n + 1)]


def cycloid():
    return sample(lambda t: (t - math.sin(t), 1 - math.cos(t)), 0.1, math.pi - 0.1)


def astroid():
    return sample(lambda t: (math.cos(t) ** 3, math.sin(t) ** 3), 0.1, math.pi / 2 - 0.1)


def semicubical():
    return sample(lambda t: (t * t, t * t * t), 0.15, 1.1)


def tractrix():
    return sample(lambda t: (1.0 / math.cosh(t), t - math.tanh(t)), 0.2, 2.0)


def heart():
    return sample(lambda t: (16 * math.sin(t) ** 3,
                             13 * math.cos(t) - 5 * math.cos(2 * t)
                             - 2 * math.cos(3 * t) - math.cos(4 * t)),
                  0.15, math.pi - 0.15)


def squircle():
    return sample(lambda t: (math.cos(t) ** 0.5, math.sin(t) ** 0.5),
                  0.1, math.pi / 2 - 0.1)


def named_section(key, branch=0, t0=0.2, t1=0.8, n=240):
    spec = next(s for s in G.NAMED if s["key"] == key)
    ctrl = G.named_data(spec)["ctrl"][branch]
    out = []
    for i in range(n + 1):
        t = F(int((t0 + (t1 - t0) * i / n) * 1000), 1000)
        out.append((float(G.homog_point(ctrl, t)[0]),
                    float(G.homog_point(ctrl, t)[1])))
    return out


SECTIONS = [
    ("Cycloid", "one half arch · split at the cusps", cycloid, {}),
    ("Astroid", "one quadrant · cusp at each end", astroid, {}),
    ("Semicubical / Neile", "one branch · cusp at the origin", semicubical, {}),
    ("Tractrix", "smooth section · cusp at the start", tractrix, {}),
    ("Heart", "one lobe · refined split", heart, {"n": 200, "max_angle": 0.1}),
    ("Squircle", "one quadrant · smooth", squircle, {}),
    ("Bicorn", "one smooth branch section · node split", lambda: named_section("bicorn", 0), {"n": 120}),
    ("Nodal", "one loop branch section · node split", lambda: named_section("nodal", 0), {"n": 120}),
    ("Tschirnhausen", "one branch section · node split", lambda: named_section("tschirnhausen", 0), {"n": 120}),
    ("Piriform 2×", "one branch section · node split", lambda: named_section("piriform 2x", 0), {"n": 120}),
]


def figure(card, w=520, h=310):
    curves = [
        (card["target"], GREY, 1.0, None),
        (card["polygon"], INK, 1.8, None),
        (card["left"], BLUE, 1.0, None),
        (card["right"], RED, 1.0, None),
        (card["cubic"], GOLD, 1.3, "5 4"),
    ]
    pts = [p for c in curves for p in c[0]]
    x0, y0 = min(p[0] for p in pts), min(p[1] for p in pts)
    x1, y1 = max(p[0] for p in pts), max(p[1] for p in pts)
    dx, dy = (x1 - x0) or 1, (y1 - y0) or 1
    pad = 0.08
    x0, x1 = x0 - pad * dx, x1 + pad * dx
    y0, y1 = y0 - pad * dy, y1 + pad * dy
    k = min((w - 18) / (x1 - x0), (h - 18) / (y1 - y0))
    ox, oy = (w - (x1 - x0) * k) / 2, (h - (y1 - y0) * k) / 2

    def put(p):
        return ox + (p[0] - x0) * k, h - (oy + (p[1] - y0) * k)

    body = []
    for pts, colour, width, dash in curves:
        d = " ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}" for p in pts)
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        body.append(f'<path d="M {d}" fill="none" stroke="{colour}" '
                    f'stroke-width="{width}" stroke-linejoin="round"{dash_attr}/>')
    return (f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">'
            f'<rect width="{w}" height="{h}" fill="{PAPER}" stroke="{GRID}"/>'
            + "".join(body) + "</svg>")


def main():
    cards = []
    for title, note, fn, opts in SECTIONS:
        options = {"n": 160, "max_angle": 0.2, "width_factor": 0.08}
        options.update(opts)
        result = convert(fn(), **options)
        result["title"] = title
        result["note"] = note
        cards.append(result)
    rows = []
    for c in cards:
        rows.append(f'''<section class="card">
  <div class="art">{figure(c)}</div>
  <h3>{c['title']}</h3>
  <p class="src">{c['note']}</p>
  <p class="note">α = {c['alpha_deg']:.3f}° · triangle {c['triangle']} · {c['chords']} chords
  · width {c['width']:.3f} · polygon max/rms {c['poly_max']:.4f}/{c['poly_rms']:.4f}
  · cubic max/rms {c['cubic_max']:.4f}/{c['cubic_rms']:.4f}</p>
</section>''')
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Euler sections from C curves — p-triple polygons and cubic rails</title>
<style>
body{{margin:0;background:#f6f1e4;color:{INK};font:16px/1.55 Georgia,serif}}
main{{max-width:1120px;margin:0 auto;padding:34px 22px 70px}}
h1{{font-size:28px;margin:0 0 4px}}
.lead{{color:#8c6a21;margin:0 0 18px}}
.panel{{background:{PAPER};border:1px solid #d8ccae;padding:16px 18px;margin:0 0 18px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.card{{background:{PAPER};border:1px solid #d8ccae;padding:10px}}
.art{{margin:0 0 8px}}
svg{{display:block;width:100%;height:auto}}
h3{{font:600 14px/1.3 Georgia,serif;margin:0 0 2px}}
.src,.note{{font:10px/1.4 ui-monospace,Menlo,monospace;color:{MUTED};margin:0}}
.note{{color:#a08a64}}
.legend{{display:flex;gap:16px;flex-wrap:wrap;font:11px ui-monospace,Menlo,monospace;
color:{MUTED};margin:0 0 14px}}
.sw{{display:inline-block;width:20px;height:0;border-top:3px solid {INK};margin-right:5px;vertical-align:middle}}
.sw.t{{border-top:2px solid {GREY}}}.sw.b{{border-top:2px solid {BLUE}}}
.sw.r{{border-top:2px solid {RED}}}.sw.c{{border-top:2px dashed {GOLD}}}
@media(max-width:720px){{.grid{{grid-template-columns:1fr}}}}
</style></head><body><main>
<h1>Euler sections from C curves</h1>
<p class="lead">The p-triple route: a rational Euler polygon, exact rational
miter rails, and a cubic seam for the canvas.</p>
<div class="panel">
<p><strong>The order.</strong> The C curve is sampled at equal arc length and
rotated so its first chord is east. A primitive triangle angle is chosen with
<code>for_angle</code>; each chord's heading change is quantized to whole
triangle turns. The resulting <code>Spiral</code> is the exact rational Euler
polygon. Its rails are the exact rational miter offsets from
<code>ribbon.rails</code>; the cubic seam from <code>spans.spans</code> is the
drawing approximation. Grey = target C curve, ink = polygon, blue/red = rails,
gold = cubic seam.</p>
<p>The polygon and its rails are exact. The target curve and the cubic drawing
are approximations; the card carries both margins. Cusps and loops are split
before conversion; these cards show one smooth section each. The full family
still needs the cusp/loop splits.</p>
</div>
<div class="legend">
<span><i class="sw t"></i> target C curve</span>
<span><i class="sw"></i> p-triple polygon</span>
<span><i class="sw b"></i> + rail</span>
<span><i class="sw r"></i> − rail</span>
<span><i class="sw c"></i> cubic seam</span>
</div>
<div class="grid">{"".join(rows)}</div>
</main></body></html>
'''
    out = ROOT / "workbench" / "euler-sections.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    for c in cards:
        print(f"  {c['title']}: α {c['alpha_deg']:.3f}°, poly {c['poly_max']:.4f}, cubic {c['cubic_max']:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
