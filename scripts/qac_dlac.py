"""Quasi-aesthetic curves and discrete log-aesthetic curves.

    .venv/bin/python scripts/qac_dlac.py
    open workbench/qac-dlac.html

The LAC family is defined by q^α = c0 s + c1 in arc length. Its two extensions
worth having:

- **qAC**: the similarity curvature obeys a Riccati equation, u' = (α−1)u² + c,
  so c = 0 recovers the LAC and c ≠ 0 is a wider fair family;
- **dLAC**: a discrete curve of constant turning whose segment ratios satisfy
  (uₙ₊₁)^a + 1/(uₙ)^a = C, with a = α−1. It is a curve in its own right, not a
  sampled approximation.

Both are numerical here; neither claims lattice exactness.
"""

from __future__ import annotations

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAPER, INK, MUTED, RULE = "#fbf7ec", "#2e2413", "#7b6c4e", "#d8ccae"
RED, BLUE, GOLD = "#a23b2a", "#1f5fa8", "#c9a441"


def qac(alpha, c, u0=None, th0=0.2, th1=1.5, n=1200):
    """Integrate u' = (α−1)u² + c, then q = exp(−∫u) and the curve."""
    if u0 is None:
        u0 = 1.0 / ((alpha - 1) * th0 + 1.0)
    pts = [(0.0, 0.0)]
    q = 1.0
    x = y = 0.0
    u = u0
    dth = (th1 - th0) / n
    for i in range(n):
        th = th0 + i * dth
        # RK4 on u
        def f(uu):
            return (alpha - 1) * uu * uu + c
        k1 = f(u)
        k2 = f(u + 0.5 * dth * k1)
        k3 = f(u + 0.5 * dth * k2)
        k4 = f(u + dth * k3)
        u_mid = u + dth * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        # q grows as exp(−∫u dθ); position integrates q(cos θ, sin θ)
        q *= math.exp(-0.5 * (u + u_mid) * dth)
        x += q * math.cos(th) * dth
        y += q * math.sin(th) * dth
        pts.append((x, y))
        u = u_mid
    return pts


def dlac(alpha, C, u0=1.6, n=70, turn_deg=9.0):
    """Constant turning; ratios from (uₙ₊₁)^a + 1/(uₙ)^a = C."""
    a = alpha - 1.0
    us = [u0]
    for _ in range(n):
        nxt = (C - 1.0 / (us[-1] ** a)) ** (1.0 / a)
        us.append(nxt)
    seg = 1.0
    heading = 0.0
    x = y = 0.0
    pts = [(0.0, 0.0)]
    for u in us:
        heading += math.radians(turn_deg)
        seg *= u
        x += seg * math.cos(heading)
        y += seg * math.sin(heading)
        pts.append((x, y))
    # the lengths grow geometrically; normalise the shape, not the law
    span = max(max(abs(a) for a, _ in pts), max(abs(b) for _, b in pts)) or 1.0
    return [(a / span, b / span) for a, b in pts]


def lac_check(alpha, th0=0.2, th1=1.5, n=2000):
    """For c = 0, q^α should be linear in arc length s."""
    lam = 1.0 / ((alpha - 1) * th0 + 1.0)
    s = 0.0
    rows = []
    for i in range(n):
        th = th0 + (th1 - th0) * i / n
        q = ((alpha - 1) * lam * th + 1.0) ** (1.0 / (alpha - 1))
        s += q * (th1 - th0) / n
        rows.append((s, q ** alpha))
    # the slope between the ends, and the worst deviation from that line
    s0, v0 = rows[0]
    s1, v1 = rows[-1]
    slope = (v1 - v0) / (s1 - s0)
    dev = max(abs(v - (v0 + slope * (s - s0))) for s, v in rows)
    return slope, dev


CASES = [
    ("qAC · α = 2, c = +1", 2.0, 1.0),
    ("qAC · α = 2, c = −1", 2.0, -1.0),
    ("qAC · α = 3, c = 0.5", 3.0, 0.5),
]
D_CASES = [
    ("dLAC · α = 2, C = 2.1", 2.0, 2.1),
    ("dLAC · α = 3, C = 2.4", 3.0, 2.4),
]


# -- drawing ----------------------------------------------------------------

