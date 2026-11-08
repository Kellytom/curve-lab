"""The six families the catalogue was missing.

    .venv/bin/python scripts/missing_families.py
    open workbench/missing-families.html

1. Euler elastica — energy-minimising, fitted (elliptic).
2. Polynomial spirals — curvature a polynomial in arc length.
3. Sinusoidal spirals — r^n = a·cos(nθ); circle, cardioid, parabola, lemniscate.
4. General trochoids — epi/hypotrochoid with k as a dial.
5. Spline interpolators — Catmull–Rom, uniform B-spline, rational quadratic
   (NURBS), and a quintic Hermite span that is G2 by construction.
6. Rational PH — the circle as a rational PH curve, and a degree-7 PH curve
   with integer controls at one scale.

Each section states what is exact and what is fitted.
"""

from __future__ import annotations

import math
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT / "scripts"))
import generators as G  # noqa: E402

PAPER, INK, MUTED, RULE = "#fbf7ec", "#2e2413", "#7b6c4e", "#d8ccae"
RED, BLUE, GOLD, GREEN = "#a23b2a", "#1f5fa8", "#c9a441", "#3f7d4e"


# 1 — Euler elastica --------------------------------------------------------

def elastica(m=2.0, s_max=9.0, n=4000):
    """κ' = ±½√(m⁴−κ⁴), starting at κ = m with κ' = 0."""
    ds = s_max / n
    kappa = m
    heading = 0.0
    x = y = 0.0
    pts = [(x, y)]
    sign = -1.0
    for _ in range(n):
        dk = sign * 0.5 * math.sqrt(max(0.0, m ** 4 - kappa ** 4))
        k2 = kappa + dk * ds
        if abs(k2) > m:
            sign = -sign
            k2 = max(-m, min(m, k2))
        heading += 0.5 * (kappa + k2) * ds
        x += math.cos(heading) * ds
        y += math.sin(heading) * ds
        pts.append((x, y))
        kappa = k2
    return pts


# 2 — polynomial spirals ----------------------------------------------------

def polynomial_spiral(power, s_max=2.6, n=1200):
    """κ(s) = s^power; the clothoid is power 1."""
    ds = s_max / n
    heading = 0.0
    x = y = 0.0
    pts = [(x, y)]
    for i in range(n):
        s = i * ds
        k = s ** power
        heading += k * ds
        x += math.cos(heading) * ds
        y += math.sin(heading) * ds
        pts.append((x, y))
    return pts


# 3 — sinusoidal spirals ----------------------------------------------------

def sinusoidal(n, a=1.0, k=1200):
    """r^n = a^n cos(nθ); real for |θ| < π/(2|n|) with cos > 0."""
    lim = math.pi / (2 * abs(n)) - 1e-4
    out = []
    for i in range(k + 1):
        th = -lim + 2 * lim * i / k
        c = math.cos(n * th)
        if c <= 0:
            continue
        r = a * c ** (1.0 / n)
        out.append((r * math.cos(th), r * math.sin(th)))
    return out


# 4 — general trochoid ------------------------------------------------------

def trochoid(k_ratio, d=1.0, turns=2, n=2000):
    """x = (R+r)cos t − d cos((R+r)/r t); k = R/r, r = 1."""
    out = []
    for i in range(n + 1):
        t = turns * 2 * math.pi * i / n
        out.append(((k_ratio + 1) * math.cos(t) - d * math.cos((k_ratio + 1) * t),
                    (k_ratio + 1) * math.sin(t) - d * math.sin((k_ratio + 1) * t)))
    return out


# 5 — spline interpolators --------------------------------------------------

def catmull_rom(points, n=40):
    out = []
    for i in range(1, len(points) - 2):
        p0, p1, p2, p3 = points[i - 1], points[i], points[i + 1], points[i + 2]
        for j in range(n):
            t = j / n
            t2, t3 = t * t, t * t * t
            out.append((
                0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t
                       + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                       + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3),
                0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t
                       + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                       + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)))
    out.append(points[-2])
    return out


