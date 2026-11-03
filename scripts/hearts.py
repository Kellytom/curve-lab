"""Hearts from one Euler arc: rotate to tangency, mirror, cut on the lattice.

    .venv/bin/python scripts/hearts.py
    open workbench/hearts.html

The construction, in the order the pieces were found:

1.  A unit clothoid starts at the origin with its tangent along +x, and its
    heading is quadratic in arc length: theta(s) = s^2 / 2.
2.  Rotate the whole arc about the origin.  At one particular rotation the arc
    comes back and *touches* the y axis -- vertical tangent, zero distance.
    The origin is already on that axis, so the arc now has both ends on it:
    one at the bottom, one at the top where it only kisses it.
3.  Mirror about the y axis.  The two arcs share the origin and meet at the
    top -- a heart, with the cleft being the tangency.
4.  Carry the arc a little past the tangency, to the next lattice point, and
    the halves cross instead of meeting.  That crossing is the extra.

Nothing here is forced onto integers except the final cut, and where that cut
lands is reported in grid units so the price is visible.
"""

from __future__ import annotations

import math
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generators as G  # noqa: E402
import euler_match as E  # noqa: E402

INK, GOLD, DOT = "#2e2413", "#c9a441", "#b23a2b"
OVERLAY = "#1f5fa8"
GRID, LINE, MUTED = "#ece4cf", "#d8ccae", "#7b6c4e"

N = 4000
TURNS = 2.0
S_MAX = math.sqrt(4 * math.pi * TURNS)     # theta = s^2/2, so 2*pi*turns


def clothoid(s_max=S_MAX, n=N):
    ds = s_max / n
    x = y = 0.0
    out = [(0.0, 0.0, 0.0)]
    for i in range(1, n + 1):
        s = i * ds
        x += math.cos(s * s / 2) * ds
        y += math.sin(s * s / 2) * ds
        out.append((s, x, y))
    return out


def rotate(p, phi):
    c, s = math.cos(phi), math.sin(phi)
    return (p[0] * c - p[1] * s, p[0] * s + p[1] * c)


def tangencies(pts):
    """(s, phi) where a rotation by phi makes the arc touch x = 0.

    After rotating by phi the tangent at s points along theta(s) + phi, so it is
    vertical exactly when phi = pi/2 - theta(s).  The touch distance at that
    rotation is the rotated x.
    """
    out = []
    prev = None
    for s, x, y in pts:
        phi = math.pi / 2 - s * s / 2
        d = x * math.cos(phi) - y * math.sin(phi)
        if prev is not None and prev[1] * d < 0:
            a, b = prev[0], s
            for _ in range(60):
                m = (a + b) / 2
                mm = m * m / 2
                xm = _interp(pts, m)[1]
                ym = _interp(pts, m)[2]
                ph = math.pi / 2 - mm
                dm = xm * math.cos(ph) - ym * math.sin(ph)
                if d * dm > 0:
                    b = m
                else:
                    a = m
            s0 = (a + b) / 2
            out.append((s0, math.pi / 2 - s0 * s0 / 2))
        prev = (s, d)
    return out


def _interp(pts, s):
    i = min(len(pts) - 1, max(0, int(s / S_MAX * (len(pts) - 1))))
    return pts[i]


def next_lattice(pts, s_from, phi, scale, tol=0.5):
    """First s past the tangency whose rotated point is closest to a node."""
    best = None
    for s, x, y in pts:
        if s <= s_from:
            continue
        rx, ry = rotate((x, y), phi)
        fx, fy = round(rx * scale), round(ry * scale)
        d = math.hypot(rx - fx / scale, ry - fy / scale)
        if d <= tol / scale:
            snapped = (fx / scale, fy / scale)
            return s, (rx, ry), snapped, d
        if best is None or d < best[3]:
            best = (s, (rx, ry), (round(rx * scale) / scale,
                                  round(ry * scale) / scale), d)
    return best


def arc_between(pts, s0, s1):
    return [(x, y) for s, x, y in pts if s0 <= s <= s1]


