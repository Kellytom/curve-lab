"""Figure T1 in grid cells, with every vertex labelled and tabulated.

Pitch 256 cells per unit. The chain has 25 vertices, all integer points; the
plot numbers them 1 to 25 along the path and the panel on the right gives every
(x, y) pair in cells. The four points where the *curve* meets the lattice are
ringed and lettered A to D.

y is up in the model; the flip happens once, in fy().

Run:  .venv/bin/python tph_tri_chain/glyph.py
"""

import csv
import os
from fractions import Fraction as F

from chain import chain, grid, integral

T_MAX = F(3)
N_HALF = 12
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")

INK, MUTED, RULE, PAPER = "#2e2413", "#7b6c4e", "#d8ccae", "#fbf7ec"
GREY, BLUE, RED = "#7a6a4a", "#5b8fc9", "#a23b2a"


def build():
    """Right half mirrored, so the nose is (0, 0) and the tips are symmetric."""
    rows, _ = chain(F(0), T_MAX, N_HALF)
    g = grid(rows)
    x = y = F(0)
    right = [(0, 0)]
    for r in rows:
        x += r["dx"]
        y += r["dy"]
        right.append((int(x * g), int(y * g)))
    mirror = [(-X, Y) for X, Y in right]
    pts = list(reversed(mirror)) + right[1:]
    return pts, g


