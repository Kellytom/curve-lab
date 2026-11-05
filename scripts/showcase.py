"""The showcase: every family of ray and curve this project has, on one page.

    .venv/bin/python scripts/showcase.py
    open workbench/showcase.html

Figures are numbered by family and lettered by panel (Fig. 1a, 1b, 1c). Three
panels across, a rule between families, and the rays last so the page can be
read as a monstrance.
"""

from __future__ import annotations

import math
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab import pyth_chain as pc  # noqa: E402
from curve_lab.taper import LogSpiral, width_ratio  # noqa: E402

INK, GOLD, BLUE, RED, GREEN = "#2e2413", "#c9a441", "#1f5fa8", "#a23b2a", "#3f7d4e"
MUTED, RULE, PAPER = "#7b6c4e", "#d8ccae", "#fbf7ec"

W, H = 336, 250


def fit(pts, pad=34):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    if x1 - x0 < 1e-9:
        x0, x1 = x0 - 1, x1 + 1
    if y1 - y0 < 1e-9:
        y0, y1 = y0 - 1, y1 + 1
    s = min((W - 2 * pad) / (x1 - x0), (H - 2 * pad) / (y1 - y0))
    ox = (W - (x1 - x0) * s) / 2
    oy = (H - (y1 - y0) * s) / 2
    return lambda p: (ox + (p[0] - x0) * s, H - oy - (p[1] - y0) * s)   # +y up, flipped here


