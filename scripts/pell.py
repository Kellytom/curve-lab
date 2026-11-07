"""Pell's equation and the √2 convergents, on the integer lattice.

    .venv/bin/python scripts/pell.py
    open workbench/pell.html

The curve x² − 2y² = 1 is the hyperbola whose integer points are Pell's
equation. One integer point is enough: the doubling law

    (x, y) -> (x² + 2y², 2xy)

stays on the curve because (x²+2y²)² − 2(2xy)² = (x²−2y²)² = 1, and the
addition law

    (x₁,y₁)·(x₂,y₂) = (x₁x₂ + 2y₁y₂, x₁y₂ + x₂y₁)

does too — it is multiplication of units in Z[√2]. Starting at (3,2), that is
3/2 → 17/12 → 577/408 by doubling, and 3/2 · 17/12 = 99/70 by addition.
Both sequences converge to √2 like 1/(2√2 y²).

This is the same algebra as the Pythagorean-triple doubling: there the unit
group is the Gaussian integers; here it is Z[√2].
"""

from __future__ import annotations

import math
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = "#fbf7ec"
INK, MUTED, GOLD, BLUE, RED = "#2e2413", "#7b6c4e", "#c9a441", "#1f5fa8", "#a23b2a"
RULE = "#d8ccae"


# -- exact algebra ----------------------------------------------------------

def multiply(p, q, d=2):
    """The addition law: multiplication of (x + y√d) units."""
    x1, y1 = p
    x2, y2 = q
    return (x1 * x2 + d * y1 * y2, x1 * y2 + x2 * y1)


def double(p, d=2):
    return multiply(p, p, d)


# the first integer point above the unit for each d
STARTS = {2: (3, 2), 3: (2, 1), 5: (9, 4), 6: (5, 2)}


def chain(start=(3, 2), n=5, law=double, d=2):
    out = [start]
    for _ in range(n):
        out.append(law(out[-1], d))
    return out


ADD_CHAIN = [multiply((3, 2), (3, 2))]
for _ in range(4):
    ADD_CHAIN.append(multiply(ADD_CHAIN[-1], (3, 2)))


# -- drawing ----------------------------------------------------------------

class Frame:
    def __init__(self, w, h, x0, x1, y0, y1):
        pad = 34
        self.w, self.h = w, h
        self.s = min((w - 2 * pad) / (x1 - x0), (h - 2 * pad) / (y1 - y0))
        self.ox = (w - (x1 - x0) * self.s) / 2 - x0 * self.s
        self.oy = (h - (y1 - y0) * self.s) / 2 + y1 * self.s

    def __call__(self, p):
        # +y up in the model; flipped here on the way to screen coordinates
        return (self.ox + p[0] * self.s, self.oy - p[1] * self.s)


def path(pts, f):
    return " ".join(("M" if i == 0 else "L") + f"{x:.1f},{y:.1f}"
                    for i, (x, y) in enumerate(f(p) for p in pts))


def fig_r1():
    f = Frame(980, 560, -20, 20, -14, 14)
    curve = []
    for i in range(721):
        t = -2.9 + 5.8 * i / 720
        curve.append((math.cosh(t), math.sinh(t)))
    branch = [(x, y) for x, y in curve]
    mirror = [(-x, y) for x, y in curve]

    pts = [(3, 2), (17, 12)]
    dots = []
    for x, y in pts:
        for sx in (1, -1):
            for sy in (1, -1):
                X, Y = f((sx * x, sy * y))
                dots.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="5" fill="{RED}"/>')
                dots.append(f'<text x="{X + 7:.1f}" y="{Y - 7:.1f}" '
                            f'font-family="ui-monospace,Menlo,monospace" font-size="12" '
                            f'fill="{INK}">({sx * x},{sy * y})</text>')
    gp = f((1, 0))
    dots.append(f'<circle cx="{gp[0]:.1f}" cy="{gp[1]:.1f}" r="4" fill="{GOLD}"/>')
    dots.append(f'<text x="{gp[0] + 8:.1f}" y="{gp[1] + 4:.1f}" '
                f'font-family="ui-monospace,Menlo,monospace" font-size="12" '
                f'fill="{MUTED}">(1,0) · the unit</text>')

    # the asymptote y = x/√2: the line the convergents approach
    asym = [(-20, -20 / math.sqrt(2)), (20, 20 / math.sqrt(2))]
    grid = []
    for k in range(-18, 19, 2):
        a, b = f((k, -14)), f((k, 14))
        grid.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
                    f'y2="{b[1]:.1f}" stroke="{RULE}" stroke-width="0.6"/>')
    for k in range(-12, 13, 2):
        a, b = f((-20, k)), f((20, k))
        grid.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
                    f'y2="{b[1]:.1f}" stroke="{RULE}" stroke-width="0.6"/>')

    return f"""<svg viewBox="0 0 980 560" width="100%" role="img" aria-label="Pell hyperbola and its integer points">
  <rect width="980" height="560" fill="{PAPER}"/>
  {''.join(grid)}
  <line x1="{f(asym[0])[0]:.1f}" y1="{f(asym[0])[1]:.1f}" x2="{f(asym[1])[0]:.1f}" y2="{f(asym[1])[1]:.1f}" stroke="{BLUE}" stroke-width="1.2" stroke-dasharray="7 5"/>
  <path d="{path(branch, f)}" fill="none" stroke="{INK}" stroke-width="2.2"/>
  <path d="{path(mirror, f)}" fill="none" stroke="{INK}" stroke-width="2.2"/>
  {''.join(dots)}
  <text x="16" y="26" font-family="Georgia,serif" font-size="13" fill="{INK}">Fig. R1 · x² − 2y² = 1 · integer points on the lattice · +y up, flipped to screen</text>
  <text x="16" y="46" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="{MUTED}">dashed: y = x/√2, the asymptote the convergents approach · x →, y ↑</text>
  <g font-family="Georgia,serif" font-size="15">
    <line x1="16" y1="524" x2="52" y2="524" stroke="{INK}" stroke-width="3"/><text x="60" y="529" fill="{INK}">hyperbola</text>
    <circle cx="176" cy="524" r="5" fill="{RED}"/><text x="190" y="529" fill="{INK}">integer point (x² − 2y² = 1)</text>
    <line x1="470" y1="524" x2="506" y2="524" stroke="{BLUE}" stroke-width="2" stroke-dasharray="7 5"/><text x="514" y="529" fill="{INK}">y = x/√2</text>
  </g>
</svg>"""