def lattice_hits(points, step=0.5, tol=0.03):
    """Lattice nodes the curve passes within tol of, on a grid of `step`."""
    out = []
    for x, y in points:
        gx, gy = round(x / step) * step, round(y / step) * step
        if math.hypot(x - gx, y - gy) <= tol:
            out.append((gx, gy))
    return out


def lattice_lines(x0, x1, y0, y1, step, put):
    out = []
    g = math.ceil(x0 / step) * step
    while g <= x1:
        a, b = put((g, y0)), put((g, y1))
        out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
                   f'y2="{b[1]:.1f}" stroke="{GRID}"/>')
        g += step
    g = math.ceil(y0 / step) * step
    while g <= y1:
        a, b = put((x0, g)), put((x1, g))
        out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
                   f'y2="{b[1]:.1f}" stroke="{GRID}"/>')
        g += step
    return "".join(out)


def heart_figure(a, b, w=430.0, h=330.0):
    """a = the right-hand arc, b = optional overshoot past the kiss.

    Flipped vertically at the end so the point hangs down and the cleft sits on
    top, which is how a heart is read.  The construction puts it the other way
    up, and either is the same curve.
    """
    a = [(x, -y) for x, y in a]
    b = [(x, -y) for x, y in b] if b else b
    allpts = list(a) + [(-x, y) for x, y in a]
    if b:
        allpts += list(b)
    xs = [p[0] for p in allpts]
    ys = [p[1] for p in allpts]
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    pad = 0.08
    x0, x1 = x0 - pad * (x1 - x0 + 1e-9), x1 + pad * (x1 - x0 + 1e-9)
    y0, y1 = y0 - pad * (y1 - y0 + 1e-9), y1 + pad * (y1 - y0 + 1e-9)
    k = min((w - 16) / (x1 - x0), (h - 16) / (y1 - y0))
    ox, oy = (w - (x1 - x0) * k) / 2, (h - (y1 - y0) * k) / 2

    def put(p):
        return ox + (p[0] - x0) * k, h - (oy + (p[1] - y0) * k)

    def path(points, colour, width):
        if len(points) < 2:
            return ""
        return ('<path d="M ' + " L ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}"
                                           for p in points) +
                f'" fill="none" stroke="{colour}" stroke-width="{width}" '
                f'stroke-linecap="round"/>')

    grid = lattice_lines(x0, x1, y0, y1, 0.5, put)
    hits = lattice_hits(a + [(-x, y) for x, y in a], 0.5)
    dots = "".join(f'<circle cx="{put(q)[0]:.1f}" cy="{put(q)[1]:.1f}" r="3.2" '
                   f'fill="{DOT}" stroke="#fffdf7" stroke-width="1"/>' for q in hits)
    return f"""<svg viewBox="0 0 {w:.0f} {h:.0f}" xmlns="http://www.w3.org/2000/svg">
    <rect x="0" y="0" width="{w:.0f}" height="{h:.0f}" fill="#fffdf7" stroke="{LINE}"/>
    {grid}
    {path(a, INK, 2.4)}{path([(-x, y) for x, y in a], INK, 2.4)}
    {path(b, GOLD, 1.6) if b else ""}
    <line x1="{put((0, y0))[0]:.1f}" y1="{put((0, y0))[1]:.1f}"
          x2="{put((0, y1))[0]:.1f}" y2="{put((0, y1))[1]:.1f}"
          stroke="{GOLD}" stroke-width="1" stroke-dasharray="5 4"/>
    {dots}
  </svg>"""


