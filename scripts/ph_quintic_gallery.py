"""PH quintic gallery: u and v on a 1/5 grid in ±2, S and C curves.

    .venv/bin/python scripts/ph_quintic_gallery.py
    open workbench/ph-quintic-gallery.html

Each case is r'(t) = (u² − v², 2uv) with u, v quadratic. The S cases have the
Wronskian root strictly inside (0,1); the C cases have it at the start or not
at all. Every case is PH (exact offsets, degree 5), and the pitch is the grid
that makes the coordinates whole at integer t.
"""

from __future__ import annotations

import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from ph_quintic_lattice import (  # noqa: E402
    Frame, PAPER, INK, MUTED, RULE, RED, BLUE, GOLD, svg,
    uv_curve, uv_samples, s_info, _fmt,
)

S_CASES = [
    ((F(-8,5), -1, F(4,5)), (-1, F(7,5), F(-8,5))),  # infl 0.47 sides 24/27 pitch 125
    ((-2, 1, 0), (F(-4,5), F(-7,5), 2)),  # infl 0.52 sides 24/45 pitch 75
    ((F(1,5), F(8,5), F(-8,5)), (F(-9,5), F(9,5), F(-9,5))),  # infl 0.5 sides 35/35 pitch 250
    ((F(4,5), F(-8,5), F(6,5)), (F(6,5), F(-1,5), F(-4,5))),  # infl 0.52 sides 31/90 pitch 375
    ((0, 1, F(-9,5)), (F(-1,5), F(-3,5), F(1,5))),  # infl 0.22 sides 45/151 pitch 125
    ((0, 2, -1), (F(1,5), F(8,5), F(7,5))),  # infl 0.26 sides 65/30 pitch 375
    ((F(3,5), F(1,5), F(2,5)), (F(1,5), -1, 2)),  # infl 0.26 sides 24/77 pitch 375
    ((F(-1,5), -1, F(4,5)), (F(4,5), 0, F(8,5))),  # infl 0.33 sides 21/30 pitch 375
    ((F(1,5), 2, F(-2,5)), (F(1,5), F(-2,5), F(7,5))),  # infl 0.31 sides 60/37 pitch 125
    ((F(3,5), F(-9,5), F(9,5)), (1, F(-8,5), F(2,5))),  # infl 0.36 sides 19/174 pitch 250
    ((F(-1,5), F(-7,5), F(7,5)), (-1, F(1,5), F(-1,5))),  # infl 0.5 sides 38/38 pitch 375
    ((0, -2, F(8,5)), (F(2,5), F(-6,5), F(7,5))),  # infl 0.47 sides 152/85 pitch 375
    ((F(-1,5), F(4,5), F(-8,5)), (0, F(-8,5), F(1,5))),  # infl 0.35 sides 156/47 pitch 375
    ((F(6,5), -2, 2), (F(-8,5), F(-2,5), F(4,5))),  # infl 0.46 sides 27/43 pitch 375
    ((1, F(-4,5), 1), (F(-3,5), F(8,5), F(-7,5))),  # infl 0.59 sides 43/18 pitch 375
    ((F(-2,5), F(-8,5), F(8,5)), (F(4,5), -2, F(9,5))),  # infl 0.54 sides 93/78 pitch 375
    ((F(-2,5), 1, -1), (F(4,5), F(2,5), F(-2,5))),  # infl 0.5 sides 34/34 pitch 250
    ((F(7,5), F(-8,5), F(6,5)), (0, F(-9,5), F(8,5))),  # infl 0.59 sides 60/37 pitch 375
    ((F(6,5), -1, F(3,5)), (F(-2,5), F(-6,5), F(8,5))),  # infl 0.47 sides 34/71 pitch 250
    ((F(-3,5), F(8,5), F(-8,5)), (1, F(-2,5), F(3,5))),  # infl 0.51 sides 38/29 pitch 375
    ((F(8,5), F(6,5), F(-2,5)), (F(-4,5), F(8,5), -2)),  # infl 0.45 sides 27/27 pitch 375
    ((0, F(-8,5), F(7,5)), (1, F(-4,5), F(2,5))),  # infl 0.64 sides 69/32 pitch 375
    ((F(3,5), F(-4,5), F(7,5)), (F(-2,5), F(-4,5), F(8,5))),  # infl 0.27 sides 24/128 pitch 375
    ((F(-3,5), 0, -2), (F(-1,5), F(-6,5), F(4,5))),  # infl 0.29 sides 27/38 pitch 375
]

