"""Cut the clothoid at its centre, then box the halves.

    .venv/bin/python scripts/clothoid_cut.py
    open workbench/clothoid-cut.html

The unit clothoid is

    x(s) = int_0^s cos(t^2/2) dt,   y(s) = int_0^s sin(t^2/2) dt.

Its eye is the limit as s -> infinity.  With u = s/sqrt(2),

    x_inf = sqrt(2) int_0^inf cos(u^2) du = sqrt(pi)/2,

and the same for y, so the two centres are

    (sqrt(pi)/2, sqrt(pi)/2) ~ (0.886227, 0.886227)

and its point reflection.  The line between them is y = x and passes through
the origin, which is where the equal-arc-length cut is made.  The spiral then
crosses that line infinitely often as it closes on the eye; those later
crossings are windings, not cuts.

The second experiment is the minimum-width box.  For a direction n the width
is max(p.n) - min(p.n).  At its minimum the two support lines are parallel and
each is tangent at one point: a double normal, not a double tangent.  The box
edge is the tangent line, so the two tangents are distinct whenever the width
is positive.  The numbers are printed in the page; the box cannot collapse to
the double tangent.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import hearts as H  # noqa: E402

INK, GOLD, DOT = "#2e2413", "#c9a441", "#b23a2b"
OVERLAY = "#1f5fa8"
GRID, LINE, MUTED = "#ece4cf", "#d8ccae", "#7b6c4e"

C = math.sqrt(math.pi) / 2.0
S = 40.0
N = 40000
TABLE_PHI = math.radians(321.544)    # 38.456 degrees clockwise


def width_at(points, theta):
    c, s = math.cos(theta), math.sin(theta)
    vals = [x * c + y * s for x, y in points]
    return max(vals) - min(vals), vals


def extent_at(points, theta):
    c, s = math.cos(theta), math.sin(theta)
    n = [x * c + y * s for x, y in points]
    m = [-x * s + y * c for x, y in points]
    return max(n) - min(n), max(m) - min(m)


def convex_hull(points):
    pts = sorted(set(points))
    if len(pts) <= 1:
        return pts

    def cross(o, a, b):
        return ((a[0] - o[0]) * (b[1] - o[1]) -
                (a[1] - o[1]) * (b[0] - o[0]))

    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def min_width(hull, samples=3600):
    best = (9e9, 0.0)
    for i in range(samples):
        th = math.pi * i / samples
        w, _ = width_at(hull, th)
        if w < best[0]:
            best = (w, th)
    lo = best[1] - math.pi / samples
    hi = best[1] + math.pi / samples
    for _ in range(80):
        m1 = lo + (hi - lo) / 3
        m2 = hi - (hi - lo) / 3
        w1, _ = width_at(hull, m1)
        w2, _ = width_at(hull, m2)
        if w1 < w2:
            hi = m2
        else:
            lo = m1
    th = (lo + hi) / 2
    w, _ = width_at(hull, th)
    return w, th


def supports(points, theta):
    _, vals = width_at(points, theta)
    imin = min(range(len(vals)), key=vals.__getitem__)
    imax = max(range(len(vals)), key=vals.__getitem__)
    return points[imin], points[imax]


def scale(points, w, h, pad=0.10):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    x0, x1 = x0 - pad * (x1 - x0), x1 + pad * (x1 - x0)
    y0, y1 = y0 - pad * (y1 - y0), y1 + pad * (y1 - y0)
    k = min((w - 18) / (x1 - x0), (h - 18) / (y1 - y0))
    ox = (w - (x1 - x0) * k) / 2
    oy = (h - (y1 - y0) * k) / 2

    def put(p):
        return ox + (p[0] - x0) * k, h - (oy + (p[1] - y0) * k)

    return put, (x0, x1, y0, y1)


def path(points, put, colour, width, dash=None):
    d = "M " + " L ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}" for p in points)
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="{d}" fill="none" stroke="{colour}" '
            f'stroke-width="{width}"{extra}/>')


def cut_figure(pts, w=520.0, h=520.0):
    half = [(x, y) for s, x, y in pts]
    other = [(-x, -y) for x, y in half]
    allpts = half + other + [(C, C), (-C, -C)]
    put, (x0, x1, y0, y1) = scale(allpts, w, h, pad=0.08)
    grid = []
    for i in range(1, 8):
        gx = x0 + (x1 - x0) * i / 8
        a, b = put((gx, y0)), put((gx, y1))
        grid.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" '
                    f'x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{GRID}"/>')
        gy = y0 + (y1 - y0) * i / 8
        a, b = put((x0, gy)), put((x1, gy))
        grid.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" '
                    f'x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{GRID}"/>')
    a, b = put((-C, -C)), put((C, C))
    eye1, eye2 = put((-C, -C)), put((C, C))
    return f"""<svg viewBox="0 0 {w:.0f} {h:.0f}" xmlns="http://www.w3.org/2000/svg">
    <rect x="0" y="0" width="{w:.0f}" height="{h:.0f}" fill="#fffdf7" stroke="{LINE}"/>
    {''.join(grid)}
    {path(other, put, MUTED, 1.7)}
    {path(half, put, INK, 2.5)}
    <line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}"
          stroke="{GOLD}" stroke-width="1" stroke-dasharray="6 4"/>
    <circle cx="{eye1[0]:.1f}" cy="{eye1[1]:.1f}" r="4" fill="{GOLD}"/>
    <circle cx="{eye2[0]:.1f}" cy="{eye2[1]:.1f}" r="4" fill="{GOLD}"/>
    <circle cx="{put((0, 0))[0]:.1f}" cy="{put((0, 0))[1]:.1f}" r="4"
            fill="{DOT}" stroke="#fffdf7" stroke-width="1.2"/>
    <text x="{eye2[0] + 8:.1f}" y="{eye2[1] - 8:.1f}" font-size="11"
          fill="{MUTED}">+eye</text>
    <text x="{eye1[0] - 34:.1f}" y="{eye1[1] + 16:.1f}" font-size="11"
          fill="{MUTED}">−eye</text>
    <text x="{put((0, 0))[0] + 6:.1f}" y="{put((0, 0))[1] - 7:.1f}"
          font-size="11" fill="{DOT}">cut</text>
  </svg>"""


def boxed_figure(points, theta, w=430.0, h=340.0):
    c, s = math.cos(theta), math.sin(theta)
    frame = [(x * c + y * s, -x * s + y * c) for x, y in points]
    # the tight data bounds, not the padded view bounds, are the box
    x0 = min(p[0] for p in frame)
    x1 = max(p[0] for p in frame)
    y0 = min(p[1] for p in frame)
    y1 = max(p[1] for p in frame)
    put, _ = scale(frame, w, h, pad=0.12)
    sp = supports(points, theta)
    # the left/right edges are the support lines (and the tangent lines)
    tl, tr = put((x0, y0)), put((x0, y1))
    bl, br = put((x1, y0)), put((x1, y1))
    sf = [(p[0] * c + p[1] * s, -p[0] * s + p[1] * c) for p in sp]
    pl, pr = put(sf[0]), put(sf[1])
    return f"""<svg viewBox="0 0 {w:.0f} {h:.0f}" xmlns="http://www.w3.org/2000/svg">
    <rect x="0" y="0" width="{w:.0f}" height="{h:.0f}" fill="#fffdf7" stroke="{LINE}"/>
    {path(frame, put, INK, 2.3)}
    <rect x="{put((x0, y1))[0]:.1f}" y="{put((x0, y1))[1]:.1f}"
          width="{put((x1, y0))[0] - put((x0, y1))[0]:.1f}"
          height="{put((x0, y0))[1] - put((x0, y1))[1]:.1f}"
          fill="none" stroke="{LINE}" stroke-width="1"/>
    <line x1="{tl[0]:.1f}" y1="{tl[1]:.1f}" x2="{tr[0]:.1f}" y2="{tr[1]:.1f}"
          stroke="{OVERLAY}" stroke-width="1.6"/>
    <line x1="{bl[0]:.1f}" y1="{bl[1]:.1f}" x2="{br[0]:.1f}" y2="{br[1]:.1f}"
          stroke="{OVERLAY}" stroke-width="1.6"/>
    <circle cx="{pl[0]:.1f}" cy="{pl[1]:.1f}" r="4" fill="{DOT}"/>
    <circle cx="{pr[0]:.1f}" cy="{pr[1]:.1f}" r="4" fill="{DOT}"/>
  </svg>"""


def table_contact(points, phi=TABLE_PHI):
    """The two lowest points of the rotated full curve, and their heights."""
    c, s = math.cos(phi), math.sin(phi)
    frame = [(x * c - y * s, x * s + y * c) for x, y in points]
    ys = [p[1] for p in frame]
    mins = [(ys[i], i) for i in range(1, len(ys) - 1)
            if ys[i] <= ys[i - 1] and ys[i] <= ys[i + 1]]
    mins.sort()
    (y1, i1), (y2, i2) = mins[0], mins[1]
    return frame, i1, i2, y1, y2


def table_figure(points, w=880.0, h=360.0):
    """The full ± curve rotated onto a near-horizontal support line."""
    frame, i1, i2, y1, y2 = table_contact(points)
    p1, p2 = frame[i1], frame[i2]
    put, _ = scale(frame, w, h, pad=0.10)
    a = put((min(q[0] for q in frame), y1))
    b = put((max(q[0] for q in frame), y1))
    q1, q2 = put(p1), put(p2)
    gap = y2 - y1
    lx, ly = q2[0] + 14, q2[1] - 22
    svg = f"""<svg viewBox="0 0 {w:.0f} {h:.0f}" xmlns="http://www.w3.org/2000/svg">
    <rect x="0" y="0" width="{w:.0f}" height="{h:.0f}" fill="#fffdf7" stroke="{LINE}"/>
    {path(frame, put, INK, 2.0)}
    <line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}"
          stroke="{GOLD}" stroke-width="1.4"/>
    <circle cx="{q1[0]:.1f}" cy="{q1[1]:.1f}" r="4.2" fill="{DOT}"/>
    <circle cx="{q2[0]:.1f}" cy="{q2[1]:.1f}" r="4.2" fill="{DOT}"/>
    <line x1="{q2[0]:.1f}" y1="{q2[1]:.1f}" x2="{lx:.1f}" y2="{ly:.1f}"
          stroke="{DOT}" stroke-width="1" stroke-dasharray="3 3"/>
    <text x="{lx + 4:.1f}" y="{ly - 2:.1f}" font-size="11" fill="{DOT}">
      second contact +{gap:.5f}</text>
  </svg>"""
    c, s = math.cos(TABLE_PHI), math.sin(TABLE_PHI)

    def inv(p):
        return (p[0] * c + p[1] * s, -p[0] * s + p[1] * c)

    return svg, inv(p1), inv(p2), gap


def width_chart(half, full, half_th, full_th, w=880.0, h=300.0):
    angles = [math.pi * i / 360 for i in range(361)]
    wh = [width_at(half, t)[0] for t in angles]
    wf = [width_at(full, t)[0] for t in angles]
    lo = min(min(wh), min(wf))
    hi = max(max(wh), max(wf))
    pad = (hi - lo) * 0.14
    y_lo, y_hi = lo - pad, hi + pad
    put, _ = scale([(0, y_lo), (180, y_hi)], w, h, pad=0.10)

    def line(p, q, colour, width=1.0):
        a, b = put(p), put(q)
        return (f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" '
                f'x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{colour}" '
                f'stroke-width="{width}"/>')

    grid = [line((deg, y_lo), (deg, y_hi), GRID) for deg in (0, 90, 180)]
    grid += [line((0, val), (180, val), GRID)
             for val in (y_lo, (y_lo + y_hi) / 2, y_hi)]

    def curve(vals, colour):
        d = "M " + " L ".join(
            f"{put((i / 360 * 180, v))[0]:.1f} {put((i / 360 * 180, v))[1]:.1f}"
            for i, v in enumerate(vals))
        return (f'<path d="{d}" fill="none" stroke="{colour}" '
                f'stroke-width="2"/>')

    def mark(theta, val, colour):
        p = put((math.degrees(theta) % 180, val))
        return (f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="4.5" '
                f'fill="{colour}" stroke="#fffdf7" stroke-width="1.2"/>'
                f'<text x="{p[0] + 7:.1f}" y="{p[1] - 7:.1f}" font-size="10" '
                f'fill="{colour}">{val:.3f}</text>')

    labels = "".join(
        f'<text x="{put((deg, y_lo))[0]:.1f}" y="{h - 6:.1f}" '
        f'text-anchor="middle" font-size="10" fill="{MUTED}">{deg}°</text>'
        for deg in (0, 90, 180))
    labels += "".join(
        f'<text x="6" y="{put((0, val))[1] + 3:.1f}" font-size="10" '
        f'fill="{MUTED}">{val:.2f}</text>'
        for val in (y_lo, (y_lo + y_hi) / 2, y_hi))

    return f"""<svg viewBox="0 0 {w:.0f} {h:.0f}" xmlns="http://www.w3.org/2000/svg">
    <rect x="0" y="0" width="{w:.0f}" height="{h:.0f}" fill="#fffdf7" stroke="{LINE}"/>
    {''.join(grid)}
    {curve(wh, INK)}
    {curve(wf, OVERLAY)}
    {mark(half_th, width_at(half, half_th)[0], INK)}
    {mark(full_th, width_at(full, full_th)[0], OVERLAY)}
    {labels}
  </svg>"""


def main():
    pts = H.clothoid(s_max=S, n=N)
    half = [(x, y) for s, x, y in pts]
    full = half + [(-x, -y) for x, y in half]
    half_hull = convex_hull(half)
    full_hull = convex_hull(full)
    half_w, half_th = min_width(half_hull)
    full_w, full_th = min_width(full_hull)
    half_h, _ = extent_at(half, half_th)[1], None
    full_h, _ = extent_at(full, full_th)[1], None
    print(f"  half  min width {half_w:.6f} at {math.degrees(half_th) % 180:.2f} deg"
          f"  height {half_h:.6f}")
    print(f"  full  min width {full_w:.6f} at {math.degrees(full_th) % 180:.2f} deg"
          f"  height {full_h:.6f}")
    tab_svg, tab1, tab2, tab_gap = table_figure(full)
    print(f"  table contact gap {tab_gap:.6f} at 38.46 deg CW")

    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Clothoid cut — the eye, the box, and the double normal</title>
<style>
body{{margin:0;background:#f6f1e4;color:{INK};font:16px/1.55 Georgia,serif}}
main{{max-width:1040px;margin:0 auto;padding:34px 22px 70px}}
h1{{font-size:28px;margin:0 0 4px}}
.lead{{color:#8c6a21;margin:0 0 22px}}
h2{{font:600 11px/1.2 ui-monospace,Menlo,monospace;letter-spacing:.12em;
text-transform:uppercase;color:{MUTED};margin:0 0 4px}}
.cap{{font-size:12px;color:{MUTED};margin:0}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
section{{background:#fffdf7;border:1px solid {LINE};padding:12px}}
.art{{background:#fffdf7;margin:4px 0 8px}}
svg{{display:block;width:100%;height:auto}}
.panel{{background:#fffdf7;border:1px solid {LINE};padding:16px 18px;margin:0 0 20px}}
li{{margin:0 0 6px}}
table{{border-collapse:collapse;margin:0 0 14px;font:12px/1.5 ui-monospace,Menlo,monospace}}
th,td{{border-bottom:1px solid {LINE};padding:4px 14px 4px 0;text-align:left}}
th{{color:{MUTED};font-weight:600}}
</style></head><body><main>
<h1>Clothoid cut</h1>
<p class="lead">The eye is <code>(√π/2, √π/2)</code>.  Cut the curve at the
origin and box one half: the box's best width is a double normal, not a double
tangent.  The full ± curve on a table is a different pair — 38.5° clockwise
leaves its outer turns level to {tab_gap:.5f}.</p>
<div class="panel">
<p><strong>The centre is exact.</strong> With <code>x(s)=∫cos(t²/2)dt</code> and
<code>u=s/√2</code>, the limit is <code>√2∫₀^∞cos(u²)du = √π/2</code>, so the two
eyes are <code>(±√π/2, ±√π/2) = (±0.886227, ±0.886227)</code>.  The line joining
them is <code>y=x</code> and it passes through the origin.  The equal-arc cut is
at the origin; the spiral crosses that line infinitely often on the way to the
eye, and those later crossings are windings, not cuts.</p>
<p><strong>The box minimum is measured, not a guess.</strong> For a direction
<code>n</code> the width is <code>max(p·n) − min(p·n)</code>.  Scanning the
convex hull and refining gives the numbers below.  At a minimum the two support
lines are parallel and each is tangent at one point — a <strong>double
normal</strong>.  The box edge <em>is</em> the tangent line, so the two tangent
lines are distinct whenever the width is positive.  A double tangent needs one
line touching twice, which the box cannot supply.</p>
<table>
<tr><th>curve</th><th>min width</th><th>angle</th><th>height at that angle</th></tr>
<tr><td>half, s ≥ 0</td><td>{half_w:.4f}</td><td>{math.degrees(half_th) % 180:.1f}°</td><td>{half_h:.4f}</td></tr>
<tr><td>full, s ≥ 0 plus its point reflection</td><td>{full_w:.4f}</td><td>{math.degrees(full_th) % 180:.1f}°</td><td>{full_h:.4f}</td></tr>
</table>
<p style="font-size:12px;color:{MUTED}">The 0.079 figure is the <em>same-half
mirror join</em>, where both contacts are on one half (the table on
<code>hearts.html</code>); that pair sits near the eye.  The full ± curve is
different: at 38.5° clockwise its two outer turns are level to
<strong>{tab_gap:.5f}</strong> (Fig. 5).  That is the usable table contact.  The box's
best is still {full_w:.3f}, so the box is not that join.</p>
</div>
<div class="grid2">
<section><h2>Fig. 1 · the cut</h2><div class="art">{cut_figure(pts)}</div>
<p class="cap">the two halves are point reflections; the cut is at the origin
on the line between the eyes</p></section>
<section><h2>Fig. 2 · one half, minimum width</h2><div class="art">{boxed_figure(half, half_th)}</div>
<p class="cap">the two blue edges are the support lines and the tangent lines;
they are parallel and {half_w:.3f} apart, not the same line</p></section>
</div>
<h2 style="margin-top:32px">The full pair</h2>
<p style="font-size:14px;color:{MUTED};max-width:70ch">Boxing both halves
together does not help.  The minimum width is {full_w:.4f}, and the two
support points are point reflections of each other; the two tangent lines are
again distinct.</p>
<section><h2>Fig. 3 · both halves, minimum width</h2><div class="art">{boxed_figure(full, full_th, w=880.0, h=330.0)}</div>
<p class="cap">full min width {full_w:.4f} at {math.degrees(full_th) % 180:.1f}° ·
height {full_h:.4f}</p></section>
<h2 style="margin-top:32px">Width against rotation</h2>
<p style="font-size:14px;color:{MUTED};max-width:70ch">The ink curve is the
half; the blue curve is the full pair.  The dots are the minima.  The width
function is periodic in 180°, and neither minimum is zero.</p>
<section><h2>Fig. 4 · width vs angle</h2><div class="art">{width_chart(half_hull, full_hull, half_th, full_th)}</div>
<p class="cap">half {half_w:.4f} at {math.degrees(half_th) % 180:.1f}° ·
full {full_w:.4f} at {math.degrees(full_th) % 180:.1f}°</p></section>
<h2 style="margin-top:32px">The table contact</h2>
<p style="font-size:14px;color:{MUTED};max-width:70ch">Rotate the whole ± curve
by <strong>38.5° clockwise</strong> and the two outer-turn points are level to
<strong>{tab_gap:.5f} units</strong> — visually a table contact, not exactly.  The two
points are on the outer turns, not near the eye, so this is a heart-sized pair.
It is a different object from the same-half mirror join (0.079) and from the
minimum-width box (0.984): here one support line touches twice.</p>
<section><h2>Fig. 5 · the full pair on a table</h2><div class="art">{tab_svg}</div>
<p class="cap">rotation 38.5° CW · contacts ({tab1[0]:.3f}, {tab1[1]:.3f}) and
({tab2[0]:.3f}, {tab2[1]:.3f}) · gap {tab_gap:.5f} units</p></section>
</main></body></html>
"""
    out = ROOT / "workbench" / "clothoid-cut.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
