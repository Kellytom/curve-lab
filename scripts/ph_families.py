"""The PH family gallery: degree ladder, integer hits, sliders, PHH/PPH.

    .venv/bin/python scripts/ph_families.py
    open workbench/ph-families.html

Every PH curve is z'(t) = h (u² − v², 2uv), with
n = deg h + 2 max(deg u, deg v) + 1.  The page carries:

* the definitions (PH, PHH, PPH) in one place, 2D only;
* the occurrence audit for the word "PH" in the prose;
* every rung of the ladder, n = 3 … 8 plus the rational rung, each with more
  than one example and all four quadrants;
* the integer lattice hits and the scale that clears them, in Fraction;
* the interactive explainer (generators, grid m, quadrants, offset, break PH);
* the PHH and PPH constructions from `curve_lab/ph_hermite.py`;
* the not-built list.

Two outputs, both generated: `workbench/ph-families.html` and the app script it
loads, `workbench/ph-families-app.js` (source: `scripts/ph_families_app.js`).
"""

from __future__ import annotations

import json
import math
import sys
from fractions import Fraction
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import generators as G  # noqa: E402
import g3_showcase as S  # noqa: E402
import missing_families as MF  # noqa: E402

from curve_lab import ph_hermite as PH  # noqa: E402
from curve_lab.parallel_bezier import fit_chain  # noqa: E402

M = 4          # the grid the printed hit tables use
ALPHA_NODE = (6.0, 0.0)

# --------------------------------------------------------------------------
# the rungs: (key, title, h, u, v, note)
# --------------------------------------------------------------------------
EXAMPLES = [
    ("alpha", "n = 3 · the full nodal Tschirnhausen alpha", (1,), (1, 1), (1, -1),
     "The whole alpha, not a segment. The node sits at t = ±√3 and the two "
     "endings run to the right. Up to similarity this is every cubic PH curve. "
     "The heavy gold arc is the C-segment t ∈ [−1, 1] that `hodograph.py` draws."),
    ("cubic-b", "n = 3 · a second cubic (same shape)", (1,), (2, -2), (1, -2),
     "A different generator pair, a scaled and rotated copy of the same "
     "Tschirnhausen curve: the cubic rung has one shape, not a family."),
    ("quartic-a", "n = 4 · PH quartic", (1, 2), (1, -1), (1, -2),
     "The even degree needs deg h = 1. It inflects, which the cubic cannot."),
    ("quartic-b", "n = 4 · a second quartic", (2, 1), (1, 2), (2, -1),
     "Another h, another shape: the quartic rung is a family, not one curve."),
    ("quintic-a", "n = 5 · PH quintic, u, v quadratic", (1,), (1, 2, 1), (1, -1, 1),
     "The workhorse: C and S shapes, one-segment Hermite interpolation, the "
     "lowest degree that carries a C² spline."),
    ("quintic-b", "n = 5 · PH quintic, h quadratic", (1, 1, 1), (2, 1), (1, -1),
     "A quintic reached the other way: 2 + 2·1 + 1 = 5. Same degree, different "
     "generator split, different shape."),
    ("quintic-c", "n = 5 · PH quintic, u = 1+t², v = 2t", (1,), (1, 0, 1), (0, 2),
     "A symmetric member: u − v = (1−t)² and u + v = (1+t)², so both ends meet "
     "the same side."),
    ("sextic", "n = 6 · PH sextic", (1, 2), (-1, 1, 0), (2, -1, 0),
     "Even degree from h linear with quadratic generators: the multiple-cusp "
     "shapes live here."),
    ("sextic-b", "n = 6 · a second sextic", (1, 1), (1, 1, 1), (1, -2, 1),
     "A second h and generator pair at n = 6; one card is not the family."),
    ("septic", "n = 7 · PH septic", (1,), (1, 2, 1, 1), (1, -1, 1, 0),
     "h = 1 with cubic generators: 0 + 6 + 1 = 7."),
    ("septic-b", "n = 7 · a second septic", (1,), (1, 0, 1, 1), (2, 1, 0, 1),
     "A second cubic generator pair at n = 7: the odd rung is a family too."),
    ("octic", "n = 8 · PH octic", (1, 2), (1, 2, 1, 0), (1, -1, 1, 1),
     "The n = 8 rung: deg h = 1 with cubic generators, 1 + 6 + 1 = 8. The "
     "general n = 8+ ladder is not enumerated; this is one member."),
    ("octic-b", "n = 8 · a second octic", (1, 1), (1, 1, 0, 1), (2, -1, 1, 0),
     "A second h and generator pair at n = 8; the ladder stops being a single "
     "example as soon as one more h is chosen."),
]


def arc_of(h, u, v):
    """Exact arc length over [0, 1]: the integral of σ = h (u² + v²)."""
    uu = G.mul(list(u), list(u))
    vv = G.mul(list(v), list(v))
    width = max(len(uu), len(vv))
    sig = [a + b for a, b in zip(uu + [0] * (width - len(uu)),
                                vv + [0] * (width - len(vv)))]
    return sum((Fraction(c, k + 1) for k, c in enumerate(G.mul(list(h), sig))),
               Fraction(0))


def hit_table(pc, m=M):
    scale = pc.scale(m)
    return {"scale": scale,
            "control": pc.integer_control(scale),
            "hits": pc.integer_milestones(m, scale),
            "m": m}


ALPHA_NODE_T = math.sqrt(3.0)


def integer_points(pc, t0, t1, qmax=60):
    """Every point of the curve that is integral in model coordinates, found by
    evaluating the exact polynomials at t = p/q with q <= qmax."""
    found = {}
    lo, hi = Fraction(t0), Fraction(t1)
    for q in range(1, qmax + 1):
        p_lo = math.floor(lo * q)
        p_hi = math.ceil(hi * q)
        for p in range(p_lo, p_hi + 1):
            t = Fraction(p, q)
            if not (lo <= t <= hi):
                continue
            x, y = G.at(pc.x, t), G.at(pc.y, t)
            if x.denominator == 1 and y.denominator == 1:
                found.setdefault((int(x), int(y)), t)
    return found


def alpha_family(kmax=4):
    """18y² = x(x−6)²: the complete set of integer points.

    x = 2t² and y = t(6−x)/3.  If x ≠ 6 then t = 3y/(6−x) is rational; writing
    t = a/b in lowest terms, x = 2a²/b² integral forces b = 1, so t is an
    integer, and 3 | t follows from y.  Hence every integer point off the node
    is (18k², ±6k(3k²−1)); the node (6, 0) sits at t = ±√3.
    """
    out = [(6, 0, "node, t = ±√3")]
    for k in range(0, kmax + 1):
        x = 18 * k * k
        y = 6 * k * (3 * k * k - 1)
        if k == 0:
            out.append((x, y, "t = 0"))
        else:
            out.append((x, y, f"t = {3 * k}"))
            out.append((x, -y, f"t = −{3 * k}"))
    return out


