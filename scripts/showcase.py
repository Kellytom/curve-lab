"""The showcase: every family of ray and curve this project has, on one page.

    .venv/bin/python scripts/showcase.py
    open workbench/showcase.html

Figures are numbered by family and lettered by panel (Fig. 1a, 1b, 1c). Three
panels across — four where a family has a fourth member — a rule between
families, and the rays last so the page can be read as a monstrance.
"""

from __future__ import annotations

import math
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import generators as G  # noqa: E402
from curve_lab import pyth_chain as pc  # noqa: E402
from curve_lab import engine, interpolate  # noqa: E402
from curve_lab import spine as spine_layer  # noqa: E402
from curve_lab import terminals as term  # noqa: E402
from curve_lab.parallel_bezier import fit_chain as fit_parallel  # noqa: E402
from curve_lab.model import Design, Segment  # noqa: E402
from curve_lab.taper import LogSpiral, width_ratio  # noqa: E402
from showcase_catalogue import FAMILIES  # noqa: E402
from modulated_width import cubic as width_cubic, rails as width_rails  # noqa: E402

INK, GOLD, BLUE, RED, GREEN = "#2e2413", "#b23a2b", "#1f5fa8", "#a23b2a", "#3f7d4e"  # no gold: construction is red
MUTED, RULE, PAPER = "#7b6c4e", "#d8ccae", "#fbf7ec"

W, H = 336, 250

from dot_chain import audit_dots, dot_finder, solved_marks  # noqa: E402
from grid_view import MARK, best_step, crossings, grid_lines, nice_step  # noqa: E402


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


def _on_curve(p, polylines, tol=1e-9):
    """True when the point lies on one of the drawn polylines."""
    for pts in polylines:
        for a, b in zip(pts, pts[1:]):
            ax, ay = a
            bx, by = b
            dx, dy = bx - ax, by - ay
            if dx == 0 and dy == 0:
                d = math.dist(p, a)
            else:
                t = ((p[0] - ax) * dx + (p[1] - ay) * dy) / (dx * dx + dy * dy)
                t = max(0.0, min(1.0, t))
                d = math.dist(p, (ax + t * dx, ay + t * dy))
            if d <= tol:
                return True
    return False


# A single-curve example gets a companion either side, as Fig. 0a does for the
# log spiral. The rule says what that companion is: an exact parallel, a fitted
# one, or a curve that is deliberately not an offset (it folds, or leaves the
# family). Charts are not curves and carry no companions.
NO_COMPANION = {"19b", "20c", "3c"}
COMPANION_RULE = {
    "10b": "not an offset",          # a constant-width curl is not a log spiral
    "10c": "exact",                  # a shifted involute is the parallel
    "13a": "exact", "13b": "exact", "13c": "exact",   # PH presets
    "19a": "exact",                  # arcs and lines, exact 3-4-5 spine
}


def companion_rule(key, title, rule=None):
    if rule:
        return rule
    if key in COMPANION_RULE:
        return COMPANION_RULE[key]
    low = title.lower()
    if "log spiral" in low or "logarithmic spiral" in low:
        return "not an offset"
    if low.endswith("circle") or "circle, quarter" in low or "involute" in low:
        return "exact"
    return "fitted"
# the catalogue's own provenance, one rule per family table
FAMILY_RULE = {"presets": "exact"}
# every entry in these tables is one curve, even when it is drawn in two or
# more pieces (branches, loops, cusp splits); composites are not listed
SINGLE_FAMILIES = {"named", "hearts", "presets", "conics", "euler", "lac",
                   "cubics", "cubics-c", "french", "leaves"}
# stem cards that are one curve in several pieces, asked for by name
FORCE_COMPANIONS = {
    "c119", "c120", "c122", "c126", "c127", "c128", "c129", "c130", "c131",
    "c132", "c133", "c134", "c135", "c138", "c140", "c141", "c143", "c146",
}