C_CASES = [
    ((1, F(-7,5), 2), (F(1,5), -2, F(-6,5))),  # infl 0.9 swing 147 pitch 375
    ((F(-3,5), F(2,5), F(-6,5)), (F(-1,5), F(-1,5), F(6,5))),  # infl 0.11 swing 99 pitch 375
    ((-1, 0, F(-4,5)), (F(-1,5), F(2,5), F(-6,5))),  # infl 0.19 swing 40 pitch 375
    ((F(-1,5), F(2,5), F(-7,5)), (F(-2,5), F(4,5), F(-3,5))),  # infl 0.0 swing 108 pitch 375
    ((F(-6,5), -2, F(-8,5)), (-1, F(4,5), F(-7,5))),  # infl 0.83 swing 43 pitch 375
    ((F(-2,5), F(-8,5), F(-6,5)), (-1, F(7,5), F(-8,5))),  # infl 0.86 swing 96 pitch 375
    ((F(3,5), F(3,5), 2), (F(-3,5), F(-6,5), F(6,5))),  # infl 0.09 swing 71 pitch 125
    ((0, F(-2,5), F(9,5)), (1, 0, 2)),  # infl 0.11 swing 53 pitch 125
    ((-1, F(-8,5), -1), (F(2,5), -2, F(2,5))),  # infl 1.0 swing 80 pitch 125
    ((2, F(-3,5), F(-4,5)), (F(-3,5), F(4,5), F(-8,5))),  # infl 0.18 swing 103 pitch 375
    ((F(3,5), F(2,5), F(-3,5)), (0, F(2,5), F(-9,5))),  # infl 0.11 swing 152 pitch 375
    ((1, 0, F(8,5)), (0, 0, F(-7,5))),  # infl 0.0 swing 57 pitch 375
    ((0, F(6,5), 0), (1, F(-1,5), 1)),  # infl 1.0 swing 67 pitch 50
    ((F(-3,5), -1, -2), (F(-4,5), 1, F(-6,5))),  # infl 0.99 swing 75 pitch 125
    ((-2, 1, F(4,5)), (-1, F(4,5), F(-2,5))),  # infl 0.2 swing 91 pitch 375
    ((2, F(4,5), F(-2,5)), (-1, -1, F(8,5))),  # infl 0.21 swing 37 pitch 375
    ((F(7,5), 2, F(-4,5)), (F(7,5), -2, F(6,5))),  # infl 0.89 swing 65 pitch 375
    ((F(7,5), F(2,5), F(-6,5)), (F(-6,5), F(7,5), F(-2,5))),  # infl 0.96 swing 45 pitch 125
    ((0, -2, F(1,5)), (F(-4,5), F(-8,5), F(-6,5))),  # infl 0.71 swing 55 pitch 375
    ((F(-9,5), F(2,5), F(-6,5)), (F(4,5), F(1,5), F(-4,5))),  # infl 0.14 swing 41 pitch 375
    ((F(7,5), 1, F(3,5)), (F(-2,5), F(1,5), F(-9,5))),  # infl 0.14 swing 38 pitch 375
    ((0, F(-8,5), F(3,5)), (F(-2,5), -2, F(2,5))),  # infl 0.72 swing 55 pitch 375
    ((-1, F(2,5), F(-2,5)), (F(9,5), F(4,5), -2)),  # infl 0.29 swing 66 pitch 375
    ((F(-9,5), 0, -2), (F(-4,5), F(-6,5), F(9,5))),  # infl 0.21 swing 48 pitch 375
]

