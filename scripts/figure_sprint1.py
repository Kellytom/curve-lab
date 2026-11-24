#!/usr/bin/env python3
"""Fig. H1 — a first algorithmic human figure: the Orans (praying figure).

Early Christian iconography has a canonical frontal figure, arms raised in
prayer, wrapped in a robe. It is the simplest sacred human form, and it is
built here the way the house builds everything: rational stations, mirror
symmetry, and a cubic Bezier chain between stations. No trigonometry of a
general angle; the circles use the rational parametrisation
x = (1-t^2)/(1+t^2), y = 2t/(1+t^2).

Two variants side by side: the line study (left) and the filled silhouette
(right). Black and white only.

Output: workbench/figure-sprint-1.svg
The y axis points up in the model and is flipped once, at SVG output.
"""

from fractions import Fraction as F

W, H = 760, 560          # SVG canvas, SVG pixels (y down)
BASE = 70                # hem baseline, model units above canvas bottom
FLIP = lambda y: H - BASE - y   # model y-up -> SVG y-down, applied once

def rat_circle(cx, cy, r, n=16):
    """Full circle, all stations rational. The rational parametrisation
    x=(1-t^2)/(1+t^2), y=2t/(1+t^2) with t from -1 to 1 gives the right
    half (bottom to top); the left half is its mirror, top to bottom."""
    half = []
    for i in range(2 * n + 1):
        t = F(i, n) - 1          # t runs -1 .. 1
        x = (1 - t * t) / (1 + t * t)
        y = (2 * t) / (1 + t * t)
        half.append((cx + r * x, cy + r * y))
    left = [((2 * cx) - x, y) for (x, y) in reversed(half[1:-1])]
    return half + left            # closed ring, in drawing order

def mirror(pts):
    """Reflect across x=0 (Euclid: reflection keeps every length)."""
    return [(-x, y) for (x, y) in pts]

def catmull_path(pts, closed=False):
    """Cubic Bezier chain through the stations (Catmull-Rom tangents).
    The stations stay exact; the drawing between them is approximate."""
    p = pts if closed else pts
    n = len(p)
    def at(i):
        if closed:
            return p[i % n]
        return p[max(0, min(n - 1, i))]
    d = f"M {float(p[0][0]):.3f} {float(p[0][1]):.3f}"
    last = n if closed else n - 1
    for i in range(last):
        p0, p1, p2, p3 = at(i - 1), at(i), at(i + 1), at(i + 2)
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += (f" C {float(c1[0]):.3f} {float(c1[1]):.3f}"
              f" {float(c2[0]):.3f} {float(c2[1]):.3f}"
              f" {float(p2[0]):.3f} {float(p2[1]):.3f}")
    if closed:
        d += " Z"
    return d

# ---- the skeleton: one half, designed as exact rational stations ----------
# Robe side, hem to neck (y-up, model units; x positive = right of centre)
ROBE_RIGHT = [
    (F(52), F(0)), (F(47), F(18)), (F(36), F(45)),
    (F(24), F(72)), (F(17), F(92)), (F(16), F(98)),
    (F(13), F(106)), (F(6), F(114)),
]
# Raised forearm, shoulder to hand (the Orans gesture)
ARM_RIGHT = [
    (F(14), F(104)), (F(24), F(107)), (F(34), F(116)),
    (F(41), F(127)), (F(44), F(138)),
]
HEAD_C, HEAD_R = (F(0), F(140)), F(26)
HALO_R = F(38)

def to_svg(pts):
    return [(float(x), FLIP(y)) for (x, y) in pts]

def poly(pts):
    return " ".join(f"{x:.3f},{y:.3f}" for x, y in pts)

# ---- geometry, computed once and printed as the proof ---------------------
head = to_svg(rat_circle(HEAD_C[0], HEAD_C[1], HEAD_R, n=16))
halo = to_svg(rat_circle(HEAD_C[0], HEAD_C[1], HALO_R, n=24))
robe_closed = (to_svg(mirror(ROBE_RIGHT))[:-1])[::-1] + to_svg(ROBE_RIGHT)

