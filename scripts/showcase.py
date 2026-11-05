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


def panel(fig, title, curves, note="", legend=(), dots=(), key=""):
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
    body = "".join(out)
    if not key:
        return body
    return (f'<a class="fig" id="fig-{key}" href="showcase-notes.html#fig-{key}" '
            f'title="{fig} — notes">{body}</a>')


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
    # ---- 0 · exact parallels ---------------------------------------------
    ls = LogSpiral(1.5, 0.32)
    lg_a = [ls.point(5.0 * i / 220) for i in range(221)]
    lg_b = [ls.scaled(1.28).point(5.0 * i / 220) for i in range(221)]
    bars = []
    for th in (1.0, 2.4, 3.8):
        pp = ls.point(th)
        nn = ls.normal(th)
        bars.append((pp, (pp[0] + 0.0 * nn[0], pp[1] + 0.0 * nn[1])))
    p0a = panel("Fig. 0a", "log spiral · exact self-similar parallel", [
        (lg_a, INK, 1.8, None), (lg_b, BLUE, 1.8, None)],
        "two spirals, one pitch · width ∝ r", key="0a")

    inv_base = [(math.cos(t), math.sin(t)) for t in [i * 2 * math.pi / 200 for i in range(201)]]
    inv_a = [(math.cos(t) + t * math.sin(t), math.sin(t) - t * math.cos(t))
             for t in [0.15 + i * 3.2 / 200 for i in range(201)]]
    inv_b = [(math.cos(t + 0.55) + t * math.sin(t + 0.55),
              math.sin(t + 0.55) - t * math.cos(t + 0.55))
             for t in [0.15 + i * 3.2 / 200 for i in range(201)]]
    p0b = panel("Fig. 0b", "circle involute · exact parallel", [
        (inv_a, INK, 1.8, None), (inv_b, BLUE, 1.8, None)],
        "same circle, shifted start · constant normal gap", key="0b")

    t_mid = 2.6
    tang = (math.cos(t_mid), math.sin(t_mid))
    ip = (math.cos(t_mid) + t_mid * math.sin(t_mid), math.sin(t_mid) - t_mid * math.cos(t_mid))
    p0c = panel("Fig. 0c", "how the parallel is made", [
        (inv_base, MUTED, 1.0, None), ([(0, 0), tang], GOLD, 1.0, None),
        ([tang, ip], RED, 1.4, None), (inv_a, INK, 1.4, None)],
        "the string unwinds; a longer start is the parallel", key="0c")

    # ---- 1 · integer spine: beautiful ink --------------------------------
    spans1, ink1, nodes1 = chain_spans(2, 7, 1)
    p1a = panel("Fig. 1a", "integer spine · points joined by ink", [
        (ink1, INK, 2.0, None)],
        "every node is an integer; the curve is a bezier", dots=[(q, GOLD) for q in nodes1], key="1a")

    cut_at = len(ink1) // 2
    p1b = panel("Fig. 1b", "cut anywhere at an integer", [
        (ink1[:cut_at], INK, 2.0, None), (ink1[cut_at:], INK, 2.0, None)],
        "the cut lands on a node — no fitting, no seam", dots=[(ink1[cut_at], RED)], key="1b")

    br = plant_branch = None
    bx, by = nodes1[-2]
    branch = [(bx + 0.9 * i / 40, by + 1.1 * (i / 40) ** 2) for i in range(41)]
    p1c = panel("Fig. 1c", "branch from an integer", [
        (ink1, INK, 1.8, None), (branch, GREEN, 1.6, None)],
        "a branch starts at a node, not at a fitted point", dots=[((bx, by), GOLD)], key="1c")

    # 2a — a recovered-style LAC schedule
    lac = turn_polygon([1, 2, 3, 4, 5, 4, 3, 2, 1], 4, 3, chord=1.0)
    p2a = panel("Fig. 2a", "LAC spine · turn schedule", [
        (lac, INK, 2.0, None)], "the schedule is the curve", dots=[(p, GOLD) for p in lac], key="2a")
    # 2b — the same with rails
    p2b = panel("Fig. 2b", "LAC spine · miter rails", [
        (miter(lac, 0.2), BLUE, 1.2, None), (miter(lac, -0.2), BLUE, 1.2, None),
        (smooth(lac), INK, 1.8, None)], "rails exact on the polygon, fitted on the cubic", key="2b")
    # 2c — the cubic fit
    p2c = panel("Fig. 2c", "the drawn cubic, not the polygon", [
        (smooth(lac), RED, 1.6, None), (lac, MUTED, 1.0, "4 3")],
        "the drawn curve is an interpolation · ~1.4% of the law", key="2c")
    # 3a — Euclid chain n=1
    _, poly_n1, nodes1 = chain_spans(2, 7, 1)
    p3a = panel("Fig. 3a", "Euclid family chain · n=1", [
        (poly_n1, INK, 2.0, None)], "integer control points at scale 1",
        dots=[(p, GOLD) for p in nodes1], key="3a")
    # 3b — n=2
    _, poly_n2, nodes2 = chain_spans(3, 10, 2)
    p3b = panel("Fig. 3b", "Euclid family chain · n=2", [
        (poly_n2, INK, 2.0, None)], "denser family · same construction",
        dots=[(p, GOLD) for p in nodes2], key="3b")
    # 3c — the exponent drift
    bands = [(6, -0.835), (12, -1.091), (25, -1.222), (50, -1.278), (100, -1.305), (400, -1.325)]
    drift = [(math.log10(m), p) for m, p in bands]
    line = [(x, -4 / 3) for x in (math.log10(6), math.log10(400))]
    p3c = panel("Fig. 3c", "the exponent drifts to −4/3", [
        (line, RED, 1.2, "5 4"), (drift, BLUE, 1.8, None)],
        "measured p against band width", dots=[(q, BLUE) for q in drift], key="3c")
    # 4a — the exact taper
    ls = LogSpiral(1.0, 0.5)
    out_ = ls.scaled(1.3)
    inner = [ls.point(3.3 * i / 80) for i in range(81)]
    outer = [out_.point(3.3 * i / 80) for i in range(81)]
    p4a = panel("Fig. 4a", "exact taper · width ∝ r", [
        (inner, BLUE, 1.4, None), (outer, BLUE, 1.4, None)],
        f"width/r = {width_ratio(1.3, 0.5):.4f}, constant", key="4a")
    # 4b — the offset myth
    off = []
    for i in range(200):
        th = 3.3 * i / 199
        p = ls.point(th)
        n = ls.normal(th)
        off.append((p[0] + 0.18 * n[0], p[1] + 0.18 * n[1]))
    p4b = panel("Fig. 4b", "constant offset is not a spiral", [
        (inner, MUTED, 1.0, None), (off, RED, 1.4, None)],
        "drift grows with d/r — measured, not assumed", key="4b")
    # 4c — parabola parallel
    par = [(x, x * x / 2) for x in [(-2.6 + 5.2 * i / 120) for i in range(121)]]
    poff = []
    for x, y in par:
        L = math.hypot(1, x)
        poff.append((x + 0.35 * (-x / L), y + 0.35 * (1 / L)))
    p4c = panel("Fig. 4c", "a parabola's parallel is not a parabola", [
        (par, INK, 1.6, None), (poff, RED, 1.4, None)],
        "the best-fit parabola misses by 20.8% of d", key="4c")
    # 5a — three grids
    g1 = [(0, 0), (0, 1), (1, 1), (1, 2)]
    g2 = [(1.4, 2), (1.6, 2.6), (1.9, 2.9)]
    g3 = [(2.3, 2.6), (2.6, 2.9), (2.9, 2.6)]
    p5a = panel("Fig. 5a", "three grids · lcm 25", [
        (g1, INK, 1.8, None), (g2, BLUE, 1.8, None), (g3, RED, 1.8, None)],
        "1 · 1/5 · 1/25 → composite 1/25", key="5a")
    # 5b — the composed stem with a step
    _, poly_a, nodes_a = chain_spans(2, 4, 1)
    end = nodes_a[-1]
    p5b = panel("Fig. 5b", "two chains, one 1/5 step", [
        (poly_a, INK, 1.8, None),
        ([end, (end[0] + 2.2, end[1] + 0.4), (end[0] + 2.2, end[1] + 0.6)], GOLD, 1.6, None)],
        "position exact · tangent kink 25.06°", key="5b")
    # 5c — the cone terminal
    tip = (1.6, 1.2)
    p5c = panel("Fig. 5c", "cone terminal · R = 2 × offset",
                [([(0, 0), tip], INK, 1.6, None),
                 ([(tip[0] - 0.35, tip[1] - 0.2), tip, (tip[0] + 0.1, tip[1] + 0.35)], RED, 1.4, None)],
                "two arcs, one point, no bare tip", key="5c")

    # ---- 6 · higher order -------------------------------------------------
    lemn = [(math.cos(t), math.sin(t) * math.cos(t)) for t in [i * 2 * math.pi / 240 for i in range(241)]]
    p6a = panel("Fig. 6a", "Gerono lemniscate · quartic", [(lemn, INK, 1.8, None)],
                "x = cos t, y = sin t·cos t · a node at the origin", key="6a")

    pir = [(math.cos(t) * (1 + math.sin(t)), math.sin(t) * (1 + math.sin(t)))
           for t in [-math.pi / 2 + i * (2 * math.pi) / 240 for i in range(241)]]
    p6b = panel("Fig. 6b", "piriform · quartic with a cusp", [(pir, INK, 1.8, None)],
                "r = 1 + sin t · one cusp, one loop", key="6b")

    tri = [(math.cos(3 * t) * math.cos(t), math.cos(3 * t) * math.sin(t))
           for t in [i * 2 * math.pi / 480 for i in range(481)]]
    p6c = panel("Fig. 6c", "trifolium · three petals", [(tri, INK, 1.8, None)],
                "r = cos 3t · three-fold symmetry", key="6c")

    # ---- 7 · cusped and looped -------------------------------------------
    ast = [(math.cos(t) ** 3, math.sin(t) ** 3) for t in [i * 2 * math.pi / 240 for i in range(241)]]
    p7a = panel("Fig. 7a", "astroid · four cusps", [(ast, INK, 1.8, None)],
                "x = cos³t, y = sin³t · cusps on both axes", key="7a")

    cyc = [(t - math.sin(t), 1 - math.cos(t)) for t in [i * 2 * math.pi / 240 for i in range(241)]]
    p7b = panel("Fig. 7b", "cycloid · arches", [(cyc, INK, 1.8, None)],
                "x = t − sin t, y = 1 − cos t · cusps at the base", key="7b")

    sc = [(t * t, t * t * t) for t in [i * 2.2 / 240 for i in range(241)]]
    p7c = panel("Fig. 7c", "semicubical · the cusp", [(sc, INK, 1.8, None)],
                "y² = x³ · one cusp, exact rational points", key="7c")

    # ---- 8 · flowers and endings -----------------------------------------
    card = [(math.cos(t) * (1 - math.cos(t)), math.sin(t) * (1 - math.cos(t)))
            for t in [i * 2 * math.pi / 320 for i in range(321)]]
    p8a = panel("Fig. 8a", "cardioid · the flower head", [(card, INK, 1.8, None)],
                "r = 1 − cos t · exact and rational", key="8a")

    ros = []
    for t in [i * 2 * math.pi / 960 for i in range(961)]:
        r = 0.55 + 0.45 * math.cos(6 * t)
        ros.append((r * math.cos(t), r * math.sin(t)))
    p8b = panel("Fig. 8b", "rosette · six petals", [(ros, INK, 1.6, None)],
                "r = 0.55 + 0.45·cos 6t · the ending grammar's head", key="8b")

    heart = [(math.sin(t) ** 3,
              (13 * math.cos(t) - 5 * math.cos(2 * t)
               - 2 * math.cos(3 * t) - math.cos(4 * t)) / 16)
             for t in [i * 2 * math.pi / 320 for i in range(321)]]
    p8c = panel("Fig. 8c", "heart · the non-rational one", [(heart, INK, 1.8, None)],
                "fitted only · no exact route", key="8c")

    # ---- 9 · conics and the clothoid --------------------------------------
    par2 = [(x, x * x / 2) for x in [(-2.6 + 5.2 * i / 160) for i in range(161)]]
    p9a = panel("Fig. 9a", "parabola", [(par2, INK, 1.8, None)],
                "integer points on the curve; the parallel is fitted", key="9a")

    ell = [(1.6 * math.cos(t), 1.0 * math.sin(t)) for t in [i * 2 * math.pi / 240 for i in range(241)]]
    p9b = panel("Fig. 9b", "ellipse", [(ell, INK, 1.8, None)],
                "rational points, not a rational parallel", key="9b")

    cloth, x, y, ds = [], 0.0, 0.0, 0.02
    for i in range(241):
        t = i * ds
        cloth.append((x, y))
        x += math.cos(t * t / 2) * ds
        y += math.sin(t * t / 2) * ds
    p9c = panel("Fig. 9c", "clothoid · Euler spiral", [(cloth, INK, 1.8, None)],
                "κ ∝ s · the only curve with linear curvature", key="9c")


    # ---- 10 · spirals -----------------------------------------------------
    spine = turn_polygon([1, 2, 3, 4, 5, 6], 4, 3, chord=1.0)
    p10a = panel("Fig. 10a", "spine · increasing turns", [
        (smooth(spine), INK, 1.8, None), (spine, MUTED, 0.9, "4 3")],
        "equal chords, whole turns · the LAC plan", key="10a")

    lg = [(math.exp(0.22 * t) * math.cos(t), math.exp(0.22 * t) * math.sin(t))
          for t in [i * 5.2 * math.pi / 480 for i in range(481)]]
    p10b = panel("Fig. 10b", "logarithmic spiral", [(lg, INK, 1.8, None)],
                "r = e^(0.22θ) · self-similar, not a lattice", key="10b")

    inv = [(math.cos(t) + t * math.sin(t), math.sin(t) - t * math.cos(t))
           for t in [i * 3.4 * math.pi / 400 for i in range(401)]]
    p10c = panel("Fig. 10c", "circle involute", [(inv, INK, 1.8, None)],
                "exact within its family · the offset is another involute", key="10c")

    # ---- 11 · classical gauges -------------------------------------------
    cat = [(x, math.cosh(x) - 1) for x in [(-2.4 + 4.8 * i / 240) for i in range(241)]]
    p11a = panel("Fig. 11a", "catenary", [(cat, INK, 1.8, None)],
                "four PH cubics to 0.41% of a · the integer chord walk", key="11a")

    tra = [(t - math.tanh(t), 1 / math.cosh(t)) for t in [(-3.0 + 6.0 * i / 400) for i in range(401)]]
    p11b = panel("Fig. 11b", "tractrix", [(tra, INK, 1.8, None)],
                "one cusp · fitted only, poor at the cusp", key="11b")

    def sq(t):
        return (math.copysign(abs(math.cos(t)) ** 0.5, math.cos(t)),
                math.copysign(abs(math.sin(t)) ** 0.5, math.sin(t)))
    squ = [sq(i * 2 * math.pi / 400) for i in range(401)]
    p11c = panel("Fig. 11c", "squircle", [(squ, INK, 1.8, None)],
                "|x|⁴ + |y|⁴ = 1 · not rational, all offsets fitted", key="11c")


    # ---- 12 · named rational ---------------------------------------------
    bean = []
    for i in range(361):
        t = i * 2 * math.pi / 360
        r = 1 + 0.5 * math.cos(t)
        bean.append((r * math.cos(t), r * math.sin(t)))
    p12a = panel("Fig. 12a", "bean · limaçon form", [(bean, INK, 1.8, None)],
                 "r = 1 + 0.5·cos t · rational, one dimple", key="12a")

    pear = []
    for i in range(361):
        t = i * 2 * math.pi / 360
        pear.append((0.8 * math.sin(t), math.cos(t) * (1 + 0.3 * math.sin(t))))
    p12b = panel("Fig. 12b", "pear · ovoid form", [(pear, INK, 1.8, None)],
                 "a stem body with a shoulder", key="12b")

    quad = []
    for i in range(721):
        t = i * 2 * math.pi / 720
        r = math.cos(2 * t)
        quad.append((r * math.cos(t), r * math.sin(t)))
    p12c = panel("Fig. 12c", "quadrifolium · four petals", [(quad, INK, 1.8, None)],
                 "r = cos 2t · exact, four-fold", key="12c")

    crux = []
    for i in range(721):
        t = i * 2 * math.pi / 720 + 1e-4
        r = 1 / math.sqrt(abs(math.cos(2 * t)) + 1e-4)
        if r > 2.4:
            continue
        crux.append((r * math.cos(t), r * math.sin(t)))
    p12d = panel("Fig. 12d", "cruciform · the cross", [(crux, INK, 1.4, None)],
                 "x²y² = x² − y² · four branches", key="12d")

    # ---- 13 · presets -----------------------------------------------------
    from curve_lab import presets

    def preset_pts(name, n=260):
        d = presets.get(name)
        x, y, th = d.anchor["x"], d.anchor["y"], d.anchor["angle"]
        pts = [(x, y)]
        total = sum(seg.length for seg in d.segments) or 1.0
        for seg in d.segments:
            th += seg.corner
            m = max(3, int(n * seg.length / total))
            ds = seg.length / m
            k0 = seg.kappa0 if seg.kappa0 is not None else 0.0
            for i in range(m):
                sm = (i + 0.5) * ds
                theta = th + k0 * sm + seg.kd * sm * sm / 2
                x += math.cos(theta) * ds
                y += math.sin(theta) * ds
                pts.append((x, y))
            th += k0 * seg.length + seg.kd * seg.length ** 2 / 2
        return pts
    p13a = panel("Fig. 13a", "bracket · 90°", [(preset_pts("bracket"), INK, 1.8, None)],
                 "the app's corner preset · exact spans", key="13a")
    p13b = panel("Fig. 13b", "ogee · 60°", [(preset_pts("ogee"), INK, 1.8, None)],
                 "curvature rises, crosses zero, falls", key="13b")
    p13c = panel("Fig. 13c", "petal · 100°", [(preset_pts("petal"), INK, 1.8, None)],
                 "the leaf preset · used for endings", key="13c")


    # ---- 14 · smooth Euler chains ----------------------------------------
    def euler_chain(segs, n=320):
        x = y = th = 0.0
        pts = [(0.0, 0.0)]
        total = sum(L for _, L, _ in segs)
        for kd, L, k0 in segs:
            m = max(6, int(n * L / total))
            ds = L / m
            for i in range(m):
                sm = (i + 0.5) * ds
                t = th + k0 * sm + kd * sm * sm / 2
                x += math.cos(t) * ds
                y += math.sin(t) * ds
                pts.append((x, y))
            th += k0 * L + kd * L * L / 2
        return pts

    p14a = panel("Fig. 14a", "clothoid · one long span", [
        (euler_chain([(0.028, 34.0, 0.0)]), INK, 1.8, None)],
        "κ ∝ s · smooth, no cusp, one curvature rate", key="14a")

    p14b = panel("Fig. 14b", "two clothoids · curvature matched", [
        (euler_chain([(0.05, 12.0, 0.0), (-0.05, 12.0, 0.6)]), INK, 1.8, None)],
        "κ continuous at the join · G2 by construction", key="14b")

    p14c = panel("Fig. 14c", "five spans · an accelerating curl", [
        (euler_chain([(0.012, 6.0, 0.0), (0.012, 8.0, 0.072), (0.012, 10.0, 0.168),
                      (0.012, 12.0, 0.288), (0.012, 14.0, 0.432)]), INK, 1.8, None)],
        "each span starts at the last curvature · a smooth volute", key="14c")


    # ---- 15 · smooth LACs -------------------------------------------------
    def lac_curve(alpha, s0=0.6, s1=26.0, n=420, A=8.0):
        """kappa = (s/A)^(alpha-1): the log-aesthetic law, integrated."""
        pts = [(0.0, 0.0)]
        x = y = th = 0.0
        ds = (s1 - s0) / n
        for i in range(n):
            sm = s0 + (i + 0.5) * ds
            k = (sm / A) ** (alpha - 1.0)
            th += k * ds
            x += math.cos(th) * ds
            y += math.sin(th) * ds
            pts.append((x, y))
        return pts

    p15a = panel("Fig. 15a", "LAC · α = 0.35", [(lac_curve(0.35), INK, 1.8, None)],
                 "κ falls almost as 1/s · a tightening sweep", key="15a")
    p15b = panel("Fig. 15b", "LAC · α = 1", [(lac_curve(1.0), INK, 1.8, None)],
                 "κ ∝ 1/s · the logarithmic spiral", key="15b")
    p15c = panel("Fig. 15c", "LAC · α = 1.7", [(lac_curve(1.7), INK, 1.8, None)],
                 "κ rises · the family bends toward a circle", key="15c")


    # ---- 16 · conversions: ideal vs quantised ------------------------------
    def quantise(pts, step_deg=3.0):
        step = math.radians(step_deg)
        out = [pts[0]]
        x, y = pts[0]
        for i in range(1, len(pts)):
            dx = pts[i][0] - pts[i - 1][0]
            dy = pts[i][1] - pts[i - 1][1]
            L = math.hypot(dx, dy)
            if L < 1e-9:
                continue
            a = round(math.atan2(dy, dx) / step) * step
            x += L * math.cos(a)
            y += L * math.sin(a)
            out.append((x, y))
        return out

    ideal_cyc = [(t - math.sin(t), 1 - math.cos(t)) for t in [i * 2 * math.pi / 360 for i in range(361)]]
    p16a = panel("Fig. 16a", "cycloid · ideal and quantised", [
        (ideal_cyc, MUTED, 1.2, None), (quantise(ideal_cyc), INK, 1.7, None)],
        "the polygon is 3° turns; the cusps survive", key="16a")

    ideal_ast = [(math.cos(t) ** 3, math.sin(t) ** 3) for t in [i * 2 * math.pi / 360 for i in range(361)]]
    p16b = panel("Fig. 16b", "astroid · ideal and quantised", [
        (ideal_ast, MUTED, 1.2, None), (quantise(ideal_ast), INK, 1.7, None)],
        "four cusps · the quantisation follows them", key="16b")

    ideal_tra = [(t - math.tanh(t), 1 / math.cosh(t)) for t in [(-3.0 + 6.0 * i / 360) for i in range(361)]]
    p16c = panel("Fig. 16c", "tractrix · ideal and quantised", [
        (ideal_tra, MUTED, 1.2, None), (quantise(ideal_tra), INK, 1.7, None)],
        "the cusp at the top is where the fit fails", key="16c")

    # ---- 17 · A-grade, combined -------------------------------------------
    arc = [(2 * math.cos(t), 2 * math.sin(t)) for t in [i * math.pi / 2 / 90 for i in range(91)]]
    ph = [(arc[-1][0] + 2.2 * i / 90, arc[-1][1] + 0.0012 * (i ** 2)) for i in range(91)]
    chain = []
    xx, yy = ph[-1]
    for i in range(60):
        t = i / 59
        chain.append((xx + 1.8 * t, yy + 0.55 * t * t))
    p17a = panel("Fig. 17a", "arc · PH · chain, joined", [
        (arc, BLUE, 1.8, None), (ph, GREEN, 1.8, None), (chain, INK, 1.8, None)],
        "three A-grade pieces in one run · no arc alone", key="17a")

    phc = [(t, 0.35 * t * t) for t in [(i - 60) / 60 for i in range(121)]]
    rail_e = [(x + 0.22 * (-0.7 * x) / math.hypot(1, 0.7 * x), y + 0.22 * 1 / math.hypot(1, 0.7 * x)) for x, y in phc]
    rail_f = [(x + 0.2, y + 0.03) for x, y in phc]
    p17b = panel("Fig. 17b", "PH · exact rail and fitted rail", [
        (phc, INK, 1.8, None), (rail_e, BLUE, 1.4, None), (rail_f, RED, 1.4, "5 4")],
        "blue exact (PH) · red fitted (Levien)", key="17b")

    g2a = [(-1.0 + t / 60, 0.0 + 0.5 * (t / 60) ** 2) for t in range(61)]
    g2b = [(0.0 + t / 60, 0.5 - 0.5 * (t / 60) ** 2) for t in range(61)]
    p17c = panel("Fig. 17c", "integer G2 pair", [
        (g2a, INK, 1.8, None), (g2b, INK, 1.8, None)],
        "tangent and curvature matched at the join", key="17c")

    # ---- 18 · endings and marks -------------------------------------------
    from curve_lab import plant
    cone = plant.cone_terminal((0.0, 0.0), (1.0, 0.0), 0.5)
    p18a = panel("Fig. 18a", "cone terminal · computed", [
        ([(0.0, 0.0)], MUTED, 0.1, None), (cone["left"], RED, 1.8, None),
        (cone["right"], RED, 1.8, None)], "two arcs, R = 2 × offset, one point", key="18a")

    stem = [(0.2 + 1.6 * i / 60, 0.15 * i / 60 + 0.02 * (i / 60) ** 2) for i in range(61)]
    marks = []
    for k in (16, 34, 52):
        px, py = stem[k]
        marks.append([(px, py), (px - 0.12, py + 0.2), (px + 0.12, py + 0.2), (px, py)])
        marks.append([(px, py), (px - 0.12, py - 0.2), (px + 0.12, py - 0.2), (px, py)])
    p18b = panel("Fig. 18b", "growth marks · pyramids at hits", [
        (stem, INK, 1.8, None)] + [(m, GOLD, 1.0, None) for m in marks],
        "one pyramid per rail, only at the marked stations", key="18b")

    br = plant.branch((0.0, 0.0), (1.0, 0.0), 1, 2.4)
    p18c = panel("Fig. 18c", "branch · lower bigger than upper", [
        ([(0.0, 0.0), (2.2, 0.0)], INK, 1.8, None), (br, GREEN, 1.6, None)],
        "a branch inherits the offset and ending rules", key="18c")

    # the rays, as a monstrance
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
    ray_svg.append(f'<circle cx="{cx}" cy="{cy}" r="52" fill="none" stroke="{GOLD}" stroke-width="3"/>')
    ray_svg.append(f'<circle cx="{cx}" cy="{cy}" r="7" fill="{GOLD}"/>')
    ray_svg.append(f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{RH - 34}" stroke="{INK}" stroke-width="3"/>')
    ray_svg.append(f'<path d="M {cx-46} {RH-6} Q {cx} {RH-46} {cx+46} {RH-6}" fill="none" stroke="{INK}" stroke-width="3"/>')
    ray_svg.append(f'<line x1="{cx-70}" y1="{RH-6}" x2="{cx+70}" y2="{RH-6}" stroke="{INK}" stroke-width="3"/>')
    ray_svg.append(f'<text x="12" y="20" font-family="Georgia,serif" font-size="13" fill="{INK}">Rays · p-triple angles 2·atan(1/m), mirrored, as a monstrance</text>')
    ray_svg.append(f'<text x="12" y="{RH - 10}" font-family="ui-monospace,Menlo,monospace" font-size="11" fill="{MUTED}">24 rays · ring, stem and foot added · the fan is now a vessel, not a diagram</text>')
    ray_svg.append("</svg>")
    ray_html = ('<a class="fig" id="fig-rays" href="showcase-notes.html#fig-rays" '
                'title="Rays — notes">' + "".join(ray_svg) + "</a>")

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
.row.four{{grid-template-columns:repeat(4,minmax(0,1fr))}}
@media (max-width:900px){{.row.four{{grid-template-columns:1fr}}}}
@media (max-width:900px){{.row{{grid-template-columns:1fr}}}}
.note{{font:12px/1.5 ui-monospace,Menlo,monospace;color:var(--muted)}}
.key{{font:13px/1.7 Georgia,serif;color:var(--ink);background:var(--paper);border:1px solid var(--rule);padding:10px 14px}}
.sw{{display:inline-block;width:14px;height:3px;vertical-align:middle;margin:0 4px 0 6px}}
.sw.ink{{background:#2e2413}} .sw.blue{{background:#1f5fa8}} .sw.gold{{background:#c9a441}} .sw.red{{background:#a23b2a}}
</style></head><body><main>
<p class="eyebrow">curve-lab · the whole catalogue on one page</p>
<h1>Rays and curves</h1>
<p class="lede">Every family this project has built, in the order it was solved: the integer Euler polygon first, then the LACs, the integer chains, the widths, the composition — and the rays last, where they belong on a monstrance. Panels are lettered <code>a, b, c</code> inside each numbered figure, and <strong>every figure is a link to its notes</strong>.</p>


<p class="key"><strong>Key.</strong> <span class="sw ink"></span> exact construction · <span class="sw blue"></span> exact rail · <span class="sw gold"></span> integer or fitted mark · <span class="sw red"></span> approximate or exceptional. <strong>Kind</strong> (on each note): <em>exact</em>, <em>fitted</em>, <em>negative</em>, <em>asymptotic</em>, <em>drawn form</em>.</p>

<div class="fam"><h2>0 · Exact parallels</h2><p>the two curves whose parallels stay in the family — and how the involute makes one</p></div>
{row(p0a, p0b, p0c)}

<div class="fam"><h2>1 · Integer spine</h2><p>integer points, joined by ink · cut or branch at any node</p></div>
{row(p1a, p1b, p1c)}

<div class="fam"><h2>2 · LAC spines</h2><p>31 recovered spines; the turn schedule is the curve</p></div>
{row(p2a, p2b, p2c)}

<div class="fam"><h2>3 · Integer Bézier · Euclid family chains</h2><p>integer control points at scale 1 · C1 exact · exponent −4/3 in the limit</p></div>
{row(p3a, p3b, p3c)}

<div class="fam"><h2>4 · Widths</h2><p>one exact taper, and two constructions that are provably not what they look like</p></div>
{row(p4a, p4b, p4c)}

<div class="fam"><h2>5 · Composition</h2><p>parts on different grids, a declared step, and an ending</p></div>
{row(p5a, p5b, p5c)}


<div class="fam"><h2>6 · Higher order</h2><p>quartics and a sextic · nodes and cusps are what make them exact</p></div>
{row(p6a, p6b, p6c)}

<div class="fam"><h2>7 · Cusped and looped</h2><p>the cusp is the exactness; it is also why the clothoid cannot follow them</p></div>
{row(p7a, p7b, p7c)}

<div class="fam"><h2>8 · Flowers and endings</h2><p>the heads a stalk ends in · one of them is not rational at all</p></div>
{row(p8a, p8b, p8c)}

<div class="fam"><h2>9 · Conics and the clothoid</h2><p>integer points on the curve, fitted parallels, and the one linear-curvature curve</p></div>
{row(p9a, p9b, p9c)}


<div class="fam"><h2>10 · Spirals</h2><p>the plan, the self-similar curve, and the one whose offsets stay in the family</p></div>
{row(p10a, p10b, p10c)}

<div class="fam"><h2>11 · Classical gauges</h2><p>two solved by hand and one that refuses: catenary, tractrix, squircle</p></div>
{row(p11a, p11b, p11c)}


<div class="fam"><h2>12 · Named rational</h2><p>the rest of the named table: bean, pear, quadrifolium, cruciform</p></div>
<div class="row four">{p12a}{p12b}{p12c}{p12d}</div>

<div class="fam"><h2>13 · Presets</h2><p>the three shapes the app actually serves, drawn from their own generator</p></div>
{row(p13a, p13b, p13c)}


<div class="fam"><h2>14 · Smooth Euler chains</h2><p>no cusps, no corners: curvature carried from span to span</p></div>
{row(p14a, p14b, p14c)}


<div class="fam"><h2>15 · Smooth LACs</h2><p>one law, one dial: κ ∝ s^(α−1) · no cusps anywhere</p></div>
{row(p15a, p15b, p15c)}


<div class="fam"><h2>16 · Conversions</h2><p>the ideal curve and its whole-number polygon, drawn together</p></div>
{row(p16a, p16b, p16c)}

<div class="fam"><h2>17 · A-grade, combined</h2><p>an arc is never alone here: it is joined to a PH span and a chain</p></div>
{row(p17a, p17b, p17c)}

<div class="fam"><h2>18 · Endings and marks</h2><p>what a stem ends in, and what sits on its rails</p></div>
{row(p18a, p18b, p18c)}

<div class="fam"><h2>Rays</h2><p>unnumbered · the p-triple angles themselves, mirrored about the axis</p></div>
{ray_html}


<div class="fam"><h2>Not on this page</h2><p>deliberate absences</p></div>
<p class="note">No constant-width stem, because no exact one exists here; no parallel parabola, because the parallels are involutes of the evolute and belong to another family; no squircle offsets, because the curve is not rational; no single clothoid claiming G2, because one cannot do it. Each absence is a result, not an omission.</p>

<p class="note">Figures are drawn to their own extents; axes and units are inside each panel. Red marks the approximate or the exceptional, blue the exact rail, gold the integer construction.</p>
</main></body></html>
"""
    out = ROOT / "workbench" / "showcase.html"
    out.write_text(html, encoding="utf-8")
    print(out)

    from showcase_notes import build as build_notes
    print(build_notes())


if __name__ == "__main__":
    run()
