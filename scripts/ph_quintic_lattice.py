"""The Tschirnhausen quintic: a PH quintic on a coarse lattice.

    .venv/bin/python scripts/ph_quintic_lattice.py
    open workbench/ph-quintic-lattice.html

TQ(k) is a primitive, polynomial PH quintic of Tschirnhausen type:

    r'(t) = (k²(t²−1)² − 1, 2k(t²−1)),   i.e.  w = k(t²−1) + i
    x(t)  = k²t⁵/5 − 2k²t³/3 + (k²−1)t
    y(t)  = 2k(t³/3 − t)
    s(t)  = k²t⁵/5 − 2k²t³/3 + (k²+1)t

h = 1 (polynomial), gcd(u, v) = 1 (primitive), v constant (Tschirnhausen type,
because the degree-3 member is the Tschirnhausen cubic).  The whole-number
points are at integer t, and how often they come depends only on k mod 15:

    15 | k      every integer t, grid 5 cells per unit
    3 | k      every 5th t,     grid 5
    5 | k      every 3rd t,     grid 15
    otherwise  every 15th t,    grid 15

Every unit piece, reparametrised, is a quintic Bézier with integer controls at
the stated grid, and its arc length is rational.
"""

from __future__ import annotations

from fractions import Fraction as F
from math import comb, lcm
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = "#fbf7ec"
INK, MUTED, GOLD, BLUE, RED = "#2e2413", "#7b6c4e", "#c9a441", "#1f5fa8", "#a23b2a"
RULE = "#d8ccae"

K = 75          # the headline member: every integer t, grid 5
K_SMALL = 3     # the small-numbers member: every 5th t, grid 5
ZOOM_T = F(1, 2)     # half-width of the Q3 / Q6 window; change it and re-run


# -- exact algebra ----------------------------------------------------------

def curve(k, t):
    k2 = k * k
    return (F(k2, 5) * t**5 - F(2 * k2, 3) * t**3 + F(k2 - 1) * t,
            F(2 * k, 3) * t**3 - F(2 * k) * t)


def samples(k, t0, t1, n=600):
    """Points equally spaced along the curve, not equally spaced in t.

    The speed grows like t^4, so a uniform grid in t leaves long straight
    jumps near the ends. s(t) is a polynomial and strictly increasing, so a
    bisection on it gives a smooth polyline with far fewer points.
    """
    k2 = k * k

    def s(t):
        return k2 * t**5 / 5 - 2 * k2 * t**3 / 3 + (k2 + 1) * t

    def p(t):
        return (k2 * t**5 / 5 - 2 * k2 * t**3 / 3 + (k2 - 1) * t,
                2 * k * (t**3 / 3 - t))

    s0, s1 = s(t0), s(t1)
    out = []
    for i in range(n + 1):
        target = s0 + (s1 - s0) * i / n
        a, b = t0, t1
        for _ in range(50):
            m = (a + b) / 2
            if s(m) < target:
                a = m
            else:
                b = m
        t = (a + b) / 2
        x, y = p(t)
        out.append((t, x, y))
    return out


def speed(k, t):
    u = k * (t * t - 1)
    return (u * u - 1, 2 * u, u * u + 1)


def arc(k, t):
    k2 = k * k
    return F(k2, 5) * t**5 - F(2 * k2, 3) * t**3 + F(k2 + 1) * t


def hit_period(k):
    for t in range(1, 61):
        x, y = curve(k, t)
        if x.denominator == 1 and y.denominator == 1:
            return t
    return 0


def shift(coeffs, m):
    """Coefficients of p(u + m), ascending."""
    out = [F(0)] * len(coeffs)
    for i, c in enumerate(coeffs):
        for j in range(i + 1):
            out[j] += c * comb(i, j) * m ** (i - j)
    return out


def bezier(coeffs, n=5):
    a = list(coeffs) + [F(0)] * (n + 1 - len(coeffs))
    return [sum(F(comb(i, j), comb(n, j)) * a[j] for j in range(i + 1))
            for i in range(n + 1)]


def piece_controls(k, m, axis):
    k2 = k * k
    if axis == 0:
        coeffs = [F(0), F(k2 - 1), F(0), F(-2 * k2, 3), F(0), F(k2, 5)]
    else:
        coeffs = [F(0), F(-2 * k), F(0), F(2 * k, 3)]
    return bezier(shift(coeffs, m))


def piece_scale(k, m):
    return lcm(*[v.denominator for v in
                 piece_controls(k, m, 0) + piece_controls(k, m, 1)])


def how_often(k):
    period = hit_period(k)
    return {1: "every integer t", 3: "every 3rd t",
            5: "every 5th t", 15: "every 15th t"}.get(period, f"every {period}th t")


# -- figure -----------------------------------------------------------------

class Frame:
    def __init__(self, w, h, xr, yr, box):
        self.w, self.h = w, h
        self.x0, self.x1 = xr
        self.y0, self.y1 = yr
        self.left, self.top, self.pw, self.ph = box

    def fx(self, v):
        return self.left + (v - self.x0) / (self.x1 - self.x0) * self.pw

    def fy(self, v):
        return self.top + (self.y1 - v) / (self.y1 - self.y0) * self.ph

    def path(self, pts):
        return " ".join(("M" if i == 0 else "L") + f"{self.fx(float(x)):.1f},{self.fy(float(y)):.1f}"
                        for i, (x, y) in enumerate(pts))

    def axes(self):
        return (f'<line x1="{self.fx(0):.1f}" y1="{self.top}" x2="{self.fx(0):.1f}" '
                f'y2="{self.top+self.ph}" stroke="{MUTED}" stroke-width="1"/>'
                f'<line x1="{self.left}" y1="{self.fy(0):.1f}" x2="{self.left+self.pw}" '
                f'y2="{self.fy(0):.1f}" stroke="{MUTED}" stroke-width="1"/>')


