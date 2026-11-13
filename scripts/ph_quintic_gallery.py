"""PH quintic gallery: u and v on a 1/5 grid in +/-2, S and C curves.

    .venv/bin/python scripts/ph_quintic_gallery.py
    open workbench/ph-quintic-gallery.html

Each case is r'(t) = (u^2 - v^2, 2uv) with u, v quadratic. The S cases have the
Wronskian root strictly inside (0,1); the C cases have it at the start or not
at all. Every case is PH (exact offsets, degree 5), and the pitch is the grid
that makes the coordinates whole at integer t.
"""

from __future__ import annotations

import sys
import json
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

Q3_CASES = [
    ((0, F(8,5), F(-7,5)), (F(1,5), F(-4,5), F(8,5))),
    ((F(-3,5), F(-3,5), F(6,5)), (F(3,5), F(-9,5), F(8,5))),
    ((0, F(6,5), F(-8,5)), (F(1,5), F(4,5), F(-3,5))),
    ((F(1,5), F(8,5), F(-8,5)), (F(1,5), F(-4,5), F(7,5))),
    ((0, F(-7,5), F(8,5)), (F(-3,5), F(1,5), 0)),
    ((F(2,5), -1, F(8,5)), (F(-2,5), -2, 2)),
    ((F(-1,5), F(1,5), -1), (F(-1,5), F(7,5), -2)),
    ((F(1,5), F(9,5), -2), (1, F(-6,5), 1)),
    ((F(-1,5), F(-1,5), F(-1,5)), (F(-1,5), 1, F(-7,5))),
    ((F(2,5), F(-9,5), 2), (F(-4,5), 1, -1)),
    ((F(-7,5), 2, F(-7,5)), (0, F(8,5), F(-8,5))),
    ((0, F(-8,5), F(8,5)), (F(6,5), F(-8,5), F(9,5))),
]

Q4_CASES = [
    ((-1, F(2,5), 2), (F(-1,10), 2, -1)),
    ((F(-2,5), F(6,5), F(1,5)), (F(-1,2), F(11,10), 2)),
    ((F(9,10), F(-9,5), F(-6,5)), (F(3,10), F(9,10), F(-9,10))),
    ((F(-1,2), F(3,2), -1), (F(17,10), F(-3,5), -2)),
    ((0, 0, F(-4,5)), (F(-3,10), F(3,10), 1)),
    ((F(-1,5), F(13,10), F(1,2)), (F(-3,5), F(9,5), F(-1,2))),
    ((F(4,5), F(1,2), -2), (F(17,10), F(1,10), -2)),
    ((F(-11,10), F(19,10), F(7,10)), (F(-13,10), F(1,5), F(1,2))),
    ((F(-3,2), F(6,5), F(19,10)), (F(-6,5), F(9,5), F(-19,10))),
    ((F(3,10), F(7,10), F(-4,5)), (F(1,10), F(-8,5), F(3,10))),
    ((F(11,10), F(-9,10), F(-4,5)), (F(6,5), F(2,5), F(-9,10))),
    ((F(-11,10), -1, F(-1,10)), (F(4,5), F(-6,5), F(-8,5))),
]

Q5_CASES = [
    ((0, F(8,5), F(-6,5)), (1, -1, F(8,5))),
    ((F(-9,10), F(-11,10), 2), (F(7,10), F(-9,5), F(3,2))),
    ((-1, F(19,10), -2), (F(8,5), F(17,10), -2)),
    ((F(3,5), F(2,5), F(-1,2)), (0, -2, 2)),
    ((F(-1,2), F(3,10), F(-2,5)), (F(-3,5), F(-19,10), F(9,5))),
    ((F(1,5), F(3,2), F(-17,10)), (F(9,10), F(-1,10), F(-3,10))),
    ((F(2,5), F(1,2), -1), (F(7,5), -2, 1)),
    ((F(-9,10), F(13,10), F(-3,2)), (F(-4,5), -2, F(3,2))),
    ((F(11,10), F(-9,10), 1), (F(-3,5), 2, -2)),
    ((F(1,2), F(-8,5), 2), (F(1,5), F(1,5), F(4,5))),
    ((F(4,5), F(-9,5), F(17,10)), (F(-7,5), F(-2,5), F(1,2))),
    ((F(-6,5), F(-11,10), 1), (F(7,10), F(-3,2), F(3,2))),
((F(-3,5), F(19,10), F(-9,5)), (F(1,10), F(3,10), F(-2,5))),  # infl 0.508 sides 94/113 pitch 500
    ((F(4,5), F(-11,10), 1), (F(-1,5), F(-13,10), F(3,2))),  # infl 0.479 sides 59/87 pitch 600
    ((F(3,10), F(-11,10), 1), (F(-1,2), F(2,5), 0)),  # infl 0.552 sides 63/128 pitch 300
    ((F(-1,5), F(-8,5), F(8,5)), (-1, F(9,5), -2)),  # infl 0.472 sides 68/71 pitch 375
    ((F(-1,2), F(3,2), F(-7,5)), (F(-2,5), F(1,10), F(-1,5))),  # infl 0.546 sides 75/50 pitch 500
    ((F(1,5), F(-13,10), F(4,5)), (F(2,5), F(-11,10), F(8,5))),  # infl 0.5 sides 143/53 pitch 250
    ((F(-13,10), F(9,5), -2), (0, -2, 2)),  # infl 0.482 sides 58/58 pitch 300
    ((F(1,10), F(4,5), F(-7,10)), (F(-1,5), F(2,5), F(-2,5))),  # infl 0.525 sides 93/56 pitch 500
    ((F(-1,5), F(7,5), -1), (F(3,5), F(-17,10), 2)),  # infl 0.516 sides 127/65 pitch 300
    ((0, F(9,5), -2), (F(-9,10), F(1,10), F(1,2))),  # infl 0.539 sides 58/125 pitch 600
    ((F(3,5), F(-9,5), F(19,10)), (0, F(9,5), F(-3,2))),  # infl 0.5 sides 143/97 pitch 250
    ((F(1,2), F(11,10), F(-7,5)), (F(7,10), F(-19,10), 2)),  # infl 0.459 sides 70/113 pitch 500
    ((F(7,10), F(4,5), F(-4,5)), (F(-3,5), F(9,5), F(-9,5))),  # infl 0.5 sides 62/62 pitch 500
    ((F(3,5), F(-17,10), 2), (F(2,5), 1, F(-3,5))),  # infl 0.462 sides 76/60 pitch 500
    ((F(-4,5), F(-9,5), 2), (F(3,5), F(-8,5), F(3,2))),  # infl 0.52 sides 57/63 pitch 100
    ((F(4,5), F(-9,5), F(3,2)), (F(1,10), F(6,5), F(-3,2))),  # infl 0.508 sides 85/143 pitch 100
]