def build_example(key, title, h, u, v):
    n = len(h) - 1 + 2 * (max(len(u), len(v)) - 1) + 1
    pc = G.PHCurve(n, u=u, v=v, h=h)
    if key == "alpha":
        pts = [pc.bezier(i / 60) for i in range(-240, 241)]
        seg = [pc.bezier(i / 60) for i in range(-60, 61)]
    else:
        pts = [pc.bezier(i / 160) for i in range(161)]
        seg = None
    t0, t1 = (-4.0, 4.0) if key == "alpha" else (0.0, 1.0)
    hits = integer_points(pc, t0, t1)
    miles = []
    for k in range(M + 1):
        x, y = G.at(pc.x, Fraction(k, M)), G.at(pc.y, Fraction(k, M))
        if (x.denominator != 1 or y.denominator != 1):
            miles.append((float(x), float(y)))
    if key == "alpha":
        hits[(6, 0)] = "irrational t"
    return {"key": key, "title": title, "pc": pc, "pts": pts, "seg": seg,
            "table": hit_table(pc), "arc": arc_of(h, u, v),
            "hits": hits, "miles": miles, "t0": t0, "t1": t1,
            "h": h, "u": u, "v": v}


# --------------------------------------------------------------------------
# interpolation: exact cubic spans and fitted rails
# --------------------------------------------------------------------------
# The alpha as one cubic Bezier: z(t) = (2t², 2t − 2t³/3), control points exact.
ALPHA_CP = ((F(0), F(0)), (F(0), F(2, 3)), (F(2, 3), F(4, 3)), (F(2), F(4, 3)))
BAND = ("#2e2413", "#a23b2a", "#1f5fa8", "#8c6a21", "#4a7c59", "#7b4a9e")


def alpha_at(t):
    u = 1 - t
    return (sum(F(math.comb(3, i)) * u ** (3 - i) * t ** i * ALPHA_CP[i][0]
                for i in range(4)),
            sum(F(math.comb(3, i)) * u ** (3 - i) * t ** i * ALPHA_CP[i][1]
                for i in range(4)))


def split_cubic(cp, t):
    """de Casteljau at t; exact in Fraction, valid for t outside [0, 1] too."""
    pts = [tuple(p) for p in cp]
    levels = [pts]
    while len(pts) > 1:
        pts = [((1 - t) * a[0] + t * b[0], (1 - t) * a[1] + t * b[1])
               for a, b in zip(pts, pts[1:])]
        levels.append(pts)
    left = [level[0] for level in levels]
    right = [level[-1] for level in levels][::-1]
    return left, right


def alpha_segment(a, b):
    """Exact control points of z on [a, b] (a, b may be any rationals)."""
    A, B = F(a), F(b)
    c = B - A
    coords = []
    for coord in (0, 1):
        power = [F(0)] * 4
        for i in range(4):
            bi = ALPHA_CP[i][coord]
            for k in range(4 - i):
                power[i + k] += bi * math.comb(3, i) * math.comb(3 - i, k) * (-1) ** k
        q = [F(0)] * 4
        for m in range(4):
            for j in range(m + 1):
                q[j] += power[m] * math.comb(m, j) * A ** (m - j) * c ** j
        coords.append([sum(q[j] * F(math.comb(i, j), math.comb(3, j))
                             for j in range(i + 1)) for i in range(4)])
    return list(zip(coords[0], coords[1]))


def _float_cp(cp):
    return [(float(x), float(y)) for x, y in cp]


def _fmt_q(v):
    v = F(v)
    return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"


def span_figure(bands, title, sub, legend, w=560, h=380, context=None):
    """Alternating two-colour cubic spans, every join labelled with exact x, y."""
    SPAN = (S.INK, S.BLUE)          # two colours only: neighbours always differ
    allp = [p for _, cp in bands for p in _float_cp(cp)]
    xs = [p[0] for p in allp]
    ys = [p[1] for p in allp]
    pad = 0.10 * max(max(xs) - min(xs), max(ys) - min(ys), 1e-9)
    f = S.Frame(w, h, min(xs) - pad, max(xs) + pad,
                min(ys) - pad, max(ys) + pad, pad=46)
    step = S._nice_step(max(xs) - min(xs))
    grid = []
    g = math.floor((min(xs) - pad) / step) * step
    while g <= max(xs) + pad:
        a, b = f((g, min(ys) - pad)), f((g, max(ys) + pad))
        grid.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
                    f'y2="{b[1]:.1f}" stroke="{S.RULE}" stroke-width="0.6"/>')
        g += step
    g = math.floor((min(ys) - pad) / step) * step
    while g <= max(ys) + pad:
        a, b = f((min(xs) - pad, g)), f((max(xs) + pad, g))
        grid.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
                    f'y2="{b[1]:.1f}" stroke="{S.RULE}" stroke-width="0.6"/>')
        g += step

    paths, labels = [], []
    if context:
        cpts = [S.bezier(context, i / 60) for i in range(61)]
        paths.append(f'<path d="{S._path(cpts, f)}" fill="none" '
                     f'stroke="{S.RULE}" stroke-width="1.4"/>')
    for k, (t_range, cp) in enumerate(bands):
        pts = [S.bezier(_float_cp(cp), i / 40) for i in range(41)]
        paths.append(f'<path d="{S._path(pts, f)}" fill="none" '
                     f'stroke="{SPAN[k % 2]}" stroke-width="3"/>')
        mid = S.bezier(_float_cp(cp), 0.5)
        mx, my = f(mid)
        labels.append(f'<text x="{mx:.1f}" y="{my - 8:.1f}" text-anchor="middle" '
                      f'font-family="ui-monospace,Menlo,monospace" font-size="10" '
                      f'font-weight="700" fill="{SPAN[k % 2]}" '
                      f'paint-order="stroke" stroke="{S.PAPER}" stroke-width="3">'
                      f'{k + 1}</text>')

    # every join, exactly, once: the seven endpoints of the six spans
    joins = []
    for _, cp in bands:
        for p in (cp[0], cp[-1]):
            if not joins or joins[-1] != p:
                joins.append(p)
    for (xq, yq) in joins:
        x, y = float(xq), float(yq)
        px, py = f((x, y))
        integer = F(xq).denominator == 1 and F(yq).denominator == 1
        if integer:
            paths.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.4" '
                         f'fill="{S.RED}"/>')
        else:
            paths.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.0" '
                         f'fill="{S.PAPER}" stroke="{S.RED}" stroke-width="1.4"/>')
        dy = -7 if y > 0 else (12 if y < 0 else 4)
        labels.append(
            f'<text x="{px + 6:.1f}" y="{py + dy:.1f}" '
            f'font-family="ui-monospace,Menlo,monospace" font-size="9.4" '
            f'fill="{S.RED}" paint-order="stroke" stroke="{S.PAPER}" '
            f'stroke-width="3">({_fmt_q(xq)}, {_fmt_q(yq)})</text>')

    a0 = f((min(xs) - pad, 0.0)) if min(ys) - pad <= 0 <= max(ys) + pad else None
    axes = ""
    if a0:
        a1 = f((max(xs) + pad, 0.0))
        axes += (f'<line x1="{a0[0]:.1f}" y1="{a0[1]:.1f}" x2="{a1[0]:.1f}" '
                 f'y2="{a1[1]:.1f}" stroke="{S.MUTED}" stroke-width="0.9" '
                 f'stroke-dasharray="4 3"/>')
    return f"""<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="{title}">
  <rect width="{w}" height="{h}" fill="{S.PAPER}"/>
  {''.join(grid)}
  {axes}
  {''.join(paths)}
  {''.join(labels)}
  <text x="10" y="17" font-family="ui-sans-serif,system-ui,sans-serif" font-size="12" font-weight="600" fill="{S.INK}">{title}</text>
  <text x="10" y="31" font-family="ui-monospace,Menlo,monospace" font-size="9" fill="{S.MUTED}">{sub}</text>
  <text x="10" y="{h - 18}" font-family="ui-sans-serif,system-ui,sans-serif" font-size="9" fill="{S.MUTED}">{legend}</text>
</svg>"""


