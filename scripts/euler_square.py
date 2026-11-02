"""A rounded square from eight Euler arcs: tighten to 45, relax to 90, four times.

    .venv/bin/python scripts/euler_square.py
    open workbench/euler-square.html

Each corner is two clothoid arcs.  The first leaves a straight edge with zero
curvature and tightens until the heading has turned 45 degrees; the second is
its mirror image about that diagonal, so it relaxes back to zero curvature as it
meets the next straight edge.  Curvature is continuous everywhere -- zero on the
edges, peaking at the diagonal -- which is what the circular-corner version
cannot do: a quarter circle starts and ends with a curvature step.

Eight arcs is four corners times two.  The straight runs between them are free.
"""

from __future__ import annotations

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INK, GOLD, DOT = "#2e2413", "#c9a441", "#b23a2b"
GRID, LINE, MUTED = "#ece4cf", "#d8ccae", "#7b6c4e"

N = 600


def corner(n=N):
    """One Euler corner: curvature 0 -> peak -> 0, heading 0 -> 90 degrees.

    The curvature is a tent: kappa(s) = s up to s1, then 2*s1 - s after it.  A
    single clothoid cannot do this -- it is monotone curvature -- so the corner
    is two arcs sharing a peak.  Integrating the tent directly is simpler and
    safer than reflecting the first half: a reflection reverses the turn and
    makes an S where a corner was wanted.
    """
    s1 = math.sqrt(math.pi / 2)            # heading reaches pi/4 at s1
    total = 2 * s1
    ds = total / n
    th = 0.0
    x = y = 0.0
    pts = [(0.0, 0.0)]
    for i in range(1, n + 1):
        mid = (i - 0.5) * ds
        kappa = mid if mid <= s1 else 2 * s1 - mid
        th += kappa * ds
        x += math.cos(th) * ds
        y += math.sin(th) * ds
        pts.append((x, y))
    return pts


def place(points, at, angle):
    c, s = math.cos(angle), math.sin(angle)
    return [(at[0] + x * c - y * s, at[1] + x * s + y * c) for x, y in points]


def square(side=0.0):
    """Four corners and four straight runs, wound counter-clockwise."""
    c = corner()
    w = c[-1][0] - c[0][0]                 # the corner's own width
    reach = c[-1][1] - c[0][1]             # ... and its height
    # corner k starts at the end of edge k, which runs along +x
    out = []
    start = (0.0, 0.0)
    for k in range(4):
        ang = k * math.pi / 2
        pts = place(c, start, ang)
        out.append(pts)
        # a straight run of length `side`; zero butts the corners together
        end = pts[-1]
        nxt = (end[0] + side * math.cos(ang + math.pi / 2),
               end[1] + side * math.sin(ang + math.pi / 2))
        if side > 0:
            out.append([end, nxt])
        start = nxt
    return out, w, reach


def figure(paths, w=430.0, h=430.0, show_grid=True):
    pts = [p for seg in paths for p in seg]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    pad = 0.06
    x0, x1 = x0 - pad * (x1 - x0), x1 + pad * (x1 - x0)
    y0, y1 = y0 - pad * (y1 - y0), y1 + pad * (y1 - y0)
    k = min((w - 16) / (x1 - x0), (h - 16) / (y1 - y0))
    ox, oy = (w - (x1 - x0) * k) / 2, (h - (y1 - y0) * k) / 2

    def put(p):
        return ox + (p[0] - x0) * k, h - (oy + (p[1] - y0) * k)

    body = "".join(
        '<path d="M ' + " L ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}" for p in seg) +
        f'" fill="none" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"/>'
        for seg in paths if len(seg) > 1)
    return f"""<svg viewBox="0 0 {w:.0f} {h:.0f}" xmlns="http://www.w3.org/2000/svg">
    <rect x="0" y="0" width="{w:.0f}" height="{h:.0f}" fill="#fffdf7" stroke="{LINE}"/>
    {body}
  </svg>"""


def superellipse(n, steps=720):
    """|x|^n + |y|^n = 1, centred, unit half-extent."""
    pts = []
    for i in range(steps + 1):
        t = 2 * math.pi * i / steps
        c, s = math.cos(t), math.sin(t)
        pts.append((math.copysign(abs(c) ** (2 / n), c),
                    math.copysign(abs(s) ** (2 / n), s)))
    return pts


def normalise(pts, half=1.0):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    w = max(max(xs) - min(xs), max(ys) - min(ys)) / 2
    return [((x - cx) / w * half, (y - cy) / w * half) for x, y in pts]


def curvature_check(paths, samples=400):
    """The heading change from one arc to the next, at every join."""
    worst = 0.0
    for seg in paths:
        if len(seg) < 6:
            continue
        for i in range(1, len(seg) - 1):
            a = math.atan2(seg[i][1] - seg[i - 1][1], seg[i][0] - seg[i - 1][0])
            b = math.atan2(seg[i + 1][1] - seg[i][1], seg[i + 1][0] - seg[i][0])
            d = abs((b - a + math.pi) % (2 * math.pi) - math.pi)
            worst = max(worst, d)
    return worst