Q6_CASES = [
    ((F(-4,5), F(17,10), F(-9,5)), (F(-4,5), F(-19,10), F(17,10))),
    ((F(3,2), F(-19,10), F(19,10)), (F(1,5), F(17,10), F(-17,10))),
    ((F(7,10), F(-7,10), F(7,10)), (0, F(-9,5), F(9,5))),
    ((F(1,2), F(4,5), F(-4,5)), (F(-1,2), F(13,10), F(-13,10))),
    ((F(2,5), F(-3,2), F(3,2)), (F(-7,10), F(7,10), F(-4,5))),
    ((F(1,5), F(1,5), F(-1,5)), (F(3,10), -1, 1)),
    ((F(4,5), F(-17,10), F(17,10)), (-1, -1, 1)),
    ((F(1,10), F(-8,5), F(8,5)), (F(4,5), F(-4,5), F(4,5))),
    ((F(7,10), F(3,2), F(-3,2)), (F(4,5), F(-9,5), F(17,10))),
    ((F(-7,10), F(-13,10), F(6,5)), (F(-1,2), F(11,10), F(-6,5))),
    ((F(3,10), F(1,10), F(-1,10)), (F(-1,10), F(11,10), F(-11,10))),
    ((F(4,5), F(9,5), -2), (F(-9,10), F(17,10), F(-3,2))),
    ((F(-1,5), F(7,5), F(-7,5)), (F(-2,5), F(8,5), F(-8,5))),
    ((F(-3,10), F(9,5), F(-9,5)), (F(-1,5), 2, F(-19,10))),
    ((F(1,5), F(-19,10), F(19,10)), (F(2,5), F(-3,2), F(8,5))),
    ((F(-3,10), F(19,10), -2), (F(-1,2), F(17,10), F(-9,5))),
]

BALANCED = [(0, 2), (0, 3), (0, 4), (0, 8),
            (1, 2), (1, 3), (1, 6), (1, 8),
            (2, 2), (2, 4), (2, 6), (2, 8)]

Q6B_CASES = [((F(1), F(-a), F(a)), (F(0), F(-b), F(b))) for a, b in BALANCED]

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
        r = 9.0 if w < 300 else 17.0
        gap = 5.0
        cxb, cyb = ex + sx * (gap + r) + nx * off * 0.6, ey + sy * (gap + r) + ny * off * 0.6
        lo_x, hi_x = r + 4, w - r - 4
        lo_y, hi_y = r + 4, h - 25 - r
        cxb, cyb = min(max(cxb, lo_x), hi_x), min(max(cyb, lo_y), hi_y)
        # the compass: a blue ring with the tangent drawn as a diameter
        out.append(f'<circle cx="{cxb:.1f}" cy="{cyb:.1f}" r="{r}" fill="{BLUE}" fill-opacity="0.07" '
                   f'stroke="{BLUE}" stroke-width="{1.2 if w < 300 else 1.8}"/>')
        out.append(f'<line x1="{cxb - sx * r * 0.62:.1f}" y1="{cyb - sy * r * 0.62:.1f}" '
                   f'x2="{cxb + sx * r * 0.62:.1f}" y2="{cyb + sy * r * 0.62:.1f}" '
                   f'stroke="{BLUE}" stroke-width="{1.6 if w < 300 else 2.4}" stroke-linecap="round"/>')
    if infl is not None:
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
                     lambda u, v: f"{shape(u, v)} | pitch {s_info(u, v)[1]}")

def fig_s_set():
    return grid_svgs(S2_CASES, 430, 340, "g2", s_label)

def fig_q3():
    return grid_svgs(Q3_CASES, 430, 340, "g2", s_label)

def fig_q4():
    def label(u, v):
        infl, pitch, end, swing = s_info(u, v)
        th = theta_curve(u, v)
        return f"swing {max(th) - min(th):.0f} deg | pitch {pitch}"

    return grid_svgs(Q4_CASES, 430, 340, "g2", label)

def s_label(u, v):
    infl, pitch, end, swing = s_info(u, v)
    th = theta_curve(u, v)
    k = min(len(th) - 1, max(0, round(infl * (len(th) - 1))))
    mn = min(abs(th[k] - th[0]), abs(th[-1] - th[k]))
    return f"infl {infl:.2f} | swing {mn:.0f} deg | pitch {pitch}"

def fig_q5():
    return grid_svgs(Q5_CASES, 430, 340, "g2", s_label)

def fig_q6():
    return grid_svgs(Q6_CASES, 430, 340, "g2", s_label)

def fig_q6b():
    return grid_svgs(Q6B_CASES, 430, 340, "g2", s_label)

def table():
    rows = []
    for idx, (u, v) in enumerate(CASES):
        infl, pitch, end, swing = s_info(u, v)
        tag = shape(u, v)
        where = " - " if infl is None else ("start" if infl <= 0.001 else
                                          "end" if infl >= 0.999 else f"{infl:.2f}")
        rows.append(f"<tr><td>{idx+1}</td><td>{tag}</td><td>{_fmt(u)}</td><td>{_fmt(v)}</td>"
                    f"<td>{where}</td><td>{pitch}</td><td>({end[0]*pitch}, {end[1]*pitch})</td></tr>")
    return "\n".join(rows)