def svg(w, h, body):
    return (f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" '
            f'aria-label="{body[0]}"><rect width="{w}" height="{h}" fill="{PAPER}"/>'
            + body[1] + "</svg>")


def curv(k, t):
    t = float(t)
    k2 = k * k
    xp = k2 * (t * t - 1) ** 2 - 1
    yp = 2 * k * (t * t - 1)
    xpp = 4 * k2 * t * (t * t - 1)
    ypp = 4 * k * t
    den = (xp * xp + yp * yp) ** 1.5
    return (xp * ypp - yp * xpp) / den


def nice_ticks(lo, hi, n=2):
    span = hi - lo
    if span <= 0:
        return [lo]
    raw = span / n
    mag = 10 ** __import__("math").floor(__import__("math").log10(raw))
    step = next(m * mag for m in (1, 2, 2.5, 5, 10) if raw <= m * mag)
    first = __import__("math").ceil(lo / step) * step
    out = []
    v = first
    while v <= hi + 1e-9:
        out.append(round(v, 10))
        v += step
    return out


def fig_family():
    W, H = 940, 320
    panels = [(60, "TQ(3)", 320, 40), (350, "TQ(15)", 7600, 190), (640, "TQ(75)", 190000, 950)]
    out = [f'<text x="60" y="24" font-size="14" font-weight="600" fill="{INK}">Fig. Q1 · the family: the same shape, stretched by k</text>',
           f'<text x="60" y="43" font-size="12" fill="{MUTED}">t = −3 … 3 in each panel · axes at x = 0, y = 0 · each panel has its own scale</text>']
    for x0, name, xr, yr in panels:
        f = Frame(W, H, (-xr, xr), (-yr, yr), (x0, 70, 240, 180))
        k = 3 if name == "TQ(3)" else 15 if name == "TQ(15)" else 75
        pts = [(x, y) for _, x, y in samples(k, -3, 3, 500)]
        out.append(f'<text x="{x0}" y="{64}" font-size="13" font-weight="600" fill="{INK}">{name}</text>')
        out.append(f'<text x="{x0}" y="{H-16}" font-size="11" fill="{MUTED}">x ±{xr:,} · y ±{yr:,}</text>')
        out.append(f.axes())
        out.append(f'<path d="{f.path(pts)}" fill="none" stroke="{INK}" stroke-width="2.2"/>')
        for t in range(-3, 4):
            px, py = curve(k, t)
            out.append(f'<circle cx="{f.fx(float(px)):.1f}" cy="{f.fy(float(py)):.1f}" r="3.4" '
                       f'fill="{PAPER}" stroke="{RED}" stroke-width="1.8"/>')
    return svg(W, H, ("the TQ family in three panels", "".join(out)))


def fig_full():
    W, H = 940, 400
    f = Frame(W, H, (-195000, 195000), (-1000, 1000), (96, 70, 800, 250))
    pts = [(x, y) for _, x, y in samples(K, -3, 3, 700)]
    out = [f'<text x="96" y="24" font-size="14" font-weight="600" fill="{INK}">Fig. Q2 · TQ(75) in the plane: all four quadrants</text>',
           f'<text x="96" y="43" font-size="12" fill="{MUTED}">t = −3 … 3 · odd in both coordinates, so point-symmetric about the origin · x and y at different scales (about 195:1)</text>',
           f'<rect x="{f.left}" y="{f.top}" width="{f.pw}" height="{f.ph}" fill="none" stroke="{RULE}"/>',
           f.axes()]
    for v in (-100000, 0, 100000):
        out.append(f'<text x="{f.fx(v):.1f}" y="{f.top+f.ph+20}" text-anchor="middle" font-size="12" fill="{MUTED}">{v:,}</text>')
    for v in (-1000, 0, 1000):
        out.append(f'<text x="{f.left-8}" y="{f.fy(v)+4:.1f}" text-anchor="end" font-size="12" fill="{MUTED}">{v:,}</text>')
    out.append(f'<path d="{f.path(pts)}" fill="none" stroke="{INK}" stroke-width="2.4"/>')
    for t in (-3, -2, 2, 3):
        x, y = curve(K, t)
        px, py = f.fx(float(x)), f.fy(float(y))
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5" fill="{PAPER}" stroke="{RED}" stroke-width="2.2"/>')
        if abs(t) == 3:
            anchor, dx, dy = ("end", -8, 18) if t > 0 else ("start", 8, -10)
            out.append(f'<text x="{px+dx:.1f}" y="{py+dy:.1f}" text-anchor="{anchor}" font-size="12" fill="{RED}">({x}, {y})</text>')
    out.append(f'<text x="{f.fx(0)+8:.1f}" y="{f.fy(0)+16:.1f}" font-size="12" fill="{MUTED}">origin · the S is the next figure</text>')
    out.append(f'<text x="26" y="{f.top+f.ph/2:.0f}" font-size="13" fill="{INK}" transform="rotate(-90 26 {f.top+f.ph/2:.0f})">y, units</text>')
    out.append(f'<text x="{f.left+f.pw/2:.0f}" y="{H-18}" text-anchor="middle" font-size="13" fill="{INK}">x, units</text>')
    return svg(W, H, ("TQ(75) in all four quadrants", "".join(out)))