def write_csv(pts, g):
    path = os.path.join(OUT, "lattice-t3.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["index", "X_cells", "Y_cells", "step_dx", "step_dy"])
        for k, (X, Y) in enumerate(pts, 1):
            px, py = pts[k - 2] if k > 1 else (X, Y)
            w.writerow([k, X, Y, X - px, Y - py])
    return path


def smooth_cells(g, n=240):
    out = []
    for k in range(n + 1):
        t = -T_MAX + 2 * T_MAX * F(k, n)
        out.append(((t - t ** 3 / 3) * g, t * t * g))
    return out


def svg(pts, g, path):
    xmin, xmax = -1664, 1664
    ymin, ymax = -192, 2496
    ml, mr, mt, mb = 200, 90, 470, 480
    plot_w = ml + (xmax - xmin) + mr
    H = mt + (ymax - ymin) + mb
    tw = 1780                                  # table panel width
    W = plot_w + tw
    tx = plot_w + 40

    def fx(X):
        return ml + (float(X) - xmin)

    def fy(Y):                      # the one flip: model y up -> SVG y down
        return mt + (ymax - float(Y))

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1240" height="{1240*H/W:.0f}" '
         f'viewBox="0 0 {W} {H}" font-family="Georgia, serif">',
         f'<rect width="{W}" height="{H}" fill="{PAPER}"/>']

    for k in range(-26, 27):
        X = k * 64
        o.append(f'<line x1="{fx(X):.0f}" y1="{fy(ymin):.0f}" x2="{fx(X):.0f}" '
                 f'y2="{fy(ymax):.0f}" stroke="#f4efe2" stroke-width="2"/>')
    for k in range(0, 41):
        Y = k * 64
        o.append(f'<line x1="{fx(xmin):.0f}" y1="{fy(Y):.0f}" x2="{fx(xmax):.0f}" '
                 f'y2="{fy(Y):.0f}" stroke="#f4efe2" stroke-width="2"/>')
    for X in range(-1536, 1537, 256):
        o.append(f'<line x1="{fx(X):.0f}" y1="{fy(ymin):.0f}" x2="{fx(X):.0f}" '
                 f'y2="{fy(ymax):.0f}" stroke="{RULE}" stroke-width="3"/>')
    for Y in range(0, 2305, 256):
        o.append(f'<line x1="{fx(xmin):.0f}" y1="{fy(Y):.0f}" x2="{fx(xmax):.0f}" '
                 f'y2="{fy(Y):.0f}" stroke="{RULE}" stroke-width="3"/>')
    for X in range(-1536, 1537, 512):
        o.append(f'<text x="{fx(X):.0f}" y="{fy(0)+52:.0f}" font-size="52" '
                 f'text-anchor="middle" fill="{MUTED}">{X}</text>')
    for Y in range(0, 2305, 512):
        o.append(f'<text x="{fx(0)-18:.0f}" y="{fy(Y)+18:.0f}" font-size="52" '
                 f'text-anchor="end" fill="{MUTED}">{Y}</text>')

    o.append(f'<line x1="{fx(xmin):.0f}" y1="{fy(0):.0f}" x2="{fx(xmax):.0f}" '
             f'y2="{fy(0):.0f}" stroke="{INK}" stroke-width="6"/>')
    o.append(f'<line x1="{fx(0):.0f}" y1="{fy(ymin):.0f}" x2="{fx(0):.0f}" '
             f'y2="{fy(ymax):.0f}" stroke="{INK}" stroke-width="6"/>')

    for k in range(1, len(pts)):
        x0, y0 = float(pts[k - 1][0]), float(pts[k - 1][1])
        x1, y1 = float(pts[k][0]), float(pts[k][1])
        o.append(f'<polyline points="{fx(x0):.0f},{fy(y0):.0f} {fx(x1):.0f},{fy(y0):.0f} '
                 f'{fx(x1):.0f},{fy(y1):.0f}" fill="none" stroke="{BLUE}" stroke-width="3"/>')

    pts_s = " ".join(f"{fx(X):.0f},{fy(Y):.0f}" for X, Y in smooth_cells(g))
    o.append(f'<polyline points="{pts_s}" fill="none" stroke="{GREY}" stroke-width="7"/>')
    pts_s = " ".join(f"{fx(X):.0f},{fy(Y):.0f}" for X, Y in pts)
    o.append(f'<polyline points="{pts_s}" fill="none" stroke="{INK}" stroke-width="6"/>')

    for k, (X, Y) in enumerate(pts, 1):
        o.append(f'<circle cx="{fx(X):.0f}" cy="{fy(Y):.0f}" r="8" fill="{INK}"/>')
        dx = 22 if X > 0 else -22
        anchor = "start" if X > 0 else "end"
        o.append(f'<text x="{fx(X)+dx:.0f}" y="{fy(Y)-16:.0f}" font-size="54" '
                 f'fill="{MUTED}" text-anchor="{anchor}">{k}</text>')

    for X, Y, letter in ((0, 0, "A"), (0, 768, "B"), (-1536, 2304, "C"),
                         (1536, 2304, "D")):
        o.append(f'<circle cx="{fx(X):.0f}" cy="{fy(Y):.0f}" r="26" fill="none" '
                 f'stroke="{RED}" stroke-width="6"/>')
        dx = 30 if X >= 0 else -30
        anchor = "start" if X >= 0 else "end"
        o.append(f'<text x="{fx(X)+dx:.0f}" y="{fy(Y)+64:.0f}" font-size="62" '
                 f'font-weight="600" fill="{RED}" text-anchor="{anchor}">{letter}</text>')

    o.append(f'<text x="48" y="92" font-size="86" font-weight="600" fill="{INK}">'
             f'Fig. T1 &#8212; 25 vertices, every one an integer point</text>')
    for k, line in enumerate([
            "pitch 256 cells per unit; the numbers 1 to 25 run along the path from the right tip",
            "curve x = t &#8722; t&#179;/3, y = t&#178;; A to D are the four parameters where the curve itself hits the lattice",
            "the sides are whole as well: 65, 73, 89, 113, 145 cells &#8230;"]):
        o.append(f'<text x="48" y="{146 + k*64}" font-size="50" fill="{MUTED}">{line}</text>')

    # legend
    lx, ly = 60, H - 420
    o.append(f'<rect x="{lx-16}" y="{ly-74}" width="1160" height="420" fill="{PAPER}" '
             f'fill-opacity="0.97" stroke="{RULE}" stroke-width="3"/>')
    for k, (col, wd, lab) in enumerate([
            (GREY, 7, "smooth curve"), (INK, 6, "chain, 24 sides"),
            (BLUE, 3, "step legs"), (RED, 5, "curve meets the lattice"),
            (RULE, 3, "grid: unit lines, pale every 1/4")]):
        yy = ly - 34 + k * 78
        o.append(f'<line x1="{lx}" y1="{yy}" x2="{lx+110}" y2="{yy}" stroke="{col}" '
                 f'stroke-width="{wd}"/>')
        o.append(f'<text x="{lx+140}" y="{yy+20}" font-size="54" fill="{INK}">{lab}</text>')

    # the 25 pairs
    o.append(f'<text x="{tx}" y="{mt-10}" font-size="62" font-weight="600" fill="{INK}">'
             f'all 25 vertices, cells</text>')
    o.append(f'<line x1="{tx}" y1="{mt+10}" x2="{tx+tw-120}" y2="{mt+10}" '
             f'stroke="{RULE}" stroke-width="3"/>')
    half = 13
    for k, (X, Y) in enumerate(pts, 1):
        col = 0 if k <= half else 1
        row = (k - 1) % half
        cx = tx + col * 850
        cy = mt + 90 + row * 88
        o.append(f'<text x="{cx}" y="{cy}" font-size="58" fill="{MUTED}" '
                 f'text-anchor="end">{k}</text>')
        o.append(f'<text x="{cx+24}" y="{cy}" font-size="58" fill="{INK}">'
                 f'({X}, {Y})</text>')

    o.append("</svg>")
    with open(path, "w") as fh:
        fh.write("\n".join(o) + "\n")
    return path, W, H


def main():
    os.makedirs(OUT, exist_ok=True)
    pts, g = build()
    csv_path = write_csv(pts, g)
    svg_path, W, H = svg(pts, g, os.path.join(OUT, "lattice-t3.svg"))
    print(f"pitch {g}  vertices {len(pts)}")
    print("first, middle, last:", pts[0], pts[len(pts)//2], pts[-1])
    print(f"csv {csv_path}")
    print(f"svg {svg_path}  viewBox {W} x {H}")


if __name__ == "__main__":
    main()