EXTRA = r"""

<section class="panel">
<h2>Fig. Q7 | the sliders: b sets the size, morphLambda sets the bend</h2>
<p><strong>b</strong> sets the scale of the exact S. <strong>a</strong> shifts where the bend sits.
<strong>morphLambda</strong> is the bend: it takes the exact family's speed recipes and adds a growing share
of the simplified curve 15's, the two-lobe S. morphLambda = 0 is the exact S; morphLambda = 1 is the target. The
starting recipe carries <code>c = 1</code>  -  a free nudge: it adds nothing to the pitch and takes the
bend from 1.09 to 1.15.</p>
<p>In plain words: <strong>bend is the arc length divided by the straight-line distance between the
ends</strong>. A straight line is 1.00; the gentle exact S is about 1.09; the target is about 5.6.
morphLambda does not scale the curve  -  it changes its shape, pulling the ends round into the two lobes. The
target is the simplified curve 15: <code>u = 0.2 - 2t + 2t^2</code>,
<code>v = 0.4 - 1.5t + 1.6t^2</code>, the clearest S of the six candidates tested.</p>
<p class="code-names">In the code: <code>b</code> is <code>scaleB</code>, <code>a</code> is
<code>shiftA</code>, <code>morphLambda</code> is <code>morphLambda</code>, the two recipes are
<code>speedX</code> and <code>speedY</code>, and their far ends are <code>targetSpeedX</code> and
<code>targetSpeedY</code>.</p>
<div class="slider-row">
  <label>b <input id="q7-scale-b" type="range" min="0.5" max="8" step="0.1" value="4"></label>
  <label>a <input id="q7-shift-a" type="range" min="-1" max="3" step="0.1" value="0"></label>
  <label>morphLambda <input id="q7-morph-lambda" type="range" min="0" max="1" step="0.01" value="0"></label>
  <span id="q7-readout" class="small"></span>
</div>
<svg id="q7-plot" viewBox="0 0 900 420" role="img" aria-label="the balanced family, live"></svg>
<p class="save-row"><button type="button" class="save-curve" data-panel="q7">save this curve</button></p>

</section>

<section class="panel">
<h2>Fig. Q8 | the recipe playground</h2>
<p>Six numbers, one curve  -  type them or drag the sliders. <code>u</code> and <code>v</code> are
the two speed recipes; <code>r(t) = integral of (u + i v)^2 dt</code>. The readout gives the bend (arc / chord)
and the exact pitch for the numbers you type. The pitch is the lcm of the integrated coefficients'
denominators, so a decimal like 1.5 costs more than 2  -  try it.</p>
<p>Two ways to a <strong>bend of 2.00</strong> with small integers: <code>u = 2 - 3t + 3t^2</code>,
<code>v = 2 - 12t + 12t^2</code> (pitch 10, and <code>v = 4u - 6</code>, so the speed path is a
straight segment) or <code>u = 3 - 9t + 9t^2</code>, <code>v = 1 - 15t + 15t^2</code> (pitch 5). The
round decimal recipe <code>u = 0.5 - 0.5t + 0.5t^2</code>, <code>v = 0.7 - 4t + 4t^2</code> is a
stronger S at bend 2.69  -  and at x10 its pitch drops to 2, the cheapest grid in the gallery.</p>
<div class="control-grid">
  <label class="control-row"><span>speedXAtEnds</span><input id="q8-speed-x0" type="number" step="0.05" value="0.2"><input id="q8-speed-x0-slider" type="range" min="-2" max="4" step="0.05" value="0.2"></label>
  <label class="control-row"><span>speedXLinear</span><input id="q8-speed-x1" type="number" step="0.05" value="-2"><input id="q8-speed-x1-slider" type="range" min="-16" max="4" step="0.05" value="-2"></label>
  <label class="control-row"><span>speedXCurvature</span><input id="q8-speed-x2" type="number" step="0.05" value="2"><input id="q8-speed-x2-slider" type="range" min="0" max="16" step="0.05" value="2"></label>
  <label class="control-row"><span>speedYAtEnds</span><input id="q8-speed-y0" type="number" step="0.05" value="0.4"><input id="q8-speed-y0-slider" type="range" min="-2" max="4" step="0.05" value="0.4"></label>
  <label class="control-row"><span>speedYLinear</span><input id="q8-speed-y1" type="number" step="0.05" value="-1.5"><input id="q8-speed-y1-slider" type="range" min="-16" max="4" step="0.05" value="-1.5"></label>
  <label class="control-row"><span>speedYCurvature</span><input id="q8-speed-y2" type="number" step="0.05" value="1.6"><input id="q8-speed-y2-slider" type="range" min="0" max="16" step="0.05" value="1.6"></label>
</div>
<div class="preset-row" id="q8-presets"></div><!--PRESETS-->
<svg id="q8-plot" viewBox="0 0 900 470" role="img" aria-label="the recipe playground"></svg>
<p class="small" id="q8-readout"></p>
<p class="small" id="q8-centered-form"></p>
<p class="small mono" id="q8-closed-form"></p>
<p class="save-row"><button type="button" class="save-curve" data-panel="q8">save this curve</button></p>
<dl class="roles">
  <dt>speedXAtEnds <code>speedXAtEnds</code></dt><dd>the horizontal speed at the two ends (when speedXLinear = -speedXCurvature). The
    middle of u is speedXAtEnds - speedXCurvature/4, so speedXAtEnds decides how close the path comes to the origin: lower speedXAtEnds, closer,
    more bend.</dd>
  <dt>speedXLinear <code>speedXLinear</code></dt><dd>the tilt of u. With speedXLinear = -speedXCurvature the recipe is even about
    t = 1/2, so u(0) = u(1).</dd>
  <dt>speedXCurvature <code>speedXCurvature</code></dt><dd>the curvature of u: how far the horizontal speed swings
    below speedXAtEnds.</dd>
  <dt>speedYAtEnds <code>speedYAtEnds</code></dt><dd>the vertical speed at the ends. The middle of v is
    speedYAtEnds + speedYLinear/2 + speedYCurvature/4.</dd>
  <dt>speedYLinear <code>speedYLinear</code></dt><dd>the asymmetry of v. The centred linear term is speedYLinear + speedYCurvature; set
    it to zero and u and v are both even, the path retraces itself, and the curve doubles back along
    its own arc.</dd>
  <dt>speedYCurvature <code>speedYCurvature</code></dt><dd>the curvature of v: the size of the vertical
    parabola.</dd>
</dl>

</section>

<section class="panel">
<h2>Fig. Q9 | the bend-2 curve (recommended)</h2>
<div class="pick">
<p><strong>The pick:</strong> <code>u = 2 - 3t + 3t^2</code>, <code>v = 2 - 12t + 12t^2</code>,
which is just <code>v = 4u - 6</code>. All integers, <strong>bend 2.00</strong>, inflection at the
middle, <strong>pitch 10</strong>, and the endpoint is <strong>(15, 4)</strong> at that pitch. The
speed path is the straight segment from (2, 2) to (1.25, -1) and back; squared and integrated it
gives this S, and it is the simplest recipe in the gallery that reaches bend 2.</p>
</div>
<p>Tune it: <code>v = k*u + c</code>, with <code>k = 4</code>, <code>c = -6</code> at the pick.
<code>k</code> tilts the segment, <code>c</code> slides it toward or away from the origin; the
readout follows both. <strong>This <code>c</code> is not Q7's <code>c</code>.</strong> Here it is the
intercept of the line between the two recipes; in Q7 it is the constant term of <code>v</code>'s own
recipe, <code>v = b(t^2 - t) + c</code>, which was set to 1 to keep the pitch free. The pick's own
constant term is <code>v(0) = 2</code>.</p>
<p class="code-names">In the code: <code>k</code> is <code>lineSlope</code>, <code>c</code> is
<code>lineIntercept</code>; Q7's constant term is <code>constantTermC</code>.</p>
<div id="q9-controls"></div>
<svg id="q9-plot" viewBox="0 0 900 470" role="img" aria-label="the bend-2 curve"></svg>
<p class="save-row"><button type="button" class="save-curve" data-panel="q9">save this curve</button></p>
<p class="small" id="q9-readout"></p>
</section>

<section class="panel">
<h2>Fig. Q10 | proposal 2: the even pair</h2>
<p>Both recipes even about <code>t = 1/2</code>: <code>u = speedXAtEnds - speedXCurvaturet + speedXCurvaturet^2</code>,
<code>v = speedYAtEnds - speedYCurvaturet + speedYCurvaturet^2</code>. The curve is point-symmetric, so it is an S with equal lobes, and
the four numbers are the whole recipe. <code>speedXAtEnds, speedYAtEnds</code> set how close the speed path comes to the
origin; <code>speedXCurvature, speedYCurvature</code> set the size of each parabola. Three landmarks: (0.6, 0.5, 0.7, 4) is
bend 1.91; (0.5, 0.5, 0.78, 4) is bend 2.01; (0.5, 0.5, 0.7, 4) is bend 2.69.</p>
<p class="code-names">In the code: <code>speedXAtEnds</code>, <code>speedXCurvature</code>,
<code>speedYAtEnds</code>, <code>speedYCurvature</code>.</p>
<div id="q10-controls"></div>
<svg id="q10-plot" viewBox="0 0 900 470" role="img" aria-label="the even pair"></svg>
<p class="save-row"><button type="button" class="save-curve" data-panel="q10">save this curve</button></p>
<p class="small" id="q10-readout"></p>
</section>

<section class="panel">
<h2>Fig. Q11 | proposal 3: the tilted pair</h2>
<p>The even pair plus one free number: <code>v = speedYAtEnds + speedYLineart + speedYCurvaturet^2</code> with <code>speedYLinear</code> no
longer forced to <code>-speedYCurvature</code>. That tilt is what the 2.04 find in Q7 actually used:
<code>u = 0.592 - 0.53t + 0.53t^2</code>, <code>v = 0.694 - 4.048t + 4.099t^2</code> (bend 2.04, pitch
15 million). Its nearest round neighbour, <code>u = 0.6 - 0.5t + 0.5t^2</code>,
<code>v = 0.7 - 4t + 4t^2</code>, is bend 1.91; at x10  -  <code>u = 6 - 5t + 5t^2</code>,
<code>v = 7 - 40t + 40t^2</code>  -  its pitch is <strong>6</strong>. Slide <code>speedYLinear</code> toward
<code>-speedYCurvature</code> to see the tilt vanish.</p>
<p class="code-names">In the code: <code>speedYLinear</code> is <code>speedYLinear</code>, the one number the
even pair does not have.</p>
<div id="q11-controls"></div>
<svg id="q11-plot" viewBox="0 0 900 470" role="img" aria-label="the tilted pair"></svg>
<p class="save-row"><button type="button" class="save-curve" data-panel="q11">save this curve</button></p>
<p class="small" id="q11-readout"></p>
</section>

<section class="panel">
<h2>Fig. Q12 | the exact bend formula</h2>
<p>No sampling is needed. Write the speed recipe in the centred frame <code>h = t - 1/2</code> as
<code>w(h) = speedMid + slopeMid*h + curvatureMid*h^2</code>, with <code>speedMid = w(1/2)</code>,
<code>slopeMid = w'(1/2)</code> and <code>curvatureMid = w''(1/2)/2</code>. Then, exactly:</p>
<pre>arc   = |speedMid|^2 + (|slopeMid|^2 + 2 speedMid.curvatureMid)/12 + |curvatureMid|^2/80
chord = speedMid^2 + (2 speedMid*curvatureMid + slopeMid^2)/12 + curvatureMid^2/80
bend  = arc / |chord|</pre>
<p><code>speedMid.curvatureMid</code> is the dot product and <code>speedMid*curvatureMid</code> the
complex product. These three lines reproduce every entry in
<a href="ph-quintic-presets.json">the preset JSON</a> to within 1e-4. The weights
<code>1, 1/12, 1/80</code> are the integrals of <code>1, h^2, h^4</code> over [-1/2, 1/2] - they are
the irregular ratios in the recipe, and nothing like Fibonacci is involved.</p>
<p><strong>Why it bends.</strong> The chord is a sum of three complex vectors -
<code>speedMid^2</code>, <code>(2 speedMid*curvatureMid + slopeMid^2)/12</code>,
<code>curvatureMid^2/80</code> - while the arc is a positive number, so the bend is large exactly when
those three cancel. For the even pair (<code>slopeMid = 0</code>) the chord is
<code>speedMid^2 (1 + ratio/6 + ratio^2/80)</code> with <code>ratio = curvatureMid/speedMid</code>,
which vanishes at <code>ratio = -20/3 +/- (8*sqrt(5)/3) i</code>:
<code>|ratio| = 4*sqrt(5) ~ 8.94</code> at <code>curvatureAngle = 138.19 deg</code>. There the curve
closes and the bend runs to infinity.</p>
<p><strong>The method.</strong> Choose <code>curvatureRatio = |curvatureMid|/|speedMid|</code> and
<code>curvatureAngle = angle(speedMid, curvatureMid)</code>, read the bend off the chart, then pick
integer vectors and clear the denominators. For bend 2 the level set is curvatureRatio ~ 6.2-7.0 for
curvatureAngle between 115 deg and 150 deg; below about 113 deg no ratio reaches bend 2. The pick
sits at curvatureRatio = 7.7, curvatureAngle = 114.6 deg. Because the formula is exact, the integer
search is instant: over small integers the smallest bend-2 even pair is the pick itself, pitch 10,
unique up to signs.</p>
<!--Q12-->
<p class="small">Above: bend against curvatureRatio for four curvatureAngle values, with the closing
angle marked. The flat grey curve is 110 deg, where bend 2 cannot be reached at any ratio.</p>
</section>

<section class="panel">
<h2>Fig. Q13 | the exact bend formula, live</h2>
<p>Six numbers: the real and imaginary parts of <code>speedMid</code>, <code>slopeMid</code> and
<code>curvatureMid</code>. The three lines give arc, chord and bend with no sampling; the curve is
drawn beside them so you can check. The diagram on the right adds the three chord vectors head to
tail - the bend is large exactly when they cancel. Drag toward the closure preset and watch the bend
run away.</p>
<p><strong>The inverse.</strong> To build a curve from a diagram, type the three chord terms and
press <em>solve for the recipe</em>. The formula inverts in closed form:
<code>speedMid = sqrt(T1)</code>, <code>curvatureMid = sqrt(80*T3)</code>,
<code>slopeMid = sqrt(12*T2 - 2*speedMid*curvatureMid)</code>. Each square root has two signs, so one
diagram gives up to eight curves - mirrors and rotations of the same shape.</p>
<div id="q13-controls"></div>
<div class="inverse-row" id="q13-inverse"></div>
<svg id="q13-plot" viewBox="0 0 900 520" role="img" aria-label="the exact bend formula, live"></svg>
<p class="small mono" id="q13-exact"></p>
<p class="small mono" id="q13-terms"></p>
<p class="save-row"><button type="button" class="save-curve" data-panel="q13">save this curve</button></p>

</section>

<section class="panel">
<h2>Fig. Q14 | any degree: paste a recipe</h2>
<p>Two coefficient lists, comma separated, any length: <code>u</code> and <code>v</code>. A degree-3
speed gives a septic curve. Fractions are read exactly (<code>1/5</code>), and the metrics are the
same three lines as Q12 - no sampling.</p>
<div class="paste-row">
  <label>u <input id="q14-u" type="text" value="2, -3, 3"></label>
  <label>v <input id="q14-v" type="text" value="2, -12, 12"></label>
  <button type="button" id="q14-draw" class="action-button">draw</button>
</div>
<svg id="q14-plot" viewBox="0 0 900 470" role="img" aria-label="a recipe at any degree"></svg>
<p class="small" id="q14-readout"></p>
<p class="small mono" id="q14-hits"></p>
</section>

<section class="panel">
<h2>Fig. Q15 | the guide spine</h2>
<p>The spine is not a PH curve. It is the polynomial that <em>places</em> the anchors:
<code>x = span*t</code>, <code>y = span*(n1 t + ... + n7 t^7)</code>. Positive low orders lift, negative high
orders brake; mixed signs turn the all-positive ramp into an arch or an S. The six crosses are the
anchors at <code>t = i/5</code>, and the quintic PH segments bridge them.</p>
<div id="q15-controls"></div>
<svg id="q15-plot" viewBox="0 0 900 560" role="img" aria-label="a guide spine with six anchors"></svg>
<p class="small mono" id="q15-table"></p>
</section>

<section class="panel">
<h2>Saved curves</h2>
<p>Every illustration has a <strong>save this curve</strong> button. Saved curves stay in this browser
and download as one JSON file, in the same shape as <a href="ph-quintic-presets.json">the preset
JSON</a>: exact recipe, bend, pitch, inflection, closest approach, endpoint and the closed form.</p>
<p><strong id="saved-count">0</strong> saved
<button type="button" id="saved-download">download JSON</button>
<button type="button" id="saved-clear">clear</button></p>
</section>

<!--SCRIPTS-->

<section class="panel">
<h2>How to find a preset</h2>
<p>Work with the speed path <code>w(t) = u + i v</code>, not with the curve. The curve is
<code>r = integral of w^2</code>, so its heading is <code>2*arg(w)</code>: the bend is decided by how far the
direction of <code>w</code> sweeps, and by how close <code>w</code> passes to the origin.</p>
<ol>
  <li><strong>Never let <code>v</code> be a multiple of <code>u</code>.</strong> If <code>v = k*u</code>
    then <code>arg(w)</code> is constant, the curve is a straight line (bend 1.00), and if that line
    passes the origin the speed vanishes and you get a cusp instead. Bend needs <code>v/u</code> to
    change with <code>t</code>.</li>
  <li><strong>Choose the heading turn first.</strong> The heading is twice <code>arg(w)</code>, so the
    turn is twice the sweep of the speed path. Measured on this page: turn 167 deg gives bend 2.00; 186 deg
    gives 2.0-2.7; 215 deg gives 5.58; past about 230 deg the curve loops and the bend runs away.</li>
  <li><strong>Use the even pair</strong> <code>u = speedXAtEnds - speedXCurvaturet + speedXCurvaturet^2</code>,
    <code>v = speedYAtEnds - speedYCurvaturet + speedYCurvaturet^2</code>. Point symmetry puts the inflection exactly at t = 1/2 and makes
    the two lobes equal, so the turn is shared evenly.</li>
  <li><strong>Fine-tune with the closest approach.</strong> Move the speed path nearer the origin to
    add bend at the same turn  -  but keep the closest approach strictly above zero, or the speed
    vanishes and the curve cusps.</li>
  <li><strong>Clear the denominators last.</strong> The pitch is the lcm of the integrated
    coefficients' denominators; scaling the whole recipe by <code>n</code> divides the pitch by
    <code>n^2</code>. Decimals cost pitch  -  1.5 is dearer than 2.</li>
  <li><strong>Read three numbers before keeping it:</strong> bend, an inflection strictly inside
    (0, 1), and a closest approach above zero. No inflection means a C, not an S; closest 0 means a
    cusp.</li>
</ol>
<p class="small">Worked example: the even pair with <code>speedXCurvature = speedYCurvature = 4</code>, <code>speedYAtEnds = 0.7</code> is
bend 2.69 at pitch 200. Drop <code>speedYAtEnds</code> to 0.5 and the same turn gives bend 2.24 at pitch 120;
double the recipe to <code>u = 1 - t + t^2</code>, <code>v = 1 - 8t + 8t^2</code> and the pitch is 30,
endpoint (7, -14). All fourteen saved recipes are in
<a href="ph-quintic-presets.json">the preset JSON</a> and on
<a href="ph-quintic-presets.svg">the preset sheet</a>.</p>
</section>

<section class="panel">
<h2>How the tests read</h2>
<p><strong>aspect</strong> is the bounding box, width / height. Requiring 0.5-2.0 keeps a curve from
being a long thin strip that fills the panel as a nearly straight line.</p>
<p><strong>min(s0, s1) >= 40 deg</strong> is the heading change on the <em>shorter</em> side of the
inflection: s0 from t = 0 to the inflection, s1 from there to t = 1. Taking the smaller forces a
visible bend on both sides  -  a C with a flat tail fails it.</p>
<p><strong>Loops.</strong> Point symmetry means a loop on one side comes with a mirror loop on the
other, so balanced loops arrive in pairs. A single loop would break the symmetry. A cusp at the
middle is possible in principle but not in the exact family: <code>W = b(2t-1)</code> has a simple
zero at 1/2, and a cusp needs a double zero. The morphLambda slider shows the other end: Q6's curve 15 is a
nearly balanced loop, and its W is a general quadratic, not a line.</p>
</section>"""