def rails_figure(cp, distance, title, sub, legend, w=520, h=360):
    """Source cubic with its two fitted (Levien) rails at ±distance."""
    src = [{"p0": (float(cp[0][0]), float(cp[0][1])),
            "c1": (float(cp[1][0]), float(cp[1][1])),
            "c2": (float(cp[2][0]), float(cp[2][1])),
            "p3": (float(cp[3][0]), float(cp[3][1]))}]
    out = []
    for d in (distance, -distance):
        r = fit_chain([dict(s) for s in src], d)
        out.append(r)
    spans_source = [[(float(x), float(y)) for x, y in cp]]
    src_pts = [S.bezier(spans_source[0], i / 120) for i in range(121)]
    rail_pts = []
    for r in out:
        for sp in r["spans"]:
            P = [sp["p0"], sp["c1"], sp["c2"], sp["p3"]]
            rail_pts.append([S.bezier(P, i / 24) for i in range(25)])
    allp = src_pts + [p for r in rail_pts for p in r]
    xs = [p[0] for p in allp]
    ys = [p[1] for p in allp]
    pad = 0.12 * max(max(xs) - min(xs), max(ys) - min(ys))
    f = S.Frame(w, h, min(xs) - pad, max(xs) + pad, min(ys) - pad, max(ys) + pad, pad=44)
    step = S._nice_step(max(xs) - min(xs))
    grid = []
    g = math.floor((min(xs) - pad) / step) * step
    while g <= max(xs) + pad:
        a, b = f((g, min(ys) - pad)), f((g, max(ys) + pad))
        grid.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
                    f'y2="{b[1]:.1f}" stroke="{S.RULE}" stroke-width="0.6"/>')
        g += step
    g = math.floor((min(ys) - pad) / step) * step
    while g <= max(ys) + pad:
        a, b = f((min(xs) - pad, g)), f((max(xs) + pad, g))
        grid.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
                    f'y2="{b[1]:.1f}" stroke="{S.RULE}" stroke-width="0.6"/>')
        g += step
    paths = [f'<path d="{S._path(src_pts, f)}" fill="none" stroke="{S.INK}" '
             f'stroke-width="2.4"/>']
    for k, r in enumerate(rail_pts):
        col = S.GOLD if k == 0 else S.BLUE
        paths.append(f'<path d="{S._path(r, f)}" fill="none" stroke="{col}" '
                     f'stroke-width="1.8" stroke-dasharray="6 4"/>')
    span_count = sum(len(r["spans"]) for r in out)
    err = max(r["error_max"] for r in out)
    return f"""<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="{title}">
  <rect width="{w}" height="{h}" fill="{S.PAPER}"/>
  {''.join(grid)}
  {''.join(paths)}
  <text x="10" y="17" font-family="ui-sans-serif,system-ui,sans-serif" font-size="12" font-weight="600" fill="{S.INK}">{title}</text>
  <text x="10" y="31" font-family="ui-monospace,Menlo,monospace" font-size="9" fill="{S.MUTED}">{sub}</text>
  <text x="10" y="{h - 18}" font-family="ui-sans-serif,system-ui,sans-serif" font-size="9" fill="{S.MUTED}">{legend} · {span_count} fitted spans both sides · max error {err:.2e}</text>
</svg>"""


# --------------------------------------------------------------------------
# figures
# --------------------------------------------------------------------------
def mirrored(pts, sx, sy):
    return [(sx * x, sy * y) for x, y in pts]


def figure(pts, title, sub, seg=None, node=None, w=430, h=330, legend=None,
           hits=None, milestones=None):
    """Title, axes with labels, the four mirrors, integer points, segment."""
    quad = [mirrored(pts, sx, sy) for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1))]
    allp = [p for q in quad for p in q]
    xs = [p[0] for p in allp]
    ys = [p[1] for p in allp]
    pad = 0.10 * max(max(xs) - min(xs), max(ys) - min(ys), 1e-9)
    x0, x1 = min(xs) - pad, max(xs) + pad
    y0, y1 = min(ys) - pad, max(ys) + pad
    f = S.Frame(w, h, x0, x1, y0, y1, pad=44)
    step = S._nice_step(max(x1 - x0, y1 - y0))
    grid = []
    gx = math.floor(x0 / step) * step
    while gx <= x1:
        a, b = f((gx, y0)), f((gx, y1))
        grid.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
                    f'y2="{b[1]:.1f}" stroke="{S.RULE}" stroke-width="0.6"/>')
        gx += step
    gy = math.floor(y0 / step) * step
    while gy <= y1:
        a, b = f((x0, gy)), f((x1, gy))
        grid.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
                    f'y2="{b[1]:.1f}" stroke="{S.RULE}" stroke-width="0.6"/>')
        gy += step

    # the axes, labelled at their ends
    marks = []
    ym = 0.0 if y0 <= 0.0 <= y1 else y0
    a, _ = f((x0, ym)), None
    b = f((x1, ym))
    marks.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
                 f'y2="{b[1]:.1f}" stroke="{S.BLUE}" stroke-width="0.9"/>')
    marks.append(f'<text x="{b[0] - 8:.1f}" y="{b[1] - 4:.1f}" font-size="9.5" '
                 f'fill="{S.BLUE}">x</text>')
    xm = 0.0 if x0 <= 0.0 <= x1 else x0
    c = f((xm, y0))
    d = f((xm, y1))
    marks.append(f'<line x1="{c[0]:.1f}" y1="{c[1]:.1f}" x2="{d[0]:.1f}" '
                 f'y2="{d[1]:.1f}" stroke="{S.BLUE}" stroke-width="0.9"/>')
    marks.append(f'<text x="{d[0] + 4:.1f}" y="{d[1] + 8:.1f}" font-size="9.5" '
                 f'fill="{S.BLUE}">y</text>')

    paths = []
    for i, q in enumerate(quad):
        fade = 1.0 if i == 0 else 0.4
        paths.append(f'<path d="{S._path(q, f)}" fill="none" stroke="{S.INK}" '
                     f'stroke-width="{2.2 if i == 0 else 1.1}" opacity="{fade}"/>')
    if seg:
        paths.append(f'<path d="{S._path(seg, f)}" fill="none" '
                     f'stroke="{S.GOLD}" stroke-width="3.6"/>')
    if milestones:
        for (mx, my) in milestones:
            for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
                px, py = f((sx * mx, sy * my))
                paths.append(f'<rect x="{px - 2.6:.1f}" y="{py - 2.6:.1f}" '
                             f'width="5.2" height="5.2" fill="none" '
                             f'stroke="{S.BLUE}" stroke-width="1.2"/>')
    if hits:
        for (hx, hy) in hits:
            for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
                px, py = f((sx * hx, sy * hy))
                paths.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.2" '
                             f'fill="{S.RED}"/>')
            px, py = f((hx, hy))
            paths.append(f'<text x="{px + 5:.1f}" y="{py - 5:.1f}" '
                         f'font-family="ui-monospace,Menlo,monospace" '
                         f'font-size="8.4" fill="{S.RED}">({hx},{hy})</text>')
    if node:
        nx, ny = f(node)
        paths.append(f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="3.8" fill="none" '
                     f'stroke="{S.RED}" stroke-width="1.7"/>')

    legend = legend or ("black: source PH · grey: mirrors · filled red: integer "
                        "point in model coords (labelled, Q I) · hollow blue: "
                        "integer only after ×scale (t = k/m) · red ring: node")
    return f"""<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="{title}">
  <rect width="{w}" height="{h}" fill="{S.PAPER}"/>
  {''.join(grid)}
  {''.join(marks)}
  {''.join(paths)}
  <text x="10" y="16" font-family="ui-sans-serif,system-ui,sans-serif" font-size="11.5" font-weight="600" fill="{S.INK}">{title}</text>
  <text x="10" y="29" font-family="ui-monospace,Menlo,monospace" font-size="8.6" fill="{S.MUTED}">{sub}</text>
  <text x="10" y="{h - 20}" font-family="ui-sans-serif,system-ui,sans-serif" font-size="8.6" fill="{S.MUTED}">{legend}</text>
  <text x="10" y="{h - 8}" font-family="ui-monospace,Menlo,monospace" font-size="8.4" fill="{S.MUTED}">x {min(xs):.2f} … {max(xs):.2f} · y {min(ys):.2f} … {max(ys):.2f} · +y up</text>
</svg>"""


