"""Biarcs: two circular arcs that meet G1, from two points and two tangents.

    .venv/bin/python scripts/biarcs.py
    open workbench/biarcs.html

The construction here is the equal-radius biarc: both arcs get the same radius
R, so their centres are P0 + R·n0 and P1 + R·n1 and the arcs touch when
|C0 − C1| = 2R. That is one quadratic in R; its positive root gives the pair.
The joint is the midpoint of the centres, and the join is G1 by construction.
R is generally irrational, so the biarc is *computed*, not declared exact.
"""

from __future__ import annotations

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INK, MUTED, RULE, PAPER = "#2e2413", "#7b6c4e", "#d8ccae", "#fbf7ec"
BLUE, GOLD, RED = "#1f5fa8", "#c9a441", "#a23b2a"


def left(t):
    return (-t[1], t[0])


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def scale(a, s):
    return (a[0] * s, a[1] * s)


def unit(a):
    L = math.hypot(*a)
    return (a[0] / L, a[1] / L)


def arc(centre, r, a0, a1, n=120):
    return [(centre[0] + r * math.cos(a0 + (a1 - a0) * i / n),
             centre[1] + r * math.sin(a0 + (a1 - a0) * i / n))
            for i in range(n + 1)]


def biarc(p0, t0, p1, t1):
    """Equal-radius biarc; returns centres, R, joint and the sampled arcs."""
    n0, n1 = left(unit(t0)), left(unit(t1))
    D = sub(p1, p0)
    A = dot(sub(n0, n1), sub(n0, n1)) - 4.0
    B = 2.0 * dot(D, sub(n1, n0))
    C = dot(D, D)
    roots = []
    if abs(A) < 1e-12:
        if abs(B) > 1e-12:
            roots = [-C / B]
    else:
        disc = B * B - 4 * A * C
        if disc >= 0:
            s = math.sqrt(disc)
            roots = [(-B + s) / (2 * A), (-B - s) / (2 * A)]
    pos = [r for r in roots if r > 1e-12]
    if not pos:
        raise ValueError("no positive equal-radius biarc for this data")
    R = max(pos)

    c0 = add(p0, scale(n0, R))
    c1 = add(p1, scale(n1, R))
    joint = scale(add(c0, c1), 0.5)

    a0 = math.atan2(p0[1] - c0[1], p0[0] - c0[0])
    a1 = math.atan2(joint[1] - c0[1], joint[0] - c0[0])
    b0 = math.atan2(joint[1] - c1[1], joint[0] - c1[0])
    b1 = math.atan2(p1[1] - c1[1], p1[0] - c1[0])

    def sweep(start, end):
        d = (end - start + math.pi) % (2 * math.pi) - math.pi
        return start, start + d

    s0, e0 = sweep(a0, a1)
    s1, e1 = sweep(b0, b1)
    return {"R": R, "c0": c0, "c1": c1, "joint": joint,
            "first": arc(c0, R, s0, e0), "second": arc(c1, R, s1, e1)}


CASES = [
    ("east to north", (0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)),
    ("east to south-east", (0.0, 0.0), (1.0, 0.0), (2.5, 1.0), (1.0, -0.3)),
    ("a shallow S", (0.0, 0.0), (1.0, 0.0), (3.0, 1.0), (-0.2, 1.0)),
]


def measure(case):
    title, p0, t0, p1, t1 = case
    b = biarc(p0, t0, p1, t1)
    j = b["joint"]
    tan0 = left(unit(sub(j, b["c0"])))
    tan1 = left(unit(sub(j, b["c1"])))
    cross = tan0[0] * tan1[1] - tan0[1] * tan1[0]
    ang = math.degrees(math.atan2(abs(cross), abs(dot(tan0, tan1))))
    return b, min(ang, 180.0 - ang)