S2_CASES = [
    ((F(3,5), F(-4,5), F(2,5)), (F(3,5), F(4,5), F(-6,5))),
    ((0, F(-6,5), F(6,5)), (F(-4,5), F(7,5), F(-6,5))),
    ((F(2,5), F(-8,5), 2), (F(4,5), F(-3,5), F(7,5))),
    ((F(-1,5), -2, 2), (F(-7,5), -1, F(4,5))),
    ((F(-6,5), F(7,5), F(-7,5)), (F(-4,5), F(9,5), F(-9,5))),
    ((F(-7,5), F(-8,5), F(7,5)), (-1, F(9,5), F(-8,5))),
    ((F(7,5), F(6,5), -1), (-1, F(7,5), F(-7,5))),
    ((F(1,5), F(-4,5), F(8,5)), (F(1,5), F(2,5), F(8,5))),
    ((F(-6,5), 2, F(-9,5)), (F(-2,5), F(-3,5), 1)),
    ((0, -2, F(8,5)), (F(-4,5), F(-6,5), F(-4,5))),
    ((F(-9,5), F(9,5), F(-4,5)), (F(3,5), F(3,5), -1)),
    ((F(6,5), F(-8,5), F(7,5)), (F(4,5), -2, 2)),
]

CASES = S_CASES + C_CASES


def theta_curve(u, v, n=200):
    import math
    ang = []
    for i in range(n + 1):
        t = i / n
        U = sum(float(c) * t ** k for k, c in enumerate(u))
        V = sum(float(c) * t ** k for k, c in enumerate(v))
        ang.append(math.degrees(math.atan2(2 * U * V, U * U - V * V)))
    out = [ang[0]]
    for a in ang[1:]:
        while a - out[-1] > 180:
            a -= 360
        while a - out[-1] < -180:
            a += 360
        out.append(a)
    return out


def shape(u, v):
    """S if the heading swings on both sides of the inflection, C if one-sided."""
    infl, pitch, end, swing = s_info(u, v)
    th = theta_curve(u, v)
    if infl is None:
        return "C"
    k = min(len(th) - 1, max(0, round(infl * (len(th) - 1))))
    s0 = abs(th[k] - th[0])
    s1 = abs(th[-1] - th[k])
    if max(th) - min(th) >= 180:
        return "loop"
    return "S" if min(s0, s1) >= 15 else "C"


