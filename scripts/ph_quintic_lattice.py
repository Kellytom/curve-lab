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


# -- exact algebra ----------------------------------------------------------

def curve(k, t):
    k2 = k * k
    return (F(k2, 5) * t**5 - F(2 * k2, 3) * t**3 + F(k2 - 1) * t,
            F(2 * k, 3) * t**3 - F(2 * k) * t)


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


def fig_family():
    W, H = 940, 320
    panels = [(60, "TQ(3)", 320, 40), (350, "TQ(15)", 7600, 190), (640, "TQ(75)", 190000, 950)]
    out = [f'<text x="60" y="24" font-size="14" font-weight="600" fill="{INK}">Fig. Q1 · the family: the same shape, stretched by k</text>',
           f'<text x="60" y="43" font-size="12" fill="{MUTED}">t = −3 … 3 in each panel · axes at x = 0, y = 0 · each panel has its own scale</text>']
    for x0, name, xr, yr in panels:
        f = Frame(W, H, (-xr, xr), (-yr, yr), (x0, 70, 240, 180))
        pts = [curve(3 if name == "TQ(3)" else 15 if name == "TQ(15)" else 75, F(3 * i, 100) - 3) for i in range(201)]
        k = 3 if name == "TQ(3)" else 15 if name == "TQ(15)" else 75
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
    pts = [curve(K, F(3 * i, 100) - 3) for i in range(201)]
    out = [f'<text x="96" y="24" font-size="14" font-weight="600" fill="{INK}">Fig. Q2 · TQ(75) in the plane: all four quadrants</text>',
           f'<text x="96" y="43" font-size="12" fill="{MUTED}">t = −3 … 3 · the curve is odd in both coordinates, so it is point-symmetric about the origin</text>',
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
    W, H = 940, 400
    f = Frame(W, H, (-8200, 8200), (-160, 160), (96, 70, 800, 250))
    pts = [curve(K, F(-8, 5) + F(16 * i, 1000)) for i in range(201)]
    out = [f'<text x="96" y="24" font-size="14" font-weight="600" fill="{INK}">Fig. Q3 · the S at the origin, and the turn near t = ±1</text>',
           f'<text x="96" y="43" font-size="12" fill="{MUTED}">t = −1.6 … 1.6 · the inflection is at (0, 0) · dashed rings: y = 0 at t = ±√3</text>',
           f'<rect x="{f.left}" y="{f.top}" width="{f.pw}" height="{f.ph}" fill="none" stroke="{RULE}"/>',
           f.axes()]
    for v in (-8000, -4000, 0, 4000, 8000):
        out.append(f'<text x="{f.fx(v):.1f}" y="{f.top+f.ph+20}" text-anchor="middle" font-size="12" fill="{MUTED}">{v:,}</text>')
    for v in (-150, 0, 150):
        out.append(f'<text x="{f.left-8}" y="{f.fy(v)+4:.1f}" text-anchor="end" font-size="12" fill="{MUTED}">{v}</text>')
    out.append(f'<path d="{f.path(pts)}" fill="none" stroke="{INK}" stroke-width="2.4"/>')
    for t in (-1, 0, 1):
        x, y = curve(K, t)
        px, py = f.fx(float(x)), f.fy(float(y))
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5" fill="{PAPER}" stroke="{RED}" stroke-width="2.2"/>')
        if t == 0:
            out.append(f'<text x="{px+10:.1f}" y="{py+18:.1f}" font-size="12" fill="{RED}">inflection, (0, 0)</text>')
        elif t == -1:
            out.append(f'<text x="{px:.1f}" y="{py-10:.1f}" text-anchor="middle" font-size="12" fill="{RED}">({x}, {y})</text>')
        else:
            out.append(f'<text x="{px:.1f}" y="{py+20:.1f}" text-anchor="middle" font-size="12" fill="{RED}">({x}, {y})</text>')
    for t in (F(177, 100), F(-177, 100)):
        x, y = curve(K, t)
        out.append(f'<circle cx="{f.fx(float(x)):.1f}" cy="{f.fy(float(y)):.1f}" r="6" fill="none" '
                   f'stroke="{GOLD}" stroke-width="2" stroke-dasharray="4 3"/>')
    out.append(f'<text x="26" y="{f.top+f.ph/2:.0f}" font-size="13" fill="{INK}" transform="rotate(-90 26 {f.top+f.ph/2:.0f})">y, units</text>')
    out.append(f'<text x="{f.left+f.pw/2:.0f}" y="{H-18}" text-anchor="middle" font-size="13" fill="{INK}">x, units</text>')
    return svg(W, H, ("the S at the origin", "".join(out)))


def fig_cut():
    W, H = 940, 400
    f = Frame(W, H, (-8000, 195000), (-250, 1050), (96, 70, 800, 250))
    out = [f'<text x="96" y="24" font-size="14" font-weight="600" fill="{INK}">Fig. Q4 · cutting at the lattice stops: three exact pieces</text>',
           f'<text x="96" y="43" font-size="12" fill="{MUTED}">t ∈ [0,1], [1,2], [2,3] · each piece is a PH quintic with integer controls on the grid of 5</text>',
           f'<rect x="{f.left}" y="{f.top}" width="{f.pw}" height="{f.ph}" fill="none" stroke="{RULE}"/>',
           f.axes()]
    for v in (0, 50000, 100000, 150000):
        out.append(f'<text x="{f.fx(v):.1f}" y="{f.top+f.ph+20}" text-anchor="middle" font-size="12" fill="{MUTED}">{v:,}</text>')
    for v in (-250, 0, 500, 1000):
        out.append(f'<text x="{f.left-8}" y="{f.fy(v)+4:.1f}" text-anchor="end" font-size="12" fill="{MUTED}">{v}</text>')
    cols = (BLUE, GOLD, RED)
    for i, col in enumerate(cols):
        pts = [curve(K, F(i) + F(j, 60)) for j in range(61)]
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
    W, H = 940, 480
    fa = Frame(W, H, (-3, 3), (-200000, 200000), (96, 70, 800, 150))
    fb = Frame(W, H, (-3, 3), (-1000, 1000), (96, 280, 800, 150))
    out = [f'<text x="96" y="24" font-size="14" font-weight="600" fill="{INK}">Fig. Q6 · TQ(75) coordinate by coordinate: whole at every integer t</text>',
           f'<text x="96" y="43" font-size="12" fill="{MUTED}">x(t) and y(t) against t · rings: the stops t = −3 … 3, where both are integers</text>']
    for f, lab in ((fa, "x, units"), (fb, "y, units")):
        out.append(f'<rect x="{f.left}" y="{f.top}" width="{f.pw}" height="{f.ph}" fill="none" stroke="{RULE}"/>')
        out.append(f.axes())
        for t in range(-3, 4):
            out.append(f'<line x1="{f.fx(t):.1f}" y1="{f.top}" x2="{f.fx(t):.1f}" y2="{f.top+f.ph}" stroke="{RULE}" stroke-width="0.7"/>')
        for t in range(-3, 4):
            out.append(f'<text x="{f.fx(t):.1f}" y="{f.top+f.ph+16}" text-anchor="middle" font-size="11" fill="{MUTED}">{t}</text>')
        out.append(f'<text x="26" y="{f.top+f.ph/2:.0f}" font-size="12" fill="{INK}" transform="rotate(-90 26 {f.top+f.ph/2:.0f})">{lab}</text>')
    out.append(f'<path d="{fa.path([(F(3*i,100)-3, curve(K, F(3*i,100)-3)[0]) for i in range(201)])}" fill="none" stroke="{INK}" stroke-width="2.2"/>')
    out.append(f'<path d="{fb.path([(F(3*i,100)-3, curve(K, F(3*i,100)-3)[1]) for i in range(201)])}" fill="none" stroke="{INK}" stroke-width="2.2"/>')
    for t in range(-3, 4):
        x, y = curve(K, t)
        out.append(f'<circle cx="{fa.fx(t):.1f}" cy="{fa.fy(float(x)):.1f}" r="4" fill="{PAPER}" stroke="{RED}" stroke-width="2"/>')
        out.append(f'<circle cx="{fb.fx(t):.1f}" cy="{fb.fy(float(y)):.1f}" r="4" fill="{PAPER}" stroke="{RED}" stroke-width="2"/>')
    out.append(f'<text x="{fa.left+fa.pw/2:.0f}" y="{H-14}" text-anchor="middle" font-size="13" fill="{INK}">t — the parameter</text>')
    return svg(W, H, ("x and y against t", "".join(out)))


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
<h2>Fig. Q2 · all four quadrants</h2>
{fig_full()}
<p class="small">The curve is odd in both coordinates, so the four quadrants hold two mirror
copies of one shape. The stops at t = ±2, ±3 are ringed; the origin and its S are the next figure.</p>
</section>

<section class="panel">
<h2>Fig. Q3 · the S, the inflection, the turn</h2>
{fig_zoom()}
<p class="small">At t = 0 the curvature is zero: the origin is an inflection. Near t = ±1 the
x-speed nearly vanishes, so the curve turns back on itself — the small wiggle. The dashed rings
are the points where y = 0, at t = ±√3, which are not rational stops.</p>
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
<p class="small">Both coordinates are integers at every integer t. That is the whole claim of the
page, and it is what makes the stops usable.</p>
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