def fig_zoom():
    """The S window, half-width ZOOM_T."""
    W, H = 940, 400
    tw = float(ZOOM_T)
    xm = abs(float(curve(K, ZOOM_T)[0]))
    ym = abs(float(curve(K, ZOOM_T)[1]))
    f = Frame(W, H, (-xm * 1.12, xm * 1.12), (-ym * 1.15, ym * 1.15), (96, 70, 800, 250))
    pts = [(x, y) for _, x, y in samples(K, -tw, tw, 600)]
    lab = f"{ZOOM_T.numerator}/{ZOOM_T.denominator}"
    out = [f'<text x="96" y="24" font-size="14" font-weight="600" fill="{INK}">Fig. Q3 · the S window t = ±{lab}</text>',
           f'<text x="96" y="43" font-size="12" fill="{MUTED}">inflection at (0, 0) · curvature at the edge {curv(K, ZOOM_T):+.2e} (zero at the origin, growing outward) · x and y at different scales</text>',
           f'<rect x="{f.left}" y="{f.top}" width="{f.pw}" height="{f.ph}" fill="none" stroke="{RULE}"/>',
           f.axes()]
    for v in nice_ticks(f.x0, f.x1):
        out.append(f'<text x="{f.fx(v):.1f}" y="{f.top+f.ph+20}" text-anchor="middle" font-size="12" fill="{MUTED}">{v:g}</text>')
    for v in nice_ticks(f.y0, f.y1):
        out.append(f'<text x="{f.left-8}" y="{f.fy(v)+4:.1f}" text-anchor="end" font-size="12" fill="{MUTED}">{v:g}</text>')
    out.append(f'<path d="{f.path(pts)}" fill="none" stroke="{INK}" stroke-width="2.6"/>')
    for t in (-ZOOM_T, F(0), ZOOM_T):
        x, y = curve(K, t)
        px, py = f.fx(float(x)), f.fy(float(y))
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5" fill="{PAPER}" stroke="{RED}" stroke-width="2.2"/>')
        anchor = "start" if t < 0 else ("end" if t > 0 else "start")
        dx = 9 if t <= 0 else -9
        dy = -9 if t < 0 else (14 if t > 0 else -9)
        label = f"±{lab}" if t != 0 else "inflection, (0, 0)"
        out.append(f'<text x="{px+dx:.1f}" y="{py+dy:.1f}" text-anchor="{anchor}" font-size="12" fill="{RED}">{label}</text>')
    out.append(f'<text x="26" y="{f.top+f.ph/2:.0f}" font-size="13" fill="{INK}" transform="rotate(-90 26 {f.top+f.ph/2:.0f})">y, units</text>')
    out.append(f'<text x="{f.left+f.pw/2:.0f}" y="{H-18}" text-anchor="middle" font-size="13" fill="{INK}">x, units</text>')
    return svg(W, H, (f"the S window at t = {lab}", "".join(out)))


def fig_cut():
    W, H = 940, 400
    f = Frame(W, H, (-8000, 195000), (-250, 1050), (96, 70, 800, 250))
    out = [f'<text x="96" y="24" font-size="14" font-weight="600" fill="{INK}">Fig. Q4 · cutting at the lattice stops: three exact pieces</text>',
           f'<text x="96" y="43" font-size="12" fill="{MUTED}">t ∈ [0,1], [1,2], [2,3] · each piece is a PH quintic with integer controls on the grid of 5 · x and y at different scales (about 156:1)</text>',
           f'<rect x="{f.left}" y="{f.top}" width="{f.pw}" height="{f.ph}" fill="none" stroke="{RULE}"/>',
           f.axes()]
    for v in (0, 50000, 100000, 150000):
        out.append(f'<text x="{f.fx(v):.1f}" y="{f.top+f.ph+20}" text-anchor="middle" font-size="12" fill="{MUTED}">{v:,}</text>')
    for v in (-250, 0, 500, 1000):
        out.append(f'<text x="{f.left-8}" y="{f.fy(v)+4:.1f}" text-anchor="end" font-size="12" fill="{MUTED}">{v}</text>')
    cols = (BLUE, GOLD, RED)
    for i, col in enumerate(cols):
        pts = [(x, y) for _, x, y in samples(K, i, i + 1, 220)]
        out.append(f'<path d="{f.path(pts)}" fill="none" stroke="{col}" stroke-width="3"/>')
    for t in range(0, 4):
        x, y = curve(K, t)
        px, py = f.fx(float(x)), f.fy(float(y))
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5.5" fill="{PAPER}" stroke="{INK}" stroke-width="2.2"/>')
        anchor, dx, dy = ("end", -8, 18) if t == 3 else ("start", 8, -10)
        out.append(f'<text x="{px+dx:.1f}" y="{py+dy:.1f}" text-anchor="{anchor}" font-size="12" fill="{INK}">({x}, {y})</text>')
    out.append(f'<text x="26" y="{f.top+f.ph/2:.0f}" font-size="13" fill="{INK}" transform="rotate(-90 26 {f.top+f.ph/2:.0f})">y, units</text>')
    out.append(f'<text x="{f.left+f.pw/2:.0f}" y="{H-18}" text-anchor="middle" font-size="13" fill="{INK}">x, units</text>')
    return svg(W, H, ("the three cut pieces", "".join(out)))