def panel_svg(u, v, idx, w, h, label, off_scale=1.0):
    """One self-contained SVG for one curve; CSS lays them out."""
    m = 0.11 * w
    cw, ch = w - 2 * m, h - 2 * m - 20
    pts = uv_samples(u, v, 260)
    xs = [q[1] for q in pts]
    ys = [q[2] for q in pts]
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    sc = min(cw / max(1e-9, x1 - x0), ch / max(1e-9, y1 - y0))
    ox = m + (cw - (x1 - x0) * sc) / 2
    oy = m + (ch - (y1 - y0) * sc) / 2

    def fx(val):
        return ox + (val - x0) * sc

    def fy(val):
        return oy + (y1 - val) * sc

    infl, pitch, end, swing = s_info(u, v)
    tag = shape(u, v)
    out = [f'<rect x="1" y="1" width="{w-2}" height="{h-2}" fill="{PAPER}" stroke="{RULE}"/>']
    d = " ".join(("M" if i == 0 else "L") + f"{fx(q[1]):.1f},{fy(q[2]):.1f}"
                 for i, q in enumerate(pts))
    out.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{1.8 if w < 300 else 2.4}"/>')
    U0, V0 = float(u[0]), float(v[0])
    U1, V1 = float(sum(u)), float(sum(v))
    off = (8.0 if w < 300 else 14.0) * off_scale
    for (px, py, U, V, sgn) in ((0.0, 0.0, U0, V0, -1),
                                (float(sum(uv_curve(u, v)[0])), float(sum(uv_curve(u, v)[1])), U1, V1, 1)):
        dx, dy = U * U - V * V, 2 * U * V
        n = max(1e-9, (dx * dx + dy * dy) ** .5)
        sx, sy = sgn * dx / n, -sgn * dy / n     # outward from the curve's end
        nx, ny = -sy, sx
        ex, ey = fx(px), fy(py)
        pcx, pcy = w / 2, (h - 20) / 2
        if ((ex + nx * off - pcx) ** 2 + (ey + ny * off - pcy) ** 2 >
                (ex - nx * off - pcx) ** 2 + (ey - ny * off - pcy) ** 2):
            nx, ny = -nx, -ny
        gap = 4.0
        bx, by = ex + sx * gap + nx * off, ey + sy * gap + ny * off
        L = 0.14 * max(x1 - x0, y1 - y0) * sc
        ex2, ey2 = bx + sx * L, by + sy * L
        lo_x, hi_x = 5, w - 5
        lo_y, hi_y = 5, h - 25
        bx, by = min(max(bx, lo_x), hi_x), min(max(by, lo_y), hi_y)
        ex2, ey2 = min(max(ex2, lo_x), hi_x), min(max(ey2, lo_y), hi_y)
        out.append(f'<line x1="{bx:.1f}" y1="{by:.1f}" x2="{ex2:.1f}" y2="{ey2:.1f}" '
                   f'stroke="{BLUE}" stroke-width="{1.6 if w < 300 else 2.2}" stroke-linecap="round"/>')
    x, y = uv_curve(u, v)
    ti = F(str(infl)).limit_denominator(400)
    tx = sum(c * ti ** k for k, c in enumerate(x))
    ty = sum(c * ti ** k for k, c in enumerate(y))
    out.append(f'<circle cx="{fx(float(tx)):.1f}" cy="{fy(float(ty)):.1f}" r="{3 if w < 300 else 5}" '
               f'fill="{PAPER}" stroke="{RED}" stroke-width="{1.6 if w < 300 else 2.2}"/>')
    out.append(f'<text x="{m}" y="{h-8}" font-size="{9 if w < 300 else 12}" font-weight="600" fill="{INK}">{idx+1}</text>')
    out.append(f'<text x="{m+16 if w < 300 else m+34}" y="{h-8}" font-size="{8.5 if w < 300 else 11}" fill="{MUTED}">{label}</text>')
    return (f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{tag} curve {idx+1}">'
            + "".join(out) + "</svg>")


def grid_svgs(cases, w, h, cls, labeler):
    return f'<div class="{cls}">' + "".join(
        panel_svg(u, v, i, w, h, labeler(u, v)) for i, (u, v) in enumerate(cases)
    ) + "</div>"


def gallery():
    return grid_svgs(CASES, 200, 220, "g8",
                     lambda u, v: f"{shape(u, v)} · pitch {s_info(u, v)[1]}")


def fig_s_set():
    return grid_svgs(S2_CASES, 430, 340, "g2",
                     lambda u, v: f"inflection {s_info(u, v)[0]:.2f} · pitch {s_info(u, v)[1]}")


def table():
    rows = []
    for idx, (u, v) in enumerate(CASES):
        infl, pitch, end, swing = s_info(u, v)
        tag = shape(u, v)
        where = "—" if infl is None else ("start" if infl <= 0.001 else
                                          "end" if infl >= 0.999 else f"{infl:.2f}")
        rows.append(f"<tr><td>{idx+1}</td><td>{tag}</td><td>{_fmt(u)}</td><td>{_fmt(v)}</td>"
                    f"<td>{where}</td><td>{pitch}</td><td>({end[0]*pitch}, {end[1]*pitch})</td></tr>")
    return "\n".join(rows)