def _svg(series, title, note, w=900, h=430):
    pad = 46
    allpts = [p for _, pts, _ in series for p in pts]
    x0, x1 = min(p[0] for p in allpts), max(p[0] for p in allpts)
    y0, y1 = min(p[1] for p in allpts), max(p[1] for p in allpts)
    s = min((w - 2 * pad) / max(1e-9, x1 - x0),
            (h - 2 * pad) / max(1e-9, y1 - y0))
    ox = (w - (x1 - x0) * s) / 2 - x0 * s
    oy = (h - (y1 - y0) * s) / 2 + y1 * s

    def f(p):
        return (ox + p[0] * s, oy - p[1] * s)

    paths = []
    for colour, pts, label in series:
        d = " ".join(("M" if i == 0 else "L") + f"{x:.1f},{y:.1f}"
                     for i, (x, y) in enumerate(f(p) for p in pts))
        paths.append(f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="2"/>')
    legend = "".join(
        f'<line x1="{20 + i * 230}" y1="{h - 14}" x2="{56 + i * 230}" y2="{h - 14}" '
        f'stroke="{c}" stroke-width="3"/><text x="{64 + i * 230}" y="{h - 9}" '
        f'font-family="Georgia,serif" font-size="15" fill="{INK}">{lab}</text>'
        for i, (c, _pts, lab) in enumerate(series))
    return f"""<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="{title}">
  <rect width="{w}" height="{h}" fill="{PAPER}"/>
  {''.join(paths)}
  <text x="{pad}" y="34" font-family="Georgia,serif" font-size="13" fill="{INK}">{title}</text>
  <text x="{pad}" y="54" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="{MUTED}">{note}</text>
  {legend}
</svg>"""


def build():
    q_series = [(c, qac(a, cc), title.split(" · ")[1])
                for title, a, cc in CASES for c in (RED,)]
    # give each curve its own colour
    palette = [RED, BLUE, GOLD]
    q_series = [(palette[i], qac(a, cc), f"α={a:g}, c={cc:g}")
                for i, (_t, a, cc) in enumerate(CASES)]
    d_series = [(palette[i], dlac(a, C), f"α={a:g}, C={C:g}")
                for i, (_t, a, C) in enumerate(D_CASES)]

    devs = {a: lac_check(a) for a in (1.5, 2.0, 3.0)}
    worst = max(d for _s, d in devs.values())

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>qAC and discrete LAC</title>
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
<p class="eyebrow">curve-lab · the aesthetic family</p>
<h1>qAC: one constant past the LAC — and its discrete analogue</h1>
<p class="lede">The log-aesthetic curve is defined by q<sup>α</sup> = c₀s + c₁ in arc length. Its
similarity curvature u satisfies u′ = (α−1)u²; adding a constant gives the <b>quasi-aesthetic curve</b>,
u′ = (α−1)u² + c, and c = 0 is exactly the LAC. The <b>discrete LAC</b> is the same idea on equal
turns: constant turning angle, segment ratios from (uₙ₊₁)<sup>a</sup> + 1/(uₙ)<sup>a</sup> = C, with
a = α−1. It is a curve in its own right, not a sampled approximation.</p>

<section class="panel">
<h2>Fig. Q1 · three qAC curves</h2>
{_svg(q_series, "qAC · u′ = (α−1)u² + c", "the parameter is the LCH slope α; c is the departure from the LAC")}
<p class="small">c = 0 recovers the LAC. The check on this page integrates the LAC form and measures
q<sup>α</sup> against arc length: it is linear to <b>{worst:.1e}</b> over α = 1.5, 2, 3, which is the
definition holding numerically.</p>
</section>

<section class="panel">
<h2>Fig. Q2 · two discrete LACs</h2>
{_svg(d_series, "dLAC · constant turn, ratios from the recurrence", "uₙ₊₁ from (uₙ₊₁)^a + 1/(uₙ)^a = C; drawn normalised")}
<p class="small">The discrete curve is the paper's recurrence: the turning is constant, the
segment lengths are the ratios, and the shape is generated without integrating anything. This is the
form that belongs on a lattice, because every step is a turn and a length, not a Fresnel integral.</p>
</section>

<section class="panel">
<h2>Where it sits</h2>
<p>These are the paper's two extensions (arXiv 1808.03104). The repo's own LAC dial is the curvature
exponent <b>p</b>, with κ ∝ s<sup>p</sup>; the paper's slope is <b>α</b>, with q<sup>α</sup> = c₀s + c₁,
so <b>p = −1/α</b>. The Gen-Arch page uses the same mapping for its radial: c = α − 1.</p>
<p>Neither family is exact on the lattice: both are integrated or iterated numerically, so they are
declared, not named. The discrete one is the promising road — a constant-turn, ratio-driven curve can
be built with rational lengths and Pythagorean turns, which is exactly what the stem cuts already do.</p>
<p class="small">Re-derive: <code>python scripts/qac_dlac.py</code> ·
test: <code>python -m unittest tests.test_qac_dlac</code></p>
</section>
</main></body></html>
"""
    out = ROOT / "workbench" / "qac-dlac.html"
    out.write_text(html, encoding="utf-8")
    print(out)
    return out


if __name__ == "__main__":
    build()