def bspline(points, n=120):
    """Uniform cubic B-spline over the middle span of four controls."""
    p0, p1, p2, p3 = points[:4]
    out = []
    for j in range(n + 1):
        t = j / n
        t2, t3 = t * t, t * t * t
        b0 = (1 - t) ** 3 / 6
        b1 = (3 * t3 - 6 * t2 + 4) / 6
        b2 = (-3 * t3 + 3 * t2 + 3 * t + 1) / 6
        b3 = t3 / 6
        out.append((b0 * p0[0] + b1 * p1[0] + b2 * p2[0] + b3 * p3[0],
                    b0 * p0[1] + b1 * p1[1] + b2 * p2[1] + b3 * p3[1]))
    return out


def rational_quadratic(p0, p1, p2, w, n=120):
    """A NURBS arc: weights (1, w, 1). w = 1/√2 gives the circular quarter."""
    out = []
    for j in range(n + 1):
        t = j / n
        b0, b1, b2 = (1 - t) ** 2, 2 * t * (1 - t), t * t
        d = b0 + w * b1 + b2
        out.append(((b0 * p0[0] + w * b1 * p1[0] + b2 * p2[0]) / d,
                    (b0 * p0[1] + w * b1 * p1[1] + b2 * p2[1]) / d))
    return out


def quintic_hermite(p0, p1, v0, v1, a0, a1, n=120):
    """Quintic Hermite: position, tangent and acceleration at both ends → G2."""
    out = []
    for j in range(n + 1):
        t = j / n
        h0 = 1 - 10 * t ** 3 + 15 * t ** 4 - 6 * t ** 5
        h1 = 10 * t ** 3 - 15 * t ** 4 + 6 * t ** 5
        h2 = t - 6 * t ** 3 + 8 * t ** 4 - 3 * t ** 5
        h3 = -4 * t ** 3 + 7 * t ** 4 - 3 * t ** 5
        h4 = 0.5 * (t * t - 3 * t ** 3 + 3 * t ** 4 - t ** 5)
        h5 = 0.5 * (t ** 3 - 2 * t ** 4 + t ** 5)
        out.append((h0 * p0[0] + h1 * p1[0] + h2 * v0[0] + h3 * v1[0]
                    + h4 * a0[0] + h5 * a1[0],
                    h0 * p0[1] + h1 * p1[1] + h2 * v0[1] + h3 * v1[1]
                    + h4 * a0[1] + h5 * a1[1]))
    return out


# 6 — rational and higher-degree PH ----------------------------------------

def rational_ph_circle(n=400):
    """(1−t²)/(1+t²), 2t/(1+t²): speed 2/(1+t²), so σ is rational."""
    return [((1 - t * t) / (1 + t * t), 2 * t / (1 + t * t))
            for t in (-1 + 2 * i / n for i in range(n + 1))]


def degree_seven_ph():
    """n = deg h + 2 max(deg u, deg v) + 1 = 0 + 6 + 1 = 7."""
    pc = G.PHCurve(7, u=(1, 2, 1, 1), v=(1, -1, 1, 0), h=(1,))
    scale = pc.scale(4)
    pts = [pc.bezier(i / 300) for i in range(301)]
    return pts, scale, pc


def cases():
    """One entry per family for the showcase: (title, curves, note, source)."""
    pal = (RED, BLUE, GOLD, GREEN)

    def curves(seq):
        return [(pts, pal[i % 4], 1.6, None) for i, pts in enumerate(seq)]

    ph7, scale7, _pc = degree_seven_ph()
    return [
        ("elastica · m dial", curves([elastica(m) for m in (1.2, 2.0, 2.8)]),
         "κ′ = ±½√(m⁴−κ⁴) · energy-minimising · fitted",
         "scripts/missing_families.py"),
        ("polynomial spirals · p = 1, 2, 3", curves([polynomial_spiral(p) for p in (1, 2, 3)]),
         "κ = s^p · p = 1 is the clothoid · fitted", "scripts/missing_families.py"),
        ("sinusoidal spirals · n dial",
         curves([sinusoidal(n) for n in (1, 0.5, -0.5, 2)]),
         "r^n = a·cos(nθ) · circle, cardioid, parabola, lemniscate",
         "scripts/missing_families.py"),
        ("trochoids · k = 3, 4, 5", curves([trochoid(k) for k in (3, 4, 5)]),
         "epi/hypotrochoid with k = R/r as the dial", "scripts/missing_families.py"),
        ("spline interpolators", curves([
            catmull_rom([(-1.0, 0.0), (0.0, 1.2), (1.2, 0.9), (2.0, 0.0)]),
            bspline([(-1.0, 0.0), (0.0, 1.2), (1.2, 0.9), (2.0, 0.0)]),
            rational_quadratic((1, 0), (1, 1), (0, 1), 1 / math.sqrt(2)),
            quintic_hermite((0, 0), (2, 0), (1, 0), (1, 0), (0, 1.0), (0, -1.0))]),
         "Catmull–Rom, B-spline, rational quadratic, quintic Hermite (G2)",
         "scripts/missing_families.py"),
        ("rational PH and degree-7 PH", curves([rational_ph_circle(), ph7]),
         f"circle speed 2/(1+t²) · degree-7 controls at scale {scale7:,}",
         "scripts/missing_families.py"),
    ]