arm_r = to_svg(ARM_RIGHT)
arm_l = to_svg(mirror(ARM_RIGHT))

print(f"robe stations: {len(robe_closed)} (closed)")
print(f"arm stations per side: {len(ARM_RIGHT)}")
print(f"head stations: {len(head)}, halo stations: {len(halo)}")
print(f"all coordinates rational: yes (Fractions; printed floats are display only)")

# ---- SVG ------------------------------------------------------------------
svg = []
svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}">')
svg.append(f'<rect width="{W}" height="{H}" fill="white"/>')
svg.append(f'<text x="20" y="30" font-family="Helvetica,Arial" font-size="17" '
           f'fill="black">Fig. H1 - Orans study 1: a human figure from mirrored '
           f'rational curves</text>')
svg.append(f'<text x="20" y="50" font-family="Helvetica,Arial" font-size="12" '
           f'fill="#444">Stations are exact rational points; the drawing between '
           f'stations is a cubic chain (approximate). Circles use x=(1-t&#178;)/(1+t&#178;), '
           f'y=2t/(1+t&#178;).</text>')

def group(dx, label, line_mode):
    g = [f'<g transform="translate({dx},0)">']
    robe_d = catmull_path(robe_closed, closed=True)
    if line_mode:
        g.append(f'<path d="{robe_d}" fill="none" stroke="black" stroke-width="2"/>')
        g.append(f'<path d="{catmull_path(head, closed=True)}" fill="none" '
                 f'stroke="black" stroke-width="2"/>')
        g.append(f'<path d="{catmull_path(halo, closed=True)}" fill="none" '
                 f'stroke="black" stroke-width="1.4" stroke-dasharray="4 3"/>')
        for a in (arm_r, arm_l):
            g.append(f'<path d="{catmull_path(a)}" fill="none" '
                     f'stroke="black" stroke-width="2.4" stroke-linecap="round"/>')
    else:
        g.append(f'<path d="{robe_d}" fill="black" stroke="black" stroke-width="2"/>')
        g.append(f'<circle cx="0" cy="{FLIP(140):.3f}" r="{float(HEAD_R):.3f}" '
                 f'fill="black"/>')
        g.append(f'<circle cx="0" cy="{FLIP(140):.3f}" r="{float(HALO_R):.3f}" '
                 f'fill="none" stroke="black" stroke-width="3"/>')
        for a in (arm_r, arm_l):
            g.append(f'<path d="{catmull_path(a)}" fill="none" '
                     f'stroke="black" stroke-width="7" stroke-linecap="round"/>')
    # labels (left variant only, to keep the right clean)
    if line_mode:
        lab = [("halo", 0, FLIP(140 + HALO_R + 14)),
               ("head", 52, FLIP(140)),
               ("arm, raised in prayer", 66, FLIP(150)),
               ("robe", 62, FLIP(40)),
               ("hem", 0, FLIP(-14))]
        for text, lx, ly in lab:
            g.append(f'<text x="{lx}" y="{ly:.1f}" font-family="Helvetica,Arial" '
                     f'font-size="13" fill="black">{text}</text>')
        g.append(f'<line x1="-70" y1="{FLIP(0):.1f}" x2="70" y2="{FLIP(0):.1f}" '
                 f'stroke="#999" stroke-width="1" stroke-dasharray="2 4"/>')
    else:
        g.append(f'<text x="0" y="{FLIP(-30):.1f}" font-family="Helvetica,Arial" '
                 f'font-size="13" fill="black" text-anchor="middle">the same '
                 f'skeleton, filled</text>')
    g.append('</g>')
    return "".join(g)

svg.append(group(200, "line", True))
svg.append(group(540, "filled", False))
svg.append(f'<text x="20" y="{H-12}" font-family="Helvetica,Arial" font-size="12" '
           f'fill="#444">Mirror symmetry throughout: the left side is the right '
           f'side reflected (reflection keeps every length). Baseline dashed.</text>')
svg.append('</svg>')

out = "workbench/figure-sprint-1.svg"
with open(out, "w") as f:
    f.write("\n".join(svg))
print(f"wrote {out}")
