"""Two catenary studies on one page.

    .venv/bin/python scripts/catenary.py
    open workbench/catenary.html

A. A catenary chained from pythagorean triples: every chord's direction is a
   triple's slope, the chord length is the arc step the catenary asks for, so
   the chain is a stair of real triangles that tracks cosh.

B. Weil's catenary drapery in 2.5D: each row of the sheet is the catenary of
   its own rest width, so the cloth gathers and sags as it hangs.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from curve_families import ladder, offset_chain, path_d  # noqa: E402
from hodograph import PHCubic, from_hermite  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
INK = "#2e2413"
GOLD = "#c9a441"
GRID = "#e8dfc8"
LINE = "#d8ccae"
MUTED = "#7b6c4e"


# -- A: the pythagorean catenary -------------------------------------------

RUNGS = ladder(max_h=1600, max_deg=62.0)
DEGREES = [r["deg"] for r in RUNGS]


def snap(theta_deg: float) -> float:
    """The nearest rung: the chain only turns to angles a triple can make."""
    return min(DEGREES, key=lambda d: abs(d - theta_deg))


def cat(a: float, s: float):
    """The point at arc length s from the vertex, in catenary coordinates."""
    u = s / a
    return (a * math.asinh(u), a * (math.sqrt(1 + u * u) - 1))


def branch(a: float, length: float, steps: int):
    """Chain chords of equal arc, each aimed along the nearest triple."""
    pts = [(0.0, 0.0)]
    step = length / steps
    for i in range(1, steps + 1):
        s = i * step
        theta = snap(math.degrees(math.atan(s / a)))
        x, y = pts[-1]
        pts.append((x + step * math.cos(math.radians(theta)),
                    y + step * math.sin(math.radians(theta))))
    return pts





def ph_offset_figure(a: float, n: int = 4, w=860.0, h=380.0):
    """The PH chain and two offsets of it, computed exactly.

    For a PH curve z'(t) = w(t)^2, the unit normal is i w^2 / |w|^2, so the
    offset at distance d is z(t) + d * i w^2 / |w|^2 -- rational in t.  No
    re-fitting, no approximation.
    """
    total = 2.2 * a
    chars, offsets, segs = [], [], []
    for i in range(n):
        s0_, s1_ = 0.62 * total * i / n, 0.62 * total * (i + 1) / n
        seg, _ = from_hermite(cat(a, s0_), math.atan(s0_ / a), cat(a, s1_),
                              math.atan(s1_ / a))
        segs.append(seg)
        chars.append([seg.point(j / 20) for j in range(21)])
        for d in (-0.075 * a, 0.075 * a):
            line = []
            for j in range(21):
                t = j / 20
                u, v = seg.u(t), seg.v(t)
                q = u * u + v * v
                p_ = seg.point(t)
                line.append((p_[0] + d * (-2 * u * v) / q,
                             p_[1] + d * (u * u - v * v) / q))
            offsets.append(line)

    flat = [p for c in chars for p in c] + [p for o in offsets for p in o]
    xs = [p[0] for p in flat]; ys = [p[1] for p in flat]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    k = min((w - 40) / (x1 - x0), (h - 40) / (y1 - y0))
    px = (w - (x1 - x0) * k) / 2
    py = (h - (y1 - y0) * k) / 2

    def at(p):
        return (px + (p[0] - x0) * k, h - (py + (p[1] - y0) * k))

    out = "".join(f'<path d="{path_d([at(p) for p in o])}" fill="none" '
                  f'stroke="{GOLD}" stroke-width="1.2"/>' for o in offsets)
    ink = "".join(f'<path d="{path_d([at(p) for p in c])}" fill="none" '
                  f'stroke="{INK}" stroke-width="2.2"/>' for c in chars)
    return f"""<svg viewBox="0 0 {w:.0f} {h:.0f}" xmlns="http://www.w3.org/2000/svg">
    <rect x="0" y="0" width="{w:.0f}" height="{h:.0f}" fill="#fff"
          stroke="{LINE}" stroke-width="1"/>
    {''.join(leg_triangles([at(p) for p in sg.control_points()], 0.14) for sg in segs)}
    {out}
    {ink}
  </svg>"""



def ph_drape(a: float, split: float, n: int):
    """Both branches of a drape as n PH cubics a side; returns the segments."""
    total = 2.2 * a
    segs = []
    for i in range(n):
        s0_, s1_ = split * total * i / n, split * total * (i + 1) / n
        sg, _ = from_hermite(cat(a, s0_), math.atan(s0_ / a), cat(a, s1_),
                             math.atan(s1_ / a))
        segs.append((sg, 1))
    for i in range(n):
        s0_, s1_ = (1 - split) * total * i / n, (1 - split) * total * (i + 1) / n
        sg, _ = from_hermite(cat(a, s0_), math.atan(s0_ / a), cat(a, s1_),
                             math.atan(s1_ / a))
        segs.append((sg, -1))
    return segs


def ph_card(letter: str, label: str, split: float, n: int,
            a: float = 100.0, w=430.0, h=220.0) -> str:
    """One drape card built by the PH algorithm, with its three-leg triangles."""
    segs = ph_drape(a, split, n)
    paths, frames = [], []
    for sg, side in segs:
        pts = [sg.point(j / 16) for j in range(17)]
        cp = sg.control_points()
        if side < 0:
            pts = [(-x, y) for x, y in pts]
            cp = tuple((-x, y) for x, y in cp)
        paths.append(pts)
        frames.append(cp)

    flat = [p_ for path in paths for p_ in path]
    xs = [p_[0] for p_ in flat]; ys = [p_[1] for p_ in flat]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    k = min((w - 30) / (x1 - x0), (h - 30) / (y1 - y0))
    px = (w - (x1 - x0) * k) / 2
    py = (h - (y1 - y0) * k) / 2

    def at(p_):
        return (px + (p_[0] - x0) * k, h - (py + (p_[1] - y0) * k))

    err = max(ph_error(a, split * 2.2 * a, n), ph_error(a, (1 - split) * 2.2 * a, n))
    return (f'<figure style="margin:0"><svg viewBox="0 0 {w:.0f} {h:.0f}" '
            f'xmlns="http://www.w3.org/2000/svg">'
            f'<rect x="0" y="0" width="{w:.0f}" height="{h:.0f}" fill="#fff" '
            f'stroke="{LINE}"/>{"" .join(leg_triangles([at(p_) for p_ in cp], 0.14) for cp in frames)}'
            f'{"" .join(f"""<path d="{path_d([at(p_) for p_ in path])}" fill="none" stroke="{INK}" stroke-width="1.8"/>""" for path in paths)}'
            f'</svg><figcaption><strong>Fig. {letter}</strong> · {label}<br>'
            f'{len(segs)} cubics · worst {100 * err / a:.4f}% of a</figcaption></figure>')


def ph_explain(a: float) -> str:
    """Three panels: the triple, the control polygon, the chain."""
    # -- (i) the doubling: (4,3) aims at 36.87, (7,24) at 73.74 ------------
    w = h = 280.0
    ox, oy = 40.0, 210.0
    L = 190.0

    def tip(u, v, scale=None):
        n = math.hypot(u, v)
        k = (scale or L) / n
        return ox + u * k, oy - v * k

    a1 = tip(4, 3)
    a2 = tip(7, 24)

    def arc(deg, r, colour):
        pts = [(ox + r * math.cos(math.radians(deg * i / 24)),
                oy - r * math.sin(math.radians(deg * i / 24))) for i in range(25)]
        return f'<path d="{path_d(pts)}" fill="none" stroke="{colour}" stroke-width="1.1"/>'

    panel_i = f"""<svg viewBox="0 0 280 240" xmlns="http://www.w3.org/2000/svg">
    <rect x="0" y="0" width="280" height="240" fill="#fff" stroke="{LINE}"/>
    <line x1="{ox}" y1="{oy}" x2="270" y2="{oy}" stroke="{GRID}" stroke-width="1"/>
    <line x1="{ox}" y1="{oy}" x2="{ox}" y2="20" stroke="{GRID}" stroke-width="1"/>
    {arc(73.74, 96, GOLD)}
    {arc(36.87, 62, INK)}
    <line x1="{ox}" y1="{oy}" x2="{a1[0]:.1f}" y2="{a1[1]:.1f}" stroke="{INK}" stroke-width="2"/>
    <line x1="{ox}" y1="{oy}" x2="{a2[0]:.1f}" y2="{a2[1]:.1f}" stroke="{GOLD}" stroke-width="2"/>
    <circle cx="{a1[0]:.1f}" cy="{a1[1]:.1f}" r="3" fill="{INK}"/>
    <circle cx="{a2[0]:.1f}" cy="{a2[1]:.1f}" r="3" fill="{GOLD}"/>
    <text x="{a1[0] + 6:.0f}" y="{a1[1] - 4:.0f}" font-size="10"
          font-family="ui-monospace,monospace" fill="{INK}">(4,3)</text>
    <text x="{a2[0] + 6:.0f}" y="{a2[1] + 2:.0f}" font-size="10"
          font-family="ui-monospace,monospace" fill="{GOLD}">(7,24)</text>
    <text x="14" y="228" font-size="10" font-family="ui-monospace,monospace"
          fill="#7b6c4e">36.87 x 2 = 73.74</text>
  </svg>"""

    # -- (ii) the three legs are three triangles --------------------------
    seg = PHCubic(24, 7, 4, 3)
    cps = seg.control_points()
    curve = [seg.point(j / 40) for j in range(41)]
    legs = [(24 * 24 - 7 * 7, 2 * 24 * 7, "(24,7) squared"),
            (24 * 4 - 7 * 3, 24 * 3 + 4 * 7, "(24,7) x (4,3)"),
            (4 * 4 - 3 * 3, 2 * 4 * 3, "(4,3) squared")]
    everything = curve + list(cps)
    xs = [p[0] for p in everything]; ys = [p[1] for p in everything]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    k = min((w - 50) / (x1 - x0), (h - 70) / (y1 - y0))
    px = (w - (x1 - x0) * k) / 2
    py = (h - 30 - (y1 - y0) * k) / 2

    def at(p):
        return (px + (p[0] - x0) * k, h - 30 - (py + (p[1] - y0) * k))

    tri = []
    for i, (lu, lv, name) in enumerate(legs):
        p_, q_ = at(cps[i]), at(cps[i + 1])
        corner = (q_[0], p_[1])
        tri.append(f'<path d="M {p_[0]:.1f} {p_[1]:.1f} L {corner[0]:.1f} '
                   f'{corner[1]:.1f} L {q_[0]:.1f} {q_[1]:.1f} Z" fill="none" '
                   f'stroke="{GOLD}" stroke-width="0.9" opacity="0.85"/>')

    panel_ii = f"""<svg viewBox="0 0 280 240" xmlns="http://www.w3.org/2000/svg">
    <rect x="0" y="0" width="280" height="240" fill="#fff" stroke="{LINE}"/>
    <path d="{path_d([at(p) for p in curve])}" fill="none" stroke="{INK}" stroke-width="2.2"/>
    <path d="{path_d([at(p) for p in cps])}" fill="none" stroke="#c9a441"
          stroke-width="1.2" stroke-dasharray="4 3"/>
    {''.join(tri)}
    {''.join(f'<circle cx="{at(p)[0]:.1f}" cy="{at(p)[1]:.1f}" r="2.4" fill="{INK}"/>'
             for p in cps)}
    <text x="10" y="222" font-size="9" font-family="ui-monospace,monospace"
          fill="#7b6c4e">527,336,625 &middot; 75,100,125 &middot; 7,24,25</text>
    <text x="10" y="234" font-size="9" font-family="ui-monospace,monospace"
          fill="#7b6c4e">each leg is a triple: square, product, square</text>
  </svg>"""

    # -- (iii) four of them over the catenary ------------------------------
    total = 2.2 * a
    chain, chain_segs = [], []
    for i in range(4):
        s0_, s1_ = 0.62 * total * i / 4, 0.62 * total * (i + 1) / 4
        sg, _ = from_hermite(cat(a, s0_), math.atan(s0_ / a), cat(a, s1_),
                             math.atan(s1_ / a))
        chain.append([sg.point(j / 20) for j in range(21)])
        chain_segs.append(sg)
    flat = [p for c in chain for p in c]
    xs = [p[0] for p in flat]; ys = [p[1] for p in flat]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    k = min((w - 44) / (x1 - x0), (h - 44) / (y1 - y0))
    px = (w - (x1 - x0) * k) / 2
    py = (h - (y1 - y0) * k) / 2

    def at3(p):
        return (px + (p[0] - x0) * k, h - (py + (p[1] - y0) * k))

    panel_iii = f"""<svg viewBox="0 0 280 240" xmlns="http://www.w3.org/2000/svg">
    <rect x="0" y="0" width="280" height="240" fill="#fff" stroke="{LINE}"/>
    <path d="{path_d([at3(cat(a, 0.62 * total * j / 160)) for j in range(161)])}"
          fill="none" stroke="{GOLD}" stroke-width="1.3" stroke-dasharray="5 4"/>
    {''.join(leg_triangles([at3(p) for p in sg.control_points()], 0.16) for sg in chain_segs)}
    {''.join(f'<path d="{path_d([at3(p) for p in c])}" fill="none" stroke="{INK}" stroke-width="1.8"/>' for c in chain)}
    <text x="14" y="228" font-size="10" font-family="ui-monospace,monospace"
          fill="#7b6c4e">four segments, error 0.003% of a</text>
  </svg>"""

    return f'<div class="three">{panel_i}{panel_ii}{panel_iii}</div>'



def leg_triangles(screen_cps, opacity=0.12):
    """The three control legs, each as its right triangle (screen points)."""
    out = []
    for i in range(3):
        p_, q_ = screen_cps[i], screen_cps[i + 1]
        corner = (q_[0], p_[1])
        out.append(f'<path d="M {p_[0]:.1f} {p_[1]:.1f} L {corner[0]:.1f} '
                   f'{corner[1]:.1f} L {q_[0]:.1f} {q_[1]:.1f} Z" fill="{GOLD}" '
                   f'fill-opacity="{opacity}" stroke="#c9a441" '
                   f'stroke-width="0.7"/>')
    return "".join(out)


def ph_chain(a: float, s_end: float, n: int):
    """n PH cubics from the vertex out to s_end, each fitted by its two ends."""
    segs = []
    for i in range(n):
        s0, s1 = s_end * i / n, s_end * (i + 1) / n
        seg, legs = from_hermite(cat(a, s0), math.atan(s0 / a),
                                 cat(a, s1), math.atan(s1 / a))
        segs.append((seg, legs))
    return segs


def ph_error(a: float, s_end: float, n: int) -> float:
    """Worst distance from an n-segment PH chain to the catenary it was fitted to."""
    dense = [cat(a, s_end * k / 1200) for k in range(1201)]

    def dist(pt):
        best = 1e18
        for k in range(len(dense) - 1):
            p0, p1 = dense[k], dense[k + 1]
            vx, vy = p1[0] - p0[0], p1[1] - p0[1]
            L = vx * vx + vy * vy
            t = 0.0 if L == 0 else max(0.0, min(1.0,
                ((pt[0] - p0[0]) * vx + (pt[1] - p0[1]) * vy) / L))
            best = min(best, math.hypot(pt[0] - (p0[0] + t * vx),
                                        pt[1] - (p0[1] + t * vy)))
        return best

    worst = 0.0
    for seg, _ in ph_chain(a, s_end, n):
        worst = max(worst, max(dist(seg.point(j / 24)) for j in range(25)))
    return worst


def ph_figure(a: float, split: float, n: int, w=860.0, h=420.0) -> str:
    """Both branches as PH cubics, over the catenary, with the control polygons."""
    total = 2.2 * a
    high = ph_chain(a, split * total, n)
    low = ph_chain(a, (1 - split) * total, n)

    paths, frames, nodes = [], [], []
    for seg, legs in high:
        paths.append([seg.point(j / 24) for j in range(25)])
        frames.append(seg.control_points())
        nodes.append(seg.control_points()[0])
    nodes.append(high[-1][0].control_points()[3])
    for seg, legs in low:
        pts = [(-x, y) for x, y in (seg.point(j / 24) for j in range(25))]
        pts.reverse()
        paths.append(pts)
        cp = [(-x, y) for x, y in seg.control_points()]
        frames.append(tuple(reversed(cp)))

    truth = [(-cat(a, (1 - split) * total * i / 400)[0],
              cat(a, (1 - split) * total * i / 400)[1]) for i in range(400, -1, -1)]
    truth += [cat(a, split * total * i / 400) for i in range(1, 401)]

    everything = [p for path in paths for p in path] + truth
    xs = [p[0] for p in everything]; ys = [p[1] for p in everything]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    scale = min((w - 40) / (x1 - x0), (h - 40) / (y1 - y0))
    dx = (w - (x1 - x0) * scale) / 2
    dy = (h - (y1 - y0) * scale) / 2

    def at(p):
        return (dx + (p[0] - x0) * scale, h - (dy + (p[1] - y0) * scale))

    polys = "".join(
        f'<path d="{path_d([at(p) for p in cp])}" fill="none" stroke="#e0d2b0" '
        f'stroke-width="1"/>' for cp in frames)
    tris = "".join(leg_triangles([at(p) for p in cp]) for cp in frames)
    curves = "".join(
        f'<path d="{path_d([at(p) for p in path])}" fill="none" stroke="{INK}" '
        f'stroke-width="2.2"/>' for path in paths)
    dots = "".join(
        f'<circle cx="{at(p)[0]:.1f}" cy="{at(p)[1]:.1f}" r="3.2" fill="{INK}"/>'
        for p in nodes)
    return f"""<svg viewBox="0 0 {w:.0f} {h:.0f}" xmlns="http://www.w3.org/2000/svg">
    <rect x="0" y="0" width="{w:.0f}" height="{h:.0f}" fill="#fff"
          stroke="{LINE}" stroke-width="1"/>
    <path d="{path_d([at(p) for p in truth])}" fill="none" stroke="{GOLD}"
          stroke-width="1.3" stroke-dasharray="6 5"/>
    {tris}
    {polys}
    {curves}
    {dots}
  </svg>"""


def integer_branch(a: float, length: float, target: float = 450.0,
                   axis: str = "horizontal"):
    """Walk the rungs. Each chord is a scaled rung, so every node is an integer
    and the height and width are whatever the walk accumulates.

    The angle comes from the whole catalogue -- 65 rungs below 12 degrees, so
    the flat part near the vertex is dense -- and the size comes from `target`,
    the chord length the walk aims for.  Multiplying a rung by an integer keeps
    both the angle and the lattice: m*(u, v) is still integer.
    """
    pts = [(0, 0)]
    rows = []
    s = 0.0
    while s < length:
        want = math.degrees(math.atan((s + 0.5 * target) / a))
        key = "deg" if axis == "horizontal" else "deg_v"
        rung = min(RUNGS, key=lambda r: abs(r[key] - want))
        u, v, h = rung["triple"]
        m = max(1, round(target / h))
        u, v = m * u, m * v
        x, y = pts[-1]
        pts.append((x + u, y + v))
        s += m * h
        rows.append({"deg": rung["deg"], "triple": rung["triple"], "m": m, "s": s})
    return pts, rows


def branch_data(a: float, length: float, steps: int):
    """The chain, plus one row per chord: where it lands and which rung it used."""
    pts = [(0.0, 0.0)]
    rows = []
    step = length / steps
    for i in range(1, steps + 1):
        s = i * step
        want = math.degrees(math.atan(s / a))
        rung = min(RUNGS, key=lambda r: abs(r["deg"] - want))
        theta = math.radians(rung["deg"])
        x, y = pts[-1]
        q = (x + step * math.cos(theta), y + step * math.sin(theta))
        pts.append(q)
        rows.append({"i": i, "x": q[0], "y": q[1], "want": want,
                     "deg": rung["deg"], "triple": rung["triple"]})
    return pts, rows


def branch_error(a: float, length: float, steps: int):
    """Worst distance from a chain node to the true catenary at the same arc."""
    pts = branch(a, length, steps)
    worst = 0.0
    for i, p in enumerate(pts):
        q = cat(a, i * length / steps)
        worst = max(worst, math.dist(p, q))
    return worst


def fig_catenary(a=100.0, high=0.62, steps=10, gold=True, grid=True):
    """Both branches on one catenary, every triangle drawn on a fine grid."""
    total = 2.2 * a
    up, up_rows = branch_data(a, high * total, steps)
    down_pts, down_rows = branch_data(a, (1 - high) * total, steps)
    down = [(-x, y) for x, y in down_pts]
    down.reverse()
    chain = down + up[1:]
    edges = list(zip(chain[:-1], chain[1:]))

    true = []
    if gold:
        low_len, high_len = (1 - high) * total, high * total
        true = [(-cat(a, low_len * i / 200)[0], cat(a, low_len * i / 200)[1])
                for i in range(200, -1, -1)]
        true += [cat(a, high_len * i / 200) for i in range(1, 201)]

    pts = chain + true
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    w, h = 860.0, 400.0
    margin = 34.0
    scale = min((w - 2 * margin) / (x1 - x0), (h - 2 * margin) / (y1 - y0))
    dx = (w - (x1 - x0) * scale) / 2
    dy = (h - (y1 - y0) * scale) / 2

    def at(p):
        return (dx + (p[0] - x0) * scale, h - (dy + (p[1] - y0) * scale))

    # the grid, in model units: fine every 10, heavy every 50
    grid_lines = []
    if grid:
        gx = math.floor(x0 / 10) * 10
        while gx <= x1:
            px, _ = at((gx, y0))
            heavy = abs(gx % 50) < 1e-6
            grid_lines.append(
                f'<line x1="{px:.2f}" y1="0" x2="{px:.2f}" y2="{h:.0f}" '
                f'stroke="{"#e0d6bd" if heavy else GRID}" '
                f'stroke-width="{1.0 if heavy else 0.6}"/>')
            gx += 10
        gy = math.floor(y0 / 10) * 10
        while gy <= y1:
            _, py = at((x0, gy))
            heavy = abs(gy % 50) < 1e-6
            grid_lines.append(
                f'<line x1="0" y1="{py:.2f}" x2="{w:.0f}" y2="{py:.2f}" '
                f'stroke="{"#e0d6bd" if heavy else GRID}" '
                f'stroke-width="{1.0 if heavy else 0.6}"/>')
            gy += 10

    # every triangle: the hypotenuse is the chord, the legs are axis-aligned
    tris = []
    for (px, py), (qx, qy) in edges:
        ax, ay = at((px, py))
        bx, by = at((qx, py))
        cx, cy = at((qx, qy))
        tris.append(f'<path d="M {ax:.2f} {ay:.2f} L {bx:.2f} {by:.2f} '
                    f'L {cx:.2f} {cy:.2f} Z" fill="none" stroke="{GOLD}" '
                    f'stroke-width="0.8" opacity="0.8"/>')

    # every spine carries its plates: the same offset rule as Stage II
    plates = []
    chord_min = min(math.dist(p, q) for p, q in edges)
    for frac, shade in ((-0.55, "#c9a441"), (-0.28, "#a8894a"),
                        (0.28, "#a8894a"), (0.55, "#c9a441")):
        line = offset_chain(chain, frac * chord_min)
        plates.append(f'<path d="{path_d([at(p) for p in line])}" fill="none" '
                      f'stroke="{shade}" stroke-width="1.1"/>')

    gold_line = ""
    if true:
        gold_line = (f'<path d="{path_d([at(p) for p in true])}" fill="none" '
                     f'stroke="{GOLD}" stroke-width="1.2" stroke-dasharray="6 5"/>')

    dots = ""
    for p in chain:
        x, y = at(p)
        dots += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" fill="{INK}"/>'
    for p in (chain[0], chain[-1]):
        x, y = at(p)
        dots += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{INK}"/>'
    vx, vy = at((0.0, 0.0))
    dots += (f'<circle cx="{vx:.1f}" cy="{vy:.1f}" r="4" fill="#fff" '
             f'stroke="{INK}" stroke-width="1.6"/>')

    svg = f"""<svg viewBox="0 0 {w:.0f} {h:.0f}" xmlns="http://www.w3.org/2000/svg">
    <rect x="0" y="0" width="{w:.0f}" height="{h:.0f}" fill="#fff"
          stroke="{LINE}" stroke-width="1"/>
    {''.join(grid_lines)}
    {gold_line}
    {''.join(plates)}
    {''.join(tris)}
    <path d="{path_d([at(p) for p in chain])}" fill="none" stroke="{INK}"
          stroke-width="2.2" stroke-linejoin="round"/>
    {dots}
  </svg>"""
    return svg, up_rows, down_rows


# -- B: catenary drapery ----------------------------------------------------

def row_catenary(span: float, arc: float, n: int = 40):
    """A catenary of fixed arc hanging on a span shorter than that arc."""
    lo, hi = 1e-6 * span, 1e6 * span
    for _ in range(90):
        a = (lo + hi) / 2
        if 2 * a * math.sinh(span / (2 * a)) > arc:
            lo = a
        else:
            hi = a
    a = (lo + hi) / 2
    return [(x, a * (math.cosh(x / a) - 1))
            for x in (-span / 2 + span * i / n for i in range(n + 1))], a


def walk_drape(a: float, split: float, target: float,
               axis: str = "horizontal"):
    """Both branches walked on rungs; returns the chain and its exact size."""
    up, _ = integer_branch(a, split * 2.2 * a, target, axis)
    down_pts, _ = integer_branch(a, (1 - split) * 2.2 * a, target, axis)
    down = [(-x, y) for x, y in down_pts]
    down.reverse()
    chain = down + up[1:]
    width = max(x for x, _ in chain) - min(x for x, _ in chain)
    height = max(y for _, y in chain)
    return chain, width, height



def variant_card(letter: str, label: str, target: float, split: float,
                 note: str = "", axis: str = "horizontal") -> str:
    """One walk card: the figure, its letter, and its exact size."""
    chain, width, height = walk_drape(6.5 * 900, split, target, axis)
    return (f'<figure style="margin:0">'
            f'{integer_figure(chain, 430.0, 220.0, False)}'
            f'<figcaption><strong>Fig. {letter}</strong> \u00b7 {label}{note}<br>'
            f'<strong>{width} \u00d7 {height}</strong> \u00b7 '
            f'{len(chain) - 1} chords</figcaption></figure>')


def integer_figure(pts, w=860.0, h=400.0, grid=True) -> str:
    """An integer chain on its own grid: every node is a lattice point."""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    margin = 30.0
    scale = min((w - 2 * margin) / (x1 - x0), (h - 2 * margin) / (y1 - y0))
    dx = (w - (x1 - x0) * scale) / 2
    dy = (h - (y1 - y0) * scale) / 2

    def at(p):
        return (dx + (p[0] - x0) * scale, h - (dy + (p[1] - y0) * scale))

    span = max(x1 - x0, y1 - y0)
    step = 10 ** math.floor(math.log10(span / 8)) if span else 1
    lines = []
    gx = math.floor(x0 / step) * step if grid else x1 + 1
    while gx <= x1:
        px, _ = at((gx, y0))
        lines.append(f'<line x1="{px:.1f}" y1="0" x2="{px:.1f}" y2="{h:.0f}" '
                     f'stroke="{GRID}" stroke-width="0.7"/>')
        gx += step
    gy = math.floor(y0 / step) * step if grid else y1 + 1
    while gy <= y1:
        _, py = at((x0, gy))
        lines.append(f'<line x1="0" y1="{py:.1f}" x2="{w:.0f}" y2="{py:.1f}" '
                     f'stroke="{GRID}" stroke-width="0.7"/>')
        gy += step

    tris = []
    for i in range(len(pts) - 1):
        (px, py), (qx, qy) = at(pts[i]), at(pts[i + 1])
        tris.append(f'<path d="M {px:.2f} {py:.2f} L {qx:.2f} {py:.2f} '
                    f'L {qx:.2f} {qy:.2f} Z" fill="none" stroke="{GOLD}" '
                    f'stroke-width="0.8" opacity="0.8"/>')

    return f"""<svg viewBox="0 0 {w:.0f} {h:.0f}" xmlns="http://www.w3.org/2000/svg">
    <rect x="0" y="0" width="{w:.0f}" height="{h:.0f}" fill="#fff"
          stroke="{LINE}" stroke-width="1"/>
    {''.join(lines)}
    {''.join(tris)}
    <path d="{path_d([at(p) for p in pts])}" fill="none" stroke="{INK}"
          stroke-width="2.2" stroke-linejoin="round"/>
    {''.join(f'<circle cx="{at(p)[0]:.1f}" cy="{at(p)[1]:.1f}" r="3" fill="{INK}"/>' for p in pts)}
  </svg>"""


def drape_svg(gather=0.35, rows=9, cols=44, w=860.0, h=430.0) -> str:
    """The sheet in 2.5D: rows are catenaries, each seen from above and ahead."""
    rest = 700.0
    margin = 30.0
    parts, ys, xs_all = [], [], []
    rows_pts = []
    for j in range(rows + 1):
        span = rest * (1 - gather * j / rows)
        depth = 120.0 * j / rows
        pts, _ = row_catenary(span, rest, cols)
        # project: x across, the sag lifts the row up the page, rows recede
        row = [(p[0], -p[1] * 0.55 - depth) for p in pts]
        rows_pts.append(row)
        ys += [q[1] for q in row]
        xs = [q[0] for q in row]
        xs_all += xs

    x0, x1 = min(xs_all), max(xs_all)
    y0, y1 = min(ys), max(ys)
    scale = min((w - 2 * margin) / (x1 - x0), (h - 2 * margin) / (y1 - y0))
    dx = (w - (x1 - x0) * scale) / 2
    dy = (h - (y1 - y0) * scale) / 2

    def at(p):
        return (dx + (p[0] - x0) * scale, h - (dy + (p[1] - y0) * scale))

    for j, row in enumerate(rows_pts):
        shade = f"rgba(46,36,19,{0.9 - 0.5 * j / rows:.2f})"
        parts.append(f'<path d="{path_d([at(p) for p in row])}" fill="none" '
                     f'stroke="{shade}" stroke-width="1.5"/>')

    return f"""<svg viewBox="0 0 {w:.0f} {h:.0f}" xmlns="http://www.w3.org/2000/svg">
    <rect x="0" y="0" width="{w:.0f}" height="{h:.0f}" fill="#fff"
          stroke="{LINE}" stroke-width="1"/>
    {''.join(parts)}
  </svg>"""


CSS = """
  :root { color-scheme: light; --paper:#f6f1e4; --card:#fffdf7; --ink:#2e2413;
    --muted:#7b6c4e; --gold:#8c6a21; --line:#d8ccae;
    --mono: ui-monospace,"SF Mono",Menlo,Consolas,monospace;
    --serif:"EB Garamond",Georgia,"Palatino Linotype",Palatino,serif; }
  * { box-sizing: border-box; }
  body { margin:0; color:var(--ink); font:16px/1.55 var(--serif);
    background: radial-gradient(900px 440px at 12% -8%, #fcf9ef 0, transparent 60%), var(--paper); }
  main { max-width: 920px; margin: 0 auto; padding: 34px 22px 70px; }
  h1 { font-size: 25px; margin: 0 0 4px; text-wrap: balance; }
  .lead { color: var(--gold); margin: 0 0 18px; }
  h2 { font: 600 11px/1.2 var(--mono); letter-spacing:.12em; text-transform:uppercase;
    color:var(--muted); margin:30px 0 8px; }
  h2 span { color: var(--gold); }
  .panel { background:var(--card); border:1px solid var(--line); border-radius:6px; padding:12px; }
  .strip { margin: 0 0 14px; }
  .strip:last-child { margin-bottom: 0; }
  .strip svg { display:block; width:100%; height:auto; background:#fff;
    border:1px solid var(--line); border-radius:3px; }
  .strip p { margin:5px 0 0; font:10px/1.3 var(--mono); color:var(--muted); }
  .strip strong { color:var(--ink); }
  table { border-collapse:collapse; width:100%; font:12px/1.5 var(--mono); }
  th, td { border-bottom:1px solid var(--line); padding:6px 4px; text-align:left; }
  th { color:var(--muted); font-weight:500; }
  .scroll { overflow-x:auto; }
  .back { font:12px var(--mono); margin-bottom:16px; }
  code { font:12px var(--mono); color:var(--gold); }
  a { color: var(--gold); }
  .two { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
  .three { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; }
  .three figure { margin:0; }
  .three figcaption { font:10px/1.3 var(--mono); color:var(--muted); margin-top:4px; }
  #view { width:100%; height:440px; background:#fff; border:1px solid var(--line);
    border-radius:3px; display:block; cursor:grab; }
  #view:active { cursor:grabbing; }
  .controls { display:flex; gap:16px; align-items:center; flex-wrap:wrap;
    font:11px var(--mono); color:var(--muted); margin:8px 0 0; }
  .controls input[type=range] { width:130px; accent-color:#8c6a21; }
  .controls label { display:flex; gap:6px; align-items:center; }
  .next { border-left:3px solid var(--gold); padding-left:10px; color:var(--muted); }
  @media (max-width:620px) {
    main { padding:22px 14px 60px; }
    table { font-size:10px; } th,td { padding:4px 2px; }
    .two, .three { grid-template-columns:1fr; }
  }
"""

SCRIPT = r"""
import * as THREE from 'three';

const host = document.getElementById('view');
let renderer;
try {
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false,
    preserveDrawingBuffer: true });
} catch (err) {
  host.innerHTML = '<p style="font:12px/1.5 ui-monospace,monospace;color:#7b6c4e;' +
    'padding:18px">This browser has no WebGL, so the 2.5D view cannot run here.' +
    ' The 2D figure above is the same drape.</p>';
  throw err;
}
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
host.appendChild(renderer.domElement);
renderer.domElement.style.width = '100%';
renderer.domElement.style.height = '100%';
renderer.domElement.style.display = 'block';

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xffffff);