def card(title, svg, note, badge="PH", bad=False):
    cls = "ph-card bad" if bad else "ph-card"
    return f"""<div class="{cls}">
<h3>{title} <span class="badge {'badge-bad' if bad else ''}">{badge}</span></h3>
{svg}
<p class="small">{note}</p>
</div>"""


# --------------------------------------------------------------------------
# PHH / PPH
# --------------------------------------------------------------------------
def ladder_cards():
    """The alpha's integer points, segment by segment, each hit labelled."""
    whole = [S.bezier(_float_cp(ALPHA_CP), i / 240) for i in range(241)]  # t in [0,1]
    # the drawn family segment for each range, as a polyline for context
    def family(a, b, n=120):
        return [S.bezier(_float_cp(alpha_segment(a, b)), i / n) for i in range(n + 1)]

    cards = []
    for a, b in ((0, 3), (3, 6), (6, 9)):
        seg = alpha_segment(a, b)
        cp = seg[0]
        end = seg[-1]
        fig = span_figure(
            [((a, b), seg)],
            f"t {a} … {b}",
            f"({_fmt_q(cp[0])}, {_fmt_q(cp[1])}) → ({_fmt_q(end[0])}, {_fmt_q(end[1])})",
            "one cubic span between two integer points · deviation 0",
            w=330, h=300, context=family(a, b))
        cards.append(f'<div class="ph-card">{fig}</div>')
    return "".join(cards)


def phh_pair():
    s1 = PH.hermite((0.0, 0.0), (4.0, 1.5), math.radians(10), math.radians(-40))
    s2 = PH.continue_span(s1, math.radians(-95), 1.2)
    pts1 = [(PH.point_at(s1, i / 90).real, PH.point_at(s1, i / 90).imag)
            for i in range(91)]
    pts2 = [(PH.point_at(s2, i / 90).real, PH.point_at(s2, i / 90).imag)
            for i in range(91)]
    return s1, s2, pts1, pts2, PH.join_defects(s1, s2)


def phh_svg(pts1, pts2):
    allp = pts1 + pts2
    xs = [p[0] for p in allp]
    ys = [p[1] for p in allp]
    pad = 0.08 * max(max(xs) - min(xs), max(ys) - min(ys))
    f = S.Frame(560, 330, min(xs) - pad, max(xs) + pad,
                min(ys) - pad, max(ys) + pad, pad=42)
    step = S._nice_step(max(xs) - min(xs))
    grid = []
    g = math.floor(min(xs) / step) * step
    while g <= max(xs):
        a, b = f((g, min(ys) - pad)), f((g, max(ys) + pad))
        grid.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
                    f'y2="{b[1]:.1f}" stroke="{S.RULE}" stroke-width="0.6"/>')
        g += step
    g = math.floor(min(ys) / step) * step
    while g <= max(ys):
        a, b = f((min(xs) - pad, g)), f((max(xs) + pad, g))
        grid.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
                    f'y2="{b[1]:.1f}" stroke="{S.RULE}" stroke-width="0.6"/>')
        g += step
    j = f(pts1[-1])
    ax = f((min(xs) - pad, 0.0)) if min(ys) - pad <= 0 <= max(ys) + pad else None
    axl = f'<line x1="{ax[0]:.1f}" y1="{ax[1]:.1f}" x2="{f((max(xs) + pad, 0.0))[0]:.1f}" y2="{ax[1]:.1f}" stroke="{S.BLUE}" stroke-width="0.9"/>' if ax else ""
    # tangent ticks at both ends of the first span, so the data is visible
    ticks = []
    for span, sign in ((pts1, 1), (pts1, -1)):
        (px, py), (qx, qy) = span[-1], span[-2]
        dx, dy = (px - qx) * sign, (py - qy) * sign
        n = math.hypot(dx, dy) or 1.0
        dx, dy = dx / n, dy / n
        if sign < 0:
            dx, dy = -dy, dx
        a = f((px, py))
        b = f((px + 0.9 * dx, py + 0.9 * dy))
        ticks.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
                     f'y2="{b[1]:.1f}" stroke="{S.GOLD}" stroke-width="1.2"/>')
    return f"""<svg viewBox="0 0 560 330" width="100%" role="img" aria-label="PHH and PPH">
  <rect width="560" height="330" fill="{S.PAPER}"/>
  {''.join(grid)}
  {axl}
  <path d="{S._path(pts1, f)}" fill="none" stroke="{S.INK}" stroke-width="2.2"/>
  <path d="{S._path(pts2, f)}" fill="none" stroke="{S.BLUE}" stroke-width="2.2"/>
  <circle cx="{j[0]:.1f}" cy="{j[1]:.1f}" r="4.2" fill="none" stroke="{S.RED}" stroke-width="1.7"/>
  {''.join(ticks)}
  <text x="10" y="16" font-family="ui-sans-serif,system-ui,sans-serif" font-size="11.5" font-weight="600" fill="{S.INK}">Fig. H1 · one PHH span (black) and the C² PPH continuation (blue)</text>
  <text x="10" y="29" font-family="ui-monospace,Menlo,monospace" font-size="8.6" fill="{S.MUTED}">P0 = (0, 0) → P1 = (4, 1.5) · tangents +10° / −40° · second span leaves at −95°</text>
  <text x="10" y="308" font-family="ui-sans-serif,system-ui,sans-serif" font-size="8.6" fill="{S.MUTED}">legend: black PH quintic · blue continued span · red ring: the C² join · gold ticks: the prescribed end tangents</text>
  <text x="10" y="321" font-family="ui-monospace,Menlo,monospace" font-size="8.4" fill="{S.MUTED}">join at ({pts1[-1][0]:.3f}, {pts1[-1][1]:.3f}) · x {min(xs):.2f}…{max(xs):.2f} · y {min(ys):.2f}…{max(ys):.2f} · +y up</text>
</svg>"""