def fig_grid():
    W, H = 940, 300
    bars = [("cubic chain, 12 steps", 256, BLUE),
            ("quintic chain, 12 steps", 442368, RED),
            ("quintic stops, exact", 5, GOLD)]
    left, top, pw, ph = 250, 70, 620, 160
    out = [f'<text x="60" y="24" font-size="14" font-weight="600" fill="{INK}">Fig. Q5 · the grid each route needs, log scale</text>',
           f'<text x="60" y="43" font-size="12" fill="{MUTED}">cells per unit · the chain buys whole-number steps with a very fine grid; the stops need only the points whole</text>']
    for i, (name, val, col) in enumerate(bars):
        y = top + i * 52
        w = (__import__("math").log10(val) / 6) * pw
        out.append(f'<text x="{left-10}" y="{y+18}" text-anchor="end" font-size="13" fill="{INK}">{name}</text>')
        out.append(f'<rect x="{left}" y="{y}" width="{w:.1f}" height="26" fill="{col}" opacity="0.35" stroke="{col}"/>')
        out.append(f'<text x="{left+w+8:.1f}" y="{y+18}" font-size="13" fill="{INK}">{val:,}</text>')
    for e in (0, 2, 4, 6):
        x = left + e / 6 * pw
        out.append(f'<line x1="{x:.1f}" y1="{top-8}" x2="{x:.1f}" y2="{top+ph}" stroke="{RULE}"/>')
        out.append(f'<text x="{x:.1f}" y="{top+ph+22}" text-anchor="middle" font-size="12" fill="{MUTED}">10^{e}</text>')
    out.append(f'<text x="{left+pw/2:.0f}" y="{H-16}" text-anchor="middle" font-size="13" fill="{INK}">grid, cells per unit (logarithmic)</text>')
    return svg(W, H, ("grid cost of the two routes", "".join(out)))


def fig_coords():
    """x(t) and y(t) side by side, on the SAME vertical scale."""
    W, H = 940, 430
    ymax = 200000
    fa = Frame(W, H, (-3, 3), (-ymax, ymax), (74, 78, 356, 240))
    fb = Frame(W, H, (-3, 3), (-ymax, ymax), (548, 78, 356, 240))
    out = [f'<text x="74" y="24" font-size="14" font-weight="600" fill="{INK}">Fig. Q6 · x(t) and y(t) side by side, at the same vertical scale</text>',
           f'<text x="74" y="43" font-size="12" fill="{MUTED}">t = −3 … 3 · both panels share the ticks: x reaches ±189,000, y only ±900 — so y is flat here</text>']
    for f, lab, col in ((fa, "x(t)", INK), (fb, "y(t)", BLUE)):
        out.append(f'<text x="{f.left}" y="{f.top-10}" font-size="13" font-weight="600" fill="{col}">{lab}</text>')
        out.append(f'<rect x="{f.left}" y="{f.top}" width="{f.pw}" height="{f.ph}" fill="none" stroke="{RULE}"/>')
        out.append(f.axes())
        for v in (-100000, 0, 100000):
            out.append(f'<text x="{f.left-8}" y="{f.fy(v)+4:.1f}" text-anchor="end" font-size="11" fill="{MUTED}">{v:,}</text>')
        for v in (-3, -1, 0, 1, 3):
            out.append(f'<text x="{f.fx(v):.1f}" y="{f.top+f.ph+18}" text-anchor="middle" font-size="11" fill="{MUTED}">{v}</text>')
        out.append(f'<text x="{f.left+f.pw/2:.0f}" y="{H-16}" text-anchor="middle" font-size="12" fill="{INK}">t</text>')
    pts = samples(K, -3, 3, 500)
    out.append(f'<path d="{fa.path([(t, x) for t, x, _ in pts])}" fill="none" stroke="{INK}" stroke-width="2.4"/>')
    out.append(f'<path d="{fb.path([(t, y) for t, _, y in pts])}" fill="none" stroke="{BLUE}" stroke-width="2.4"/>')
    for t in (-3, 0, 3):
        x, y = curve(K, t)
        out.append(f'<circle cx="{fa.fx(t):.1f}" cy="{fa.fy(float(x)):.1f}" r="4" fill="{PAPER}" stroke="{RED}" stroke-width="2"/>')
        out.append(f'<circle cx="{fb.fx(t):.1f}" cy="{fb.fy(float(y)):.1f}" r="4" fill="{PAPER}" stroke="{RED}" stroke-width="2"/>')
    return svg(W, H, ("x and y at the same vertical scale", "".join(out)))