def gerono_leaf():
    """Gerono's lemniscate: the line y = 1/2 touches both lobes; mirror the
    outer arc between the two touch points and a leaf closes."""
    spec = [x for x in G.NAMED if x["key"] == "gerono"][0]
    data = G.named_data(spec)
    pts = []
    for ctrl in data["ctrl"]:
        deg = len(ctrl) - 1
        for i in range(1200):
            s = F(i, 1199)
            w = sum(F(p_[2]) * G.bern_n(j, deg, s) for j, p_ in enumerate(ctrl))
            if w == 0:
                continue
            x, y = G.homog_point(ctrl, s)
            pts.append((float(x), float(y)))
    lines = [(abs(y - 0.5), i) for i, (x, y) in enumerate(pts)]
    lines.sort()
    i1 = lines[0][1]
    i2 = next(i for _, i in lines[1:] if abs(i - i1) > 40)
    lo, hi = sorted((i1, i2))
    arc_a, arc_b = pts[lo:hi + 1], pts[hi:] + pts[:lo + 1]
    outer = max((arc_a, arc_b), key=lambda a: sum(math.hypot(x, y) for x, y in a))
    return pts, outer


def leaf_figure(pts, arc, w=430.0, h=330.0):
    mirror = [(x, 1.0 - y) for x, y in arc]
    allpts = pts + mirror
    xs = [p[0] for p in allpts]
    ys = [p[1] for p in allpts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    pad = 0.08
    x0, x1 = x0 - pad * (x1 - x0), x1 + pad * (x1 - x0)
    y0, y1 = y0 - pad * (y1 - y0), y1 + pad * (y1 - y0)
    k = min((w - 16) / (x1 - x0), (h - 16) / (y1 - y0))
    ox, oy = (w - (x1 - x0) * k) / 2, (h - (y1 - y0) * k) / 2

    def put(p):
        return ox + (p[0] - x0) * k, h - (oy + (p[1] - y0) * k)

    def path(q, colour, width, dash=""):
        d = "M " + " L ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}" for p in q)
        return (f'<path d="{d}" fill="none" stroke="{colour}" '
                f'stroke-width="{width}" {dash}/>')

    a, b = put((x0, 0.5)), put((x1, 0.5))
    return f"""<svg viewBox="0 0 {w:.0f} {h:.0f}" xmlns="http://www.w3.org/2000/svg">
    <rect x="0" y="0" width="{w:.0f}" height="{h:.0f}" fill="#fffdf7" stroke="{LINE}"/>
    {path(pts, MUTED, 1.1, 'stroke-dasharray="4 3"')}
    {path(arc, INK, 2.4)}
    {path(mirror, INK, 2.4)}
    <line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}"
          stroke="{GOLD}" stroke-width="1" stroke-dasharray="6 4"/>
  </svg>"""


def heart_half():
    """The positive-x half of the sextic, as one ordered arc.

    The heart is symmetric in x, so the right half runs from the bottom point
    (0, -1) out around the lobe and back to the cleft (0, 1).  Sampling gives
    the upper and lower branches separately; this walks the upper one outward
    and the lower one back.

    Both branches now end on the lobe tip (``generators.heart_tip``), so the
    join is that shared point.  The reversed lower branch repeats it, and the
    repeat is dropped: a zero-length chord would break the tangent fit.
    """
    # the page sampler is deliberately coarse; the fit needs a dense one.
    # 4000 keeps the chord across the vertical tangent at the tip under 0.04
    # units, where 400 left a 0.107 chord that was itself most of the error.
    upper, lower = G.heart_branches(4000)
    up = [p for p in upper if p[0] >= -1e-9]
    lo = [p for p in lower if p[0] >= -1e-9]
    back = [(float(a), float(b)) for a, b in reversed(lo)]
    return [(float(a), float(b)) for a, b in up] + back[1:]