def build():
    blocks = []
    for case in CASES:
        b, ang = measure(case)
        blocks.append((case, b, ang))

    cards = []
    for case, b, ang in blocks:
        title, p0, t0, p1, t1 = case
        pts = b["first"] + b["second"]
        w, h, pad = 420, 340, 44
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        s = min((w - 2 * pad) / max(1e-9, x1 - x0),
                (h - 2 * pad) / max(1e-9, y1 - y0))
        ox = (w - (x1 - x0) * s) / 2 - x0 * s
        oy = (h - (y1 - y0) * s) / 2 + y1 * s

        def f(p):
            return (ox + p[0] * s, oy - p[1] * s)

        d1 = " ".join(("M" if i == 0 else "L") + f"{x:.1f},{y:.1f}"
                      for i, (x, y) in enumerate(f(p) for p in b["first"]))
        d2 = " ".join(("M" if i == 0 else "L") + f"{x:.1f},{y:.1f}"
                      for i, (x, y) in enumerate(f(p) for p in b["second"]))
        j = f(b["joint"])
        cards.append(f"""<div><svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="biarc {title}">
  <rect width="{w}" height="{h}" fill="{PAPER}"/>
  <path d="{d1}" fill="none" stroke="{INK}" stroke-width="2.2"/>
  <path d="{d2}" fill="none" stroke="{INK}" stroke-width="2.2"/>
  <circle cx="{j[0]:.1f}" cy="{j[1]:.1f}" r="4" fill="{RED}"/>
  <circle cx="{f(b['c0'])[0]:.1f}" cy="{f(b['c0'])[1]:.1f}" r="2.5" fill="{BLUE}"/>
  <circle cx="{f(b['c1'])[0]:.1f}" cy="{f(b['c1'])[1]:.1f}" r="2.5" fill="{BLUE}"/>
  <text x="10" y="20" font-family="Georgia,serif" font-size="12" fill="{INK}">{title}</text>
  <text x="10" y="{h - 10}" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="{MUTED}">R = {b['R']:.4f} · join {ang:.1e}° · x →, y ↑</text>
</svg></div>""")

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Biarcs · two arcs, one G1 join</title>
<style>
:root{{--paper:{PAPER};--ink:{INK};--muted:{MUTED};--rule:{RULE}}}
*{{box-sizing:border-box}} body{{margin:0;background:#f3eddf;color:var(--ink);font:16px/1.55 Georgia,serif}}
main{{max-width:1120px;margin:0 auto;padding:34px 22px 70px}}
.eyebrow{{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}}
h1{{font-size:31px;line-height:1.12;margin:0 0 8px}} h2{{font-size:20px;margin:0 0 8px}}
.lede{{max-width:920px;color:var(--muted)}}
.panel{{background:var(--paper);border:1px solid var(--rule);padding:16px 18px;margin:0 0 18px}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}}
@media(max-width:900px){{.grid{{grid-template-columns:1fr}}}}
.small{{font:12px/1.6 ui-monospace,Menlo,monospace;color:var(--muted)}}
code{{font:12px ui-monospace,Menlo,monospace;background:#f4ecd7;padding:1px 4px}}
</style></head><body><main>
<p class="eyebrow">curve-lab · biarcs</p>
<h1>Two arcs, one G1 join</h1>
<p class="lede">A biarc is the simplest curve that matches two points and two tangents: two circular
arcs that meet with a common tangent. This page builds the <b>equal-radius</b> member — both arcs get
the same R, so the centres are <code>P ± R·n</code> and the arcs touch when <code>|C₀C₁| = 2R</code>.
That is one quadratic in R. The joint is the midpoint of the centres; the join is G1 by construction,
not by fitting.</p>

<section class="panel">
<h2>Fig. B1 · three biarcs</h2>
<div class="grid">{''.join(cards)}</div>
<p class="small">Red: the joint. Blue: the two centres. The measured join is the angle between the
directed tangents there, and it is zero to rounding: {', '.join(f"{c[0][0]} {b['R']:.3f} R / {a:.1e}°" for c, b, a in blocks)}.</p>
</section>

<section class="panel">
<h2>What it is and is not</h2>
<p><b>Is:</b> exact endpoints, exact end tangents, G1 at the joint, and arcs — so the offset of each
piece is another arc, exactly. That is why biarcs matter for a width: an arc spline can carry a
constant band with no fitting error.</p>
<p><b>Is not:</b> exact in R. The equal-radius root is generally irrational (the first case is
√2 − 1), so the centres are computed numbers. A biarc is an <em>arc</em>-exact curve, not a rational
one, and it does not claim to be a NAMED curve.</p>
<p>For the lattice the useful version is different: choose rational centres and radii on the grid,
which constrains the endpoint data. The arches page does the mirroring; this page does the join.</p>
<p class="small">Re-derive: <code>python scripts/biarcs.py</code> ·
test: <code>python -m unittest tests.test_biarcs</code></p>
</section>
</main></body></html>
"""
    out = ROOT / "workbench" / "biarcs.html"
    out.write_text(html, encoding="utf-8")
    print(out)
    return out


if __name__ == "__main__":
    for case in CASES:
        b, ang = measure(case)
        print(f"{case[0]:22s} R {b['R']:.6f} · join {ang:.1e}° · joint {b['joint']}")
    build()
