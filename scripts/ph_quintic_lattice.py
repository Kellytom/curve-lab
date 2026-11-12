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
points are at integer t, with a period set by k mod 15:

    15 | k      every integer t, scale 5
    3 | k       5ℤ,            scale 5
    5 | k       3ℤ,            scale 15
    otherwise   15ℤ,           scale 15

Every unit piece, reparametrised, is a quintic Bézier with integer controls at
scale 5, and its arc length is rational.  The page links to ph-families.
"""

from __future__ import annotations

from fractions import Fraction as F
from math import comb, lcm
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = "#fbf7ec"
INK, MUTED, GOLD, BLUE, RED = "#2e2413", "#7b6c4e", "#c9a441", "#1f5fa8", "#a23b2a"
RULE = "#d8ccae"

K = 15          # the headline member: every integer t, scale 5
K_SMALL = 3     # the small-controls member: hits at 5ℤ


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
    """Power-basis coefficients -> Bézier control values (exact)."""
    a = list(coeffs) + [F(0)] * (n + 1 - len(coeffs))
    return [sum(F(comb(i, j), comb(n, j)) * a[j] for j in range(i + 1))
            for i in range(n + 1)]


def piece_controls(k, m, axis):
    """Controls of the piece [m, m+1] on x (axis 0) or y (axis 1)."""
    k2 = k * k
    if axis == 0:
        coeffs = [F(0), F(k2 - 1), F(0), F(-2 * k2, 3), F(0), F(k2, 5)]
    else:
        coeffs = [F(0), F(-2 * k), F(0), F(2 * k, 3)]
    return bezier(shift(coeffs, m))


def piece_scale(k, m):
    return lcm(*[v.denominator for v in
                 piece_controls(k, m, 0) + piece_controls(k, m, 1)])


# -- figure -----------------------------------------------------------------

def fig():
    W, H = 940, 500
    left, right = 86, 34
    pw = W - left - right
    xtop, xh = 58, 150
    ytop, yh = 264, 150
    t0, t1 = 0, 3
    xmax = 7600
    ylo, yhi = -30, 190

    def ft(t):
        return left + (t - t0) / (t1 - t0) * pw

    def fvx(v):
        return xtop + (1 - v / xmax) * xh

    def fvy(v):
        return ytop + (1 - (v - ylo) / (yhi - ylo)) * yh

    def path(pts, fn):
        return " ".join(("M" if i == 0 else "L") + f"{ft(t):.1f},{fn(v):.1f}"
                        for i, (t, v) in enumerate(pts))

    xs = [(F(i, 20), curve(K, F(i, 20))[0]) for i in range(61)]
    ys = [(F(i, 20), curve(K, F(i, 20))[1]) for i in range(61)]

    g = [f'<rect x="{left}" y="{xtop}" width="{pw}" height="{xh}" fill="none" stroke="{RULE}"/>',
         f'<rect x="{left}" y="{ytop}" width="{pw}" height="{yh}" fill="none" stroke="{RULE}"/>']
    for t in range(t0, t1 + 1):
        g.append(f'<line x1="{ft(t):.1f}" y1="{xtop}" x2="{ft(t):.1f}" y2="{xtop+xh}" stroke="{RULE}" stroke-width="0.8"/>')
        g.append(f'<line x1="{ft(t):.1f}" y1="{ytop}" x2="{ft(t):.1f}" y2="{ytop+yh}" stroke="{RULE}" stroke-width="0.8"/>')
        g.append(f'<text x="{ft(t):.1f}" y="{ytop+yh+18}" text-anchor="middle" font-size="12" fill="{MUTED}">{t}</text>')
    for v in (0, 2000, 4000, 6000):
        g.append(f'<text x="{left-8}" y="{fvx(v)+4:.1f}" text-anchor="end" font-size="12" fill="{MUTED}">{v:,}</text>')
    for v in (-30, 0, 60, 120, 180):
        g.append(f'<text x="{left-8}" y="{fvy(v)+4:.1f}" text-anchor="end" font-size="12" fill="{MUTED}">{v}</text>')

    pts = []
    for t in range(t0, t1 + 1):
        x, y = curve(K, t)
        last = t == t1
        ax, dx = ("end", -6) if last else ("middle", 0)
        pts.append(f'<circle cx="{ft(t):.1f}" cy="{fvx(x):.1f}" r="5" fill="{PAPER}" stroke="{RED}" stroke-width="2.4"/>')
        pts.append(f'<text x="{ft(t)+dx:.1f}" y="{fvx(x)-10:.1f}" text-anchor="{ax}" font-size="12" fill="{RED}">{x}</text>')
        pts.append(f'<circle cx="{ft(t):.1f}" cy="{fvy(y):.1f}" r="5" fill="{PAPER}" stroke="{RED}" stroke-width="2.4"/>')
        pts.append(f'<text x="{ft(t)+dx:.1f}" y="{fvy(y)-10:.1f}" text-anchor="{ax}" font-size="12" fill="{RED}">{y}</text>')

    return f"""<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="TQ(15): x and y against t, whole at every integer t">
  <rect width="{W}" height="{H}" fill="{PAPER}"/>
  <text x="{left}" y="22" font-size="14" font-weight="600" fill="{INK}">Fig. Q1 · TQ(15): both coordinates are whole at every integer t</text>
  <text x="{left}" y="40" font-size="12" fill="{MUTED}">x = 45t⁵ − 150t³ + 224t · y = 10t³ − 30t · rings: the lattice points, labelled with their value</text>
  {''.join(g)}
  <path d="{path(xs, fvx)}" fill="none" stroke="{INK}" stroke-width="2.2"/>
  <path d="{path(ys, fvy)}" fill="none" stroke="{INK}" stroke-width="2.2"/>
  {''.join(pts)}
  <text x="20" y="{xtop+xh/2:.0f}" font-size="13" fill="{INK}" transform="rotate(-90 20 {xtop+xh/2:.0f})">x, units</text>
  <text x="20" y="{ytop+yh/2:.0f}" font-size="13" fill="{INK}" transform="rotate(-90 20 {ytop+yh/2:.0f})">y, units</text>
  <text x="{left+pw/2:.0f}" y="{H-16}" text-anchor="middle" font-size="13" fill="{INK}">t — the parameter; the grid lines are the integer stops</text>
  <g font-size="12">
    <line x1="{left}" y1="{H-42}" x2="{left+22}" y2="{H-42}" stroke="{INK}" stroke-width="2.2"/><text x="{left+30}" y="{H-38}" fill="{INK}">curve</text>
    <circle cx="{left+110}" cy="{H-42}" r="5" fill="{PAPER}" stroke="{RED}" stroke-width="2.4"/><text x="{left+124}" y="{H-38}" fill="{INK}">lattice point (t integer)</text>
  </g>