def half_figure(pts, w=430.0, h=330.0, poly=None, spans=None):
    allpts = list(pts) + ([p for p in poly] if poly else [])
    xs = [p[0] for p in allpts]
    ys = [p[1] for p in allpts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    pad = 0.10
    x0, x1 = x0 - pad * (x1 - x0), x1 + pad * (x1 - x0)
    y0, y1 = y0 - pad * (y1 - y0), y1 + pad * (y1 - y0)
    k = min((w - 16) / (x1 - x0), (h - 16) / (y1 - y0))
    ox, oy = (w - (x1 - x0) * k) / 2, (h - (y1 - y0) * k) / 2

    def put(q):
        return ox + (q[0] - x0) * k, h - (oy + (q[1] - y0) * k)

    def path(points, colour, width, dash=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        return ('<path d="M ' + " L ".join(f"{put(q)[0]:.1f} {put(q)[1]:.1f}"
                                           for q in points) +
                f'" fill="none" stroke="{colour}" stroke-width="{width}"'
                f'{extra}/>')

    body = path(pts, INK, 2.4)
    # the fit goes on top, wide and dashed: gold at 1.3 over a 2.4 ink line
    # was invisible, so the figure could not be read as a comparison
    over = path(poly, OVERLAY, 1.9, "6 4") if poly else ""
    grid = lattice_lines(x0, x1, y0, y1, 0.25, put)
    dots = "".join(f'<circle cx="{put(q)[0]:.1f}" cy="{put(q)[1]:.1f}" r="3" '
                   f'fill="{DOT}" stroke="#fffdf7" stroke-width="1"/>'
                   for q in lattice_hits(pts, 0.25, tol=0.02))
    return f"""<svg viewBox="0 0 {w:.0f} {h:.0f}" xmlns="http://www.w3.org/2000/svg">
    <rect x="0" y="0" width="{w:.0f}" height="{h:.0f}" fill="#fffdf7" stroke="{LINE}"/>
    {grid}
    {body}
    <line x1="{put((0, y0))[0]:.1f}" y1="{put((0, y0))[1]:.1f}"
          x2="{put((0, y1))[0]:.1f}" y2="{put((0, y1))[1]:.1f}"
          stroke="{GOLD}" stroke-width="1" stroke-dasharray="5 4"/>
    {dots}
    {over}
  </svg>"""


def double_tangent_gaps(turns_list=(2, 4, 8, 16)):
    """Closest separation of two vertical-tangent contacts on one arc.

    At rotation phi = pi/2 the vertical tangents sit at s = sqrt(2 k pi).  The
    closest pair is the last two even-k contacts; their x separation (here the
    y separation, since X = -y at phi = pi/2) shrinks toward the eye and never
    reaches zero.  The table on the page is this measurement.
    """
    rows = []
    for turns in turns_list:
        s_max = math.sqrt(4 * math.pi * turns)
        pts = clothoid(s_max=s_max, n=20000)
        ds = s_max / (len(pts) - 1)

        def y_at(s):
            i = min(int(s / ds), len(pts) - 2)
            t = (s - i * ds) / ds
            return pts[i][2] * (1 - t) + pts[i + 1][2] * t

        k = 2 * turns
        s2 = s_max
        s1 = math.sqrt(2 * (k - 2) * math.pi)
        rows.append((turns, abs(y_at(s1) - y_at(s2)), s1, s2))
    return rows


def whole_heart(pts, poly=None):
    """One closed heart: the positive-x half plus its mirror.

    The half starts at the cleft (0, 1) and ends at the bottom (0, -1).  The
    mirror runs the other way, so the two halves share both joins exactly.
    """
    mirror = [(-x, y) for x, y in pts]
    full = list(pts) + list(reversed(mirror))[1:]
    full_poly = None
    if poly:
        mpol = [(-x, y) for x, y in poly]
        full_poly = list(poly) + list(reversed(mpol))[1:]
    return half_figure(full, w=880.0, h=460.0, poly=full_poly)


def sampled_figure(spec, w=430.0, h=300.0):
    """A curve with no parametrisation: draw the samples, claim nothing more."""
    paths = G.named_data(spec)["paths"] or []
    pts = [p for br in paths for p in br]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    pad = 0.08
    x0, x1 = x0 - pad * (x1 - x0), x1 + pad * (x1 - x0)
    y0, y1 = y0 - pad * (y1 - y0), y1 + pad * (y1 - y0)
    k = min((w - 16) / (x1 - x0), (h - 16) / (y1 - y0))
    ox, oy = (w - (x1 - x0) * k) / 2, (h - (y1 - y0) * k) / 2

    def put(q):
        return ox + (q[0] - x0) * k, h - (oy + (q[1] - y0) * k)

    body = "".join(
        '<path d="M ' + " L ".join(f"{put(q)[0]:.1f} {put(q)[1]:.1f}" for q in br) +
        f'" fill="none" stroke="{INK}" stroke-width="2.2"/>' for br in paths)
    return (f'<svg viewBox="0 0 {w:.0f} {h:.0f}" xmlns="http://www.w3.org/2000/svg">'
            f'<rect x="0" y="0" width="{w:.0f}" height="{h:.0f}" fill="#fffdf7"'
            f' stroke="{LINE}"/>{body}</svg>')


def main():
    pts = clothoid()
    tans = tangencies(pts)
    print(f"  {len(tans)} tangencies on a {TURNS:g}-turn arc")
    for s, phi in tans:
        x = _interp(pts, s)[1]
        y = _interp(pts, s)[2]
        rx, ry = rotate((x, y), phi)
        print(f"    s={s:.3f} ({s*s/(4*math.pi):.2f} turns)  rotation "
              f"{math.degrees(phi) % 360:6.2f} deg  touch at (0, {ry:.3f})")

    cards = []
    for i, (s_t, phi) in enumerate(tans[:-1]):        # the last one folds back
        right = [rotate((x, y), phi) for s, x, y in pts if 0 <= s <= s_t]
        s_cut, exact, snapped, d = next_lattice(pts, s_t, phi, scale=8)
        over = [rotate((x, y), phi) for s, x, y in pts if s_t <= s <= s_cut]
        cap = (f"{s_t*s_t/(4*math.pi):.2f} turns · rotation "
               f"{math.degrees(phi) % 360:.1f}° · cut {d*8:.2f} grid units early")
        cards.append(f"""<section><h2>Fig. {i+1}</h2>
  <div class="art">{heart_figure(right, over)}</div>
  <p class="cap">{cap}</p></section>""")

    half = heart_half()
    n, dev, poly, L = E.fit_branch(half)
    end_drift = max(math.dist(poly[0], half[0]), math.dist(poly[-1], half[-1]))
    join_gap = 2 * abs(poly[-1][0])
    dt_rows = double_tangent_gaps()
    dt_table = "".join(
        f"<tr><td>{t}</td><td>{g:.4f}</td><td>{s1:.2f}, {s2:.2f}</td></tr>"
        for t, g, s1, s2 in dt_rows)
    k_spans, dev_spans, span_poly = None, None, None
    for k in (4, 8, 16, 32, 64):
        sp = E.clothoid_spans(half, k)
        d = E.deviation(sp, half) / E.size(half)
        if dev_spans is None or d < dev_spans:
            k_spans, dev_spans, span_poly = k, d, sp
        if d <= 0.01:
            break
    print(f"  heart, positive-x half: {n} chords, Euler error {100*dev:.2f}% of size;"
          f" {k_spans} clothoid spans, error {100*dev_spans:.2f}%")

    phis = [math.degrees(phi) % 360 for _, phi in tans]
    corner = abs(180 - 2 * phis[0]) % 360
    corner = min(corner, 360 - corner)

    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hearts — one Euler arc, mirrored</title>
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
<h1>Hearts</h1>
<p class="lead">One Euler arc, rotated until it kisses the y axis, then mirrored.
The cleft is the kiss; the little extra is where it carries on past it.</p>
<p class="lead">The expanded set — <a href="heart-forms.html">fifteen formulaic
hearts</a> — is a separate page; this page is the clothoid-heart proof.</p>
<div class="panel">
<p><strong>What the mirror needs, and what is still open.</strong> For the join
to be smooth the arc has to meet the y axis at two places <em>tangentially</em> —
it runs along the axis at both, so the mirror continues without a kink. After a
rotation φ the vertical-tangent points are fixed by s²/2 + φ = π/2 + kπ; the
two contacts lie on one line only when their rotated x agree. For <em>one half
mirrored about the axis</em>, both contacts must be on that half; on a finite
unit arc the gap never reaches zero — those contacts crowd toward the clothoid's
eye and only tend to it (table below). Fixing the arc's endpoints, as the
figures below do, leaves only the rotation free and one contact — which is why
the bottom of Fig. 1 is a corner rather than a blend. The <em>full ± curve</em>
is a different pair: rotated 38.5° clockwise, its two outer turns are level to
under 0.0001, a usable table contact (<code>clothoid-cut</code> Fig. 5). The
mirror-axis join still needs two placed arcs or a stated gap.</p>
<p>The rotations below are therefore not a family to pick from: they are the
rotation at which the far end is tangent, for each half turn the arc completes.
Any of them draws a heart. The first is merely the smallest.</p>
<p style="font-size:12px;color:{MUTED}">Every percentage on this page, and on
every page in the workbench, is an <strong>error</strong>: a distance between
what was drawn and what was wanted, as a share of a stated reference. Where a
number is not an error it says so in words.</p>
</div>
<div class="grid2">{''.join(cards)}</div>
<h2 style="margin-top:32px">Double tangency: the half mirror join</h2>
<p style="font-size:14px;color:{MUTED};max-width:70ch">This table is the
same-half mirror join: both contacts on one half. For each turn count the arc
was rotated to the closest approach; the two vertical-tangent contacts never
share an x. They crowd toward the clothoid's eye, so the gap shrinks with every
doubling of turns and reaches zero only in the limit. The full ± curve's table
contact is a different pair — under 0.0001 at 38.5° CW (<code>clothoid-cut</code>
Fig. 5).</p>
<table>
<tr><th>turns</th><th>closest gap</th><th>contacts (s)</th></tr>
{dt_table}
</table>
<p style="font-size:14px;color:{MUTED};max-width:70ch">Closest always at
φ = 90°. The closest pairs sit near the eye, so they are not heart-sized lobes:
this is a limit, not a join. The full ± outer-turn contact is the usable join;
the same-half axis join needs two placed arcs or a stated gap.</p>
<h2 style="margin-top:32px">The heart, split at x = 0</h2>
<p style="font-size:14px;color:{MUTED};max-width:70ch">The heart is symmetric
in x, so it is two curves. Taking the positive-x half alone gives one open arc
from the bottom point to the cleft — the shape we actually have to build.
<strong>Correct method is a clothoid chain fitted to that arc, not a chord
walk</strong>: the blue dashed line drawn over the curve is an Euler polygon
against the same samples. The sample path now closes on the lobe tip, where
the two y-roots merge, so the polygon is judged on the geometry rather than on
the old jump.</p>
<div class="grid2">
<section><h2>Fig. 3 · positive x</h2><div class="art">{half_figure(half, poly=poly)}</div>
<p class="cap">{n} chords · error {100*dev:.2f}% of size · both ends within
{end_drift:.3f} units of the axis</p></section>
<section><h2>Fig. 4 · negative x</h2><div class="art">{half_figure([(-x, y) for x, y in half], poly=[(-x, y) for x, y in poly])}</div>
<p class="cap">the mirror — the same curve, and the same chain flipped</p></section>
</div>
<h2 style="margin-top:32px">The whole heart</h2>
<p style="font-size:14px;color:{MUTED};max-width:70ch">Fig. 5 puts Fig. 3 and
Fig. 4 back together. The ink halves share the two joins exactly — the cleft
at (0, 1) and the bottom at (0, −1). The only gap is in the Euler fit, whose two
ends miss the axis by the amount below.</p>
<section><h2>Fig. 5 · both halves</h2><div class="art">{whole_heart(half, poly)}</div>
<p class="cap">the ink halves meet at the cleft and the bottom; the Euler halves
meet within {join_gap:.3f} units at the bottom, and exactly at the cleft</p></section>
</main></body></html>
"""
    out = ROOT / "workbench" / "hearts.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