def panel(fig, title, curves, note="", legend=(), dots=()):
    allpts = [p for pts, *_ in curves for p in pts]
    put = fit(allpts)
    out = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="{title}">',
           f'<rect width="{W}" height="{H}" fill="{PAPER}"/>']
    for pts, colour, width, dash in curves:
        d = " ".join(("M" if i == 0 else "L") + f"{put(p)[0]:.1f},{put(p)[1]:.1f}"
                     for i, p in enumerate(pts))
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        out.append(f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{width}"{dash_attr}/>')
    for p, colour in dots:
        q = put(p)
        out.append(f'<circle cx="{q[0]:.1f}" cy="{q[1]:.1f}" r="2.6" fill="{colour}"/>')
    out.append(f'<text x="10" y="18" font-family="Georgia,serif" font-size="12" fill="{INK}">{fig} · {title}</text>')
    out.append(f'<text x="10" y="{H - 8}" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="{MUTED}">{note}</text>')
    out.append(f'<text x="{W - 14}" y="{H - 24}" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="{MUTED}" text-anchor="end">x →</text>')
    out.append(f'<text x="12" y="34" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="{MUTED}">y ↑</text>')
    out.append("</svg>")
    return "".join(out)


# ---- geometry helpers ------------------------------------------------------

def turn_polygon(schedule, a, b, chord=1.0, mirrored=False):
    """Equal chords turned by whole multiples of the (a,b,c) angle."""
    c = math.hypot(a, b)
    cos_t, sin_t = a / c, b / c
    if mirrored:
        sin_t = -sin_t
    px = py = 0.0
    dx, dy = 1.0, 0.0
    pts = [(0.0, 0.0)]
    for k in schedule:
        for _ in range(abs(k)):
            if k > 0:
                dx, dy = cos_t * dx - sin_t * dy, sin_t * dx + cos_t * dy
            else:
                dx, dy = cos_t * dx + sin_t * dy, -sin_t * dx + cos_t * dy
        px += chord * dx
        py += chord * dy
        pts.append((px, py))
    return pts


def miter(pts, d):
    out = []
    for i, p in enumerate(pts):
        a = pts[max(0, i - 1)]
        b = pts[min(len(pts) - 1, i + 1)]
        e0 = (p[0] - a[0], p[1] - a[1])
        e1 = (b[0] - p[0], b[1] - p[1])
        l0 = math.hypot(*e0) or 1
        l1 = math.hypot(*e1) or 1
        e0 = (e0[0] / l0, e0[1] / l0)
        e1 = (e1[0] / l1, e1[1] / l1)
        n0 = (-e0[1], e0[0])
        n1 = (-e1[1], e1[0])
        mx, my = n0[0] + n1[0], n0[1] + n1[1]
        L = math.hypot(mx, my) or 1
        mx, my = mx / L, my / L
        k = d / max(0.25, mx * n0[0] + my * n0[1])
        out.append((p[0] + k * mx, p[1] + k * my))
    return out


def smooth(pts, n=8):
    """Catmull-Rom through the points, for display only."""
    out = []
    for i in range(len(pts) - 1):
        p0 = pts[max(0, i - 1)]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[min(len(pts) - 1, i + 2)]
        for j in range(n):
            t = j / n
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t +
                       (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
                       (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t +
                       (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
                       (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    out.append(pts[-1])
    return out


def chain_spans(m0, m1, n=1):
    pts = [{"a": m * m - n * n, "b": 2 * m * n} for m in range(m0, m1 + 1)]
    T = pc.tangents(pts)
    spans = pc.spans(T)
    poly = [c for sp in spans for c in [pc.bezier(sp, i / 18) for i in range(19)]]
    return spans, poly, pc.nodes(T)


def run() -> None:
    # 1a — the 3-4-5 turn
    a, b = 4.0, 3.0
    tri = [(0, 0), (a, 0), (a, b), (0, 0)]
    arc = [(1.15 * math.cos(t), 1.15 * math.sin(t)) for t in
           [math.atan2(b, a) * i / 24 for i in range(25)]]
    p1a = panel("Fig. 1a", "the 3-4-5 turn", [
        (tri, INK, 1.8, None), (arc, RED, 1.4, None)],
        "cos 4/5 · sin 3/5 · exact fractions", dots=[((a, b), RED)])

    # 1b — Euler polygon with rational rails
    poly = turn_polygon([1, 1, 1, 1, 1, 1, 1, 1], 4, 3, chord=1.0)
    p1b = panel("Fig. 1b", "integer Euler polygon · rational rails", [
        (miter(poly, 0.22), BLUE, 1.3, None),
        (miter(poly, -0.22), BLUE, 1.3, None),
        (poly, INK, 2.0, None)],
        "eight equal chords · turns sum to 8", dots=[(p, GOLD) for p in poly])

    # 1c — closure: a balanced turn schedule
    sched = [1, 2, 3, 2, 1, -1, -2, -3, -2, -1]
    poly2 = turn_polygon(sched, 4, 3, chord=1.0)
    p1c = panel("Fig. 1c", "closure: turns sum to zero", [
        (smooth(poly2), INK, 2.0, None), (poly2, MUTED, 0.9, "4 3")],
        "schedule 1,2,3,2,1,−1,−2,−3,−2,−1 · ends east", dots=[(poly2[0], GOLD), (poly2[-1], RED)])

    # 2a — a recovered-style LAC schedule
    lac = turn_polygon([1, 2, 3, 4, 5, 4, 3, 2, 1], 4, 3, chord=1.0)
    p2a = panel("Fig. 2a", "LAC spine · turn schedule", [
        (lac, INK, 2.0, None)], "the schedule is the curve", dots=[(p, GOLD) for p in lac])

    # 2b — the same with rails
    p2b = panel("Fig. 2b", "LAC spine · miter rails", [
        (miter(lac, 0.2), BLUE, 1.2, None), (miter(lac, -0.2), BLUE, 1.2, None),
        (smooth(lac), INK, 1.8, None)], "rails exact on the polygon, fitted on the cubic")

    # 2c — the cubic fit
    p2c = panel("Fig. 2c", "the drawn cubic, not the polygon", [
        (smooth(lac), RED, 1.6, None), (lac, MUTED, 1.0, "4 3")],
        "the drawn curve is an interpolation · ~1.4% of the law")

    # 3a — Euclid chain n=1
    _, poly_n1, nodes1 = chain_spans(2, 7, 1)
    p3a = panel("Fig. 3a", "Euclid family chain · n=1", [
        (poly_n1, INK, 2.0, None)], "integer control points at scale 1",
        dots=[(p, GOLD) for p in nodes1])

    # 3b — n=2
    _, poly_n2, nodes2 = chain_spans(3, 10, 2)
    p3b = panel("Fig. 3b", "Euclid family chain · n=2", [
        (poly_n2, INK, 2.0, None)], "denser family · same construction",
        dots=[(p, GOLD) for p in nodes2])

    # 3c — the exponent drift
    bands = [(6, -0.835), (12, -1.091), (25, -1.222), (50, -1.278), (100, -1.305), (400, -1.325)]
    drift = [(math.log10(m), p) for m, p in bands]
    line = [(x, -4 / 3) for x in (math.log10(6), math.log10(400))]
    p3c = panel("Fig. 3c", "the exponent drifts to −4/3", [
        (line, RED, 1.2, "5 4"), (drift, BLUE, 1.8, None)],
        "measured p against band width", dots=[(q, BLUE) for q in drift])

    # 4a — the exact taper
    ls = LogSpiral(1.0, 0.5)
    out_ = ls.scaled(1.3)
    inner = [ls.point(3.3 * i / 80) for i in range(81)]
    outer = [out_.point(3.3 * i / 80) for i in range(81)]
    p4a = panel("Fig. 4a", "exact taper · width ∝ r", [
        (inner, BLUE, 1.4, None), (outer, BLUE, 1.4, None)],
        f"width/r = {width_ratio(1.3, 0.5):.4f}, constant")

    # 4b — the offset myth
    off = []
    for i in range(200):
        th = 3.3 * i / 199
        p = ls.point(th)
        n = ls.normal(th)
        off.append((p[0] + 0.18 * n[0], p[1] + 0.18 * n[1]))
    p4b = panel("Fig. 4b", "constant offset is not a spiral", [
        (inner, MUTED, 1.0, None), (off, RED, 1.4, None)],
        "drift grows with d/r — measured, not assumed")

    # 4c — parabola parallel
    par = [(x, x * x / 2) for x in [(-2.6 + 5.2 * i / 120) for i in range(121)]]
    poff = []
    for x, y in par:
        L = math.hypot(1, x)
        poff.append((x + 0.35 * (-x / L), y + 0.35 * (1 / L)))
    p4c = panel("Fig. 4c", "a parabola's parallel is not a parabola", [
        (par, INK, 1.6, None), (poff, RED, 1.4, None)],
        "the best-fit parabola misses by 20.8% of d")

    # 5a — three grids
    g1 = [(0, 0), (0, 1), (1, 1), (1, 2)]
    g2 = [(1.4, 2), (1.6, 2.6), (1.9, 2.9)]
    g3 = [(2.3, 2.6), (2.6, 2.9), (2.9, 2.6)]
    p5a = panel("Fig. 5a", "three grids · lcm 25", [
        (g1, INK, 1.8, None), (g2, BLUE, 1.8, None), (g3, RED, 1.8, None)],
        "1 · 1/5 · 1/25 → composite 1/25")

    # 5b — the composed stem with a step
    _, poly_a, nodes_a = chain_spans(2, 4, 1)
    end = nodes_a[-1]
    p5b = panel("Fig. 5b", "two chains, one 1/5 step", [
        (poly_a, INK, 1.8, None),
        ([end, (end[0] + 2.2, end[1] + 0.4), (end[0] + 2.2, end[1] + 0.6)], GOLD, 1.6, None)],
        "position exact · tangent kink 25.06°")

    # 5c — the cone terminal
    tip = (1.6, 1.2)
    p5c = panel("Fig. 5c", "cone terminal · R = 2 × offset",
                [([(0, 0), tip], INK, 1.6, None),
                 ([(tip[0] - 0.35, tip[1] - 0.2), tip, (tip[0] + 0.1, tip[1] + 0.35)], RED, 1.4, None)],
                "two arcs, one point, no bare tip")

    # 6 — the rays, as a monstrance
    RW, RH = 980, 420
    cx, cy = RW / 2, RH - 40
    rays = []
    for m in range(2, 13):
        ang = math.atan2(2 * m, m * m - 1)          # n = 1 family angle
        L = 250 - 8 * m
        rays.append(((cx, cy), (cx + L * math.cos(ang), cy - L * math.sin(ang))))
        rays.append(((cx, cy), (cx - L * math.cos(ang), cy - L * math.sin(ang))))
    ray_svg = [f'<svg viewBox="0 0 {RW} {RH}" width="100%" role="img" aria-label="rays as a monstrance">',
               f'<rect width="{RW}" height="{RH}" fill="{PAPER}"/>']
    for i, (p0, p1) in enumerate(rays):
        colour = GOLD if i % 2 else INK
        ray_svg.append(f'<line x1="{p0[0]:.1f}" y1="{p0[1]:.1f}" x2="{p1[0]:.1f}" y2="{p1[1]:.1f}" stroke="{colour}" stroke-width="{2.2 if i % 2 else 1.2}"/>')
    ray_svg.append(f'<circle cx="{cx}" cy="{cy}" r="7" fill="{GOLD}"/>')
    ray_svg.append(f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{RH - 6}" stroke="{INK}" stroke-width="3"/>')
    ray_svg.append(f'<text x="12" y="20" font-family="Georgia,serif" font-size="13" fill="{INK}">Fig. 6 · the rays · p-triple angles 2·atan(1/m), mirrored, as a monstrance</text>')
    ray_svg.append(f'<text x="12" y="{RH - 10}" font-family="ui-monospace,Menlo,monospace" font-size="11" fill="{MUTED}">24 rays · 53.13° at the centre falling to 9.5° at the tips · stem on the axis</text>')
    ray_svg.append("</svg>")

    def row(a, b, c):
        return f'<div class="row">{a}{b}{c}</div>'

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Showcase · rays and curves</title>
<style>
:root{{--paper:{PAPER};--ink:{INK};--muted:{MUTED};--rule:{RULE}}}
*{{box-sizing:border-box}} body{{margin:0;background:#f3eddf;color:var(--ink);font:16px/1.55 Georgia,serif}}
main{{max-width:1120px;margin:0 auto;padding:34px 22px 70px}}
h1{{font-size:32px;line-height:1.1;margin:0 0 8px}}
.eyebrow{{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}}
.lede{{max-width:940px;color:var(--muted);margin:0 0 18px}}
.fam{{margin:34px 0 10px;padding-top:12px;border-top:2px solid var(--ink)}}
.fam h2{{font-size:21px;margin:0 0 4px}} .fam p{{margin:0 0 10px;color:var(--muted);font:13px/1.5 ui-monospace,Menlo,monospace}}
.row{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin:0 0 8px}}
.row > svg{{background:var(--paper);border:1px solid var(--rule)}}
@media (max-width:900px){{.row{{grid-template-columns:1fr}}}}
.note{{font:12px/1.5 ui-monospace,Menlo,monospace;color:var(--muted)}}
</style></head><body><main>
<p class="eyebrow">curve-lab · the whole catalogue on one page</p>
<h1>Rays and curves</h1>
<p class="lede">Every family this project has built, in the order it was solved: the integer Euler polygon first, then the LACs, the integer chains, the widths, the composition — and the rays last, where they belong on a monstrance. Panels are lettered <code>a, b, c</code> inside each numbered figure.</p>

<div class="fam"><h2>1 · Integer Euler</h2><p>exact turns, exact closure, rational rails; only the drawn cubic is fitted</p></div>
{row(p1a, p1b, p1c)}

<div class="fam"><h2>2 · LAC spines</h2><p>31 recovered spines; the turn schedule is the curve</p></div>
{row(p2a, p2b, p2c)}

<div class="fam"><h2>3 · Integer Bézier · Euclid family chains</h2><p>integer control points at scale 1 · C1 exact · exponent −4/3 in the limit</p></div>
{row(p3a, p3b, p3c)}

<div class="fam"><h2>4 · Widths</h2><p>one exact taper, and two constructions that are provably not what they look like</p></div>
{row(p4a, p4b, p4c)}

<div class="fam"><h2>5 · Composition</h2><p>parts on different grids, a declared step, and an ending</p></div>
{row(p5a, p5b, p5c)}

<div class="fam"><h2>6 · Rays</h2><p>the p-triple angles themselves, mirrored about the axis</p></div>
{ray_svg}

<p class="note">Figures are drawn to their own extents; axes and units are inside each panel. Red marks the approximate or the exceptional, blue the exact rail, gold the integer construction.</p>
</main></body></html>
"""
    out = ROOT / "workbench" / "showcase.html"
    out.write_text(html, encoding="utf-8")
    print(out)


if __name__ == "__main__":
    run()