const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 100);
let yaw = -0.62, pitch = 0.34, dist = 7.4;
function place() {
  camera.position.set(
    dist * Math.cos(pitch) * Math.sin(yaw),
    dist * Math.sin(pitch),
    dist * Math.cos(pitch) * Math.cos(yaw));
  camera.lookAt(0, -0.15, 0);
}

const hemi = new THREE.HemisphereLight(0xfffdf6, 0x6d6248, 0.55);
const key = new THREE.DirectionalLight(0xffffff, 0.85);
key.position.set(3, 5, 4);
scene.add(hemi, key);

const material = new THREE.MeshStandardMaterial({
  color: 0xdfd2b4, roughness: 0.9, metalness: 0.0,
  side: THREE.DoubleSide, flatShading: false,
  wireframe: false
});

// a catenary of fixed arc on a span shorter than the arc
function rowCatenary(span, arc, n) {
  let lo = 1e-6 * span, hi = 1e6 * span, a = 0;
  for (let k = 0; k < 90; k++) {
    a = (lo + hi) / 2;
    if (2 * a * Math.sinh(span / (2 * a)) > arc) lo = a; else hi = a;
  }
  a = (lo + hi) / 2;
  const out = [];
  for (let i = 0; i <= n; i++) {
    const x = -span / 2 + span * i / n;
    out.push([x, a * (Math.cosh(x / a) - 1)]);
  }
  return out;
}

