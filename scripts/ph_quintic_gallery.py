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


def gallery():
    cols, rows = 8, 6
    pw, ph, gap = 105, 105, 8
    W = 22 + cols * pw + (cols - 1) * gap + 22
    H = 70 + rows * (ph + 26) + 14
    out = [f'<text x="22" y="24" font-size="14" font-weight="600" fill="{INK}">Fig. G1 · 48 PH quintics: 24 S curves, 24 C curves</text>',
           f'<text x="22" y="43" font-size="12" fill="{MUTED}">u and v on a 1/5 grid in ±2 · red ring: the inflection · the number matches the table below</text>']
    for idx, (u, v) in enumerate(CASES):
        cx = 22 + (idx % cols) * (pw + gap)
        cy = 70 + (idx // cols) * (ph + 26)
        pts = uv_samples(u, v, 160)
        xs = [q[1] for q in pts]
        ys = [q[2] for q in pts]
        x0, x1 = min(xs), max(xs)
        y0, y1 = min(ys), max(ys)
        sc = min(pw / max(1e-9, x1 - x0), ph / max(1e-9, y1 - y0))
        ox = cx + (pw - (x1 - x0) * sc) / 2
        oy = cy + (ph - (y1 - y0) * sc) / 2

        def fx(val):
            return ox + (val - x0) * sc

        def fy(val):
            return oy + (y1 - val) * sc

        out.append(f'<rect x="{cx}" y="{cy}" width="{pw}" height="{ph}" fill="none" stroke="{RULE}"/>')
        out.append(f'<line x1="{fx(0):.1f}" y1="{cy}" x2="{fx(0):.1f}" y2="{cy+ph}" stroke="{RULE}"/>')
        out.append(f'<line x1="{cx}" y1="{fy(0):.1f}" x2="{cx+pw}" y2="{fy(0):.1f}" stroke="{RULE}"/>')
        d = " ".join(("M" if i == 0 else "L") + f"{fx(q[1]):.1f},{fy(q[2]):.1f}"
                     for i, q in enumerate(pts))
        out.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="1.6"/>')
        infl, pitch, end, swing = s_info(u, v)
        if infl is not None and 0 < infl < 1:
            x, y = uv_curve(u, v)
            tx = sum(c * F(str(infl)).limit_denominator(1000) ** k for k, c in enumerate(x))
            ty = sum(c * F(str(infl)).limit_denominator(1000) ** k for k, c in enumerate(y))
            out.append(f'<circle cx="{fx(float(tx)):.1f}" cy="{fy(float(ty)):.1f}" r="3.4" fill="{PAPER}" stroke="{RED}" stroke-width="1.8"/>')
        out.append(f'<text x="{cx+4}" y="{cy+ph+13}" font-size="10" font-weight="600" fill="{INK}">{idx+1}</text>')
        tag = shape(u, v)
        out.append(f'<text x="{cx+18}" y="{cy+ph+13}" font-size="10" fill="{MUTED}">{tag} · pitch {pitch}</text>')
    return svg(W, H, ("48 PH quintics", "".join(out)))


def _k(u, v, t):
    U = sum(c * F(t) ** k for k, c in enumerate(u))
    V = sum(c * F(t) ** k for k, c in enumerate(v))
    dU = sum(k * c * F(t) ** (k - 1) for k, c in enumerate(u) if k)
    dV = sum(k * c * F(t) ** (k - 1) for k, c in enumerate(v) if k)
    xp = U * U - V * V
    yp = 2 * U * V
    xpp = 2 * (U * dU - V * dV)
    ypp = 2 * (dU * V + U * dV)
    return (xp * ypp - yp * xpp) / ((xp * xp + yp * yp) ** 1.5)


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


def heading_range(u, v):
    """How far the heading swings over the span, in degrees."""
    import math
    ang = []
    for i in range(201):
        t = i / 200
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
    return max(out) - min(out)


def s_quality(u, v):
    """Lower is a cleaner S: middle inflection, balanced bend, square aspect."""
    import math
    infl, pitch, end, swing = s_info(u, v)
    if infl is None:
        return 1e9
    k0 = abs(float(_k(u, v, 0.0)))
    k1 = abs(float(_k(u, v, 1.0)))
    if min(k0, k1) <= 0:
        return 1e9
    pts = uv_samples(u, v, 60)
    xs = [q[1] for q in pts]
    ys = [q[2] for q in pts]
    asp = (max(xs) - min(xs)) / max(1e-9, max(ys) - min(ys))
    hr = heading_range(u, v)
    if hr < 35 or not (0.5 < asp < 2.0):
        return 1e9
    return abs(infl - 0.5) + 0.005 * abs(hr - 80) + 0.2 * abs(math.log(asp))


def fig_s_set(cases, tag, sub):
    """Four S curves at a time, 2 by 2, with room for the tangent bars."""
    cols = 2
    rows = (len(cases) + 1) // 2
    pw, ph, gapx, gapy = 430, 300, 20, 26
    W = 22 + cols * pw + (cols - 1) * gapx + 22
    H = 84 + rows * (ph + 34) + 14
    out = [f'<text x="22" y="24" font-size="14" font-weight="600" fill="{INK}">{tag} · {sub}</text>',
           f'<text x="22" y="43" font-size="12" fill="{MUTED}">one scale for x and y · the curve sits inside a margin so the blue pen strokes never touch it</text>',
           f'<text x="22" y="60" font-size="11" fill="{MUTED}">red ring: the inflection · blue: the tangent at each end, drawn to the side</text>']
    for idx, (u, v) in enumerate(cases):
        cx = 22 + (idx % cols) * (pw + gapx)
        cy = 84 + (idx // cols) * (ph + gapy + 8)
        pts = uv_samples(u, v, 300)
        xs = [q[1] for q in pts]
        ys = [q[2] for q in pts]
        x0, x1 = min(xs), max(xs)
        y0, y1 = min(ys), max(ys)
        m = 44
        iw, ih = pw - 2 * m, ph - 2 * m
        sc = min(iw / max(1e-9, x1 - x0), ih / max(1e-9, y1 - y0))
        ox = cx + m + (iw - (x1 - x0) * sc) / 2
        oy = cy + m + (ih - (y1 - y0) * sc) / 2

        def fx(val):
            return ox + (val - x0) * sc

        def fy(val):
            return oy + (y1 - val) * sc

        infl, pitch, end, swing = s_info(u, v)
        out.append(f'<rect x="{cx}" y="{cy}" width="{pw}" height="{ph}" fill="none" stroke="{RULE}"/>')
        d = " ".join(("M" if i == 0 else "L") + f"{fx(q[1]):.1f},{fy(q[2]):.1f}"
                     for i, q in enumerate(pts))
        out.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="2.4"/>')
        # end tangents, drawn to the side
        U0, V0 = float(u[0]), float(v[0])
        U1, V1 = float(sum(u)), float(sum(v))
        for (px, py, U, V) in ((0.0, 0.0, U0, V0),
                               (float(sum(uv_curve(u, v)[0])), float(sum(uv_curve(u, v)[1])), U1, V1)):
            dx, dy = U * U - V * V, 2 * U * V
            n = max(1e-9, (dx * dx + dy * dy) ** .5)
            sx, sy = dx / n, -dy / n
            nx, ny = -sy, sx
            ex, ey = fx(px), fy(py)
            pcx, pcy = cx + pw / 2, cy + ph / 2
            if ((ex + nx * 14 - pcx) ** 2 + (ey + ny * 14 - pcy) ** 2 >
                    (ex - nx * 14 - pcx) ** 2 + (ey - ny * 14 - pcy) ** 2):
                nx, ny = -nx, -ny
            bx, by = ex + nx * 14, ey + ny * 14
            L = 0.16 * max(x1 - x0, y1 - y0) * sc
            ex2, ey2 = bx + sx * L, by + sy * L
            lo_x, hi_x = cx + 6, cx + pw - 6
            lo_y, hi_y = cy + 6, cy + ph - 6
            bx, by = min(max(bx, lo_x), hi_x), min(max(by, lo_y), hi_y)
            ex2, ey2 = min(max(ex2, lo_x), hi_x), min(max(ey2, lo_y), hi_y)
            out.append(f'<line x1="{bx:.1f}" y1="{by:.1f}" x2="{ex2:.1f}" y2="{ey2:.1f}" '
                       f'stroke="{BLUE}" stroke-width="2.2" stroke-linecap="round"/>')
        x, y = uv_curve(u, v)
        ti = F(str(infl)).limit_denominator(400)
        tx = sum(c * ti ** k for k, c in enumerate(x))
        ty = sum(c * ti ** k for k, c in enumerate(y))
        out.append(f'<circle cx="{fx(float(tx)):.1f}" cy="{fy(float(ty)):.1f}" r="5" fill="{PAPER}" stroke="{RED}" stroke-width="2.2"/>')
        out.append(f'<text x="{cx}" y="{cy+ph+18}" font-size="12" font-weight="600" fill="{INK}">{idx+1}</text>')
        out.append(f'<text x="{cx+34}" y="{cy+ph+18}" font-size="11" fill="{MUTED}">inflection {infl:.2f} · pitch {pitch}</text>')
    return svg(W, H, (tag, "".join(out)))


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
{fig_s_set(S2_CASES, "Fig. G2", "twelve S curves, two beside each other, six rows")}
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