# --------------------------------------------------------------------------
# the occurrence audit
# --------------------------------------------------------------------------
AUDIT_ROWS = [
    ("<code>\\bPH</code> · every <code>*.md</code>", "116", "the operator's number"),
    ("<code>\\bPH\\b</code> · every <code>*.md</code>", "90", "exact token only"),
    ("<code>\\bPH\\b</code> · <code>docs/</code>", "32", "prose plus the generated HTML twin"),
    ("<code>\\bPH\\b</code> · <code>docs/*.md</code>", "18", "the hand-edited docs only"),
]


def audit_panel():
    rows = "\n".join(f"| {a} | {b} | {c} |" for a, b, c in AUDIT_ROWS)
    return f"""<section class="panel">
<h2>The occurrence audit</h2>
<p>The operator's note said <strong>116 standalone PH</strong> occurrences. It is
reproducible, but only under a wider pattern than the exact token:
<code>\\bPH</code> (a word starting with PH) over every tracked
<code>*.md</code> file, at commit <code>8f26aa7</code>, gives
<strong>116</strong>. That count includes <code>PHH</code>, <code>PPH</code> and
hyphenated forms such as <code>PH-families</code>. The exact token
<code>\\bPH\\b</code> gives 90 over the same files, 32 over <code>docs/</code>
(which includes the generated HTML twin) and 18 over <code>docs/*.md</code>.</p>
<p>So the note is <strong>not stale</strong>: it is a prefix count, and any claim
built on it must name the pattern. Re-derive at the commit:</p>
<pre><code>git grep -o -E '\\bPH'  HEAD -- '*.md' | wc -l   # 116
git grep -o -E '\\bPH\\b' HEAD -- '*.md' | wc -l   # 90</code></pre>

| pattern · scope | occurrences | meaning |
|---|---|---|
{rows}
</section>"""