def fig_points():
    """The calculated points, joined, against the real curve."""
    W, H = 940, 400
    f = Frame(W, H, (-195000, 195000), (-1000, 1000), (96, 70, 800, 250))
    real = [(x, y) for _, x, y in samples(K, -3, 3, 700)]
    calc = [curve(K, t) for t in range(-3, 4)]
    out = [f'<text x="96" y="24" font-size="14" font-weight="600" fill="{INK}">Fig. Q7 · the calculated points, joined, against the real curve</text>',
           f'<text x="96" y="43" font-size="12" fill="{MUTED}">(x, y) at t = −3 … 3 · pale: the real quintic · blue: the straight joins · rings: the calculated points · scales about 195:1</text>',
           f'<rect x="{f.left}" y="{f.top}" width="{f.pw}" height="{f.ph}" fill="none" stroke="{RULE}"/>',
           f.axes()]
    for v in (-100000, 0, 100000):
        out.append(f'<text x="{f.fx(v):.1f}" y="{f.top+f.ph+20}" text-anchor="middle" font-size="12" fill="{MUTED}">{v:,}</text>')
    for v in (-1000, 0, 1000):
        out.append(f'<text x="{f.left-8}" y="{f.fy(v)+4:.1f}" text-anchor="end" font-size="12" fill="{MUTED}">{v:,}</text>')
    out.append(f'<path d="{f.path(real)}" fill="none" stroke="{MUTED}" stroke-width="1.6" opacity="0.55"/>')
    out.append(f'<path d="{f.path(calc)}" fill="none" stroke="{BLUE}" stroke-width="1.8" stroke-dasharray="6 4"/>')
    for i, (x, y) in enumerate(calc):
        t = i - 3
        px, py = f.fx(float(x)), f.fy(float(y))
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5" fill="{PAPER}" stroke="{RED}" stroke-width="2.2"/>')
        if abs(t) >= 2:
            if t == 3:
                anchor, dx, dy = "end", -8, 18
            elif t == -3:
                anchor, dx, dy = "start", 8, -10
            elif t == 2:
                anchor, dx, dy = "start", 8, -10
            else:
                anchor, dx, dy = "end", -8, 18
            out.append(f'<text x="{px+dx:.1f}" y="{py+dy:.1f}" text-anchor="{anchor}" font-size="12" fill="{RED}">({x}, {y})</text>')
    out.append(f'<text x="{f.fx(0)+10:.1f}" y="{f.fy(0)+20:.1f}" font-size="12" fill="{MUTED}">t = −1, 0, 1 sit within 3 px of the origin here — see Fig. Q3</text>')
    out.append(f'<text x="26" y="{f.top+f.ph/2:.0f}" font-size="13" fill="{INK}" transform="rotate(-90 26 {f.top+f.ph/2:.0f})">y, units</text>')
    out.append(f'<text x="{f.left+f.pw/2:.0f}" y="{H-18}" text-anchor="middle" font-size="13" fill="{INK}">x, units</text>')
    return svg(W, H, ("the calculated points against the real curve", "".join(out)))


# -- the general PH quintic: u, v any polynomials ---------------------------

S_CASES = [
    ((-6, -5, 6), (-2, 4, -6)),     # gentle S, 40 deg
    ((-6, -1, -6), (-4, -4, 6)),    # 50 deg, inflection early
    ((-6, -1, 6), (-3, 4, -3)),     # 74 deg, inflection near the middle
    ((1, 2, -1), (1, -1, 1)),       # the repo's case 1, 37 deg, pitch 30
    ((0, -3, 2), (3, 3, 4)),        # 349 deg, nearly a loop
    ((0, -4, 5), (-5, -4, -3)),     # 350 deg
    ((-6, 1, 6), (-2, 2, -3)),      # 180 deg
    ((3, 0, -3), (1,)),             # TQ(3): the inflection at the start
]


def _mul(a, b):
    out = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def _pad(a, n):
    return list(a) + [F(0)] * (n - len(a))


def _integ(p):
    return [F(0)] + [c / (k + 1) for k, c in enumerate(p)]


def uv_curve(u, v):
    """Power coefficients of x and y for r' = (u²−v², 2uv), r(0) = 0."""
    n = max(len(u), len(v))
    u = _pad([F(c) for c in u], n)
    v = _pad([F(c) for c in v], n)
    uu = _mul(u, u)
    vv = _mul(v, v)
    m = max(len(uu), len(vv))
    xp = [a - b for a, b in zip(_pad(uu, m), _pad(vv, m))]
    yp = [2 * c for c in _mul(u, v)]
    return _integ(xp), _integ(yp)


def _ev(p, t):
    return sum(c * t ** k for k, c in enumerate(p))


def uv_samples(u, v, n=260):
    """Equal-arc-length samples of the uv curve over t in [0, 1]."""
    x, y = uv_curve(u, v)
    n_ = max(len(u), len(v))
    uu = _mul(_pad([F(c) for c in u], n_), _pad([F(c) for c in u], n_))
    vv = _mul(_pad([F(c) for c in v], n_), _pad([F(c) for c in v], n_))
    sig = [a + b for a, b in zip(_pad(uu, max(len(uu), len(vv))),
                                 _pad(vv, max(len(uu), len(vv))))]
    arc = _integ(sig)
    s1 = float(_ev(arc, 1))
    out = []
    for i in range(n + 1):
        target = s1 * i / n
        a, b = 0.0, 1.0
        for _ in range(45):
            m = (a + b) / 2
            if float(_ev(arc, m)) < target:
                a = m
            else:
                b = m
        t = (a + b) / 2
        out.append((t, float(_ev(x, t)), float(_ev(y, t))))
    return out