def fig_r2():
    series = [Fraction(x, y) for x, y in chain((3, 2), 5, double)]
    xs = [math.log10(r.denominator) for r in series]
    ys = [math.log10(1.0 / (r.denominator ** 2 * (float(r) + math.sqrt(2))))
          for r in series]
    law = [math.log10(1 / (2 * math.sqrt(2) * r.denominator ** 2)) for r in series]

    x0, x1 = min(xs) - 0.3, max(xs) + 0.3
    y0, y1 = min(ys + law) - 0.3, max(ys + law) + 0.3
    w, h, pad = 880, 420, 70
    f = Frame(w, h, x0, x1, y0, y1)

    pts = [f((x, y)) for x, y in zip(xs, ys)]
    d = " ".join(("M" if i == 0 else "L") + f"{x:.1f},{y:.1f}"
                 for i, (x, y) in enumerate(pts))
    lp = [f((x, y)) for x, y in zip(xs, law)]
    ld = " ".join(("M" if i == 0 else "L") + f"{x:.1f},{y:.1f}"
                  for i, (x, y) in enumerate(lp))
    marks = []
    for (x, y), r in zip(pts, series):
        marks.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{PAPER}" '
                     f'stroke="{RED}" stroke-width="2"/>')
        marks.append(f'<text x="{x:.1f}" y="{y + 22:.1f}" text-anchor="middle" '
                     f'font-family="ui-monospace,Menlo,monospace" font-size="12" '
                     f'fill="{INK}">{r.numerator}/{r.denominator}</text>')
    return f"""<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="convergent error on a log-log grid">
  <rect width="{w}" height="{h}" fill="{PAPER}"/>
  <line x1="{pad}" y1="{h - pad}" x2="{w - pad}" y2="{h - pad}" stroke="{INK}" stroke-width="1.2"/>
  <line x1="{pad}" y1="{pad}" x2="{pad}" y2="{h - pad}" stroke="{INK}" stroke-width="1.2"/>
  <path d="{ld}" fill="none" stroke="{GOLD}" stroke-width="2" stroke-dasharray="7 5"/>
  <path d="{d}" fill="none" stroke="{RED}" stroke-width="2"/>
  {''.join(marks)}
  <text x="{pad}" y="34" font-family="Georgia,serif" font-size="13" fill="{INK}">Fig. R2 · the error is 1/(2√2·y²): points and the law, log–log</text>
  <text x="{pad}" y="54" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="{MUTED}">each decade in y buys two decades of accuracy — the dashed reference has slope −2</text>
  <text x="{w / 2:.0f}" y="{h - 20}" text-anchor="middle" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="{MUTED}">log10(y) — the denominator</text>
  <text x="18" y="{h / 2:.0f}" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="{MUTED}" transform="rotate(-90 18 {h / 2:.0f})">log10|x/y − √2|</text>
  <g font-family="Georgia,serif" font-size="15">
    <circle cx="300" cy="{h - 12}" r="5" fill="{PAPER}" stroke="{RED}" stroke-width="2"/><text x="314" y="{h - 7}" fill="{INK}">measured points</text>
    <line x1="470" y1="{h - 12}" x2="506" y2="{h - 12}" stroke="{GOLD}" stroke-width="2" stroke-dasharray="7 5"/><text x="514" y="{h - 7}" fill="{INK}">1/(2√2 y²)</text>
  </g>
</svg>"""