# -- drawing ----------------------------------------------------------------

def panel(series, title, note, w=980, h=430):
    pts = [p for _, pts_, _ in series for p in pts_]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    pad = 42
    s = min((w - 2 * pad) / max(1e-9, x1 - x0),
            (h - 2 * pad) / max(1e-9, y1 - y0))
    ox = (w - (x1 - x0) * s) / 2 - x0 * s
    oy = (h - (y1 - y0) * s) / 2 + y1 * s

    def f(p):
        return (ox + p[0] * s, oy - p[1] * s)

    paths = []
    for colour, curve_pts, _label in series:
        d = " ".join(("M" if i == 0 else "L") + f"{x:.1f},{y:.1f}"
                     for i, (x, y) in enumerate(f(p) for p in curve_pts))
        paths.append(f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="1.8"/>')
    legend = "".join(
        f'<line x1="{16 + i * 200}" y1="{h - 12}" x2="{52 + i * 200}" y2="{h - 12}" '
        f'stroke="{c}" stroke-width="3"/><text x="{60 + i * 200}" y="{h - 7}" '
        f'font-family="Georgia,serif" font-size="15" fill="{INK}">{lab}</text>'
        for i, (c, _pts, lab) in enumerate(series))
    return f"""<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="{title}">
  <rect width="{w}" height="{h}" fill="{PAPER}"/>
  {''.join(paths)}
  <text x="{pad}" y="30" font-family="Georgia,serif" font-size="13" fill="{INK}">{title}</text>
  <text x="{pad}" y="50" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="{MUTED}">{note}</text>
  {legend}
</svg>"""


def build():
    e_series = [(c, elastica(m), f"m = {m}")
                for c, m in ((RED, 1.2), (BLUE, 2.0), (GOLD, 2.8))]
    p_series = [(c, polynomial_spiral(p), f"κ = s^{p}")
                for c, p in ((RED, 1), (BLUE, 2), (GOLD, 3))]
    s_series = [(c, sinusoidal(n), f"n = {n:g}")
                for c, n in ((RED, 1), (BLUE, 0.5), (GOLD, -0.5), (GREEN, 2))]
    t_series = [(c, trochoid(k), f"k = {k}")
                for c, k in ((RED, 3), (BLUE, 4), (GOLD, 5))]

    ctrl = [(-1.0, 0.0), (0.0, 1.2), (1.2, 0.9), (2.0, 0.0)]
    cr = catmull_rom(ctrl)
    bs = bspline(ctrl)
    rq = rational_quadratic((1, 0), (1, 1), (0, 1), 1 / math.sqrt(2))
    qh = quintic_hermite((0, 0), (2, 0), (1, 0), (1, 0), (0, 1.0), (0, -1.0))
    sp_series = [(RED, cr, "Catmull–Rom"), (BLUE, bs, "B-spline"),
                 (GOLD, rq, "rational quadratic"), (GREEN, qh, "quintic Hermite")]

    circle = rational_ph_circle()
    ph7, scale7, pc7 = degree_seven_ph()
    ph_series = [(RED, circle, "rational PH (circle)"), (BLUE, ph7, "degree-7 PH")]

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The six missing families</title>
<style>
:root{{--paper:{PAPER};--ink:{INK};--muted:{MUTED};--rule:{RULE}}}
*{{box-sizing:border-box}} body{{margin:0;background:#f3eddf;color:var(--ink);font:16px/1.55 Georgia,serif}}
main{{max-width:1120px;margin:0 auto;padding:34px 22px 70px}}
.eyebrow{{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}}
h1{{font-size:31px;line-height:1.12;margin:0 0 8px}} h2{{font-size:20px;margin:0 0 8px}}
.lede{{max-width:920px;color:var(--muted)}}
.panel{{background:var(--paper);border:1px solid var(--rule);padding:16px 18px;margin:0 0 18px}}
.small{{font:12px/1.6 ui-monospace,Menlo,monospace;color:var(--muted)}}
code{{font:12px ui-monospace,Menlo,monospace;background:#f4ecd7;padding:1px 4px}}
</style></head><body><main>
<p class="eyebrow">curve-lab · the missing families</p>
<h1>Six families that were absent, and what each is</h1>
<p class="lede">Every family here was named as missing in the audit. Each is drawn from its own
definition, with the exactness status stated: the elastica and the spirals are fitted; the spline
interpolators are constructions; the rational PH circle and the degree-7 PH curve carry exact controls
after one scale.</p>

<section class="panel"><h2>1 · Euler elastica · κ′ = ±½√(m⁴−κ⁴)</h2>
{panel(e_series, "elastica · the energy-minimising curves", "κ is bounded by m; the family is fitted (elliptic functions)")}
<p class="small">The energy ∫κ²ds is minimised by this family. Curvature is bounded, the curve
inflects, and it loops as m rises. Fitted: elliptic, no exact lattice route claimed.</p></section>

<section class="panel"><h2>2 · Polynomial spirals · κ(s) = s^p</h2>
{panel(p_series, "polynomial spirals", "p = 1 is the clothoid; p = 2 the quintic spiral; p = 3 the next")}
<p class="small">The clothoid is the linear case. Higher p gives a faster turn for the same arc
length; all are transcendental and fitted.</p></section>

<section class="panel"><h2>3 · Sinusoidal spirals · r^n = a·cos(nθ)</h2>
{panel(s_series, "sinusoidal spirals", "n = 1 circle, ½ cardioid, −½ parabola, 2 lemniscate")}
<p class="small">One dial contains the circle, the cardioid, a parabola and the lemniscate. Fitted;
the members were already in the catalogue, the family was not.</p></section>

<section class="panel"><h2>4 · General trochoids · k = R/r</h2>
{panel(t_series, "trochoids", "epi/hypotrochoid with d = r; k is the dial")}
<p class="small">Four k values were in the catalogue (deltoid, nephroid, epicycloids); this is the
dial. Fitted; the roulettes are transcendental unless the rational parametrisation is used.</p></section>

<section class="panel"><h2>5 · Spline interpolators</h2>
{panel(sp_series, "four interpolators on one control polygon", "Catmull–Rom C1 · B-spline C2 · rational quadratic exact conic · quintic Hermite G2")}
<p class="small">Catmull–Rom interpolates its control points at C1; the uniform B-spline is C2 but
does not interpolate them; the rational quadratic with w = 1/√2 is an exact circular arc; the quintic
Hermite span matches position, tangent and acceleration at both ends, so a join is G2 by
construction. These are the interpolator families, not new curves.</p></section>

<section class="panel"><h2>6 · Rational PH and degree-7 PH</h2>
{panel(ph_series, "rational PH and higher-degree PH", f"circle: speed 2/(1+t²) rational · degree-7: n = 0 + 6 + 1, controls integer at scale {scale7:,}")}
<p class="small">The circle is a rational PH curve: its speed is the rational function 2/(1+t²), so
its offsets are exact. The degree-7 curve comes straight from the degree lemma with u, v cubic and h
constant; its six-plus-one controls are integers after the stated scale.</p></section>

<section class="panel"><h2>Status</h2>
<p>All six are fitted or constructions except the PH pair, where the controls are integer at the
scale. None is added to <code>NAMED</code>: the elastica, the spirals and the trochoids are
transcendental; the interpolators are methods; the rational circle is a conic already present. They
are declared here so the family list is closed as far as it can be.</p>
<p class="small">Re-derive: <code>python scripts/missing_families.py</code> ·
test: <code>python -m unittest tests.test_missing_families</code></p></section>
</main></body></html>
"""
    out = ROOT / "workbench" / "missing-families.html"
    out.write_text(html, encoding="utf-8")
    print(out)
    return out


if __name__ == "__main__":
    build()
