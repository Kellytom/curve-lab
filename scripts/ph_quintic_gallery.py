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
                     lambda u, v: f"{shape(u, v)} · pitch {s_info(u, v)[1]}")


def fig_s_set():
    return grid_svgs(S2_CASES, 430, 340, "g2", s_label)


def fig_q3():
    return grid_svgs(Q3_CASES, 430, 340, "g2", s_label)


def fig_q4():
    def label(u, v):
        infl, pitch, end, swing = s_info(u, v)
        th = theta_curve(u, v)
        return f"swing {max(th) - min(th):.0f}° · pitch {pitch}"

    return grid_svgs(Q4_CASES, 430, 340, "g2", label)


def s_label(u, v):
    infl, pitch, end, swing = s_info(u, v)
    th = theta_curve(u, v)
    k = min(len(th) - 1, max(0, round(infl * (len(th) - 1))))
    mn = min(abs(th[k] - th[0]), abs(th[-1] - th[k]))
    return f"infl {infl:.2f} · swing {mn:.0f}° · pitch {pitch}"


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
        where = "—" if infl is None else ("start" if infl <= 0.001 else
                                          "end" if infl >= 0.999 else f"{infl:.2f}")
        rows.append(f"<tr><td>{idx+1}</td><td>{tag}</td><td>{_fmt(u)}</td><td>{_fmt(v)}</td>"
                    f"<td>{where}</td><td>{pitch}</td><td>({end[0]*pitch}, {end[1]*pitch})</td></tr>")
    return "\n".join(rows)