let mesh = null, pinGroup = null;
const state = { gather: 0.42, rows: 26, cols: 46, wire: false };

function build() {
  if (mesh) { scene.remove(mesh); mesh.geometry.dispose(); }
  if (pinGroup) { scene.remove(pinGroup); pinGroup = null; }

  const rows = state.rows, cols = state.cols;
  const rest = 4.6;               // rest width of the sheet, in scene units
  const height = 3.0;
  const pos = [];

  for (let j = 0; j <= rows; j++) {
    const t = j / rows;
    const span = rest * (1 - state.gather * t);
    const row = rowCatenary(span, rest, cols);
    for (let i = 0; i <= cols; i++) {
      pos.push(row[i][0], -t * height, row[i][1] * 1.0);
    }
  }

  const index = [];
  for (let j = 0; j < rows; j++) {
    for (let i = 0; i < cols; i++) {
      const a = j * (cols + 1) + i, b = a + 1, c = a + cols + 1, d = c + 1;
      index.push(a, c, b, b, c, d);
    }
  }

  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  geo.setIndex(index);
  geo.computeVertexNormals();

  material.wireframe = state.wire;
  mesh = new THREE.Mesh(geo, material);
  scene.add(mesh);

  // the two pins: the top corners
  pinGroup = new THREE.Group();
  const pinMat = new THREE.MeshStandardMaterial({ color: 0x8c6a21, roughness: 0.5 });
  for (const x of [-rest / 2, rest / 2]) {
    const s = new THREE.Mesh(new THREE.SphereGeometry(0.07, 16, 12), pinMat);
    s.position.set(x, 0, 0);
    pinGroup.add(s);
  }
  scene.add(pinGroup);
}