# --------------------------------------------------------------------------
# the page
# --------------------------------------------------------------------------
def build():
    examples = [build_example(*e[:5]) for e in EXAMPLES]
    notes = {e[0]: e[5] for e in EXAMPLES}

    cards = []
    for e in examples:
        t = e["table"]
        sub = (f"n={e['pc'].n} · h={e['h']} · u={e['u']} · v={e['v']} · "
               f"scale {t['scale']:,} at m={t['m']} · arc {float(e['arc']):.3f}")
        svg = figure(e["pts"], e["title"].replace(" · ", " — "), sub,
                     seg=e["seg"], hits=list(e["hits"]),
                     milestones=e["miles"],
                     node=ALPHA_NODE if e["key"] == "alpha" else None)
        cards.append(card(e["title"], svg, notes[e["key"]]))

    from curve_lab.pyth_cubic import representatives
    rep = representatives()["s"][0]
    P = [rep["p0"], rep["p1"], rep["p2"], rep["p3"]]
    cards.append(card(
        "n = 3 · integer cubic 3-4-5",
        figure([S.bezier(P, i / 200) for i in range(201)],
               "n = 3 — exact integer cubic, not PH",
               "control triple (a,−b), (2c−a,b) · hodograph not Pythagorean",
               legend="black: integer controls at scale 1 · no rational offset"),
        "An exact integer-control cubic, <strong>not</strong> a PH curve. The "
        "control triple is Pythagorean; the hodograph is not, so the 3-4-5 base "
        "has no rational offset. See <a href='integer-cubic.html'>integer "
        "cubics</a>.", badge="not PH", bad=True))

    cards.append(card(
        "rational rung · the circle",
        figure(MF.rational_ph_circle(), "rational rung — the circle",
               "x = (1−t²)/(1+t²) · y = 2t/(1+t²) · speed 2/(1+t²) rational",
               legend="black: rational PH · no polynomial n = 2 exists"),
        "There is no polynomial PH quadratic. The rational circle is the n = 2 "
        "rung: the speed is rational, so the arc length and the offset are "
        "rational — but not polynomial."))

    hit_rows = []
    for e in examples:
        t = e["table"]
        coords = " ".join(f"({x},{y})" for x, y in t["hits"][:4])
        hit_rows.append(
            f"| {e['title'].split(' · ')[0]} | {e['pc'].n} | "
            f"`h={e['h']}` `u={e['u']}` `v={e['v']}` | {t['scale']:,} | "
            f"{t['m']} | {len(t['hits'])} | {coords} |")
    hit_table_html = "\n".join(hit_rows)

    # integer points in model coordinates, per rung
    point_rows = []
    for e in examples:
        pts = sorted(e["hits"])
        shown = " ".join(f"({x},{y})" for x, y in pts[:6])
        name = e["title"].split(" · ")[-1]
        point_rows.append(
            f"| {name} | {e['pc'].n} | {e['t0']:g} … {e['t1']:g} | "
            f"{len(pts)} | {shown} |")
    point_table = "\n".join(point_rows)

    fam = alpha_family(5)
    fam_rows = "\n".join(
        (f"| {k} | {18 * k * k:,} | 0 | 0 |" if k == 0 else
         f"| {k} | {18 * k * k:,} | ±{6 * k * (3 * k * k - 1):,} | ±{3 * k} |")
        for k in range(6))
    alpha_pts = [x for x in fam]

    # ---- interpolation: exact cubic splits and fitted rails
    ts = [-3, -2, -1, 0, 1, 2, 3]
    bands = [((a, b), alpha_segment(a, b)) for a, b in zip(ts, ts[1:])]
    fig26 = span_figure(
        bands, "Fig. 26 · tschirnhausen · 6 spans (exact re-split)",
        "t = −3 … 3 · cubic spans 1–6 · every join labelled (x, y) · "
        "filled red = integer, hollow = 4/3",
        "spans alternate ink / blue · 6 spans · 1 path · deviation 0 "
        "(a split, not a fit) · worst Δ(dκ/ds) 0")
    fig_c6 = rails_figure(
        ALPHA_CP, 0.60, "Fig. C6 · tschirnhausen ±0.60 fitted",
        "27y² = (1 − x)(8 + x)² · the same curve under x → (2 − 2x)/3, y → 2y/3",
        "black source · gold +d · blue −d · Levien cubic fit")
    fig_c61 = rails_figure(
        alpha_segment(0, 1.5), 0.22, "Fig. C61 · tschirnhausen ±0.22 fitted",
        "one branch section · node split (t = 0 … 1.5, node at t = ±√3)",
        "black branch section · gold +d · blue −d · Levien cubic fit")

    ladder = ladder_cards()
    lattice_rows = []
    for a, b in ((0, 3), (3, 6)):
        cp = alpha_segment(a, b)
        lattice_rows.append(
            f"| t {a} … {b} | {cp[0][0]}, {cp[0][1]} | {cp[1][0]}, {cp[1][1]} | "
            f"{cp[2][0]}, {cp[2][1]} | {cp[3][0]}, {cp[3][1]} |")
    lattice_table = "\n".join(lattice_rows)

    # the polygon route: exact rational nodes, and what their common integer
    # scale costs.  Measured here, not remembered.
    poly_note = ""
    try:
        from curve_lab.euler_polygon import convert as _convert
        _sec = [(float(G.homog_point(G.named_data(
            next(sp for sp in G.NAMED if sp["key"] == "tschirnhausen"))["ctrl"][0],
            F(int((0.2 + 0.6 * i / 120) * 1000), 1000))[0]),
                 float(G.homog_point(G.named_data(
            next(sp for sp in G.NAMED if sp["key"] == "tschirnhausen"))["ctrl"][0],
            F(int((0.2 + 0.6 * i / 120) * 1000), 1000))[1])) for i in range(121)]
        _small = _convert(_sec, n=6, max_angle=0.2, width_factor=0.08)
        poly_note = (
            "The p-triple Euler polygon is the other middleman, and it makes many "
            "exact <em>rational</em> nodes — 121 of them at 120 chords, 7 at 6. "
            "Their common integer scale is the catch: on this section the 6-chord "
            f"polygon needs a {_small['node_scale_digits']:,}-digit scale, and more "
            "chords do not help (the digits are dominated by the triple's "
            "hypotenuse, not by the chord count). That is why the page "
            "quotes 5⁶ = 15,625 for six 3-4-5 spans and nothing larger: the "
            "polygon gives exact nodes, but integer nodes cost an exponential "
            "scale. For six spans or fewer it is the best lattice route there is; "
            "for a whole curve it is not.")
    except Exception as exc:
        poly_note = f"(the polygon measurement did not run: {exc})"

    # the interpolated alternative, measured, for comparison
    fit_note = ""
    try:
        import g3_catalogue as C3
        pts = [(float(alpha_at(F(-3) + F(6 * i, 600))[0]),
                float(alpha_at(F(-3) + F(6 * i, 600))[1])) for i in range(601)]
        r = C3.fit_poly(pts, 6)
        if r:
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            size = math.hypot(max(xs) - min(xs), max(ys) - min(ys))
            fit_note = (f"A six-span <strong>quintic</strong> G3 interpolation of the same "
                        f"curve measures {r['error']:.3f} units — "
                        f"{100 * r['error'] / size:.2f}% of its size — with worst "
                        f"Δ(dκ/ds) {r['g3']:.1e}. That is what the interpolation "
                        f"buys when the curve is not cubic; here it is not needed.")
    except Exception as exc:  # the page must build even if g3 is unavailable
        fit_note = f"(the interpolation comparison did not run: {exc})"

    s1, s2, p1, p2, defects = phh_pair()
    miss = abs(PH.point_at(s1, 1.0) - complex(4.0, 1.5))
    phh_note = (f"endpoint miss {miss:.1e} · |Δz| {defects['position']:.1e} · "
                f"|Δz′| {defects['velocity']:.1e} · "
                f"|Δz″| {defects['acceleration']:.1e} · "
                f"|Δκ| {defects['curvature']:.1e}")

    presets = [
        {"key": e["key"], "name": e["title"].split(" · ")[1], "n": e["pc"].n,
         "h": list(e["h"]), "u": list(e["u"]), "v": list(e["v"]),
         "t0": -4.0 if e["key"] == "alpha" else 0.0,
         "t1": 4.0 if e["key"] == "alpha" else 1.0,
         "ints": [list(q) for q in sorted(e["hits"])]}
        for e in examples
    ]

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PH families · degree ladder</title>
<style>{S.CSS}
.ph-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:14px}}
.ph-card{{background:var(--paper);border:1px solid var(--rule);padding:8px 10px}}
.ph-card.bad{{border-color:#a23b2a;background:#fff8f6}}
.ph-card h3{{font-size:15px;margin:0 0 6px}}
.badge-bad{{color:#a23b2a;border-color:#a23b2a}}
.lede{{max-width:960px;color:var(--muted)}}
.defs{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px}}
.def{{border:1px solid var(--rule);padding:10px 12px;background:var(--paper)}}
.def h3{{margin:0 0 6px;font-size:14.5px}}
.lab{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px 18px;margin:10px 0 4px}}
.lab label{{display:block;font:600 11px/1.5 ui-monospace,Menlo,monospace;
letter-spacing:.04em;text-transform:uppercase;color:var(--muted)}}
.lab input[type=range]{{width:100%}}
.lab .inline{{display:inline-block;margin-right:12px;text-transform:none}}
#readout{{font:13px/1.7 ui-monospace,Menlo,monospace;margin:8px 0 0}}
table.small td,table.small th{{font-size:12.5px}}
</style></head><body><main>
<p class="eyebrow">curve-lab · PH families</p>
<h1>PH families · degree ladder, integer hits, PHH and PPH</h1>
<p class="lede">2D only. Every planar PH curve is
<code>z'(t) = h(t)·(u²−v², 2uv)</code> with
<code>n = deg h + 2·max(deg u, deg v) + 1</code>. With <code>h=1</code> only odd
degrees appear; the <code>h</code> factor is the only route to an even degree.
Model coordinates, +y up — the flip to screen y happens in the SVG frame at
output. Blue lines are the axes; every figure shows all four quadrants.</p>

<section class="panel">
<h2>Definitions, in one place</h2>
<div class="defs">
<div class="def"><h3>PH · polynomial Pythagorean-hodograph curve</h3>
<p>A planar curve whose <strong>speed is a polynomial</strong>:
<code>x'² + y'² = σ²</code>. Then the arc length is a polynomial, the tangent
frame is rational, and the <strong>offset is rational</strong> instead of
refitted. If the speed is only <em>rational</em> the curve is <em>rational</em>
PH — the circle is the example.</p></div>
<div class="def"><h3>PHH · PH Hermite</h3>
<p>The PH <strong>quintic</strong> through two points with prescribed endpoint
tangents: <code>z(0)=P₀</code>, <code>z(1)=P₁</code>,
<code>arg z'(0)=θ₀</code>, <code>arg z'(1)=θ₁</code>. With
<code>w = a(1−t)² + 2bt(1−t) + ct²</code> and <code>z' = w²</code>, the endpoint
condition is one quadratic in <code>b</code>:
<code>2b² + 3(a+c)b + (3a² + ac + 3c² − 15Δ) = 0</code>. The speeds
<code>|a|²</code> and <code>|c|²</code> are free, so PHH is a
<strong>two-parameter family</strong> per endpoint pair — not one curve. This
page's declared rule is <code>|a| = |c| = √|Δ|</code>.</p></div>
<div class="def"><h3>PPH · piecewise PH</h3>
<p>PH spans joined with <strong>C² continuity</strong>: at each join
<code>z</code>, <code>z'</code> and <code>z''</code> agree. With
<code>z' = w²</code> and <code>z'' = 2ww'</code>, that means the next span's
<code>a</code> is the previous span's <code>c</code>, and its <code>b</code> is
fixed by the previous end slope. The join is exact by construction, with no
fitting. A <em>general</em> C² spline solve — five conditions per join, both ends
free — is not built.</p></div>
</div>
<p class="small">The spatial/helix reading of PHH and PPH is out of scope: the
operator's only self-imposed limitation is to stay in the plane.</p>
</section>

{audit_panel()}

<section class="panel">
<h2>The degree ladder</h2>
<p><strong>n = deg h + 2·max(deg u, deg v) + 1.</strong>
<code>h=1, u,v linear → 3</code> · <code>h linear, u,v linear → 4</code> ·
<code>h=1, u,v quadratic → 5</code> · <code>h quadratic, u,v linear → 5</code> ·
<code>h linear, u,v quadratic → 6</code> · <code>h=1, u,v cubic → 7</code> ·
<code>h linear, u,v cubic → 8</code>. A rational <code>h</code> gives rational
PH (the circle). n = 2 exists only rationally.</p>
<p class="small"><strong>The trap.</strong> <code>pyth_cubic</code> is exact but
<strong>not PH</strong>: its name is the control triple, not the hodograph. The
cubic PH family is the Tschirnhausen alpha — one shape up to similarity.</p>
</section>

<div class="ph-grid">{''.join(cards)}</div>

<section class="panel">
<h2>Integer lattice hits and the scale</h2>
<p>A hit is a point at a chosen rational parameter <code>t = k/m</code> that
lands on integer coordinates after one common scale. The scale clears the
control points and the milestones together, in <code>fractions.Fraction</code>.
It is not a property of the curve: it is arithmetic about one generator set.
At <code>m = {M}</code>:</p>
<table class="small">
<thead><tr><th>curve</th><th>n</th><th>generators</th><th>scale</th>
<th>m</th><th>hits</th><th>first integer milestones</th></tr></thead>
<tbody>
{hit_table_html}
</tbody></table>
<p class="small">The scale grows as <code>mⁿ</code> times the denominators of the
control points. PH never improves that: a plain integer Bézier pays the same
<code>mⁿ</code> and already has integer controls at scale 1. What PH buys is the
polynomial arc length, the rational frame and the rational offset.</p>
</section>

<section class="panel">
<h2>Integer points on the curve itself — the real numbers</h2>
<p>Two different things carry the word “hit”, and they are now drawn
differently. A <strong>milestone</strong> is integral <em>after</em> the scale
above is applied: it exists by construction, and its coordinates are large. An
<strong>integer point of the curve</strong> is integral in model coordinates,
with no scale at all. <strong>Filled red circles</strong> are the second kind,
labelled with their coordinates; <strong>hollow blue squares</strong> are the
first, drawn at <code>t = k/m</code> and unlabelled because their value is
<code>coordinate × scale</code>. The table above lists those scaled values.</p>

<p><strong>The alpha, completely.</strong> The curve this page draws is
<code>18y² = x(x−6)²</code>, from <code>x = 2t²</code>,
<code>y = t(6−x)/3</code>. Every integer point follows: if <code>x ≠ 6</code>
then <code>t = 3y/(6−x)</code> is rational, and writing it in lowest terms makes
<code>x = 2a²/b²</code> integral force <code>b = 1</code>, so <code>t</code> is
an integer and <code>3 | t</code>. That gives <code>(18k², ±6k(3k²−1))</code>.
The node at <code>(6, 0)</code> is the one point at an irrational parameter,
<code>t = ±√3</code>. So the set is exact, not a sample:

| k | x | y | t |
|---|---|---|---|
{fam_rows}

<p>In the drawn window <code>t ∈ [−4, 4]</code> that is <strong>four</strong>
distinct points — <code>(0,0)</code>, the node <code>(6,0)</code> at
<code>t = ±√3</code>, and <code>(18,−12)</code>, <code>(18,12)</code> at
<code>t = ±3</code>. There are more along the arms (<code>(72,±132)</code> at
<code>t = ±6</code>, <code>(162,±468)</code> at <code>t = ±9</code>), which is
why a fixed count is a statement about the window, not about the curve. Note
also <code>x = 2</code> gives <code>y = ±4/3</code> — on the curve, but not a
lattice point.</p>

<p><strong>The other rungs.</strong> Searched exactly at
<code>t = p/q</code>, <code>q ≤ 60</code>, over each drawn range; the points
found are listed. Only the start point is integral, which is the honest reason
the page uses the scaled milestones for the catalogue:</p>

<table class="small">
<thead><tr><th>curve</th><th>n</th><th>drawn t</th><th>integer points</th>
<th>coordinates</th></tr></thead>
<tbody>
{point_table}
</tbody></table>
<p class="small">That search cannot see a point at an irrational parameter — the
alpha's node is exactly one — so it is a lower bound for those rungs, stated as
such. The alpha is the one rung where the complete set is proved.</p>
</section>

<section class="panel">
<h2>The interactive explainer</h2>
<p>The sliders move only PH-valid generators: any polynomials <code>u, v, h</code>
give a PH curve, so no slider setting can leave the family. The grid
<code>m</code> recomputes the exact hit count and scale in the browser; the
quadrant boxes mirror; the offset slider shows the <strong>exact</strong> PH
offset beside a <strong>fitted</strong> normal offset; and “break PH” shifts a
control point, after which the drawn speed is no longer the polynomial σ and the
identity fails — the readout says by how much.</p>
<div class="lab">
  <div><label for="preset">rung</label><select id="preset"></select></div>
  <div><label for="m">grid m · <span id="mv">4</span></label><input id="m" type="range" min="2" max="12" step="1" value="4"></div>
  <div><label for="d">offset d · <span id="dv">0.25</span></label><input id="d" type="range" min="0" max="0.8" step="0.05" value="0.25"></div>
  <div><label for="u0">u₀ · <span id="u0v"></span></label><input id="u0" type="range" min="-3" max="3" step="1"></div>
  <div><label for="u1">u₁ · <span id="u1v"></span></label><input id="u1" type="range" min="-3" max="3" step="1"></div>
  <div><label for="u2">u₂ · <span id="u2v"></span></label><input id="u2" type="range" min="-3" max="3" step="1"></div>
  <div><label for="u3">u₃ · <span id="u3v"></span></label><input id="u3" type="range" min="-3" max="3" step="1"></div>
  <div><label for="v0">v₀ · <span id="v0v"></span></label><input id="v0" type="range" min="-3" max="3" step="1"></div>
  <div><label for="v1">v₁ · <span id="v1v"></span></label><input id="v1" type="range" min="-3" max="3" step="1"></div>
  <div><label for="v2">v₂ · <span id="v2v"></span></label><input id="v2" type="range" min="-3" max="3" step="1"></div>
  <div><label for="v3">v₃ · <span id="v3v"></span></label><input id="v3" type="range" min="-3" max="3" step="1"></div>
  <div><label>quadrants</label><span>
    <label class="inline"><input id="qx" type="checkbox" checked> x</label>
    <label class="inline"><input id="qy" type="checkbox" checked> y</label></span></div>
  <div><label for="brk">break PH</label><input id="brk" type="checkbox"></div>
</div>
<div id="stage"></div>
<p id="readout"></p>
</section>

<section class="panel">
<h2>PHH and PPH, pinned</h2>
{phh_svg(p1, p2)}
<p><strong>The exact Hermite data.</strong> Two points and two tangent
<em>directions</em>; the tangent <em>magnitudes</em> are the free parameters, and
the shape moves with them. The endpoint is hit exactly because the quadratic in
<code>b</code> is solved for it.</p>
<p><strong>The join.</strong> {phh_note}. The blue span is not fitted: its
<code>a</code> is the black span's <code>c</code> and its <code>b</code> is set by
the black span's end slope, so the join is C² by construction.</p>
<p class="small">A general C² PPH — five conditions per join, both end tangents
free — is <strong>not built</strong>. What is proved here is the one-sided rule
and one two-span chain.</p>
</section>

<section class="panel">
<h2>What is made, and what is not</h2>
<p><strong>Made:</strong> the full nodal Tschirnhausen alpha and the C-segment
inside it; two cubics; two quartics; three quintics; two sextics; a septic; an
octic; the rational circle; the integer scales and milestones for every rung; the
four-quadrant renders; the PHH interpolant; one C² PPH pair; the sliders.</p>
<p><strong>Not made yet:</strong></p>
<ul>
<li>the <strong>general</strong> PH quintic family — three examples, not the
five-parameter family;</li>
<li>the classical PHH magnitude rule — this page declares <code>√|Δ|</code>; the
bending-energy-optimal choice is not implemented;</li>
<li>a general C² PPH solve with five conditions per join;</li>
<li>integer lattice hits for PHH/PPH: their coefficients carry <code>√</code>, so
no common scale puts them on the lattice;</li>
<li>the PH quintic transition curve (straight line to circular arc);</li>
<li>the general degree-7 and degree-8 families — one example each;</li>
<li>rational PH beyond the circle;</li>
<li>anything in 3D — deliberately out of scope.</li>
</ul>
<p class="small">Arithmetic: <a href="../docs/PH-INTEGER.html">the PH-INTEGER
notes</a>, generated by <code>scripts/ph_doc.py</code>. The rational circle and
the septic also live on <a href="missing-families.html">the missing families</a>;
<a href="catenary.html">the catenary</a> is four PH cubics. This page is built by
<code>scripts/ph_families.py</code>; do not hand-edit it.</p>
</section>

<section class="panel">
<h2>Interpolation — from the curve to cubic spans for Inkscape</h2>
<p>The blue-sky question: use an interpolated Euler/clothoid chain as the
middleman, and hand Inkscape a <em>few</em> cubic Béziers that start and end on
integer lattice points. For the Tschirnhausen the middleman is not needed: the
alpha <strong>is</strong> a cubic, so splitting it is exact. A split is not a
fit — the spans are the curve, not an approximation of it.</p>

{fig26}
<p class="small"><strong>Fig. 26</strong> · the alpha cut at
<code>t = −3, −2, −1, 0, 1, 2, 3</code> into six cubic spans, one path.
Deviation <strong>0</strong> and worst Δ(dκ/ds) <strong>0</strong> are not
roundings: de Casteljau on one cubic reproduces it exactly, and the joins are
the same curve. The full curve needs no interpolation at all.</p>
<p class="small">{fit_note}</p>
<p class="small">{poly_note}</p>

<div class="ph-grid">
<div class="ph-card">{fig_c6}
<p class="small">Two fitted rails at <code>±0.60</code>. Levien's cubic fit, not
an exact offset: the alpha's offset is rational, but a cubic-Bézier rail is a
fit, and the error is printed on the figure.</p></div>
<div class="ph-card">{fig_c61}
<p class="small">One branch section, node split: the branch
<code>t ∈ [0, 1.5]</code> stops short of the node at <code>t = ±√3</code>, so
the rail never has to cross itself. Rails at <code>±0.22</code>.</p></div>
</div>

<h3>The spans that land on the lattice</h3>
<p>Cut only at the integer points, and each span ends where the next begins.
The control points are exact — thirds, no rounding — and the endpoints are
whole numbers:</p>
<table class="small">
<thead><tr><th>parameter</th><th>start</th><th>c1</th><th>c2</th>
<th>end</th></tr></thead>
<tbody>
{lattice_table}
</tbody></table>
<p>So the arm <code>(0,0) → (18,−12) → (72,−132)</code> is <strong>two cubic
spans</strong>, exact, with lattice endpoints; the mirrored arm is two more.
That is the whole Inkscape payload for this curve: no per-lattice-point spans,
no interpolation error, and no curve between each pair of hits — just the two
spans that join the hits.</p>

<h3>The ladder — every integer point of the alpha, in order</h3>
<p>Walk further out and the hits continue, each one exactly
<code>(18k², ±6k(3k²−1))</code>. Eight of them lie inside
<code>t ∈ [−9, 9]</code>, and every one is labelled on its span:</p>
<div class="ph-grid">{ladder}</div>
<p class="small">The full list to <code>t = 9</code>:
<code>(0,0)</code>, the node <code>(6,0)</code> at <code>t = ±√3</code>,
<code>(18,±12)</code>, <code>(72,±132)</code>, <code>(162,±468)</code>.
That is <strong>eight lattice points</strong> on one cubic — not because the
curve was fitted to them, but because the curve passes through them exactly, and
a cubic can be cut at any two of them with no error.</p>
<p class="small">Where: <code>scripts/euler_sections.py</code> <code>SECTIONS</code>
(the branch sections), <code>scripts/showcase.py</code> and
<code>scripts/g3_showcase.py</code> (the catalogue and the G3 panels).
Re-derive: <code>python scripts/ph_families.py</code> rebuilds this page and
prints the span numbers; <code>python scripts/g3_showcase.py</code>,
<code>python scripts/showcase.py</code> rebuild the twins it compares against.
The rail figures use <code>curve_lab/parallel_bezier.py</code>.</p>
</section>
</main>
<script>window.PH_PRESETS = {json.dumps(presets)};</script>
<script src="ph-families-app.js"></script>
</body></html>
"""
    out = ROOT / "workbench" / "ph-families.html"
    out.write_text(html, encoding="utf-8")
    app = ROOT / "workbench" / "ph-families-app.js"
    app.write_text((ROOT / "scripts" / "ph_families_app.js").read_text(encoding="utf-8"),
                   encoding="utf-8")
    print(out)
    print(app)
    return out


if __name__ == "__main__":
    build()