def mixed_figure(w=560.0, h=560.0):
    """The tight Euler square, the squircle, and the family between them."""
    paths, _, _ = square()
    euler = [pt for seg in paths for pt in seg]
    euler = normalise(euler)
    squircle = superellipse(4)
    family = [superellipse(n) for n in (2, 3, 6, 12)]

    allpts = euler + squircle + [p for f in family for p in f]
    xs = [p[0] for p in allpts]
    ys = [p[1] for p in allpts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    pad = 0.10
    x0, x1 = x0 - pad * (x1 - x0), x1 + pad * (x1 - x0)
    y0, y1 = y0 - pad * (y1 - y0), y1 + pad * (y1 - y0)
    k = min((w - 16) / (x1 - x0), (h - 16) / (y1 - y0))
    ox, oy = (w - (x1 - x0) * k) / 2, (h - (y1 - y0) * k) / 2

    def put(p):
        return ox + (p[0] - x0) * k, h - (oy + (p[1] - y0) * k)

    def line(q, colour, width, dash=""):
        d = "M " + " L ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}" for p in q)
        return (f'<path d="{d}" fill="none" stroke="{colour}" '
                f'stroke-width="{width}" {dash}/>')

    fam = "".join(line(f, "#cbb98a", 1.0, 'stroke-dasharray="2 4"') for f in family)
    return f"""<svg viewBox="0 0 {w:.0f} {h:.0f}" xmlns="http://www.w3.org/2000/svg">
    <rect x="0" y="0" width="{w:.0f}" height="{h:.0f}" fill="#fffdf7" stroke="{LINE}"/>
    {fam}
    <path d="M {" L ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}" for p in squircle)}"
          fill="none" stroke="{GOLD}" stroke-width="1.8" stroke-dasharray="7 5"/>
    <path d="M {" L ".join(f"{put(p)[0]:.1f} {put(p)[1]:.1f}" for p in euler)}"
          fill="none" stroke="{INK}" stroke-width="2.6" stroke-linejoin="round"/>
  </svg>"""


def main():
    c = corner()
    corner_len = sum(math.dist(a, b) for a, b in zip(c, c[1:]))
    kinks = curvature_check([c])
    paths, w, reach = square()
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>A rounded square from eight Euler arcs</title>
<style>
body{{margin:0;background:#f6f1e4;color:{INK};font:16px/1.55 Georgia,serif}}
main{{max-width:980px;margin:0 auto;padding:34px 22px 70px}}
h1{{font-size:28px;margin:0 0 4px}}
.lead{{color:#8c6a21;margin:0 0 22px}}
h2{{font:600 11px/1.2 ui-monospace,Menlo,monospace;letter-spacing:.12em;
text-transform:uppercase;color:{MUTED};margin:0 0 6px}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
section{{background:#fffdf7;border:1px solid {LINE};padding:12px}}
svg{{display:block;width:100%;height:auto}}
.panel{{background:#fffdf7;border:1px solid {LINE};padding:16px 18px;margin:0 0 20px}}
.cap{{font-size:12px;color:{MUTED};margin:0}}
</style></head><body><main>
<h1>A rounded square from eight Euler arcs</h1>
<p class="lead">Tighten to 45°, relax to 90°, four times. Eight arcs and no
straight runs: the corners meet each other.</p>
<div class="panel">
<p><strong>Why eight.</strong> A corner has to leave a straight edge and arrive
at another one, at right angles. One clothoid cannot do both ends: it has a
single linear curvature law, so if it starts flat it cannot finish flat again.
Two can — one tightening to the diagonal, one relaxing away from it, each the
other's mirror image in curvature. Four corners,
eight arcs.</p>
<p><strong>What it buys.</strong> Curvature is continuous the whole way round:
zero along each edge, peaking at the 45° diagonal, and no step anywhere. The
circular-corner version on the generators page is one degree worse — a quarter
circle meets its straight edge with an instant change of curvature, which is a
visible kink on a cut path and an audible one on a machine.</p>
<p class="cap">measured here: corner arc length {corner_len:.4f} units on the
unit clothoid · largest heading change between consecutive samples
{math.degrees(kinks):.3f}° (this is sampling, not a kink) · corner width
{w:.3f}, height {reach:.3f}</p>
</div>
<div class="grid2">
<section><h2>one corner</h2>{figure([c])}
<p class="cap">curvature a tent: 0 at both ends, peak at the 45° diagonal</p></section>
<section><h2>the tight square</h2>{figure(paths, 430.0, 430.0)}
<p class="cap">eight arcs, nothing else — each corner butts the next</p></section>
</div>

<h2 style="margin-top:32px">Fig. 3 · the tight square, the squircle, and the family between</h2>
<p style="font-size:14px;color:{MUTED};max-width:72ch">Ink is the eight-arc
Euler square, gold is the squircle <code>|x|⁴ + |y|⁴ = 1</code>, and the dashed
pale curves are the superellipse family at <code>n = 2, 3, 6, 12</code> — circle
through squircle to square. The Euler square sits outside the squircle of the
same width, because its corners are built from a curvature tent rather than one
formula: it is slightly fuller at the diagonal and quite a lot straighter along
the sides. Not the same curve, and there is no reason it should be.</p>
<section><div>{mixed_figure()}</div></section>
</main></body></html>
"""
    out = ROOT / "workbench" / "euler-square.html"
    out.write_text(page, encoding="utf-8")
    print(out)
    print(f"  corner {corner_len:.4f} · kink {math.degrees(kinks):.3f} deg · "
          f"width {w:.3f} height {reach:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