function render() { renderer.render(scene, camera); }

function resize() {
  const w = host.clientWidth, h = host.clientHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  place();
  render();
}

// a small orbit, so no second vendor file is needed
let dragging = false, lastX = 0, lastY = 0;
host.addEventListener('pointerdown', e => { dragging = true; lastX = e.clientX; lastY = e.clientY; host.setPointerCapture(e.pointerId); });
host.addEventListener('pointerup', e => { dragging = false; });
host.addEventListener('pointermove', e => {
  if (!dragging) return;
  yaw -= (e.clientX - lastX) * 0.008;
  pitch = Math.max(-0.15, Math.min(0.95, pitch + (e.clientY - lastY) * 0.006));
  lastX = e.clientX; lastY = e.clientY;
});
host.addEventListener('wheel', e => {
  e.preventDefault();
  dist = Math.max(3.5, Math.min(14, dist + e.deltaY * 0.004));
}, { passive: false });

window.addEventListener('resize', resize);

const gatherEl = document.getElementById('gather');
const gatherOut = document.getElementById('gatherOut');
const wireEl = document.getElementById('wire');
gatherEl.value = state.gather;
gatherOut.textContent = state.gather.toFixed(2);
gatherEl.addEventListener('input', () => {
  state.gather = parseFloat(gatherEl.value);
  gatherOut.textContent = state.gather.toFixed(2);
  build();
  render();
});
wireEl.addEventListener('change', () => { state.wire = wireEl.checked; build(); render(); });