EXTRA = r"""<section class="panel">
<h2>Fig. Q7 · the sliders: b sets the size, λ sets the bend</h2>
<p><strong>b</strong> sets the scale of the exact S. <strong>a</strong> shifts where the bend sits.
<strong>λ</strong> is the bend: it takes the exact family's speed recipes and adds a growing share
of the simplified curve 15's, the two-lobe S. λ = 0 is the exact S; λ = 1 is the target. The
starting recipe carries <code>c = 1</code> — a free nudge: it adds nothing to the pitch and takes the
bend from 1.09 to 1.15.</p>
<p>In plain words: <strong>bend is the arc length divided by the straight-line distance between the
ends</strong>. A straight line is 1.00; the gentle exact S is about 1.09; the target is about 5.6.
λ does not scale the curve — it changes its shape, pulling the ends round into the two lobes. The
target is the simplified curve 15: <code>u = 0.2 − 2t + 2t²</code>,
<code>v = 0.4 − 1.5t + 1.6t²</code>, the clearest S of the six candidates tested.</p>
<div class="slider-row">
  <label>b <input id="qb" type="range" min="0.5" max="8" step="0.1" value="4"></label>
  <label>a <input id="qa" type="range" min="-1" max="3" step="0.1" value="0"></label>
  <label>λ <input id="ql" type="range" min="0" max="1" step="0.01" value="0"></label>
  <span id="qread" class="small"></span>
</div>
<svg id="qpanel" viewBox="0 0 900 420" role="img" aria-label="the balanced family, live"></svg>
<script>
(function () {
  const svg = document.getElementById("qpanel");
  const W = 900, H = 420, m = 46, N = 800;
  const UT = [0.2, -2, 2], VT = [0.4, -1.5, 1.6];
  const ev = (p, t) => p[0] + p[1] * t + p[2] * t * t;
  const dv = (p, t) => p[1] + 2 * p[2] * t;
  function draw() {
    const a = +document.getElementById("qa").value;
    const b = +document.getElementById("qb").value;
    const lam = +document.getElementById("ql").value;
    const U = [1, -a, a].map((c, i) => c + lam * (UT[i] - c));
    const V = [1, -b, b].map((c, i) => c + lam * (VT[i] - c));
    const pts = [];
    let x = 0, y = 0;
    pts.push([0, 0]);
    for (let i = 1; i <= N; i++) {
      const t = (i - 0.5) / N, u = ev(U, t), v = ev(V, t);
      x += (u * u - v * v) / N;
      y += 2 * u * v / N;
      pts.push([x, y]);
    }
    const th = [];
    for (let i = 0; i <= N; i++) {
      const t = i / N, u = ev(U, t), v = ev(V, t);
      th.push(Math.atan2(2 * u * v, u * u - v * v));
    }
    const un = [th[0]];
    for (let i = 1; i <= N; i++) {
      let q = th[i];
      while (q - un[i - 1] > Math.PI) q -= 2 * Math.PI;
      while (q - un[i - 1] < -Math.PI) q += 2 * Math.PI;
      un.push(q);
    }
    const Wf = t => {
      const u = ev(U, t), v = ev(V, t);
      return u * dv(V, t) - v * dv(U, t);
    };
    let root = null;
    for (let i = 0; i < N; i++) {
      const t0 = i / N, t1 = (i + 1) / N;
      if (Wf(t0) * Wf(t1) <= 0) {
        let lo = t0, hi = t1;
        for (let k = 0; k < 40; k++) {
          const mid = (lo + hi) / 2;
          if (Wf(lo) * Wf(mid) <= 0) hi = mid; else lo = mid;
        }
        root = (lo + hi) / 2;
        break;
      }
    }
    const mid = root === null ? N / 2 : Math.round(root * N);
    const s0 = Math.abs(un[mid] - un[0]) * 180 / Math.PI;
    const s1 = Math.abs(un[N] - un[mid]) * 180 / Math.PI;
    const bal = 100 * Math.min(s0, s1) / Math.max(s0, s1);
    let arc = 0;
    for (let i = 1; i < pts.length; i++) arc += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
    const chord = Math.hypot(pts[N][0] - pts[0][0], pts[N][1] - pts[0][1]);
    const bend = chord > 1e-9 ? arc / chord : Infinity;
    const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]);
    const x0 = Math.min(...xs), x1 = Math.max(...xs);
    const y0 = Math.min(...ys), y1 = Math.max(...ys);
    const sc = Math.min((W - 2 * m) / Math.max(1e-6, x1 - x0),
                        (H - 2 * m) / Math.max(1e-6, y1 - y0));
    const ox = m + (W - 2 * m - (x1 - x0) * sc) / 2;
    const oy = m + (H - 2 * m - (y1 - y0) * sc) / 2;
    const fx = v => ox + (v - x0) * sc;
    const fy = v => oy + (y1 - v) * sc;
    const d = "M" + pts.map(p => fx(p[0]).toFixed(1) + "," + fy(p[1]).toFixed(1)).join("L");
    const compass = (px, py, u, v, sgn) => {
      const dx = u * u - v * v, dy = 2 * u * v, n = Math.hypot(dx, dy) || 1;
      const sx = sgn * dx / n, sy = -sgn * dy / n, rr = 17;
      const gx = fx(px) + sx * (5 + rr), gy = fy(py) + sy * (5 + rr);
      return `<circle cx="${gx}" cy="${gy}" r="${rr}" fill="#1f5fa8" fill-opacity="0.07" stroke="#1f5fa8" stroke-width="1.8"/>` +
        `<line x1="${gx - sx * rr * 0.62}" y1="${gy - sy * rr * 0.62}" x2="${gx + sx * rr * 0.62}" y2="${gy + sy * rr * 0.62}" stroke="#1f5fa8" stroke-width="2.4" stroke-linecap="round"/>`;
    };
    svg.innerHTML =
      `<rect width="${W}" height="${H}" fill="#fbf7ec"/>` +
      `<path d="${d}" fill="none" stroke="#2e2413" stroke-width="2.4"/>` +
      `<circle cx="${fx(pts[mid][0])}" cy="${fy(pts[mid][1])}" r="5" fill="#fbf7ec" stroke="#a23b2a" stroke-width="2.2"/>` +
      compass(pts[0][0], pts[0][1], ev(U, 0), ev(V, 0), -1) +
      compass(pts[N][0], pts[N][1], ev(U, 1), ev(V, 1), 1) +
      `<text x="${m}" y="${H - 12}" font-size="12" fill="#7b6c4e">bend ${bend.toFixed(2)} (arc ÷ chord) · inflection ${root === null ? "—" : root.toFixed(2)} · turn ${s0.toFixed(0)}° / ${s1.toFixed(0)}° · b = ${b.toFixed(1)} · a = ${a.toFixed(1)} · λ = ${lam.toFixed(2)}</text>`;
    document.getElementById("qread").textContent =
      `bend ${bend.toFixed(2)} · inflection ${root === null ? "—" : root.toFixed(2)}`;
  }
  for (const id of ["qa", "qb", "ql"]) document.getElementById(id).addEventListener("input", draw);
  draw();
})();
</script>
</section>

<section class="panel">
<h2>How the tests read</h2>
<p><strong>aspect</strong> is the bounding box, width ÷ height. Requiring 0.5–2.0 keeps a curve from
being a long thin strip that fills the panel as a nearly straight line.</p>
<p><strong>min(s0, s1) ≥ 40°</strong> is the heading change on the <em>shorter</em> side of the
inflection: s0 from t = 0 to the inflection, s1 from there to t = 1. Taking the smaller forces a
visible bend on both sides — a C with a flat tail fails it.</p>
<p><strong>Loops.</strong> Point symmetry means a loop on one side comes with a mirror loop on the
other, so balanced loops arrive in pairs. A single loop would break the symmetry. A cusp at the
middle is possible in principle but not in the exact family: <code>W = b(2t−1)</code> has a simple
zero at 1/2, and a cusp needs a double zero. The λ slider shows the other end: Q6's curve 15 is a
nearly balanced loop, and its W is a general quadratic, not a line.</p>
</section>"""


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
#qpanel{{width:100%;height:auto;display:block;border:1px solid var(--rule)}}
</style></head><body><main>
<p class="eyebrow">curve-lab · PH quintics · gallery</p>
<h1>48 PH quintics: 24 S and 24 C, on a 1/5 grid</h1>
<p class="lede">Every curve here is <code>r′(t) = (u² − v², 2uv)</code> with u and v quadratic and
coefficients on the 1/5 grid in ±2. An <strong>S</strong> bends one way and then the other — the
heading swings at least 15° on each side of the inflection. A <strong>C</strong> bends one way
throughout. All are PH, so the offsets are exact and a span is G3-capable.</p>

