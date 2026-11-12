"""Diagram: why the midpoint rule works, and what happens at the ends.

Four panels, all exact at three steps over t in [0, 3], so the step width is 1:

  A  one step: the sampled tangent, the walked step, the curve's own chord
  B  y is exact, because y' = 2t is a straight line and the midpoint rule is
     exact on a straight line (the rectangle equals the triangle)
  C  x drifts, because x' = 1 - t^2 bends: the midpoint rectangle is 3/4,
     the true area is 2/3, so each step runs 1/12 too long in x
  D  the ends: three steps of 1/12 make the 1/4 gap at the far tip, while every
     node's y sits exactly on the curve

y is up in the model. Each panel flips once, in its own fy().

Run:  .venv/bin/python tph_tri_chain/diagram.py
"""

import os
from fractions import Fraction as F

from chain import chain

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
INK, MUTED, RULE, PAPER = "#2e2413", "#7b6c4e", "#d8ccae", "#fbf7ec"
BLUE, RED, GREY = "#1f5fa8", "#a23b2a", "#7a6a4a"


def curve(t):
    t = float(t)
    return (t - t ** 3 / 3, t ** 2)


class Panel:
    def __init__(self, box, xr, yr):
        self.left, self.top, self.w, self.h = box
        self.x0, self.x1 = xr
        self.y0, self.y1 = yr
        self.s = min(self.w / (xr[1] - xr[0]), self.h / (yr[1] - yr[0]))

    def fx(self, x):
        return self.left + (x - self.x0) * self.s

    def fy(self, y):                        # the one flip: model y up -> screen down
        return self.top + (self.y1 - y) * self.s

    def line(self, a, b, col, w=1.4, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        return (f'<line x1="{self.fx(a[0]):.2f}" y1="{self.fy(a[1]):.2f}" '
                f'x2="{self.fx(b[0]):.2f}" y2="{self.fy(b[1]):.2f}" '
                f'stroke="{col}" stroke-width="{w}"{d}/>')

    def poly(self, pts, col, w=2.2, fill="none"):
        d = " ".join(f"{self.fx(x):.2f},{self.fy(y):.2f}" for x, y in pts)
        return f'<polyline points="{d}" fill="{fill}" stroke="{col}" stroke-width="{w}"/>'

    def rect(self, a, b, col, fill, op=0.5):
        x0, y0 = self.fx(a[0]), self.fy(a[1])
        x1, y1 = self.fx(b[0]), self.fy(b[1])
        return (f'<rect x="{min(x0,x1):.2f}" y="{min(y0,y1):.2f}" '
                f'width="{abs(x1-x0):.2f}" height="{abs(y1-y0):.2f}" '
                f'fill="{fill}" fill-opacity="{op}" stroke="{col}" stroke-width="1"/>')

    def dot(self, x, y, r=4.2, col=INK):
        return f'<circle cx="{self.fx(x):.2f}" cy="{self.fy(y):.2f}" r="{r}" fill="{col}"/>'

    def text(self, x, y, s, size=13, anchor="start", col=INK, dx=0, dy=0):
        return (f'<text x="{self.fx(x)+dx:.2f}" y="{self.fy(y)+dy:.2f}" font-size="{size}" '
                f'text-anchor="{anchor}" fill="{col}">{s}</text>')

    def axes(self):
        o = [self.line((self.x0, 0), (self.x1, 0), RULE, 1),
             self.line((0, self.y0), (0, self.y1), RULE, 1)]
        return o


def title(o, x, y, text, sub):
    o.append(f'<text x="{x}" y="{y}" font-size="15" font-weight="600" fill="{INK}">{text}</text>')
    o.append(f'<text x="{x}" y="{y+19}" font-size="12" fill="{MUTED}">{sub}</text>')


def panel_a(box):
    p = Panel(box, (-0.12, 0.92), (-0.16, 1.22))
    o = p.axes()
    o.append(p.poly([curve(F(k, 24)) for k in range(25)], GREY, 2.4))
    o.append(p.line((0, 0), (3 / 4, 1), INK, 2.6))
    o.append(p.line((0, 0), (3 / 4, 0), BLUE, 1.6))
    o.append(p.line((3 / 4, 0), (3 / 4, 1), BLUE, 1.6))
    o.append(p.line((0, 0), curve(F(1)), RED, 1.4, "6 4"))
    mx, my = curve(F(1, 2))
    o.append(p.dot(mx, my, 5, BLUE))
    o.append(p.line((mx - 0.30, my - 0.40), (mx + 0.30, my + 0.40), BLUE, 1.6, "5 4"))
    o.append(p.text(0.75, 1.0, "step end (3/4, 1)", anchor="end", dx=10, dy=-2))
    o.append(p.text(*curve(F(1)), "chord end (2/3, 1)", anchor="end", dx=-6, dy=20))
    o.append(p.text(mx, my, "middle t = 1/2", dx=12, dy=-6, col=BLUE))
    o.append(p.text(mx, my, "tangent there", dx=12, dy=10, col=BLUE))
    o.append(p.text(0.02, 0.30, "step sides", dx=6, dy=0, size=12))
    o.append(p.text(0.02, 0.22, "3/4, 1, 5/4", dx=6, dy=0, size=12))
    return o


def panel_b(box):
    p = Panel(box, (-0.08, 1.12), (-0.15, 2.35))
    o = p.axes()
    o.append(p.rect((0, 0), (1, 1.0), BLUE, BLUE, 0.18))
    o.append(p.line((0, 0), (1, 2.0), INK, 2.2))
    o.append(p.dot(0.5, 1.0, 5, BLUE))
    o.append(p.text(0.5, 1.0, "v(1/2) = 1", dx=10, dy=-4, col=BLUE))
    o.append(p.text(1.0, 2.0, "v = 2t", anchor="end", dx=-4, dy=-6))
    o.append(p.text(0.30, 0.18, "rectangle 1", size=12, col=BLUE))
    o.append(p.text(0.62, 0.55, "triangle 1", size=12))
    o.append(p.text(0.0, 2.15, "equal &mdash; no error", dx=4, dy=0, size=12, col=MUTED))
    return o


def panel_c(box):
    p = Panel(box, (-0.08, 1.12), (-0.12, 1.28))
    o = p.axes()
    o.append(p.rect((0, 0), (1, 0.75), BLUE, BLUE, 0.18))
    o.append(p.poly([(F(k, 40), 1 - (F(k, 40)) ** 2) for k in range(41)], INK, 2.2))
    o.append(p.dot(0.5, 0.75, 5, RED))
    o.append(p.text(0.5, 0.75, "v(1/2) = 3/4", dx=10, dy=-4, col=RED))
    o.append(p.text(1.0, 0.0, "t = 1", anchor="end", dx=0, dy=16, size=12))
    o.append(p.text(0.12, 0.10, "true area 2/3", size=12))
    o.append(p.text(0.52, 0.38, "rectangle 3/4", size=12, col=BLUE))
    o.append(p.text(0.02, 1.14, "3/4 &minus; 2/3 = 1/12 too long", dx=2, dy=0, size=12, col=MUTED))
    return o


def panel_d(box):
    p = Panel(box, (-6.5, 1.4), (-0.7, 9.9))
    o = p.axes()
    for gy in (3, 9):
        o.append(p.line((p.x0, gy), (p.x1, gy), "#efe7d2", 1))
    o.append(p.poly([curve(F(k, 60) * 3) for k in range(61)], GREY, 2.4))
    rows, _ = chain(F(0), F(3), 3)
    x = y = F(0)
    nodes = [(0.0, 0.0)]
    for r in rows:
        x += r["dx"]
        y += r["dy"]
        nodes.append((float(x), float(y)))
    o.append(p.poly(nodes, INK, 2.6))
    for a, b in nodes:
        o.append(p.dot(a, b, 4))
    o.append(f'<circle cx="{p.fx(-6):.2f}" cy="{p.fy(9):.2f}" r="8.5" fill="none" '
             f'stroke="{RED}" stroke-width="2"/>')
    o.append(p.text(-6, 9, "curve tip (&minus;6, 9)", anchor="end", dx=-12, dy=-6, col=RED))
    o.append(p.text(nodes[-1][0], nodes[-1][1], "chain tip (&minus;23/4, 9)",
                    dx=9, dy=14, size=12))
    o.append(p.text(0.1, 0.0, "nose", dx=8, dy=15, size=12))
    o.append(p.text(-2.1, 3.0, "waist (0, 3)", dx=10, dy=-6, size=12, col=MUTED))
    o.append(p.text(-6.2, 8.2, "gap 1/4 = 3 &times; 1/12", size=12, col=RED))
    o.append(p.text(-6.2, 6.9, "y exact at every node", size=12, col=MUTED))
    return o


def main():
    os.makedirs(OUT, exist_ok=True)
    W, H = 880, 800
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" font-family="Georgia, serif">',
         f'<rect width="{W}" height="{H}" fill="{PAPER}"/>',
         f'<text x="46" y="38" font-size="19" font-weight="600" fill="{INK}">'
         f'Fig. T2 &mdash; why the midpoint rule holds, and what the ends do</text>',
         f'<text x="46" y="60" font-size="13" fill="{MUTED}">'
         f'x = t &minus; t&sup3;/3, y = t&sup2; &middot; three steps over t = 0 to 3, '
         f'step width 1 &middot; y is up</text>']

    boxes = [((60, 100, 360, 250), "A. one step, sampled at its middle",
              "the step is not the curve&rsquo;s chord: 1/12 apart at the end"),
             ((480, 100, 360, 250), "B. y is exact",
              "y&prime; = 2t is a straight line; midpoint equals the area"),
             ((60, 430, 360, 250), "C. x drifts",
              "x&prime; = 1 &minus; t&sup2; bends; each step is 1/12 too long"),
             ((480, 430, 360, 250), "D. the ends",
              "three steps of 1/12 make the gap at the far tip")]
    for (box, head, sub), fn in zip(boxes, (panel_a, panel_b, panel_c, panel_d)):
        o += fn(box)
        title(o, box[0], box[1] - 14, head, sub)

    o.append(f'<text x="60" y="770" font-size="13" fill="{INK}">'
             'At t = 0 the first step is centred on t = 1/2, so the chain leaves the nose on the '
             'tangent there, not on the tangent at 0.</text>')
    o.append(f'<text x="60" y="788" font-size="13" fill="{INK}">'
             'At t = 3 the last step is centred on t = 5/2, and the 1/4 has accumulated, one '
             '1/12 per step, all in the same direction.</text>')
    o.append("</svg>")

    path = os.path.join(OUT, "midpoint.svg")
    with open(path, "w") as fh:
        fh.write("\n".join(o) + "\n")
    print(f"wrote {path}  ({W}x{H})")


if __name__ == "__main__":
    main()