def s_info(u, v):
    """Inflection t, pitch, endpoint in cells, tangent swing in degrees."""
    import math
    x, y = uv_curve(u, v)
    n = max(len(u), len(v))
    U = _pad([F(c) for c in u], n)
    V = _pad([F(c) for c in v], n)
    du = [U[1], 2 * U[2]] if n > 2 else [U[1]]
    dv = [V[1], 2 * V[2]] if n > 2 else [V[1]]
    a = _mul(U, dv)
    b = _mul(V, du)
    m = max(len(a), len(b))
    W = [p - q for p, q in zip(_pad(a, m), _pad(b, m))]
    while len(W) > 1 and W[-1] == 0:
        W.pop()
    infl = None
    if len(W) == 3:
        A, B, C = W[2], W[1], W[0]
        d = float(B * B - 4 * A * C)
        if d > 0:
            for r in ((-float(B) + d ** .5) / (2 * float(A)),
                      (-float(B) - d ** .5) / (2 * float(A))):
                if 0 <= r <= 1:
                    infl = r
    elif len(W) == 2 and W[1]:
        r = -float(W[0]) / float(W[1])
        if 0 <= r <= 1:
            infl = r
    pitch = 1
    for poly in (x, y):
        for j, c in enumerate(poly):
            if j == 0:
                continue
            num = int(c * j)          # the integrand coefficient at t^(j-1)
            if num == 0:
                continue
            pitch = lcm(pitch, j // __import__("math").gcd(abs(num), j))
    u0, v0 = float(U[0]), float(V[0])
    u1, v1 = float(sum(U)), float(sum(V))
    a0 = math.degrees(math.atan2(2 * u0 * v0, u0 * u0 - v0 * v0))
    a1 = math.degrees(math.atan2(2 * u1 * v1, u1 * u1 - v1 * v1))
    swing = abs((a1 - a0 + 180) % 360 - 180)
    return infl, pitch, (sum(x), sum(y)), swing


def fig_gallery():
    W, H = 940, 700
    cols, rows = 4, 2
    pw, ph, gapx, gapy = 196, 250, 18, 24
    x0, y0 = 26, 60
    out = [f'<text x="26" y="24" font-size="14" font-weight="600" fill="{INK}">Fig. Q8 · eight S curves, variable v, every one on a small pitch</text>',
           f'<text x="26" y="43" font-size="12" fill="{MUTED}">each panel: the curve, the endpoints, and the inflection ring · u and v are the two speed recipes</text>']
    for idx, (u, v) in enumerate(S_CASES):
        cx = x0 + (idx % cols) * (pw + gapx)
        cy = y0 + (idx // cols) * (ph + gapy)
        pts = uv_samples(u, v)
        xs = [q[1] for q in pts]
        ys = [q[2] for q in pts]
        xr = max(1e-9, max(abs(min(xs)), abs(max(xs)))) * 1.15
        yr = max(1e-9, max(abs(min(ys)), abs(max(ys)))) * 1.15
        f = Frame(W, H, (-xr, xr), (-yr, yr), (cx, cy + 34, pw, 170))
        infl, pitch, end, swing = s_info(u, v)
        out.append(f'<text x="{cx}" y="{cy+12}" font-size="11" font-weight="600" fill="{INK}">u={u}  v={v}</text>')
        where = f"inflection {infl:.2f}" if infl is not None else "inflection at the start"
        out.append(f'<text x="{cx}" y="{cy+26}" font-size="10" fill="{MUTED}">{where} · pitch {pitch}</text>')
        out.append(f'<rect x="{f.left}" y="{f.top}" width="{f.pw}" height="{f.ph}" fill="none" stroke="{RULE}"/>')
        out.append(f.axes())
        out.append(f'<path d="{f.path([(q[1], q[2]) for q in pts])}" fill="none" stroke="{INK}" stroke-width="2"/>')
        for t, x, y in (pts[0], pts[-1]):
            out.append(f'<circle cx="{f.fx(x):.1f}" cy="{f.fy(y):.1f}" r="3.2" fill="{PAPER}" stroke="{MUTED}" stroke-width="1.6"/>')
        if infl is not None and 0 < infl < 1:
            tx, ty = _ev(uv_curve(u, v)[0], infl), _ev(uv_curve(u, v)[1], infl)
            out.append(f'<circle cx="{f.fx(float(tx)):.1f}" cy="{f.fy(float(ty)):.1f}" r="4" fill="{PAPER}" stroke="{RED}" stroke-width="2"/>')
        out.append(f'<text x="{cx}" y="{cy+ph-4}" font-size="10" fill="{MUTED}">end ({end[0] * pitch:.0f}, {end[1] * pitch:.0f}) in cells</text>')
    return svg(W, H, ("eight S curves", "".join(out)))


def member_rows():
    rows = []
    for k in (3, 5, 15, 25, 75):
        period = hit_period(k)
        hits = sum(1 for t in range(0, 6) if all(c.denominator == 1 for c in curve(k, t)))
        scale = piece_scale(k, 0)
        maxc = max(abs(v * scale) for v in
                   piece_controls(k, 0, 0) + piece_controls(k, 0, 1))
        rows.append((k, hits, how_often(k), scale, maxc))
    return rows


def hit_rows(k, n=5):
    rows = []
    for t in range(0, n + 1):
        x, y = curve(k, t)
        rows.append((t, x, y, arc(k, t)))
    return rows


def build():
    rows = "".join(
        f"<tr><td>TQ({k})</td><td>{hits}</td><td>{often}</td><td>{scale}</td><td>{maxc}</td></tr>"
        for k, hits, often, scale, maxc in member_rows())
    hits = "".join(
        f"<tr><td>{t}</td><td>{x}</td><td>{y}</td><td>{s}</td></tr>"
        for t, x, y, s in hit_rows(K))
    cx = [int(v * 5) for v in piece_controls(K, 0, 0)]
    cy = [int(v * 5) for v in piece_controls(K, 0, 1)]

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Tschirnhausen quintic: a PH quintic on a coarse lattice</title>
<style>
:root{{--paper:{PAPER};--ink:{INK};--muted:{MUTED};--rule:{RULE}}}
*{{box-sizing:border-box}} body{{margin:0;background:#f3eddf;color:var(--ink);font:16px/1.55 Georgia,serif}}
main{{max-width:1120px;margin:0 auto;padding:34px 22px 70px}}
.eyebrow{{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}}
h1{{font-size:31px;line-height:1.12;margin:0 0 8px}} h2{{font-size:20px;margin:0 0 8px}}
.lede{{max-width:900px;color:var(--muted)}}
.panel{{background:var(--paper);border:1px solid var(--rule);padding:16px 18px;margin:0 0 18px}}
table{{border-collapse:collapse;font:12px/1.5 ui-monospace,Menlo,monospace;margin:10px 0;width:100%}}
th,td{{border:1px solid var(--rule);padding:5px 8px;text-align:right}} th{{color:var(--muted);font-weight:400}}
.small{{font:12px/1.6 ui-monospace,Menlo,monospace;color:var(--muted)}}
code{{font:12px ui-monospace,Menlo,monospace;background:#f4ecd7;padding:1px 4px}}
</style></head><body><main>
<p class="eyebrow">curve-lab · PH quintics · Tschirnhausen type</p>
<h1>A PH quintic that lands on a coarse lattice</h1>
<p class="lede">TQ(75) is a primitive, polynomial Pythagorean-hodograph quintic with a constant
second hodograph component. Every integer t is a whole-number point, the control points are
integers on a grid of 5 cells per unit, and the length between stops is rational. So the curve
can be cut at its lattice points without losing exactness.</p>

<section class="panel">
<h2>The family</h2>
<p>Write the hodograph as <code>w = k(t²−1) + i</code>. Then
<code>x′ = k²(t²−1)² − 1</code>, <code>y′ = 2k(t²−1)</code>, and the speed is
<code>σ = k²(t²−1)² + 1</code> — a polynomial, so the curve is PH and its length is exact.
The degree is <code>2·2 + 1 = 5</code>. <code>h = 1</code> makes it polynomial;
<code>gcd(u, v) = 1</code> makes it primitive; <code>v</code> constant makes it
Tschirnhausen type — the degree-3 member of exactly this family is the Tschirnhausen cubic.
Because <code>v</code> is constant, <code>y</code> is a cubic; only <code>x</code> carries the
fifth-degree work.</p>
{fig_family()}
<p class="small">k stretches the same shape: x grows like k², y like k. TQ(3) is compact enough
to read; TQ(75) is the same curve on a much longer leash. k is taken positive: a negative k is
the same curve mirrored in the x-axis — the hits, the grid and the lengths do not change — and
k = 0 degenerates to a straight line.</p>
</section>

<section class="panel">
<h2>How many hits, and how fine the grid</h2>
<p>Whole-number points come at integer t. How often, and how fine the grid, depends only on
which of 3 and 5 divide k. In the window t = 0…5:</p>
<table>
<tr><th>member</th><th>hits in t = 0…5</th><th>they come</th><th>grid, cells per unit</th><th>biggest control number</th></tr>
{rows}
</table>
<p class="small">k = 75 is the same class as k = 15: every integer t, grid 5. Raising k does not
buy more hits — it only multiplies the coordinates by (k/15)². The biggest control number is the
largest number in the six control points of the first piece.</p>
</section>

<section class="panel">
<h2>Stops at a pitch: t does not have to be an integer</h2>
<p>The integer t are the stops of the <em>unit</em> lattice. At a pitch, any rational t is a stop:
the point is rational, and the pitch that clears its denominators makes it an integer cell. The
price is the pitch, and it grows fast.</p>
<table>
<tr><th>t</th><th>the point</th><th>pitch that makes it whole</th><th>the point in cells</th></tr>
<tr><td>1/2</td><td>(76109/32, −275/4)</td><td>32</td><td>(76109, −2200)</td></tr>
<tr><td>1/5</td><td>(27379/25, −148/5)</td><td>25</td><td>(27379, −740)</td></tr>
<tr><td>1/4</td><td>(1380869/1024, −1175/32)</td><td>1024</td><td>(1380869, −37600)</td></tr>
</table>
<p class="small">So the answer to "how many hits" depends on the pitch: pitch 1 gives the integers,
pitch 32 adds the halves, pitch 1024 adds the quarters. The grid of 5 in the table above is the
control grid, not the hit grid — those are different numbers.</p>
</section>

<section class="panel">
<h2>Fig. Q2 · all four quadrants</h2>
{fig_full()}
<p class="small">The curve is odd in both coordinates, so the four quadrants hold two mirror
copies of one shape. The stops at t = ±2, ±3 are ringed; the origin and its S are the next figure.</p>
</section>

<section class="panel">
<h2>Fig. Q3 · the S, with the outliers left out</h2>
{fig_zoom()}
<p class="small">This is the window t = ±1/2. The curvature is zero at the origin and grows
outward, so the S is most visible at the edge of the window: about 1.5×10⁻⁵ there. The curve is
regular everywhere — the speed is <code>k²(t²−1)² + 1</code>, never zero — so there are no cusps.
Change <code>ZOOM_T</code> in the generator and re-run to move the window.</p>
</section>

<section class="panel">
<h2>The stops, exactly</h2>
<table>
<tr><th>t</th><th>x</th><th>y</th><th>arc length s(t)</th></tr>
{hits}
</table>
<p class="small">s(t) = 1125t⁵ − 3750t³ + 5626t. Every value in the table is an integer, and so
is every length — no square roots anywhere.</p>
</section>

<section class="panel">
<h2>Fig. Q4 · cutting at the stops</h2>
{fig_cut()}
<p class="small">Three pieces, cut at t = 1 and t = 2. Each is a PH quintic with integer
endpoints and a rational length; the pieces can be separated and used on their own.</p>
</section>

<section class="panel">
<h2>Cutting, in controls</h2>
<p>Take the piece <code>t ∈ [0, 1]</code>. Reparametrised to <code>u ∈ [0, 1]</code> it is a
quintic Bézier with integer controls on the grid of 5:</p>
<p class="small">x: ({', '.join(str(v) for v in cx)}) · y: ({', '.join(str(v) for v in cy)})</p>
<p>The same holds for every unit piece <code>t ∈ [m, m+1]</code>: shifting <code>t = u + m</code>
keeps integer coefficients, so the controls stay integers on the same grid, and the piece is
still PH. That is the difference from the Tschirnhausen cubic: there, exact lattice nodes meant
irrational chord sides; here the cut points and the lengths are both exact.</p>
</section>

<section class="panel">
<h2>Fig. Q5 · what the two routes cost</h2>
{fig_grid()}
<p class="small">The chain's whole-number steps are real, but at degree 5 they need a grid of
442,368 and still miss the endpoint by 31 units in x. Cutting at the exact stops needs only the
points whole: a grid of 5.</p>
</section>

<section class="panel">
<h2>Fig. Q6 · coordinate by coordinate</h2>
{fig_coords()}
<p class="small">The earlier version scaled each panel to its own values, which made the two look
comparable. On the same ticks they are not: x does all the work, and y is flat. That is the
200:1 ratio that makes the plane curve a long shallow sweep, and it is why "gentle x and y" was
a misleading reading of the autoscaled panels.</p>
</section>

<section class="panel">
<h2>Fig. Q7 · the calculated points, joined</h2>
{fig_points()}
<p class="small">The pale line is the real quintic; the blue dashes join the calculated points.
The points are exact — whole-number coordinates sitting on the curve. The joins between them are
the only approximation, and at this scale they are almost indistinguishable from the curve.</p>
</section>

<section class="panel">
<h2>The S, in plain words</h2>
<p>Two recipes decide everything: <code>u(t)</code> is the sideways speed and <code>v(t)</code> the
up speed. The curve's heading is twice the angle whose tangent is <code>v/u</code>. When that
heading turns around — when <code>u·v′ − v·u′</code> changes sign — the curve stops bending one way
and starts bending the other. That place is the inflection, and that is the S.</p>
<p>With <code>v</code> constant, <code>u·v′ − v·u′</code> is just <code>−u′</code>, which is zero
only at the start: the turn is stuck at the endpoint. With <code>v</code> free, the expression is a
quadratic, so its zero can be placed anywhere in the span. That is the knob.</p>
<p>Integer points: if the <em>integrated</em> coefficients are integers, every integer t is a
whole-number point. Integration divides by 2, 3, 4 and 5, so the pitch is the smallest number that
clears those divisions. Every curve below is on a pitch-5 or pitch-30 grid, and the inflection, the
turn and the endpoint are all exact.</p>
</section>

<section class="panel">
<h2>Fig. Q8 · eight S curves, one page</h2>
{fig_gallery()}
<p class="small">The red ring is the inflection. Left to right, top to bottom: a gentle 40° S, a
50° S with an early inflection, a 74° S with the inflection near the middle, the repo's case 1 on a
pitch-30 grid, then four strong turns — 349°, 350°, 180°, and TQ(3) with its inflection at the very
start. Every panel is exact; the pitch is the graph paper, not an approximation.</p>
</section>

<section class="panel">
<h2>See also</h2>
<p><a href="ph-families.html">PH families, degree by degree</a> — the three quintics used as the
comparison, with the PH–Hermite interpolant and the milestone table.
<a href="ph-families.html#ph-integer">PH integer milestones</a> — the t = k/m lattice.
The discrete chain on the Tschirnhausen cubic is
<a href="../tph_tri_chain/tph-tri-sandbox.html">the tph_tri_chain sandbox</a>; the sandbox's
two-method table is the degree-3 version of the comparison on this page.</p>
<p class="small">Re-derive: <code>python scripts/ph_quintic_lattice.py</code> · test:
<code>python -m unittest tests.test_ph_quintic_lattice</code></p>
</section>
</main></body></html>
"""
    out = ROOT / "workbench" / "ph-quintic-lattice.html"
    out.write_text(html, encoding="utf-8")
    print(out)
    return out


if __name__ == "__main__":
    build()