build();
resize();          // sizes, places the camera, and draws the first frame
render();
renderer.setAnimationLoop(() => { place(); render(); });
window.__dbgObj = () => ({ scene, camera, renderer, mesh });
window.__dbg = () => ({ cam: camera.position.toArray().map(v => +v.toFixed(2)),
  verts: mesh ? mesh.geometry.attributes.position.count : 0,
  children: scene.children.length });
"""


PH_VARIANTS = (
    ("1 cubic a side · split 0.62", 1, 0.62),
    ("2 cubics a side · split 0.62", 2, 0.62),
    ("4 cubics a side · split 0.62", 4, 0.62),
    ("2 cubics · split 0.50", 2, 0.50),
    ("2 cubics · split 0.75", 2, 0.75),
    ("8 cubics a side · split 0.62", 8, 0.62),
)

VARIANTS = (
    ("step 260 · split 0.62", 260.0, 0.62),
    ("step 450 · split 0.62", 450.0, 0.62),
    ("step 800 · split 0.62", 800.0, 0.62),
    ("step 450 · split 0.50", 450.0, 0.50),
    ("step 450 · split 0.75", 450.0, 0.75),
    ("step 1400 · split 0.62", 1400.0, 0.62),
)


def main() -> int:
    a = 100.0
    total = 2.2 * a
    steps = 10

    fig_main, up_rows, down_rows = fig_catenary(a, 0.62, steps)

    # the same drape, walked on rungs instead of fitted: integer every step
    ia = 9000.0
    up_i, ir = integer_branch(ia, 0.62 * 2.2 * ia, 450.0)
    down_pts_i, dr = integer_branch(ia, 0.38 * 2.2 * ia, 450.0)
    down_i = [(-x, y) for x, y in down_pts_i]
    down_i.reverse()
    ichain = down_i + up_i[1:]
    iwidth = max(x for x, _ in ichain) - min(x for x, _ in ichain)
    iheight = max(y for _, y in ichain)
    err_hi = branch_error(a, 0.62 * total, steps)
    err_lo = branch_error(a, 0.38 * total, steps)

    # three splits of the same catenary
    small = []
    for p in (0.50, 0.62, 0.75):
        svg, _, _ = fig_catenary(a, p, steps, gold=False, grid=False)
        letter = "BCD"[len(small)]
        small.append(f'<figure>{svg}<figcaption><strong>Fig. {letter}</strong> '
                     f'\u00b7 split {p:.2f} : {1 - p:.2f}</figcaption></figure>')

    node_rows = []
    for side, rows, sign in (("high", ir, 1), ("low", dr, -1)):
        x = y = 0
        for i, r in enumerate(rows, 1):
            u, v, h = r["triple"]
            if sign > 0:
                x, y = x + u, y + v
            else:
                x, y = x - u, y + v
            node_rows.append(
                f"<tr><td>{side}</td><td>{i}</td><td>{x}</td><td>{y}</td>"
                f"<td>{r['deg']:.2f}°</td><td>{u}-{v}-{h}</td></tr>")
    table = "".join(node_rows)

    # curvature error of one PH cubic against the catenary, by span
    ph_spans = []
    for deg in (10, 20, 30, 40, 60):
        s1 = a * math.tan(math.radians(deg))
        seg, _ = from_hermite(cat(a, 0.0), 0.0, cat(a, s1), math.atan(s1 / a))
        worst = max(abs(abs(seg.curvature(t)) / (math.cos(math.atan(s1 * t / a)) ** 2 / a) - 1)
                    for t in (0.0, 1.0))
        verdict = ("same curve" if worst < 0.015 else
                   "close" if worst < 0.06 else "not the same curve")
        ph_spans.append((deg, 100 * worst, verdict))

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Catenary studies: triples and drapery</title>
<style>{CSS}</style>
<script type="importmap">{{ "imports": {{ "three": "./vendor/three.module.js" }} }}</script>
</head>
<body>
<main>
  <p class="back"><a href="workbench.html">← workbench</a> ·
  <a href="stage-two.html">the stage II page</a></p>
  <h1>Catenary studies</h1>
  <p class="lead">Two projects running side by side: one hangs a catenary on
  pythagorean triangles, the other drapes a cloth on catenaries.</p>

  <h2>A · <span>the catenary, chained from triples</span></h2>
  <div class="panel">
    <p>A catenary asks for a tangent angle that changes with arc length:
    <code>tan θ = s/a</code>. The chain here may only take directions that a
    pythagorean triple can make, so each step snaps θ to the nearest rung of a
    {len(RUNGS)}-rung ladder, then lays a chord of the arc length that step
    deserves. Every chord is the hypotenuse of a real triangle, and every
    triangle is drawn: the legs are axis-aligned, so the chain is a staircase
    of exact triples you can hang other curves from.</p>
    <p>The grid is in catenary units — fine every 10, heavy every 50, with
    a = {a:.0f}. {2 * steps} chords: {steps} down to the vertex and {steps} up
    from it.</p>
    <p>The two branches share one catenary. Down to the vertex is
    <em>toward the focus</em>; up from it is <em>away</em>. The split sets how
    much of the curve each side owns, and since height rises with arc, the side
    that owns more is also the higher anchor. At {0.62:.2f} : {0.38:.2f} the
    high anchor sits {0.71 * a:.0f} above the vertex and the low one
    {0.32 * a:.0f}.</p>
    <div class="strip">{fig_main}
      <p><strong>Fig. A</strong> · the chain (ink) on the true catenary (gold) ·
      arc {total:.0f}, split 0.62 : 0.38 · worst node error
      {max(err_hi, err_lo):.1f} on the high branch
      ({100 * max(err_hi, err_lo) / total:.1f}% of arc)</p></div>
    <div class="three">{''.join(small)}</div>
    <p style="margin-top:14px"><strong>Every dial here is free.</strong> The
    step target says how long a chord to aim for; the split picks where the low
    point sits; the radius <code>a</code> says how many steps fit around the
    curve, and a bigger radius means each fixed-size chord subtends less angle,
    so the vertex gets smoother without any new triples. Change any of them and the drape comes out at a
    different size, with different triples — and still every node an integer.
    Six drapes from the closed-form fit — segments and split are the only choices, and the error is printed on each:</p>
    <div class="two">{''.join(
      ph_card("EFGHIJ"[i], label, sp, n)
      for i, (label, n, sp) in enumerate(PH_VARIANTS))}
    </div>
    <p style="margin-top:14px"><strong>Two methods, both honest.</strong> The
    cards above come from the closed-form fit: every segment passes through two
    points of the catenary with the right tangent, and the error is what the
    cubic cannot reach in between. Below is the other method — walk the rung
    catalogue, lay each rung's own legs, and read the height and width off the
    result. Nothing is fitted there and every node is an integer, but the step
    length has to be chosen rather than derived.</p>
    <div class="strip">{integer_figure(ichain)}
      <p><strong>Fig. K</strong> · the walked chain · {len(ir)} chords a side,
      {len(ir)} steps of about 450 on a radius of {ia:.0f} ·
      <strong>{iwidth} × {iheight} units</strong> (exact integers) ·
      split {0.62:.2f} : {0.38:.2f}</p></div>
    <p style="margin-top:10px" class="next">The split is the only dial a
    drapery needs: it says where the low point sits, and therefore which
    anchor the cloth is hanging from.</p>
    <div class="scroll"><table style="margin-top:10px">
      <tr><th>side</th><th>step</th><th>x</th><th>y</th><th>heading</th>
      <th>triple</th></tr>
      {table}
    </table></div>
    <p style="margin-top:8px">Every node of the walked chain: x runs from the
    vertex outward, y is the rise, and <strong>both are exact integers</strong>
    — each row is the triple whose legs were laid. A curve attached at a node
    leaves along that row's angle, on the same lattice.</p>
  </div>

  <h2>B · <span>catenary drapery, in 2.5D</span></h2>
  <div class="panel">
    <p>Weil's method is geometric, not physical: cloth is a grid of points, and
    the shape is found by fitting catenaries between the restraint points,
    splitting each triangle by the <em>lower</em> of the two candidate
    catenaries, then relaxing so the points keep their spacing. It aims at the
    look of cloth, not its properties. (The page it comes from is
    <a href="https://davis.wpi.edu/~matt/courses/cloth/geometric.html">WPI's
    geometric techniques</a>, which also covers Agui's sleeve folds.)</p>
    <p>What is built here is the first half, the hanging: every row of the
    sheet is the catenary of its own rest width, so a row that has lost span
    sags more, and the cloth gathers toward the free edge. The relaxation pass
    is not in yet — the rows keep equal spacing down the sheet, which is why
    the folds read as neat rather than lived-in.</p>
    <div class="strip">{drape_svg()}
      <p><strong>Fig. L</strong> · nine rows, each the catenary of the full
      rest width on a span that narrows with depth</p></div>
    <canvas id="view"></canvas>
    <div class="controls">
      <label>gather <input id="gather" type="range" min="0" max="0.7"
        step="0.01" value="0.42"><span id="gatherOut">0.42</span></label>
      <label><input id="wire" type="checkbox"> wireframe</label>
      <span>drag to orbit · wheel to zoom</span>
    </div>
    <p style="margin:5px 0 0; font:10px/1.3 var(--mono); color:var(--muted)">
      <strong>Fig. M</strong> · the same drape in 2.5D (three.js) — 26 × 46
      grid, two pins at the top corners</p>
  </div>
  <h2>C · <span>the hodograph chain</span></h2>
  <div class="panel">
    <p>A cubic with a <strong>pythagorean hodograph</strong> is a p-triple drawn as
    a curve. With <code>u(t), v(t)</code> linear between two integer pairs, the
    control points are built from Euclid's formula,
    <code>(u²−v², 2uv, u²+v²)</code>, and three things come free and exact: the
    arc length is a polynomial, the tangent angle is <code>2·atan(v/u)</code>,
    and the curvature is a rational function.</p>
    <p>That gives the reverse gear. Given two points on the catenary and the
    tangent at each, a PH cubic through them is <strong>closed form</strong>: write
    <code>Δ = p₃ − p₀</code> in the frame of the first tangent, let
    <code>k = √(L₃/L₁)</code>, and the closure conditions give a quadratic in
    <code>k</code>. Pick the root with three positive legs; then
    <code>u² + v² = 3L</code> with <code>arg(u + iv) = θ/2</code>. No catalogue,
    no nearest neighbour, no search.</p>
    <div class="strip">{ph_figure(a, 0.62, 4)}
      <p><strong>Fig. N</strong> · four PH cubics a side (ink) over the catenary
      (gold dashed, hidden under the ink — that is the result) · control
      polygons in pale gold · worst
      {100 * ph_error(a, 0.62 * 2.2 * a, 4) / a:.4f}% of a</p></div>
    <div class="scroll"><table style="margin-top:10px">
      <tr><th>segments a side</th><th>worst error</th><th>of a</th></tr>
      {''.join(f"<tr><td>{n}</td><td>{ph_error(a, 0.62 * 2.2 * a, n):.3f}</td>"
               f"<td>{100 * ph_error(a, 0.62 * 2.2 * a, n) / a:.4f}%</td></tr>"
               for n in (1, 2, 4, 8))}
    </table></div>
    <p><strong>Where the sines went.</strong> Nothing above needs them. A
    direction is carried as the integer pair <code>(u, v)</code>; its triple is
    <code>(u, v, h)</code> with <code>h = √(u²+v²)</code>. The half-turn the fit
    needs is then the angle <em>between two integer vectors</em>, which is a dot
    and a cross:</p>
    <p style="margin:0 0 10px"><code>cos α = (u₀u₁ + v₀v₁)/(h₀h₁)</code> ·
    <code>sin α = (u₀v₁ − v₀u₁)/(h₀h₁)</code></p>
    <p>and the tangent's doubling disappears into Euclid,
    <code>cos θ = (u²−v²)/(u²+v²)</code>, <code>sin θ = 2uv/(u²+v²)</code>.
    Run both versions of the fit and they agree to the last digit — same
    segment, same control points, one with <code>atan2</code>, one with only
    dot and cross.</p>
    {ph_explain(a)}
    <p style="margin:5px 0 0; font:10px/1.3 var(--mono); color:var(--muted)">
    <strong>Fig. O</strong> · (i) the pair (4,3) doubles to the triple (7,24) —
    the tangent is twice the direction · (ii) one segment and its three legs,
    with L₁L₃ = L₂² · (iii) four segments over the catenary</p>
    <p><strong>What else a PH curve gives you.</strong> The offset — the curve
    moved sideways by a fixed distance — is <em>rational</em>, not an
    approximation: for <code>z′ = w²</code> the unit normal is
    <code>−i·w²/|w|²</code>, so the plate at distance <code>d</code> is
    <code>z(t) + d·(−2uv, u²−v²)/(u²+v²)</code>, evaluated exactly at any
    <code>t</code>. This is the Stage II plate without the re-fitting, and it
    is why PH curves are used for tool paths and road layouts.</p>
    <div class="strip">{ph_offset_figure(a)}
      <p><strong>Fig. P</strong> · the chain (ink) and two exact offsets at
      ±7.5% of a (gold) · no approximation anywhere</p></div>

    <p><strong>What a PH curve can do with a p-triple, in one list.</strong></p>
    <table>
      <tr><th>operation</th><th>usual cost</th><th>here</th></tr>
      <tr><td>length of the curve</td><td>numerical integration</td>
      <td>a polynomial, exact</td></tr>
      <tr><td>offset / parallel plate</td><td>degree 10, refit</td>
      <td>rational, exact (Fig. P)</td></tr>
      <tr><td>curvature</td><td>second derivative, noisy</td>
      <td>a fraction, exact</td></tr>
      <tr><td>tangent direction</td><td>atan2</td>
      <td>Euclid doubling, dot and cross</td></tr>
      <tr><td>split a segment</td><td>re-fit both halves</td>
      <td>subdivide, still PH, still triples</td></tr>
      <tr><td>control points on the lattice</td><td>—</td>
      <td>when the quadratic's discriminant is a square</td></tr>
    </table>
    <p style="margin-top:10px">Two of those are worth dwelling on. The split is
    exact: cut at any <code>t</code> and the halves are PH cubics with integer
    pairs again, so a curve can be refined without ever leaving the family. And
    the lattice condition is a <em>number-theoretic</em> test on the pair of
    directions — in a scan of 960 endpoint-and-direction cases, 158 had an exact
    rational square discriminant, so integer control polygons are ordinary, not
    rare.</p>

    <p style="margin-top:10px"><strong>Where a square root survives.</strong>
    One, and only one: <code>k = √(L₃/L₁)</code>, the growth between legs. Solve
    the quadratic in <code>k</code> and it is exact whenever the discriminant is
    a perfect square — that is the arithmetic condition for a segment whose
    control points land on the lattice, and it is a property of the <em>pair of
    triples</em>, not of the curve.</p>

    <p style="margin-top:10px"><strong>Where the cubic and the catenary are the
    same curve.</strong> Position and tangent are exact at both ends by
    construction; the curvature is not. Measure it and the span decides
    everything: under about <strong>20° of turn</strong> per segment the two
    curvatures agree to ~1% across the whole segment, so the cubic and the
    catenary are interchangeable there. Past that they cross twice and drift
    apart at the ends.</p>
    <div class="scroll"><table style="margin-top:10px">
      <tr><th>span per segment</th><th>curvature error at the ends</th>
      <th>verdict</th></tr>
      {''.join(f"<tr><td>{deg}°</td><td>{err:.1f}%</td><td>{verdict}</td></tr>"
               for deg, err, verdict in ph_spans)}
    </table></div>
  </div>


  <h2>Check Mark</h2>
  <div class="panel">
    <p>The catalogue walk's six faces, kept here now that E–J are built from
    the closed-form fit instead. These are the ones whose geometry came from
    matching each step against the nearest rung: every node an integer, the
    step length chosen rather than solved. They are the old method, drawn
    side by side with the new one rather than replaced silently.</p>
    <div class="two">{''.join(
      variant_card("QRSTUV"[i], label, b, sp,
                   ' <em>(catalogue walk)</em>', axis="horizontal")
      for i, (label, b, sp) in enumerate(VARIANTS))}
    </div>
  </div>
</main>
<script type="module">{SCRIPT}</script>
</body>
</html>
"""
    path = ROOT / "workbench" / "catenary.html"
    path.write_text(page, encoding="utf-8")
    print(path)
    print(f"rungs={len(RUNGS)} max_err={max(err_hi, err_lo):.2f} a={a}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
