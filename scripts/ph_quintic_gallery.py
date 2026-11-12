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
    ((F(2,5), -2, 2), (F(-8,5), F(4,5), 0)),
    ((1, F(-2,5), F(7,5)), (F(-3,5), F(-4,5), 1)),
    ((F(-8,5), -1, F(8,5)), (F(-9,5), F(-1,5), -2)),
    ((2, F(-8,5), F(9,5)), (F(1,5), F(8,5), F(-6,5))),
    ((F(-9,5), F(6,5), F(-4,5)), (F(3,5), F(8,5), F(-9,5))),
    ((1, 0, F(3,5)), (F(3,5), F(4,5), -2)),
    ((F(-6,5), F(-8,5), F(9,5)), (F(-9,5), F(-8,5), 0)),
    ((F(-2,5), F(1,5), F(-6,5)), (F(4,5), F(7,5), F(-4,5))),
    ((F(-9,5), 0, F(-3,5)), (F(3,5), F(4,5), F(-8,5))),
    ((F(-7,5), F(3,5), F(-8,5)), (F(1,5), F(-9,5), F(6,5))),
    ((1, F(-3,5), F(2,5)), (F(-9,5), F(-3,5), F(2,5))),
    ((F(1,5), 2, F(-4,5)), (F(9,5), F(-8,5), F(7,5))),
    ((F(-6,5), F(6,5), F(-4,5)), (2, F(1,5), F(-2,5))),
    ((F(3,5), 1, F(-6,5)), (F(9,5), F(-1,5), 2)),
    ((F(-7,5), F(3,5), F(-9,5)), (F(2,5), F(3,5), F(-3,5))),
    ((F(6,5), F(4,5), -2), (F(-7,5), 0, F(-4,5))),
    ((F(-4,5), F(-3,5), F(6,5)), (F(8,5), F(2,5), F(4,5))),
    ((F(-1,5), -2, F(8,5)), (F(-1,5), F(-1,5), F(-8,5))),
    ((F(-3,5), 0, F(8,5)), (1, F(-8,5), 1)),
    ((F(-6,5), F(-4,5), F(9,5)), (F(-8,5), F(3,5), -2)),
    ((2, -2, 1), (F(4,5), 0, -1)),
    ((F(-2,5), F(-4,5), F(3,5)), (F(9,5), F(1,5), F(4,5))),
    ((1, F(8,5), -2), (-2, F(-4,5), F(-3,5))),
    ((F(-8,5), F(-8,5), F(9,5)), (-1, F(2,5), 0)),
    ((F(-3,5), F(2,5), F(-9,5)), (F(-9,5), F(-2,5), F(-3,5))),
    ((-1, F(6,5), -2), (F(9,5), F(-1,5), 1)),
    ((0, -1, F(4,5)), (F(1,5), F(6,5), F(-2,5))),
    ((F(2,5), F(3,5), F(-2,5)), (F(-6,5), F(6,5), F(-4,5))),
    ((F(7,5), F(-1,5), F(3,5)), (F(-9,5), -2, F(8,5))),
    ((F(4,5), 0, F(2,5)), (2, F(4,5), F(-7,5))),
    ((F(4,5), F(4,5), F(-7,5)), (2, F(2,5), F(-6,5))),
    ((F(1,5), F(7,5), F(-8,5)), (F(4,5), F(1,5), F(4,5))),
    ((F(1,5), -2, F(-6,5)), (F(3,5), F(-8,5), F(9,5))),
    ((F(6,5), F(4,5), F(-6,5)), (F(-7,5), F(2,5), F(-9,5))),
    ((-1, -2, 1), (F(2,5), F(2,5), 1)),
    ((F(2,5), F(-3,5), F(6,5)), (2, F(-3,5), F(8,5))),
    ((F(-1,5), -2, 2), (F(-4,5), F(-7,5), F(-6,5))),
    ((F(3,5), F(-8,5), F(7,5)), (F(1,5), F(2,5), F(-6,5))),
    ((F(-8,5), F(2,5), F(-7,5)), (F(4,5), 0, F(-1,5))),
    ((F(-7,5), F(-7,5), F(4,5)), (F(-6,5), 1, F(-6,5))),
]

C_CASES = [
    ((F(4,5), F(8,5), F(6,5)), (F(3,5), F(6,5), F(-6,5))),
    ((-1, F(-7,5), F(4,5)), (F(-1,5), F(-6,5), F(-8,5))),
    ((1, F(-2,5), F(6,5)), (2, F(-4,5), F(-3,5))),
    ((F(-8,5), F(8,5), F(-8,5)), (F(-6,5), F(6,5), F(-2,5))),
    ((F(-7,5), 0, -2), (0, 0, F(2,5))),
    ((F(6,5), F(-8,5), F(-9,5)), (F(-9,5), F(-4,5), F(-3,5))),
    ((F(9,5), 0, F(1,5)), (F(-2,5), 0, F(9,5))),
    ((F(9,5), -2, F(4,5)), (0, F(4,5), F(8,5))),
]

CASES = S_CASES + C_CASES