def side_offsets(pts, d):
    """The numeric parallels at +d and -d, one point per source point."""
    left, right = [], []
    last = len(pts) - 1
    for i, p in enumerate(pts):
        a, b = pts[max(0, i - 1)], pts[min(last, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        if length == 0:
            left.append(p)
            right.append(p)
            continue
        nx, ny = -dy / length, dx / length
        left.append((p[0] + d * nx, p[1] + d * ny))
        right.append((p[0] - d * nx, p[1] - d * ny))
    return left, right


def panel(fig, title, curves, note="", legend=(), dots=(), key="", curve="",
          joins=False, rule=None, single_curve=None, composite=False):
    """One cue per figure. A *curve example* is one curve even when it is
    drawn in pieces — two hyperbola branches, two lemniscate loops, a cusped
    curve split at its cusps, or an ideal and its quantised twin. Those all
    get the companion pair; constructions and composites do not."""
    solid = [c[0] for c in curves if not c[3]]
    main = [c[0] for c in curves if not c[3] and c[1] == INK]
    single = (len(solid) == 1 if single_curve is None else bool(single_curve))
    single = single and key not in NO_COMPANION
    comp_curves = []
    comp_label = ""
    if composite and key not in NO_COMPANION:
        chain = []
        for pts in (main or solid):
            chain.extend(pts)
        rule = companion_rule(key, title, rule)
        xs = [p[0] for p in chain]
        ys = [p[1] for p in chain]
        d = 0.05 * max(max(xs) - min(xs), max(ys) - min(ys))
        if d > 0:
            left, right = side_offsets(chain, d)
            comp_curves = [(left, BLUE, 1.0, None), (right, BLUE, 1.0, None)]
            comp_label = f"±{d:.2f} {rule}"
    elif single:
        branches = main or solid
        rule = companion_rule(key, title, rule)
        pts_all = [p for pts in branches for p in pts]
        xs = [p[0] for p in pts_all]
        ys = [p[1] for p in pts_all]
        d = 0.05 * max(max(xs) - min(xs), max(ys) - min(ys))
        if d > 0:
            for pts in branches:
                left, right = side_offsets(pts, d)
                comp_curves += [(left, BLUE, 1.0, None), (right, BLUE, 1.0, None)]
            comp_label = f"±{d:.2f} {rule}"
    allpts = [p for pts, *_ in curves for p in pts]
    allpts += [p for pts, *_ in comp_curves for p in pts]
    put = fit(allpts)
    out = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="{title}">',
           f'<rect width="{W}" height="{H}" fill="{PAPER}"/>']
    xs = [p[0] for p in allpts]
    ys = [p[1] for p in allpts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    chain = solved_marks(solid) if joins else None
    if chain and chain["chord"] > 0:
        span = max(x1 - x0, y1 - y0)
        k = max(1, round(span / (10.0 * chain["chord"])))
        step = chain["chord"] * k          # the chain's own lattice, kept legible
    else:
        step = best_step(solid, max(x1 - x0, y1 - y0))
    out += grid_lines(put, x0, x1, y0, y1, step, RULE)
    for pts, colour, width, dash in comp_curves:
        seen = [put(p) for p in pts]
        path = " ".join(("M" if i == 0 else "L") + f"{x:.1f},{y:.1f}"
                        for i, (x, y) in enumerate(seen))
        out.append(f'<path class="comp" d="{path}" fill="none" '
                   f'stroke="{colour}" stroke-width="{width}"/>')
    for pts, colour, width, dash in curves:
        seen = []
        for p in pts:
            q = put(p)
            r = (round(q[0], 1), round(q[1], 1))
            if not seen or r != seen[-1]:
                seen.append(r)
        d = " ".join(("M" if i == 0 else "L") + f"{x:.1f},{y:.1f}"
                     for i, (x, y) in enumerate(seen))
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        out.append(f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{width}"{dash_attr}/>')
    marks = [(p, MARK) for p in dot_finder(solid, step)]
    for p, colour in marks:
        q = put(p)
        out.append(f'<circle class="lattice" cx="{q[0]:.1f}" cy="{q[1]:.1f}" '
                   f'r="2.2" fill="{colour}"/>')
    for p, colour in dots:
        q = put(p)
        out.append(f'<rect x="{q[0]-2:.1f}" y="{q[1]-2:.1f}" width="4" height="4" '
                   f'fill="none" stroke="{colour}" stroke-width="1"/>')
    out.append(f'<text x="10" y="18" font-family="Georgia,serif" font-size="12" fill="{INK}">{fig} · {title}</text>')
    # the note is wrapped to the panel width: 10px mono, ~52 characters a line
    words, lines, line = str(note).split(), [], ""
    for w in words:
        if len(line) + len(w) + 1 <= 52:
            line = (line + " " + w).strip()
        else:
            lines.append(line)
            line = w
    if line:
        lines.append(line)
    if len(lines) > 2:
        lines = lines[:2]
        lines[1] = lines[1][:49].rstrip() + "…"
    for i, text in enumerate(reversed(lines)):        # last line sits lowest
        y = H - 8 - 12 * i
        out.append(f'<text x="10" y="{y}" font-family="ui-monospace,Menlo,monospace" '
                   f'font-size="10" fill="{MUTED}">{text}</text>')
    out.append(f'<text x="{W - 14}" y="{H - 24}" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="{MUTED}" text-anchor="end">x →</text>')
    if comp_label:
        out.append(f'<text x="10" y="{H - 32}" font-family="ui-monospace,Menlo,monospace" '
                   f'font-size="10" fill="{BLUE}">{comp_label}</text>')
    out.append(f'<text x="12" y="34" font-family="ui-monospace,Menlo,monospace" font-size="10" fill="{MUTED}">y ↑</text>')
    out.append("</svg>")
    body = "".join(out)
    if not key:
        return body
    attrs = ''
    if comp_curves:
        attrs = f' data-companion="{rule}"' + (' data-single="1"' if single else '')
    return (f'<a class="fig" id="fig-{key}" data-curve="{curve}"{attrs} '
            f'href="showcase-notes.html#fig-{key}" '
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


def span_points(span, n=24):
    """Sample one cubic span written as p0/c1/c2/p3."""
    p0, c1, c2, p3 = span["p0"], span["c1"], span["c2"], span["p3"]
    out = []
    for i in range(n + 1):
        t = i / n
        mt = 1 - t
        out.append((mt ** 3 * p0[0] + 3 * mt * mt * t * c1[0]
                    + 3 * mt * t * t * c2[0] + t ** 3 * p3[0],
                    mt ** 3 * p0[1] + 3 * mt * mt * t * c1[1]
                    + 3 * mt * t * t * c2[1] + t ** 3 * p3[1]))
    return out


def line_span(p0, p1):
    a = ((p1[0] - p0[0]) / 3.0, (p1[1] - p0[1]) / 3.0)
    return {"p0": p0, "c1": (p0[0] + a[0], p0[1] + a[1]),
            "c2": (p1[0] - a[0], p1[1] - a[1]), "p3": p1}


def terminal_shape(kind, x0, length=1.0, half=0.2):
    """One ribbon from x0 with `kind` closing its right end."""
    pos = {"spans": [line_span((x0, half), (x0 + length, half))]}
    neg = {"spans": [line_span((x0, -half), (x0 + length, -half))]}
    spans = term.terminal_spans(pos, neg, kind)
    if not spans:
        return []
    pts = [spans[0]["p0"]]
    for s in spans:
        pts.extend(span_points(s)[1:])
    return pts


def squircle_point(t):
    c, s = math.cos(t), math.sin(t)
    return (math.copysign(abs(c) ** 0.5, c),
            math.copysign(abs(s) ** 0.5, s))


def squircle_euler():
    """Eight Euler spans, one per 45 degree station of the squircle."""
    out = []
    for k in range(8):
        t0, t1 = k * math.pi / 4.0, (k + 1) * math.pi / 4.0
        p0, p1 = squircle_point(t0), squircle_point(t1)
        a = squircle_point(t0 - 1e-6)
        b = squircle_point(t0 + 1e-6)
        c = squircle_point(t1 - 1e-6)
        d = squircle_point(t1 + 1e-6)
        th0 = math.atan2(b[1] - a[1], b[0] - a[0])
        th1 = math.atan2(d[1] - c[1], d[0] - c[0])
        k0, kd, length = interpolate.fit(p0, th0, p1, th1)
        chain = engine.build(Design(
            segments=[Segment(kappa0=k0, kd=kd, length=length)],
            anchor={"x": p0[0], "y": p0[1], "angle": th0}))
        out.append([chain.point(chain.length * i / 28.0) for i in range(29)])
    return out


def named_curve(key, n=240):
    """The named curve's branches, sampled from generators.NAMED."""
    spec = next(s for s in G.NAMED if s["key"] == key)
    data = G.named_data(spec)
    out = []
    for ctrl in data["ctrl"]:
        pts = []
        for i in range(n + 1):
            p = G.homog_point(ctrl, Fraction(i, n))
            if p is not None:
                pts.append((float(p[0]), float(p[1])))
        if len(pts) > 1:
            out.append(pts)
    return out


def chaikin(pts, it=5):
    """Corner cutting: a smooth curve that follows the polygon without
    overshooting it. More iterations = more triangles, less wobble."""
    for _ in range(it):
        out = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            out.append((0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]))
            out.append((0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1]))
        out.append(pts[-1])
        pts = out
    return pts


def fine_triple(target_deg=4.4, c_max=3125):
    """The p-triple whose turn is closest to `target_deg`, with its turn angle."""
    from curve_lab.pyth_triples import base_triples
    pairs = [(abs(math.degrees(math.atan2(bb, aa)) - target_deg), aa, bb)
             for t in base_triples(c_max)
             for aa, bb in ((t["a"], t["b"]), (t["b"], t["a"]))]
    _, a, b = min(pairs)
    return a, b, math.atan2(b, a)


def euler_curve(points, n=120, sub=4):
    """The house method: convert to an Euler polygon, then Béziers that follow
    it. Dense polygon, C2 spline through its nodes, so the ink is smooth."""
    from curve_lab.euler_polygon import convert
    d = convert(points, n=n)
    return bspline(d["polygon"], sub), d["polygon"]


def bspline(pts, n=24):
    """Uniform cubic B-spline through the polygon: C2, so curvature is
    continuous at every join. This is the G2 version of the display curve."""
    # natural ends: mirror one point past each end, which is far gentler than
    # triplicating the ends (that pinches the curvature at the tips)
    p_start = (2 * pts[0][0] - pts[1][0], 2 * pts[0][1] - pts[1][1])
    p_end = (2 * pts[-1][0] - pts[-2][0], 2 * pts[-1][1] - pts[-2][1])
    P = [p_start] + list(pts) + [p_end]
    out = []
    for i in range(len(P) - 3):
        p0, p1, p2, p3 = P[i:i + 4]
        for j in range(n):
            t = j / n
            t2, t3 = t * t, t * t * t
            b0 = (1 - t) ** 3 / 6.0
            b1 = (3 * t3 - 6 * t2 + 4) / 6.0
            b2 = (-3 * t3 + 3 * t2 + 3 * t + 1) / 6.0
            b3 = t3 / 6.0
            q = (b0 * p0[0] + b1 * p1[0] + b2 * p2[0] + b3 * p3[0],
                 b0 * p0[1] + b1 * p1[1] + b2 * p2[1] + b3 * p3[1])
            if not out or math.dist(q, out[-1]) > 1e-12:
                out.append(q)
    if math.dist(pts[-1], out[-1]) > 1e-12:
        out.append(pts[-1])
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
    from curve_lab import plant

    def offset_polyline(pts, d):
        out = []
        for i, q in enumerate(pts):
            a = pts[max(0, i - 1)]
            b = pts[min(len(pts) - 1, i + 1)]
            tx, ty = b[0] - a[0], b[1] - a[1]
            L = math.hypot(tx, ty) or 1
            out.append((q[0] - ty / L * d, q[1] + tx / L * d))
        return out

    def lac_curve(alpha, s0=0.6, s1=26.0, n=420, A=8.0):
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

    # ---- 2 · LAC ribbon ---------------------------------------------------
    lac1 = lac_curve(0.6)
    p2a = panel("Fig. 2a", "LAC ribbon · curve and rails", [
        (offset_polyline(lac1, 0.2), BLUE, 1.3, None),
        (offset_polyline(lac1, -0.2), BLUE, 1.3, None),
        (lac1, INK, 2.0, None)],
        "κ ∝ s^(α−1) · a smooth stem with two rails", key="2a")

    tip = lac1[-1]
    cone2 = plant.cone_terminal(tip, (lac1[-1][0] - lac1[-6][0], lac1[-1][1] - lac1[-6][1]), 0.2)
    p2b = panel("Fig. 2b", "LAC ribbon · with a cone ending", [
        (lac1, INK, 1.8, None), (cone2["left"], RED, 1.6, None),
        (cone2["right"], RED, 1.6, None)],
        "the stem ends in a cone, not a bare tip", key="2b")

    lac2 = lac_curve(0.5)
    p2c = panel("Fig. 2c", "LAC ribbon · a different α", [
        (offset_polyline(lac2, 0.2), BLUE, 1.3, None),
        (offset_polyline(lac2, -0.2), BLUE, 1.3, None),
        (lac2, INK, 2.0, None)],
        "α = 0.5 · same grammar, another curve", key="2c")

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
    # 4d — modulated width, drawn from its own width law
    mw_spine = width_cubic((0.0, 0.0), (3.2, 2.6), (6.8, -2.6), (10.0, 0.0), 240)
    mw_left, mw_right = width_rails(mw_spine, 0.6)
    p4d = panel("Fig. 4d", "modulated width · not an offset", [
        (mw_left, BLUE, 1.2, None), (mw_right, BLUE, 1.2, None),
        (mw_spine, INK, 1.8, None)],
        "w = w0(1 + 64a u^3 (1-u)^3) · rails not equidistant", key="4d")
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
                "x = cos t, y = sin t·cos t · a node at the origin", key="6a", curve="gerono")

    pir = [(math.cos(t) * (1 + math.sin(t)), math.sin(t) * (1 + math.sin(t)))
           for t in [-math.pi / 2 + i * (2 * math.pi) / 240 for i in range(241)]]
    p6b = panel("Fig. 6b", "piriform · quartic with a cusp", [(pir, INK, 1.8, None)],
                "r = 1 + sin t · one cusp, one loop", key="6b", curve="piriform")

    tri = [(math.cos(3 * t) * math.cos(t), math.cos(3 * t) * math.sin(t))
           for t in [i * 2 * math.pi / 480 for i in range(481)]]
    p6c = panel("Fig. 6c", "trifolium · three petals", [(tri, INK, 1.8, None)],
                "r = cos 3t · three-fold symmetry", key="6c", curve="trifolium")

    # ---- 7 · cusped and looped -------------------------------------------
    ast = [(math.cos(t) ** 3, math.sin(t) ** 3) for t in [i * 2 * math.pi / 240 for i in range(241)]]
    p7a = panel("Fig. 7a", "astroid · four cusps", [(ast, INK, 1.8, None)],
                "x = cos³t, y = sin³t · cusps on both axes", key="7a", curve="astroid")

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
                "r = 1 − cos t · exact and rational", key="8a", curve="cardioid")

    ros = []
    for t in [i * 2 * math.pi / 960 for i in range(961)]:
        r = 0.55 + 0.45 * math.cos(6 * t)
        ros.append((r * math.cos(t), r * math.sin(t)))
    p8b = panel("Fig. 8b", "rosette · six petals", [(ros, INK, 1.6, None)],
                "r = 0.55 + 0.45·cos 6t · the ending grammar's head", joins=True, key="8b")

    heart = [(math.sin(t) ** 3,
              (13 * math.cos(t) - 5 * math.cos(2 * t)
               - 2 * math.cos(3 * t) - math.cos(4 * t)) / 16)
             for t in [i * 2 * math.pi / 320 for i in range(321)]]
    p8c = panel("Fig. 8c", "heart · the non-rational one", [(heart, INK, 1.8, None)],
                "fitted only · no exact route", key="8c", curve="heart")

    stalk8 = [(0.0, 0.0), (0.04, 0.55), (0.0, 1.15)]
    blades8 = plant.seagrass((0.0, 1.15), (0.0, 1.0), 0.3)
    p8d = panel("Fig. 8d", "seagrass · the blade ending", [
        (stalk8, INK, 1.8, None)] + [(b, GREEN, 1.5, None) for b in blades8],
        "three tapered blades · no bare tip", key="8d")

    p8e = panel("Fig. 8e", "squircle · eight Eulers", [
        (pts, INK, 1.8, None) for pts in squircle_euler()],
        "eight 45° Euler spans · rotated into place", key="8e", composite=True)

    bicorn = named_curve("bicorn")
    p8f = panel("Fig. 8f", "bicorn · one quartic", [
        (b, INK, 1.8, None) for b in bicorn],
        "two halves joined at (±1, 0) · the node sits at (0, 1/3)", joins=True, key="8f",
        single_curve=True)

    bic_flower = []
    for k in range(4):
        a = k * math.pi / 2.0                     # 90° apart
        ca, sa = math.cos(a), math.sin(a)
        for branch in bicorn:
            moved = [(x, y - 1.0) for x, y in branch]   # top at the origin
            bic_flower.append([(ca * x - sa * y, sa * x + ca * y)
                               for x, y in moved])
    p8g = panel("Fig. 8g", "bicorn flower · four quartics", [
        (b, INK, 1.5, None) for b in bic_flower],
        "four bicorns, moved to the origin and turned 90° apart", joins=True, key="8g")

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

    hyp_r = [(math.cosh(t), math.sinh(t)) for t in [(-1.9 + 3.8 * i / 160) for i in range(161)]]
    hyp_l = [(-x, y) for x, y in hyp_r]
    p9d = panel("Fig. 9d", "hyperbola · two branches", [
        ([(x, x) for x in (-2.4, 2.4)], MUTED, 0.9, "4 3"),
        ([(x, -x) for x in (-2.4, 2.4)], MUTED, 0.9, "4 3"),
        (hyp_r, INK, 1.8, None), (hyp_l, INK, 1.8, None)],
        "x^2 - y^2 = 1 · rational points, fitted parallel", key="9d",
        single_curve=True)


    # ---- 10 · spirals -----------------------------------------------------
    spine = turn_polygon([1, 2, 2, 1, 1], 4, 3, chord=1.0)
    fine = []
    for a, b in zip(spine, spine[1:]):
        for k in range(6):
            t = k / 6.0
            fine.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
    fine.append(spine[-1])
    # the finest turn the 3125 ladder offers near 4.4°, not the 3-4-5's 36.87°
    fa, fb, fine_alpha = fine_triple()
    units = (1, 2, 2, 1, 1)
    counts = [max(1, round(u * math.asin(3 / 5) / fine_alpha)) for u in units]
    chord = 7.0 / sum(counts)                 # same total length as the 3-4-5 spine
    spine_fine = turn_polygon(counts, fa, fb, chord=chord)
    euler_ink, euler_poly = euler_curve(spine_fine)
    p10a = panel("Fig. 10a", "spine · a clean sweep", [
        (euler_ink, INK, 1.8, None), (euler_poly, MUTED, 0.7, "3 4")],
        f"{sum(counts)} chords of {math.degrees(fine_alpha):.2f}° "
        f"({fa}-{fb}-{int(math.hypot(fa, fb))}) · Euler polygon + Bézier chain",
        key="10a")

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
                "|x|⁴ + |y|⁴ = 1 · not rational, all offsets fitted", key="11c", curve="squircle")


    # ---- 12 · named rational ---------------------------------------------
    bean = []
    for i in range(361):
        t = i * 2 * math.pi / 360
        r = 1 + 0.5 * math.cos(t)
        bean.append((r * math.cos(t), r * math.sin(t)))
    p12a = panel("Fig. 12a", "bean · limaçon form", [(bean, INK, 1.8, None)],
                 "r = 1 + 0.5·cos t · rational, one dimple", key="12a", curve="bean")

    pear = []
    for i in range(361):
        t = i * 2 * math.pi / 360
        pear.append((0.8 * math.sin(t), math.cos(t) * (1 + 0.3 * math.sin(t))))
    p12b = panel("Fig. 12b", "pear · ovoid form", [(pear, INK, 1.8, None)],
                 "a stem body with a shoulder", key="12b", curve="pear")

    quad = []
    for i in range(721):
        t = i * 2 * math.pi / 720
        r = math.cos(2 * t)
        quad.append((r * math.cos(t), r * math.sin(t)))
    p12c = panel("Fig. 12c", "quadrifolium · four petals", [(quad, INK, 1.8, None)],
                 "r = cos 2t · exact, four-fold", key="12c", curve="quadrifolium")

    crux = []
    for i in range(721):
        t = i * 2 * math.pi / 720 + 1e-4
        r = 1 / math.sqrt(abs(math.cos(2 * t)) + 1e-4)
        if r > 2.4:
            continue
        crux.append((r * math.cos(t), r * math.sin(t)))
    p12d = panel("Fig. 12d", "cruciform · the cross", [(crux, INK, 1.4, None)],
                 "x²y² = x² − y² · four branches", key="12d", curve="cruciform")

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

    def offset_polyline(pts, d):
        out = []
        for i, q in enumerate(pts):
            a = pts[max(0, i - 1)]
            b = pts[min(len(pts) - 1, i + 1)]
            tx, ty = b[0] - a[0], b[1] - a[1]
            L = math.hypot(tx, ty) or 1
            out.append((q[0] - ty / L * d, q[1] + tx / L * d))
        return out

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

    stem14 = euler_chain([(0.028, 34.0, 0.0)])
    p14a = panel("Fig. 14a", "clothoid stem · with its offsets", [
        (offset_polyline(stem14, 0.34), BLUE, 1.4, None),
        (offset_polyline(stem14, -0.34), BLUE, 1.4, None),
        (stem14, INK, 2.0, None)],
        "κ ∝ s · smooth stem, two rails at ±d", key="14a")

    p14b = panel("Fig. 14b", "two clothoids · curvature matched", [
        (euler_chain([(0.05, 12.0, 0.0), (-0.05, 12.0, 0.6)]), INK, 1.8, None)],
        "κ continuous at the join · G2 by construction", joins=True, key="14b")

    p14c = panel("Fig. 14c", "five spans · an accelerating curl", [
        (euler_chain([(0.012, 6.0, 0.0), (0.012, 8.0, 0.072), (0.012, 10.0, 0.168),
                      (0.012, 12.0, 0.288), (0.012, 14.0, 0.432)]), INK, 1.8, None)],
        "each span starts at the last curvature · a smooth volute", joins=True, key="14c")


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
                 "α = 1 is exactly a circle — the member, not a failure", joins=True, key="15b")
    p15c = panel("Fig. 15c", "LAC · α = 1.7", [(lac_curve(1.7), INK, 1.8, None)],
                 "κ rises · the family bends toward a circle", joins=True, key="15c")


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
        "the polygon is 3° turns; the cusps survive", key="16a", single_curve=True)

    ideal_ast = [(math.cos(t) ** 3, math.sin(t) ** 3) for t in [i * 2 * math.pi / 360 for i in range(361)]]
    p16b = panel("Fig. 16b", "astroid · ideal and quantised", [
        (ideal_ast, MUTED, 1.2, None), (quantise(ideal_ast), INK, 1.7, None)],
        "four cusps · the quantisation follows them", key="16b", single_curve=True)

    ideal_tra = [(t - math.tanh(t), 1 / math.cosh(t)) for t in [(-3.0 + 6.0 * i / 360) for i in range(361)]]
    p16c = panel("Fig. 16c", "tractrix · ideal and quantised", [
        (ideal_tra, MUTED, 1.2, None), (quantise(ideal_tra), INK, 1.7, None)],
        "the cusp at the top is where the fit fails", key="16c", single_curve=True)

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
        dx, dy = stem[k + 1][0] - stem[k - 1][0], stem[k + 1][1] - stem[k - 1][1]
        n = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / n, dx / n                      # the curve's normal
        tx, ty = dx / n, dy / n                       # along the curve
        for sgn in (1.0, -1.0):                       # both rails
            base = (px + sgn * 0.02 * nx, py + sgn * 0.02 * ny)
            tip = (base[0] + sgn * 0.2 * nx, base[1] + sgn * 0.2 * ny)
            a = (base[0] + 0.06 * tx, base[1] + 0.06 * ty)
            b = (base[0] - 0.06 * tx, base[1] - 0.06 * ty)
            marks.append([a, tip, b, a])
    p18b = panel("Fig. 18b", "growth marks · pyramids at hits", [
        (stem, INK, 1.8, None)] + [(m, GOLD, 1.0, None) for m in marks],
        "one pyramid per rail, only at the marked stations", key="18b")

    br = plant.branch((0.0, 0.0), (1.0, 0.0), 1, 2.4)
    p18c = panel("Fig. 18c", "branch · lower bigger than upper", [
        ([(0.0, 0.0), (2.2, 0.0)], INK, 1.8, None), (br, GREEN, 1.6, None)],
        "a branch inherits the offset and ending rules", key="18c")

    # ---- 19 · 3-4-5 exact spine ------------------------------------------
    pkg = spine_layer.load()
    sa, sb, s_alpha = fine_triple()
    # the spiral package wants a <= b; its turn is atan2(a, b), the reverse of
    # turn_polygon's convention, so the pair is ordered here explicitly
    tri345 = pkg.Triple(min(sa, sb), max(sa, sb),
                        int(round(math.hypot(sa, sb))))
    # 20a on the same fine ladder: the 3-4-5 rungs scaled to ~4.4 degrees,
    # mirrored so the turns still cancel exactly
    sa, sb, s_alpha = fine_triple()
    pos = [max(1, round(u * math.asin(3 / 5) / s_alpha)) for u in (1, 2, 3, 4, 5)]
    schedule345 = pos + [-x for x in reversed(pos)]
    chain345 = pkg.Spiral(tri345, 1)
    chain345.extend(schedule345)
    assert chain345.coeff == 0 and chain345.heading.is_axis_aligned()
    nodes345, scale345 = chain345.integer_form()
    pts345 = chain345.floats()
    turn_sum = sum(chain345.turns)

    p19a = panel("Fig. 19a", "3-4-5 spiral · exact spine", [
        (pts345, INK, 2.0, None)],
        f"1+2+3+4+5-5-4-3-2-1 = {turn_sum} · {len(nodes345)} int nodes x5^15",
        dots=[(q, GOLD) for q in pts345], key="19a")

    cumulative = [0] + list(chain345.cumulative())
    p19b = panel("Fig. 19b", "closure · the turns cancel", [
        ([(float(i), float(c)) for i, c in enumerate(cumulative)], INK, 1.8, None)],
        f"sum = {turn_sum} · exit heading {chain345.heading.axis_name()}",
        dots=[((float(i), float(c)), GOLD) for i, c in enumerate(cumulative)], key="19b")

    alpha = tri345.radians
    tri_pts = [(0.0, 0.0), (float(tri345.b), 0.0),
               (float(tri345.b), float(tri345.a)), (0.0, 0.0)]
    arc = [(math.cos(alpha * i / 24), math.sin(alpha * i / 24)) for i in range(25)]
    p19c = panel("Fig. 19c", "the 3-4-5 rotation · no trigonometry", [
        (tri_pts, INK, 1.8, None), (arc, RED, 1.4, None)],
        "(4x-3y, 3x+4y)/5 · exact at every power", key="19c")

    # ---- 20 · terminals ---------------------------------------------------
    cap_curves = []
    for i, kind in enumerate(("butt", "point", "arc", "round")):
        x0 = i * 1.6
        cap_curves.append(([(x0, 0.2), (x0 + 1.0, 0.2)], MUTED, 1.1, None))
        cap_curves.append(([(x0, -0.2), (x0 + 1.0, -0.2)], MUTED, 1.1, None))
        shape = terminal_shape(kind, x0)
        if shape:
            cap_curves.append((shape, INK, 1.8, None))
    p20a = panel("Fig. 20a", "caps · butt, point, arc, round", cap_curves,
                 "left to right · a cap closes the section, it does not turn it",
                 key="20a")

    taper_curves = []
    for i, kind in enumerate(("taper", "bulb", "cone")):
        x0 = i * 1.9
        taper_curves.append(([(x0, 0.2), (x0 + 1.0, 0.2)], MUTED, 1.1, None))
        taper_curves.append(([(x0, -0.2), (x0 + 1.0, -0.2)], MUTED, 1.1, None))
        taper_curves.append((terminal_shape(kind, x0), INK, 1.8, None))
    p20b = panel("Fig. 20b", "tapers · taper, bulb, cone", taper_curves,
                 "left to right · the width laws from curve_lab/terminals.py",
                 key="20b")

    reach = [(float(i), term.terminal_extension(k, 1.0) / 0.5)
             for i, k in enumerate(("butt", "point", "arc", "round",
                                    "taper", "bulb", "cone"))]
    p20c = panel("Fig. 20c", "how far each end reaches", [
        (reach, BLUE, 1.8, None)],
        "extension / half-width · butt 0, the tapers 4", dots=[(q, GOLD) for q in reach],
        key="20c")

    # ---- 21 · fitted parallels -------------------------------------------
    src_span = {"p0": (0.0, 0.0), "c1": (1.2, 2.0),
                "c2": (2.6, 2.0), "p3": (3.8, 0.0)}
    src_pts = span_points(src_span, 160)
    true_off = offset_polyline(src_pts, 0.4)
    fit = fit_parallel([src_span], 0.4, tol=0.005)
    fit_pts = []
    for s in fit["spans"]:
        fit_pts.extend(span_points(s, 20))
    p21a = panel("Fig. 21a", "Levien fit · a fitted parallel", [
        (src_pts, INK, 1.8, None), (true_off, MUTED, 1.0, "4 3"),
        (fit_pts, BLUE, 1.6, None)],
        f"max error {fit['error_max']:.1e} · fitted, never exact", key="21a")

    big = fit_parallel([src_span], 1.4, tol=0.005)
    big_pts = []
    for s in big["spans"]:
        big_pts.extend(span_points(s, 20))
    p21b = panel("Fig. 21b", "a larger offset · cusp report", [
        (src_pts, INK, 1.8, None), (offset_polyline(src_pts, 1.4), MUTED, 1.0, "4 3"),
        (big_pts, RED, 1.5, None)],
        f"d = 1.4 · {len(big['cusps'])} cusp interval(s) flagged", key="21b")

    tols = [0.2, 0.1, 0.05, 0.02, 0.01, 0.005, 0.002, 0.001]
    grid = []
    for t in tols:
        f = fit_parallel([src_span], 0.4, tol=t)
        grid.append((math.log10(t), math.log10(max(f["error_max"], 1e-12))))
    ref = [(math.log10(tols[-1]), math.log10(tols[-1])),
           (math.log10(tols[0]), math.log10(tols[0]))]
    p21c = panel("Fig. 21c", "the fit buys error with spans", [
        (ref, MUTED, 0.9, "4 3"), (grid, BLUE, 1.6, None)],
        "log10 error against log10 tolerance", dots=[(q, GOLD) for q in grid],
        key="21c")

    # These five panels move to the notes page: it is the page that explains,
    # and the notes page can carry an illustration without a catalogue id.
    def _svg_body(anchor):
        import re as _re
        return _re.search(r"<svg\b.*?</svg>", anchor, _re.S).group(0)

    circle_pts = [(math.cos(t), math.sin(t))
                  for t in (2 * math.pi * i / 240 for i in range(241))]
    MOVED_TO_NOTES = {
        "19a": _svg_body(p19a), "19b": _svg_body(p19b),
        "19c": _svg_body(p19c), "20c": _svg_body(p20c),
        "21c": _svg_body(p21c),
        "elastica-setup": panel(
            "Fig. E*", "elastica · m = 1.2, correctly started at the inflection",
            [([(x, y) for x, y in __import__("missing_families").elastica(1.2)],
              INK, 1.6, None)],
            "κ starts at 0, not at m · this is a shallow wave, not a circle",
            single_curve=False),
        "quintic-hermite-setup": panel(
            "Fig. H*", "quintic Hermite · the G2 S",
            [([(x, y) for x, y in __import__("missing_families").quintic_hermite(
                (0.0, 0.0), (2.0, 1.0), (2.0, 1.2), (1.2, -2.0),
                (0.0, 3.0), (-2.0, 0.0))], INK, 1.6, None)],
            "p, p′, p″ at both ends · four spans make the S",
            single_curve=False),
        "sin-circle": panel("Fig. n=1", "sinusoidal · n = 1 · the circle",
                            [(circle_pts, INK, 1.6, None)],
                            "r = cos θ · the definition, not an example",
                            single_curve=False),
    }

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
    rstep = nice_step(max(RW, RH))
    for gx in range(0, int(RW) + 1, int(rstep)):
        ray_svg.append(f'<line x1="{gx}" y1="0" x2="{gx}" y2="{RH}" stroke="{RULE}"/>')
    for gy in range(0, int(RH) + 1, int(rstep)):
        ray_svg.append(f'<line x1="0" y1="{gy}" x2="{RW}" y2="{gy}" stroke="{RULE}"/>')
    ray_hits = []
    for p0, p1 in rays:
        for axis, level in (("x", None), ("y", None)):
            lo = min(p0[0], p1[0]) if axis == "x" else min(p0[1], p1[1])
            hi = max(p0[0], p1[0]) if axis == "x" else max(p0[1], p1[1])
            g = math.ceil(lo / rstep) * rstep
            while g <= hi + 1e-9:
                a0, a1 = (p0[0], p1[0]) if axis == "x" else (p0[1], p1[1])
                t = (g - a0) / ((a1 - a0) or 1e-9)
                if 0.0 <= t <= 1.0:
                    q = ((g, p0[1] + t * (p1[1] - p0[1])) if axis == "x"
                         else (p0[0] + t * (p1[0] - p0[0]), g))
                    ray_hits.append(q)
                g += rstep
    if len(ray_hits) > 26:
        stride = len(ray_hits) / 26
        ray_hits = [ray_hits[int(i * stride)] for i in range(26)]
    for hx, hy in ray_hits:
        ray_svg.append(f'<circle class="lattice" cx="{hx:.1f}" cy="{hy:.1f}" '
                       f'r="2.2" fill="{MARK}"/>')
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

    def row(a, b="", c=""):
        return f'<div class="row">{a}{b}{c}</div>'

    def catalogue_rows(panels, rule=None, single=None, force=frozenset()):
        chunks = [panels[i:i + 3] for i in range(0, len(panels), 3)]
        return "".join(
            '<div class="row">' + "".join(
                panel(p["fig"], p["title"], p["curves"], p["note"],
                      dots=p["dots"], key=p["key"], curve=p["curve"],
                      rule=rule,
                      single_curve=(True if p["key"] in force else single))
                for p in chunk) + "</div>"
            for chunk in chunks)

    catalogue_html = ""
    for i, (_key, title, blurb, panels) in enumerate(FAMILIES):
        if _key == "clouds":          # lives on showcase-effects.html, as 34
            continue
        catalogue_html += (
            f'<div class="fam"><h2>{24 + i} · {title}</h2><p>{blurb}</p></div>'
            + catalogue_rows(panels, rule=FAMILY_RULE.get(_key),
                             single=(True if _key in SINGLE_FAMILIES else None),
                             force=FORCE_COMPANIONS))

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
.also{{max-width:940px;font:13px/1.6 ui-monospace,Menlo,monospace;color:var(--muted);margin:0 0 20px;padding:10px 14px;border-left:3px solid var(--rule)}}
.also a{{color:{GOLD};font-weight:600;text-decoration:none}}
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
.capmarks{{display:inline-flex;gap:8px;align-items:center;font:12px/1.4 ui-monospace,Menlo,monospace;color:#7b6c4e;margin:0 0 18px}}
</style></head><body><main>
<p class="eyebrow">curve-lab · the whole catalogue on one page</p>
<h1>Rays and curves</h1>
<p class="lede">Every family this project has built, in the order it was solved: the integer Euler polygon first, then the LACs, the integer chains, the widths, the composition — and the rays last, where they belong on a monstrance. Panels are lettered <code>a, b, c, d</code> inside each numbered figure, and <strong>every figure is a link to its notes</strong>.</p>
<p class="also"><a href="showcase-notes.html">The notes →</a> one section per figure, plus the explanations that belong in prose — including the 3-4-5 spine and the two charts that used to sit here. <a href="showcase-effects.html">Cloud effects →</a> the veil and its six billow layers, on their own page.</p>

<label class="capmarks"><input type="checkbox" id="capmarks">
 limit hits to 24 per figure</label>
<script>
(() => {{
  const box = document.getElementById("capmarks");
  const apply = () => {{
    document.querySelectorAll("svg").forEach((sv) => {{
      sv.querySelectorAll("circle.lattice").forEach((c, i) => {{
        c.style.display = box.checked && i >= 24 ? "none" : "";
      }});
    }});
  }};
  box.addEventListener("change", apply);
  apply();
}})();
</script>


<p class="key"><strong>Key.</strong> <span class="sw ink"></span> exact construction · <span class="sw blue"></span> exact rail · <span class="sw gold"></span> integer or fitted mark · <span class="sw red"></span> approximate or exceptional. <strong>Kind</strong> (on each note): <em>exact</em>, <em>fitted</em>, <em>negative</em>, <em>asymptotic</em>, <em>drawn form</em>.</p>

<div class="fam"><h2>0 · Exact parallels and complementary side curves</h2><p>the two curves whose parallels stay in the family — and how the involute makes one</p></div>
{row(p0a, p0b, p0c)}

<div class="fam"><h2>1 · Integer spine</h2><p>integer points, joined by ink · cut or branch at any node</p></div>
{row(p1a, p1b, p1c)}

<div class="fam"><h2>2 · LAC spines</h2><p>31 recovered spines; the turn schedule is the curve</p></div>
{row(p2a, p2b, p2c)}

<div class="fam"><h2>3 · Integer Bézier · Euclid family chains</h2><p>integer control points at scale 1 · C1 exact · exponent −4/3 in the limit</p></div>
{row(p3a, p3b, p3c)}

<div class="fam"><h2>4 · Widths</h2><p>one exact taper, two constructions that are provably not what they look like, and one width that is declared not an offset</p></div>
{row(p4a, p4b, p4c)}{row(p4d)}

<div class="fam"><h2>5 · Composition</h2><p>parts on different grids, a declared step, and an ending</p></div>
{row(p5a, p5b, p5c)}


<div class="fam"><h2>6 · Higher order</h2><p>quartics and a sextic · nodes and cusps are what make them exact</p></div>
{row(p6a, p6b, p6c)}

<div class="fam"><h2>7 · Cusped and looped</h2><p>the cusp is the exactness; it is also why the clothoid cannot follow them</p></div>
{row(p7a, p7b, p7c)}

<div class="fam"><h2>8 · Flowers and endings</h2><p>the heads a stalk ends in · one of them is not rational at all</p></div>
{row(p8a, p8b, p8c)}{row(p8d, p8e, p8f)}{row(p8g)}

<div class="fam"><h2>9 · Conics and the clothoid</h2><p>integer points on the curve, fitted parallels, and the one linear-curvature curve</p></div>
{row(p9a, p9b, p9c)}{row(p9d)}


<div class="fam"><h2>10 · Spirals</h2><p>the plan, the self-similar curve, and the one whose offsets stay in the family</p></div>
{row(p10a, p10b, p10c)}

<div class="fam"><h2>11 · Classical gauges</h2><p>two solved by hand and one that refuses: catenary, tractrix, squircle</p></div>
{row(p11a, p11b, p11c)}


<div class="fam"><h2>12 · Named rational</h2><p>the rest of the named table: bean, pear, quadrifolium, cruciform</p></div>
{row(p12a, p12b, p12c)}{row(p12d)}

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


<div class="fam"><h2>20 · Terminals</h2><p>how a stroke ends, computed: caps, tapers, and how far each one reaches</p></div>
{row(p20a, p20b)}

<div class="fam"><h2>21 · Fitted parallels</h2><p>Levien's cubic-Bézier fit: the honest approximate rail, with its error and its cusps</p></div>
{row(p21a, p21b)}

{catalogue_html}

<div class="fam"><h2>Rays</h2><p>unnumbered · the p-triple angles themselves, mirrored about the axis</p></div>
{ray_html}

</main></body></html>
"""

    # move the important families to the top, then renumber every figure
    def move(marker, before):
        nonlocal html
        i = html.index(marker)
        j = html.index('<div class="fam">', i + 10)
        block = html[i:j]
        html = html[:i] + html[j:]
        k = html.index(before)
        return html[:k] + block + html[k:]

    html = move('<div class="fam"><h2>14 · Smooth Euler chains</h2>',
                '<div class="fam"><h2>1 · Integer spine</h2>')
    html = move('<div class="fam"><h2>15 · Smooth LACs</h2>',
                '<div class="fam"><h2>3 · Integer Bézier')
    html = move('<div class="fam"><h2>5 · Composition</h2>',
                '<div class="fam"><h2>Rays</h2>')
    html = move('<div class="fam"><h2>38 · Primal · 4</h2>',
                '<div class="fam"><h2>Rays</h2>')

    order = [int(n) for n in __import__("re").findall(r'<div class="fam"><h2>(\d+) ·', html)]
    mapping = {old: i + 1 for i, old in enumerate(order)}
    html = __import__("re").sub(r'<h2>(\d+) ·',
                                lambda m: f"<h2>{mapping.get(int(m.group(1)), int(m.group(1)))} ·", html)
    # headings are renumbered by document order: two families once shared a
    # number after the clouds moved, and a dict keyed by the old number cannot
    # separate them.
    import itertools
    seq = itertools.count(1)
    html = __import__("re").sub(r'<h2>(\d+) ·',
                                lambda m: f"<h2>{next(seq)} ·", html)
    html = __import__("re").sub(r'Fig\. (\d+)',
                                lambda m: f"Fig. {mapping.get(int(m.group(1)), int(m.group(1)))}", html)

    out = ROOT / "workbench" / "showcase.html"
    out.write_text(html, encoding="utf-8")
    print(out)

    from showcase_notes import build as build_notes
    # every figure carries its own SVG into its note, so it can be copied
    # straight into Inkscape or Glyphs
    import re as _re
    page_figures = {}
    for _m in _re.finditer(r'<a class="fig" id="fig-([0-9a-zA-Z]+)"[^>]*>(.*?)</a>',
                           html, _re.S):
        _svg = _re.search(r"<svg\b.*?</svg>", _m.group(2), _re.S)
        if _svg:
            page_figures[_m.group(1)] = _svg.group(0)
    figures = dict(page_figures)
    figures.update(MOVED_TO_NOTES)
    print(build_notes(mapping, figures=figures))


if __name__ == "__main__":
    run()