def fig_q12_svg():
    """Bend against curvatureRatio = |Q| / |P|, for four curvatureAngle values."""
    import math

    def bend(curvature_ratio, curvature_angle):
        qx = curvature_ratio * math.cos(curvature_angle)
        qy = curvature_ratio * math.sin(curvature_angle)
        numerator = 1 + qx / 6 + curvature_ratio * curvature_ratio / 80
        chord = (complex(1, 0) + complex(qx, qy) / 6
                 + complex(qx * qx - qy * qy, 2 * qx * qy) / 80)
        return numerator / abs(chord) if abs(chord) > 1e-12 else float("nan")

    width, height = 900, 400
    left, right, top, bottom = 74, 260, 62, 62
    plot_w = width - left - right
    plot_h = height - top - bottom
    ratio_max, bend_max = 12.0, 8.0
    curves = [
        (110, "#8a8f98", "110 deg | no bend 2"),
        (120, "#1f5fa8", "120 deg"),
        (138.19, "#a23b2a", "138.19 deg | closure"),
        (150, "#5b7f3a", "150 deg"),
    ]
    fx = lambda value: left + value / ratio_max * plot_w
    fy = lambda value: top + plot_h - min(value, bend_max) / bend_max * plot_h
    parts = [
        f'<rect width="{width}" height="{height}" fill="#fbf7ec"/>',
        f'<text x="{left}" y="24" font-size="15" font-weight="600" fill="#2e2413">'
        f"Fig. Q12 | bend against the speed-path ratio</text>",
        f'<text x="{left}" y="40" font-size="12" fill="#7b6c4e">'
        f"|speedMid| = 1, slopeMid = 0 (the even pair); the bend depends only on curvatureRatio and curvatureAngle</text>",
    ]
    parts.append(f'<line x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}" stroke="#8a7a58"/>')
    parts.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" stroke="#8a7a58"/>')
    for value in range(0, 13, 2):
        x = fx(value)
        parts.append(f'<line x1="{x:.1f}" y1="{top + plot_h}" x2="{x:.1f}" y2="{top + plot_h + 5}" stroke="#8a7a58"/>')
        parts.append(f'<text x="{x:.1f}" y="{top + plot_h + 19}" font-size="12" text-anchor="middle" fill="#7b6c4e">{value}</text>')
    for value in range(1, 9):
        y = fy(value)
        parts.append(f'<line x1="{left - 5}" y1="{y:.1f}" x2="{left}" y2="{y:.1f}" stroke="#8a7a58"/>')
        parts.append(f'<text x="{left - 10}" y="{y + 4:.1f}" font-size="12" text-anchor="end" fill="#7b6c4e">{value}</text>')
    parts.append(f'<text x="{left + plot_w / 2}" y="{height - 16}" font-size="13" text-anchor="middle" fill="#2e2413">curvatureRatio = |Q| / |P|</text>')
    parts.append(f'<text x="20" y="{top + plot_h / 2}" font-size="13" text-anchor="middle" fill="#2e2413" transform="rotate(-90 20 {top + plot_h / 2})">bend</text>')
    closure = 4 * math.sqrt(5)
    x = fx(closure)
    parts.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top + plot_h}" stroke="#a23b2a" stroke-dasharray="4 4"/>')
    parts.append(f'<text x="{x + 6:.1f}" y="{top + 14}" font-size="11" fill="#a23b2a">closure: 4sqrt5</text>')
    for degrees, colour, _label in curves:
        angle = math.radians(degrees)
        points = []
        value = 0.05
        while value <= ratio_max:
            height_at = bend(value, angle)
            if height_at == height_at and height_at <= bend_max * 1.05:
                points.append(f"{fx(value):.1f},{fy(height_at):.1f}")
            elif points:
                break
            value += 0.05
        if len(points) > 1:
            parts.append(f'<path d="M{" L".join(points)}" fill="none" stroke="{colour}" stroke-width="2"/>')
    parts.append(f'<line x1="{left}" y1="{fy(2):.1f}" x2="{left + plot_w}" y2="{fy(2):.1f}" stroke="#b9a97f" stroke-dasharray="2 5"/>')
    parts.append(f'<text x="{left + 6}" y="{fy(2) - 6:.1f}" font-size="11" fill="#8a7a58">bend 2.00</text>')
    parts.append(f'<text x="{left + plot_w + 16}" y="{top + 4}" font-size="12" font-weight="600" fill="#2e2413">curvatureAngle</text>')
    for index, (_degrees, colour, label) in enumerate(curves):
        y = top + 26 + index * 20
        parts.append(f'<line x1="{left + plot_w + 16}" y1="{y}" x2="{left + plot_w + 40}" y2="{y}" stroke="{colour}" stroke-width="2.4"/>')
        parts.append(f'<text x="{left + plot_w + 46}" y="{y + 4}" font-size="12" fill="#2e2413">{label}</text>')
    parts.append(f'<text x="{left + plot_w + 16}" y="{top + 26 + 4 * 20 + 10}" font-size="11" fill="#7b6c4e">'
                 f"at the closing angle the chord</text>")
    parts.append(f'<text x="{left + plot_w + 16}" y="{top + 26 + 4 * 20 + 26}" font-size="11" fill="#7b6c4e">'
                 f"vanishes and the bend runs away</text>")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'role="img" aria-label="bend against the ratio of the speed-path vectors">'
            + "".join(parts) + "</svg>")

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
.slider-row{{display:flex;gap:22px;align-items:center;flex-wrap:wrap;margin:8px 0 10px}}
.slider-row input{{vertical-align:middle}}
.control-grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px 22px;margin:10px 0 12px}}
.control-row{{display:flex;align-items:center;gap:8px;font:13px ui-monospace,Menlo,monospace}}
.control-row span{{min-width:22px;color:#8a3b2a}}
.control-row input[type=number]{{width:66px;font:12px ui-monospace,Menlo,monospace}}
.control-row input[type=range]{{flex:1;min-width:80px;vertical-align:middle}}
.code-names{{font-size:14px;color:var(--muted);margin:6px 0 10px}}
.save-row{{margin:8px 0 0}}
#q13-exact{{white-space:pre-line}}
.paste-row{{display:flex;gap:14px;flex-wrap:wrap;align-items:center;margin:0 0 10px}}
.paste-row label{{display:flex;gap:8px;align-items:center;font:13px ui-monospace,Menlo,monospace}}
.paste-row input{{width:320px;font:12px ui-monospace,Menlo,monospace;padding:4px 6px}}
.inverse-row{{display:flex;gap:14px;flex-wrap:wrap;align-items:center;margin:0 0 10px}}
.inverse-row .control-row span{{min-width:34px}}
.inverse-row input[type=number]{{width:74px;font:12px ui-monospace,Menlo,monospace}}
.term-dot{{display:inline-block;width:12px;height:12px;border-radius:50%;margin-right:5px;vertical-align:middle;border:1px solid rgba(0,0,0,.15)}}
.save-curve,.action-button,.save-row button{{font:12px/1.2 ui-monospace,Menlo,monospace;padding:5px 9px;background:#fbf7ec;color:var(--ink);border:1px solid var(--rule);border-radius:3px;cursor:pointer}}
.save-curve:hover{{background:#efe6d2}}
.mono{{font:12px/1.5 ui-monospace,Menlo,monospace}}
.preset-row{{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 12px}}
.preset-row button{{font:12px/1.2 ui-monospace,Menlo,monospace;padding:5px 9px;background:#fbf7ec;color:var(--ink);border:1px solid var(--rule);border-radius:3px;cursor:pointer}}
.preset-row button:hover{{background:#efe6d2}}
.roles{{display:grid;grid-template-columns:auto 1fr;gap:2px 14px;margin:10px 0 0;font-size:14px}}
.roles dt{{font:13px ui-monospace,Menlo,monospace;color:#8a3b2a}}
.roles dd{{margin:0;color:var(--muted)}}
.pick{{border-left:4px solid #a23b2a;background:#fbf7ec;padding:10px 14px;margin:10px 0 12px}}
.pick p{{margin:0}}
#q8panel{{width:100%;height:auto;display:block;border:1px solid var(--rule)}}
#qpanel{{width:100%;height:auto;display:block;border:1px solid var(--rule)}}
</style></head><body><main>
<p class="eyebrow">curve-lab | PH quintics | gallery</p>
<h1>48 PH quintics: 24 S and 24 C, on a 1/5 grid</h1>
<p class="lede">Every curve here is <code>r'(t) = (u^2 - v^2, 2uv)</code> with u and v quadratic and
coefficients on the 1/5 grid in +/-2. An <strong>S</strong> bends one way and then the other  -  the
heading swings at least 15 deg on each side of the inflection. A <strong>C</strong> bends one way
throughout. All are PH, so the offsets are exact and a span is G3-capable.</p>

<section class="panel">
<h2>Fig. Q1 | the grid, 8 by 6</h2>
{gallery()}
<p class="small">Each thumbnail is its own SVG; CSS lays them out. The red ring is the inflection,
the blue compass rings are the end tangents (annotations, not design). The pitch under each panel
is the grid that makes the coordinates whole at integer t.</p>
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
<h2>Fig. Q2 | the S curves, enlarged</h2>
{fig_s_set()}
<p class="small">Twelve curves chosen for balance: the heading swings at least 23 deg on each side of
the inflection. The blue compass rings are the end tangents  -  an annotation, not part of the
design. The red ring is where the curvature passes through zero.</p>
</section>

<section class="panel">
<h2>Fig. Q3 | the dramatic S curves</h2>
{fig_q3()}
<p class="small">The same balance test, but requiring a swing of at least 45 deg on <em>each</em> side
of the inflection  -  up to 147 deg. Same construction, same exactness; the difference is that
<code>v/u</code> turns much faster, so the bend is unmistakable.</p>
</section>

<section class="panel">
<h2>Fig. Q4 | curls and U-turns</h2>
{fig_q4()}
<p class="small">Found on a 1/10 grid, and allowed to curl: the heading swings 120 deg-390 deg across
the span. Same construction and exactness; these are the shapes where <code>v/u</code> turns
almost all the way round.</p>
</section>

<section class="panel">
<h2>Fig. Q5 | the inflection in the middle</h2>
{fig_q5()}
<p class="small">A 1/10 grid, with the inflection required to sit between t = 0.46 and 0.54  -  so
the curve bends one way for the first half and the other way for the second, with the ring at the
turn.</p>
</section>

<section class="panel">
<h2>Fig. Q6 | balanced: the inflection in the middle, equal swing both sides</h2>
{fig_q6()}
<p class="small">The strictest test: the inflection between t = 0.47 and 0.53, at least 40 deg of
swing on each side, and the two sides within 12% of each other. The first twelve are ordinary
S shapes; the last four are balanced loops, included because they pass the same test  -  not the
focus.</p>
</section>

<section class="panel">
<h2>Fig. Q6b | the exact balanced family</h2>
<p>Balance is not a search result here  -  it is forced by the choice of the two speed recipes:</p>
<pre class="small">u = a(t^2 - t) + 1        v = b(t^2 - t)

W = u v' - v u' = b(2t - 1)      zero at t = 1/2, and nowhere else

r(1/2 + h) + r(1/2 - h) = 2 r(1/2)      the curve is point-symmetric about its middle</pre>
<p>The Wronskian is a straight line through t = 1/2, so the inflection is exactly there. The
point symmetry means the tangent at t = 0 and at t = 1 are the same, and the swing on each side is
exactly</p>
<pre class="small">swing per side = 2 | atan( b / (4 - a) )</pre>
<p>So one number, b, sets the swing and a shifts where the bend sits. The whole family is a PH
quintic, so the offsets are exact and the endpoints land on a small pitch (5 to 30 below).</p>
{fig_q6b()}
<p class="small">Twelve members, a = 0, 1, 2 and b = 2...8: the swing runs from 53 deg to 152 deg per
side, and every one is exactly balanced. This is the panel a slider would drive  -  b is the
slider, and the top half is the bottom half turned through 180 deg.</p>
</section>

{EXTRA}

<section class="panel">
<h2>Moving the root inside</h2>
<p>The S is the sign change of <code>W = u v' - v u'</code>. Adding a multiple of u to v does not
change W  -  the Wronskian is blind to it  -  so you have to move v in a different direction. Take the
operator's case 1, <code>u = 1 + t/5 + t^2</code>, <code>v = t</code>: then W = 1 - t^2, whose only
root is at t = 1. Replace v by <code>v = (4/9)t</code> and W becomes <code>(4/9)u - t u'</code>,
which vanishes at t = 1/2. The curve turns from a C into an S, at the price of a 9 in the pitch.</p>
<p class="small">That is the design lever in one sentence: choose where you want the turn, then
choose v so that <code>u v' - v u'</code> vanishes there.</p>
</section>

<section class="panel">
<h2>See also</h2>
<p><a href="ph-quintic-lattice.html">The Tschirnhausen quintic on a coarse lattice</a>  -  the
integer-t stops, the cut pieces and the grid-cost comparison.
<a href="ph-families.html">PH families, degree by degree</a>  -  the ladder and the PH-Hermite
interpolant.</p>
<p><a href="ph-quintic-yours.svg">Curves saved from the gallery</a> - cleaned to integer recipes -
and <a href="ph-quintic-yours.json">the same curves as JSON</a>, with the scale each needed.</p>
<p><a href="ph-quintic-presets.svg">The preset sheet</a> - every named recipe drawn and
labelled - and <a href="ph-quintic-presets.json">the same presets as JSON</a>, with exact fractions,
bend, pitch and the endpoint at that pitch. Regenerate both with
<code>python scripts/ph_quintic_presets.py</code>.</p>
<p class="small">Re-derive: <code>python scripts/ph_quintic_gallery.py</code> | test:
<code>python -m unittest tests.test_ph_quintic_gallery tests.test_ph_quintic_presets</code></p>
</section>
</main></body></html>
"""
    html = html.replace("<!--Q12-->", fig_q12_svg())
    maths = (ROOT / "scripts" / "ph_math.js").read_text()
    panels = (ROOT / "scripts" / "ph_panels.js").read_text()
    html = html.replace("<!--SCRIPTS-->", "<script>\n" + maths + "\n" + panels + "</script>")
    presets = json.loads((ROOT / "workbench" / "ph-quintic-presets.json").read_text())["presets"]
    html = html.replace("<!--PRESETS-->",
                        "<script>window.phPresets = "
                        + json.dumps(presets, separators=(",", ":")) + ";</script>")
    out = ROOT / "workbench" / "ph-quintic-gallery.html"
    out.write_text(html, encoding="utf-8")
    print(out)
    return out

if __name__ == "__main__":
    build()