def build():
    rows = []
    for name, pts in (("doubling (3,2)", chain((3, 2), 4, double)),
                      ("adding (3,2)", [(3, 2)] + ADD_CHAIN[:4])):
        for x, y in pts:
            frac = Fraction(x, y)
            rows.append(
                f"<tr><td>{name}</td><td>({x}, {y})</td><td>{x * x - 2 * y * y}</td>"
                f"<td>{float(frac):.9f}</td>"
                f"<td>{1.0 / (y * y * (float(frac) + math.sqrt(2))):.3e}</td></tr>")

    d_rows = "".join(
        f"<tr><td>{d}</td><td>({STARTS[d][0]}, {STARTS[d][1]})</td>"
        f"<td>({chain(STARTS[d], 1, d=d)[1][0]}, {chain(STARTS[d], 1, d=d)[1][1]})</td>"
        f"<td>{chain(STARTS[d], 1, d=d)[1][0] ** 2 - d * chain(STARTS[d], 1, d=d)[1][1] ** 2}</td></tr>"
        for d in (2, 3, 5, 6))

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pell, √2, and the integer hyperbola</title>
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
<p class="eyebrow">curve-lab · Pell and the integer hyperbola</p>
<h1>x² − 2y² = 1: the lattice points that approximate √2</h1>
<p class="lede">One integer point on this hyperbola is enough to generate every other. The doubling
law is the same algebra as the Pythagorean triple doubling, with the Gaussian integers replaced by
Z[√2]; the ratios are the convergents of √2, and the error is exactly 1/(2√2 y²).</p>

<section class="panel">
<h2>Fig. R1 · the hyperbola, its lattice points, and the asymptote</h2>
{fig_r1()}
<p class="small">(3,2) and (17,12) are the first two points after the unit (1,0); every one of them satisfies
x² − 2y² = 1 exactly, so x/y is a rational approximation to √2. The dashed line is y = x/√2 — irrational,
so the integer points approach it but never touch it.</p>
</section>

<section class="panel">
<h2>Fig. R2 · the error law, measured</h2>
{fig_r2()}
<p class="small">For any point, (x/y)² − 2 = 1/y², so |x/y − √2| = 1/(y²(x/y + √2)). The product
error × y² therefore tends to 1/(2√2) = {1 / (2 * math.sqrt(2)):.6f}. The plot is that product, and
it is already at the limit by the fourth point.</p>
</section>

<section class="panel">
<h2>The two laws</h2>
<p>Both are one line of integer arithmetic. <strong>Doubling</strong>: (x,y) → (x² + 2y², 2xy).
<strong>Adding</strong>: (x₁,y₁)·(x₂,y₂) = (x₁x₂ + 2y₁y₂, x₁y₂ + x₂y₁). The second is multiplication
of x + y√2, so the norm x² − 2y² multiplies: (x²−2y²)(u²−2v²) = (xu+2yv)² − 2(xv+yu)². Start at
norm 1 and every product has norm 1.</p>
<table>
<tr><th>law</th><th>point</th><th>x² − 2y²</th><th>x/y</th><th>|x/y − √2|</th></tr>
{''.join(rows)}
</table>
<p class="small">Doubling gives 3/2 → 17/12 → 577/408; adding (3,2) gives 3/2 → 17/12 → 99/70. Both are
Pell sequences; the addition law and the doubling law agree because 17/12 is already (3,2)².</p>
</section>

<section class="panel">
<h2>Other d: the same two laws</h2>
<p>Nothing in the doubling law is special to 2. For a square-free <code>d</code>, the units of
Z[√d] have norm <code>x² − d y²</code>, and the same multiplication keeps the norm at 1. The first
point above the unit differs with d; after that the chain is mechanical.</p>
<table>
<tr><th>d</th><th>first point</th><th>doubled</th><th>x² − d y²</th></tr>
{d_rows}
</table>
<p class="small">Squares are excluded: for <code>d = k²</code> the equation factors as
(x−ky)(x+ky)=1, so its only integer points are the trivial ones. The non-square d are the interesting
ones — and the larger d, the faster the convergents improve, because the error is 1/(2√d·y²).</p>
</section>

<section class="panel">
<h2>Why it belongs beside the p-triple plane</h2>
<p>The Pythagorean triples come from units in the Gaussian integers: (u+iv)² doubles an angle and
produces the next triple. Pell comes from units in Z[√2]: (x+y√2)² doubles the “hyperbolic angle”
and produces the next point. The integer cubic family uses the first; this page is the second, on
the same lattice, with the same exactness rule — integers and Fractions, never a floating point
claim. The difference is the conic: a circle has finite order, the hyperbola has infinite order,
which is why Pell has infinitely many integer points and the circle only finitely many.</p>
<p class="small">Re-derive: <code>python scripts/pell.py</code> · test: <code>python -m unittest tests.test_pell</code></p>
</section>
</main></body></html>
"""
    out = ROOT / "workbench" / "pell.html"
    out.write_text(html, encoding="utf-8")
    print(out)
    return out


if __name__ == "__main__":
    build()