def gallery():
    cols, rows = 8, 6
    pw, ph, gap = 105, 105, 8
    W = 22 + cols * pw + (cols - 1) * gap + 22
    H = 70 + rows * (ph + 26) + 14
    out = [f'<text x="22" y="24" font-size="14" font-weight="600" fill="{INK}">Fig. G1 · 48 PH quintics: 40 S curves, 8 C curves</text>',
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
        out.append(f'<path d="{" ".join(f"{fx(q[1]):.1f},{fy(q[2]):.1f}" for q in pts)}" fill="none" stroke="{INK}" stroke-width="1.6"/>')
        infl, pitch, end, swing = s_info(u, v)
        if infl is not None and 0 < infl < 1:
            x, y = uv_curve(u, v)
            tx = sum(c * F(str(infl)).limit_denominator(1000) ** k for k, c in enumerate(x))
            ty = sum(c * F(str(infl)).limit_denominator(1000) ** k for k, c in enumerate(y))
            out.append(f'<circle cx="{fx(float(tx)):.1f}" cy="{fy(float(ty)):.1f}" r="3.4" fill="{PAPER}" stroke="{RED}" stroke-width="1.8"/>')
        out.append(f'<text x="{cx+4}" y="{cy+ph+13}" font-size="10" font-weight="600" fill="{INK}">{idx+1}</text>')
        tag = "S" if idx < len(S_CASES) else "C"
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


def fig_s_set():
    best = sorted(S_CASES, key=lambda uv: s_quality(*uv))[:12]
    cols, rows = 4, 3
    pw, ph, gap = 210, 210, 12
    W = 22 + cols * pw + (cols - 1) * gap + 22
    H = 76 + rows * (ph + 30) + 16
    out = [f'<text x="22" y="24" font-size="14" font-weight="600" fill="{INK}">Fig. G2 · the S curves, enlarged: the heading turns around at the ring</text>',
           f'<text x="22" y="43" font-size="12" fill="{MUTED}">one scale for x and y · short bars: the tangent at each end · the ring is the inflection, where the curvature is zero</text>',
           f'<text x="22" y="60" font-size="11" fill="{MUTED}">chosen from the 40 by: a heading swing of 35° to 108°, the inflection inside, a box near square</text>']
    for idx, (u, v) in enumerate(best):
        cx = 22 + (idx % cols) * (pw + gap)
        cy = 76 + (idx // cols) * (ph + 30)
        pts = uv_samples(u, v, 240)
        xs = [q[1] for q in pts]
        ys = [q[2] for q in pts]
        x0, x1 = min(xs), max(xs)
        y0, y1 = min(ys), max(ys)
        sc = min((pw - 16) / max(1e-9, x1 - x0), (ph - 16) / max(1e-9, y1 - y0))
        ox = cx + (pw - (x1 - x0) * sc) / 2
        oy = cy + (ph - (y1 - y0) * sc) / 2

        def fx(val):
            return ox + (val - x0) * sc

        def fy(val):
            return oy + (y1 - val) * sc

        infl, pitch, end, swing = s_info(u, v)
        out.append(f'<rect x="{cx}" y="{cy}" width="{pw}" height="{ph}" fill="none" stroke="{RULE}"/>')
        d = " ".join(("M" if i == 0 else "L") + f"{fx(q[1]):.1f},{fy(q[2]):.1f}"
                     for i, q in enumerate(pts))
        out.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="2.2"/>')
        # end tangents, short bars
        U0 = float(u[0])
        V0 = float(v[0])
        U1 = float(sum(u))
        V1 = float(sum(v))
        for (px, py, U, V) in ((0.0, 0.0, U0, V0), (float(sum(uv_curve(u, v)[0])), float(sum(uv_curve(u, v)[1])), U1, V1)):
            dx, dy = U * U - V * V, 2 * U * V
            n = max(1e-9, (dx * dx + dy * dy) ** .5)
            L = 0.18 * max(x1 - x0, y1 - y0)
            out.append(f'<line x1="{fx(px):.1f}" y1="{fy(py):.1f}" x2="{fx(px + dx / n * L):.1f}" y2="{fy(py + dy / n * L):.1f}" stroke="{BLUE}" stroke-width="2"/>')
        x, y = uv_curve(u, v)
        ti = F(str(infl)).limit_denominator(200)
        tx = sum(c * ti ** k for k, c in enumerate(x))
        ty = sum(c * ti ** k for k, c in enumerate(y))
        out.append(f'<circle cx="{fx(float(tx)):.1f}" cy="{fy(float(ty)):.1f}" r="4" fill="{PAPER}" stroke="{RED}" stroke-width="2"/>')
        out.append(f'<text x="{cx}" y="{cy+ph+14}" font-size="11" font-weight="600" fill="{INK}">{idx+1}</text>')
        out.append(f'<text x="{cx+20}" y="{cy+ph+14}" font-size="10" fill="{MUTED}">inflection {infl:.2f} · pitch {pitch}</text>')
    return svg(W, H, ("the S curves, enlarged", "".join(out)))


def table():
    rows = []
    for idx, (u, v) in enumerate(CASES):
        infl, pitch, end, swing = s_info(u, v)
        tag = "S" if idx < len(S_CASES) else "C"
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
<h1>48 PH quintics: S and C, on a 1/5 grid</h1>
<p class="lede">Every curve here is <code>r′(t) = (u² − v², 2uv)</code> with u and v quadratic and
coefficients on the 1/5 grid in ±2. An <strong>S</strong> has its inflection strictly inside the
span; a <strong>C</strong> has it at the start or not at all. All are PH, so the offsets are exact
and a span is G3-capable.</p>

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
<p class="small">The endpoints are exact integers at the stated pitch. A dash in the inflection
column means the Wronskian has no root in [0,1]; "start" and "end" mean the root sits exactly on
the boundary.</p>
</section>

<section class="panel">
<h2>Fig. G2 · the S curves, enlarged</h2>
{fig_s_set()}
<p class="small">Twelve of the 40, chosen for a visible swing: the heading turns through 35° to
108°, the inflection sits inside, and the box is near square. The blue bars are the tangents at t = 0
and t = 1; the ring between them is where the curvature passes through zero.</p>
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