<section class="panel">
<h2>Fig. Q1 · the grid, 8 by 6</h2>
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
<h2>Fig. Q2 · the S curves, enlarged</h2>
{fig_s_set()}
<p class="small">Twelve curves chosen for balance: the heading swings at least 23° on each side of
the inflection. The blue compass rings are the end tangents — an annotation, not part of the
design. The red ring is where the curvature passes through zero.</p>
</section>

<section class="panel">
<h2>Fig. Q3 · the dramatic S curves</h2>
{fig_q3()}
<p class="small">The same balance test, but requiring a swing of at least 45° on <em>each</em> side
of the inflection — up to 147°. Same construction, same exactness; the difference is that
<code>v/u</code> turns much faster, so the bend is unmistakable.</p>
</section>

<section class="panel">
<h2>Fig. Q4 · curls and U-turns</h2>
{fig_q4()}
<p class="small">Found on a 1/10 grid, and allowed to curl: the heading swings 120°–390° across
the span. Same construction and exactness; these are the shapes where <code>v/u</code> turns
almost all the way round.</p>
</section>

<section class="panel">
<h2>Fig. Q5 · the inflection in the middle</h2>
{fig_q5()}
<p class="small">A 1/10 grid, with the inflection required to sit between t = 0.46 and 0.54 — so
the curve bends one way for the first half and the other way for the second, with the ring at the
turn.</p>
</section>

<section class="panel">
<h2>Fig. Q6 · balanced: the inflection in the middle, equal swing both sides</h2>
{fig_q6()}
<p class="small">The strictest test: the inflection between t = 0.47 and 0.53, at least 40° of
swing on each side, and the two sides within 12% of each other. The first twelve are ordinary
S shapes; the last four are balanced loops, included because they pass the same test — not the
focus.</p>
</section>

<section class="panel">
<h2>Fig. Q6b · the exact balanced family</h2>
<p>Balance is not a search result here — it is forced by the choice of the two speed recipes:</p>
<pre class="small">u = a(t² − t) + 1        v = b(t² − t)

W = u v′ − v u′ = b(2t − 1)      zero at t = 1/2, and nowhere else

r(1/2 + h) + r(1/2 − h) = 2 r(1/2)      the curve is point-symmetric about its middle</pre>
<p>The Wronskian is a straight line through t = 1/2, so the inflection is exactly there. The
point symmetry means the tangent at t = 0 and at t = 1 are the same, and the swing on each side is
exactly</p>
<pre class="small">swing per side = 2 · atan( b / (4 − a) )</pre>
<p>So one number, b, sets the swing and a shifts where the bend sits. The whole family is a PH
quintic, so the offsets are exact and the endpoints land on a small pitch (5 to 30 below).</p>
{fig_q6b()}
<p class="small">Twelve members, a = 0, 1, 2 and b = 2…8: the swing runs from 53° to 152° per
side, and every one is exactly balanced. This is the panel a slider would drive — b is the
slider, and the top half is the bottom half turned through 180°.</p>
</section>

{EXTRA}

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