</svg>"""


def member_rows():
    rows = []
    for k in (3, 5, 6, 10, 15, 25, 30):
        period = hit_period(k)
        scale = piece_scale(k, 0)
        maxc = max(abs(v) for v in piece_controls(k, 0, 0) + piece_controls(k, 0, 1))
        rows.append((k, period, scale, maxc))
    return rows


def hit_rows(k, n=5):
    rows = []
    for t in range(0, n + 1):
        x, y = curve(k, t)
        rows.append((t, x, y, arc(k, t)))
    return rows


def build():
    rows = "".join(
        f"<tr><td>TQ({k})</td><td>{period}</td><td>{scale}</td><td>{maxc:.0f}</td></tr>"
        for k, period, scale, maxc in member_rows())
    hits = "".join(
        f"<tr><td>{t}</td><td>{x}</td><td>{y}</td><td>{s}</td></tr>"
        for t, x, y, s in hit_rows(K))

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
<p class="lede">TQ(15) is a primitive, polynomial Pythagorean-hodograph quintic with a constant
second hodograph component. Both coordinates are whole numbers at every integer parameter, the
control points are integers on a scale-5 grid, and the length between stops is rational. So the
curve can be cut at its lattice points without losing exactness.</p>

<section class="panel">
<h2>The family</h2>
<p>Write the hodograph as <code>w = k(t²−1) + i</code>. Then
<code>x′ = k²(t²−1)² − 1</code> and <code>y′ = 2k(t²−1)</code>, and the speed is
<code>σ = k²(t²−1)² + 1</code> — a polynomial, so the curve is PH and its length is exact.
The degree is <code>2·2 + 1 = 5</code>. <code>h = 1</code> makes it polynomial;
<code>gcd(u, v) = 1</code> makes it primitive; <code>v</code> constant makes it
Tschirnhausen type — the degree-3 member of exactly this family is the Tschirnhausen cubic.</p>
<p>Because <code>v</code> is constant, <code>y′</code> is quadratic and <code>y</code> is a cubic —
the lowest degree a quintic allows. Only <code>x</code> carries the fifth-degree work.</p>
</section>

<section class="panel">
<h2>Where it hits whole numbers</h2>
<p>The ÷5 in <code>x</code> comes from integrating <code>t⁴</code>; the ÷3 in <code>y</code> comes
from integrating <code>t²</code>. Whichever divides <code>k</code> disappears, and the hit period
follows. The scale never exceeds 15, so there is no ceiling on <code>k</code> — only the control
numbers grow, like <code>k²</code>.</p>
<table>
<tr><th>member</th><th>lattice hits at</th><th>control scale</th><th>largest control</th></tr>
{rows}
</table>
<p class="small">TQ(25) is a downgrade: 25 ≡ 10 (mod 15), so it hits only every third t and needs
scale 15. TQ(15) hits every integer t at scale 5.</p>
</section>

<section class="panel">
<h2>Fig. Q1 · TQ(15), coordinate by coordinate</h2>
{fig()}
<p class="small">The rings are the lattice points. At t = 1 the curve is at (119, −20); at t = 2,
(688, 20); at t = 3, (7557, 180). The parameter is not a length — the curve grows like
<code>t⁵</code>, so the stops are far apart in space even though they are adjacent in t.</p>
</section>

<section class="panel">
<h2>The stops, exactly</h2>
<table>
<tr><th>t</th><th>x</th><th>y</th><th>arc length s(t)</th></tr>
{hits}
</table>
<p class="small">s(t) = 45t⁵ − 150t³ + 226t. Every value in the table is an integer, and so is
every length — no square roots anywhere.</p>
</section>

<section class="panel">
<h2>Cutting at a stop</h2>
<p>Take the piece <code>t ∈ [0, 1]</code>. Reparametrised to <code>u ∈ [0, 1]</code> it is a
quintic Bézier with integer controls at scale 5:</p>
<p class="small">x: (0, 224, 448, 597, 596, 595) · y: (0, −30, −60, −85, −100, −100)</p>
<p>The same holds for every unit piece <code>t ∈ [m, m+1]</code>: shifting <code>t = u + m</code>
keeps integer coefficients, so the controls stay integers at scale 5, and the piece is still PH.
Cut at t = 1, 2, 3 … and each piece has an exact endpoint and an exact length. That is the
difference from the Tschirnhausen cubic: there, exact lattice nodes meant irrational chord sides;
here the cut points and the lengths are both exact.</p>
</section>

<section class="panel">
<h2>Why not the midpoint chain</h2>
<p>The triangle chain still produces whole-number steps on any PH curve, but a quintic's speed is
quartic, so the chain's grid grows like the fourth power of the step denominator. On TQ(3) over
<code>t ∈ [0, 5]</code> with twelve steps the chain needs a grid of 442,368 and still misses the
endpoint by 31 units in x; the cubic's 256 and 1/64 were a degree-3 accident. For a quintic, cut
at the exact stops instead.</p>
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