def build():
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PH quintic gallery: S and C curves on a 1/5 grid</title>
<style>
:root{{--paper:{PAPER};--ink:{INK};--muted:{MUTED};--rule:{RULE}}}
*{{box-sizing:border-box}} body{{margin:0;background:#f3eddf;color:var(--ink);font:16px/1.55 Georgia,serif}}
main{{max-width:1120px;margin:0 auto;padding:34px 22px 70px}}
.eyebrow{{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}}
h1{{font-size:31px;line-height:1.12;margin:0 0 8px}} h2{{font-size:20px;margin:0 0 8px}}
.lede{{max-width:900px;color:var(--muted)}}
.panel{{background:var(--paper);border:1px solid var(--rule);padding:16px 18px;margin:0 0 18px}}
table{{border-collapse:collapse;font:11px/1.45 ui-monospace,Menlo,monospace;margin:10px 0;width:100%}}
th,td{{border:1px solid var(--rule);padding:3px 6px;text-align:right}} th{{color:var(--muted);font-weight:400}}
.small{{font:12px/1.6 ui-monospace,Menlo,monospace;color:var(--muted)}}
code{{font:12px ui-monospace,Menlo,monospace;background:#f4ecd7;padding:1px 4px}}
.g8{{display:grid;grid-template-columns:repeat(8,1fr);gap:6px}}
.g2{{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}}
.g8 svg,.g2 svg{{width:100%;height:auto;display:block}}
</style></head><body><main>
<p class="eyebrow">curve-lab · PH quintics · gallery</p>
<h1>48 PH quintics: 24 S and 24 C, on a 1/5 grid</h1>
<p class="lede">Every curve here is <code>r′(t) = (u² − v², 2uv)</code> with u and v quadratic and
coefficients on the 1/5 grid in ±2. An <strong>S</strong> bends one way and then the other — the
heading swings at least 15° on each side of the inflection. A <strong>C</strong> bends one way
throughout. All are PH, so the offsets are exact and a span is G3-capable.</p>

<section class="panel">
<h2>Fig. G1 · the grid, 8 by 6</h2>
{gallery()}
<p class="small">Each thumbnail is drawn in its own box; the axes are the curve's own x = 0 and
y = 0. The red ring is the inflection. The pitch under each panel is the grid that makes the
coordinates whole at integer t — the price of the fractions.</p>
</section>

<section class="panel">
<h2>The 48, in numbers</h2>
<table>
<tr><th>#</th><th>S/C</th><th>u</th><th>v</th><th>inflection</th><th>pitch</th><th>endpoint (cells)</th></tr>
{table()}
</table>
<p class="small">The endpoints are exact integers at the stated pitch. The S/C column is the shape
the curve actually makes: S when the heading swings on both sides of the inflection, C when it
bends one way. A dash means the Wronskian has no root in [0,1].</p>
</section>

<section class="panel">
<h2>Fig. G2 · the S curves, enlarged</h2>
{fig_s_set()}
<p class="small">Twelve curves chosen for balance: the heading swings at least 23° on each side of
the inflection. The blue strokes are the end tangents, drawn to the side; the ring is where the
curvature passes through zero.</p>
</section>

<section class="panel">
<h2>Moving the root inside</h2>
<p>The S is the sign change of <code>W = u v′ − v u′</code>. Adding a multiple of u to v does not
change W — the Wronskian is blind to it — so you have to move v in a different direction. Take the
operator's case 1, <code>u = 1 + t/5 + t²</code>, <code>v = t</code>: then W = 1 − t², whose only
root is at t = 1. Replace v by <code>v = (4/9)t</code> and W becomes <code>(4/9)u − t u′</code>,
which vanishes at t = 1/2. The curve turns from a C into an S, at the price of a 9 in the pitch.</p>
<p class="small">That is the design lever in one sentence: choose where you want the turn, then
choose v so that <code>u v′ − v u′</code> vanishes there.</p>
</section>

<section class="panel">
<h2>See also</h2>
<p><a href="ph-quintic-lattice.html">The Tschirnhausen quintic on a coarse lattice</a> — the
integer-t stops, the cut pieces and the grid-cost comparison.
<a href="ph-families.html">PH families, degree by degree</a> — the ladder and the PH–Hermite
interpolant.</p>
<p class="small">Re-derive: <code>python scripts/ph_quintic_gallery.py</code> · test:
<code>python -m unittest tests.test_ph_quintic_gallery</code></p>
</section>
</main></body></html>
"""
    out = ROOT / "workbench" / "ph-quintic-gallery.html"
    out.write_text(html, encoding="utf-8")
    print(out)
    return out


if __name__ == "__main__":
    build()
