"""Figure T1 in grid cells, not units: every coordinate an integer.

Pitch 256 cells per unit, so one unit is 256 cells and the whole-number points
sit at integer cells: nose (0, 0), waist (0, 768), tips (+-1536, 2304).
The SVG is drawn in cell coordinates with width/height set to display size, so
Inkscape opens it on the integer grid.

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
    pos, dt = chain(F(0), T_MAX, N_HALF)
    g = grid(pos)
    left, x, y = [], F(0), F(0)
    for r in pos:
        x -= r["dx"]
        y += r["dy"]
        left.append(dict(t=-r["t"], dx=-r["dx"], dy=r["dy"], ds=r["ds"], x=x, y=y))
    nodes = [dict(i=0, t=F(0), dx=F(0), dy=F(0), ds=F(0), x=F(0), y=F(0))]
    nodes += [dict(i=0, **nd) for nd in reversed(left)]
    cx = cy = F(0)
    for r in pos:
        cx += r["dx"]
        cy += r["dy"]
        nodes.append(dict(i=0, t=r["t"], dx=r["dx"], dy=r["dy"], ds=r["ds"], x=cx, y=cy))
    for k, nd in enumerate(nodes):
        nd["i"] = k
    return nodes, g, dt


def write_csv(nodes, g):
    path = os.path.join(OUT, "lattice-t3.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["step", "t_mid", "X_cells", "Y_cells", "dx_cells", "dy_cells",
                    "ds_cells", "x_unit", "y_unit"])
        for nd in nodes[1:]:
            w.writerow([nd["i"], f"{float(nd['t']):+.2f}", int(nd["x"] * g),
                        int(nd["y"] * g), int(nd["dx"] * g), int(nd["dy"] * g),
                        int(nd["ds"] * g), f"{float(nd['x']):.6f}",
                        f"{float(nd['y']):.6f}"])
    return path


def smooth_cells(g, n=240):
    out = []
    for k in range(n + 1):
        t = -T_MAX + 2 * T_MAX * F(k, n)
        out.append(((t - t ** 3 / 3) * g, t * t * g))
    return out


def svg(nodes, g, path):
    # canvas in cells
    xmin, xmax = -1664, 1664
    ymin, ymax = -192, 2496
    ml, mr, mt, mb = 200, 90, 460, 520
    W = ml + (xmax - xmin) + mr
    H = mt + (ymax - ymin) + mb

    def fx(X):
        return ml + (float(X) - xmin)

    def fy(Y):                      # the one flip: model y up -> SVG y down
        return mt + (ymax - float(Y))

    step = 256 * 2                  # a labelled tick every two units
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{900*H/W:.0f}" '
         f'viewBox="0 0 {W} {H}" font-family="Georgia, serif">',
         f'<rect width="{W}" height="{H}" fill="{PAPER}"/>']

    # pale lines every quarter unit (64 cells), solid every unit (256 cells)
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

    for X in range(-1536, 1537, step):
        o.append(f'<text x="{fx(X):.0f}" y="{fy(0)+52:.0f}" font-size="52" '
                 f'text-anchor="middle" fill="{MUTED}">{X}</text>')
    for Y in range(0, 2305, step):
        o.append(f'<text x="{fx(0)-18:.0f}" y="{fy(Y)+18:.0f}" font-size="52" '
                 f'text-anchor="end" fill="{MUTED}">{Y}</text>')

    o.append(f'<line x1="{fx(xmin):.0f}" y1="{fy(0):.0f}" x2="{fx(xmax):.0f}" '
             f'y2="{fy(0):.0f}" stroke="{INK}" stroke-width="6"/>')
    o.append(f'<line x1="{fx(0):.0f}" y1="{fy(ymin):.0f}" x2="{fx(0):.0f}" '
             f'y2="{fy(ymax):.0f}" stroke="{INK}" stroke-width="6"/>')
    o.append(f'<text x="{fx(xmax)+24:.0f}" y="{fy(0)+16:.0f}" font-size="56" '
             f'fill="{INK}">x</text>')
    o.append(f'<text x="{fx(0)+20:.0f}" y="{fy(ymax)-24:.0f}" font-size="56" '
             f'fill="{INK}">y</text>')

    # right triangles: legs in cell space
    for nd in nodes[1:]:
        x0, y0 = float(nd["x"] * g), float(nd["y"] * g)
        x1, y1 = x0 + float(nd["dx"] * g), y0 + float(nd["dy"] * g)
        o.append(f'<polyline points="{fx(x0):.0f},{fy(y0):.0f} {fx(x1):.0f},{fy(y0):.0f} '
                 f'{fx(x1):.0f},{fy(y1):.0f}" fill="none" stroke="{BLUE}" '
                 f'stroke-width="3"/>')

    pts = " ".join(f"{fx(X):.0f},{fy(Y):.0f}" for X, Y in smooth_cells(g))
    o.append(f'<polyline points="{pts}" fill="none" stroke="{GREY}" stroke-width="7"/>')

    pts = " ".join(f"{fx(float(n['x'] * g)):.0f},{fy(float(n['y'] * g)):.0f}"
                   for n in nodes)
    o.append(f'<polyline points="{pts}" fill="none" stroke="{INK}" stroke-width="6"/>')
    for nd in nodes:
        o.append(f'<circle cx="{fx(float(nd["x"] * g)):.0f}" '
                 f'cy="{fy(float(nd["y"] * g)):.0f}" r="9" fill="{INK}"/>')

    hits = [(0, 0, "A", 0, 0, "start"),
            (0, 768, "B", 0, 0, "start"),
            (1536, 2304, "C", 0, 0, "start"),
            (-1536, 2304, "D", 0, 0, "start")]
    for X, Y, letter, _, _, _ in hits:
        o.append(f'<circle cx="{fx(X):.0f}" cy="{fy(Y):.0f}" r="26" fill="none" '
                 f'stroke="{RED}" stroke-width="6"/>')
        dx, dy, anchor = (34, -22, "start") if X >= 0 else (-34, -22, "end")
        o.append(f'<text x="{fx(X)+dx:.0f}" y="{fy(Y)+dy:.0f}" font-size="66" '
                 f'font-weight="600" fill="{RED}" text-anchor="{anchor}">{letter}</text>')

    tipX = float(nodes[-1]["x"] * g)
    o.append(f'<text x="{fx(tipX)+18:.0f}" y="{fy(2304)+64:.0f}" font-size="50" '
             f'fill="{INK}">chain tip ({tipX:.0f}, 2304)</text>')

    o.append(f'<text x="48" y="86" font-size="86" font-weight="600" fill="{INK}">'
             f'Fig. T1 &#8212; 24 triangles on the integer grid</text>')
    for k, line in enumerate([
            "coordinates are grid cells, not units: pitch 256, so one unit is 256 cells; A to D below",
            "curve x = t &#8722; t&#179;/3, y = t&#178;; whole-number points at t = 0, 3 and the waist",
            "the chain stops at &#8722;1532 in x, four cells short of &#8722;1536"]):
        o.append(f'<text x="48" y="{140 + k*68}" font-size="52" fill="{MUTED}">{line}</text>')

    lx, ly = 60, H - 430
    o.append(f'<rect x="{lx-16}" y="{ly-74}" width="1180" height="430" fill="{PAPER}" '
             f'fill-opacity="0.97" stroke="{RULE}" stroke-width="3"/>')
    rows = [(GREY, 7, "smooth curve"), (INK, 6, "chain, 24 hypotenuses"),
            (BLUE, 3, "step legs"), (RED, 5, "whole-number point"),
            (RULE, 3, "grid: unit lines, pale every 1/4 unit")]
    for k, (col, wd, lab) in enumerate(rows):
        yy = ly - 34 + k * 82
        o.append(f'<line x1="{lx}" y1="{yy}" x2="{lx+120}" y2="{yy}" stroke="{col}" '
                 f'stroke-width="{wd}"/>')
        o.append(f'<text x="{lx+150}" y="{yy+20}" font-size="54" fill="{INK}">{lab}</text>')

    tx, ty = 1400, H - 500
    o.append(f'<rect x="{tx-24}" y="{ty-70}" width="1360" height="430" fill="{PAPER}" '
             f'fill-opacity="0.97" stroke="{RULE}" stroke-width="3"/>')
    o.append(f'<text x="{tx}" y="{ty-18}" font-size="54" font-weight="600" fill="{INK}">'
             f'points where the curve hits the lattice</text>')
    table = [("A", "(0, 0)", "(0, 0)"), ("B", "(0, 768)", "(0, 3)"),
             ("C", "(&#8722;1536, 2304)", "(&#8722;6, 9)"),
             ("D", "(1536, 2304)", "(6, 9)")]
    o.append(f'<text x="{tx}" y="{ty+34}" font-size="44" fill="{MUTED}">point</text>')
    o.append(f'<text x="{tx+150}" y="{ty+34}" font-size="44" fill="{MUTED}">cells</text>')
    o.append(f'<text x="{tx+780}" y="{ty+34}" font-size="44" fill="{MUTED}">units</text>')
    for k, (letter, cells, units) in enumerate(table):
        yy = ty + 96 + k * 82
        o.append(f'<text x="{tx}" y="{yy}" font-size="54" font-weight="600" '
                 f'fill="{RED}">{letter}</text>')
        o.append(f'<text x="{tx+150}" y="{yy}" font-size="54" fill="{INK}">{cells}</text>')
        o.append(f'<text x="{tx+780}" y="{yy}" font-size="54" fill="{INK}">{units}</text>')

    o.append("</svg>")
    with open(path, "w") as fh:
        fh.write("\n".join(o) + "\n")
    return path, W, H


def main():
    os.makedirs(OUT, exist_ok=True)
    nodes, g, dt = build()
    csv_path = write_csv(nodes, g)
    svg_path, W, H = svg(nodes, g, os.path.join(OUT, "lattice-t3.svg"))
    print(f"pitch {g}  triangles {len(nodes)-1}  step width {dt}")
    print(f"tip cells ({nodes[-1]['x']*g}, {nodes[-1]['y']*g})  "
          f"curve tip cells ({-6*g}, {9*g})")
    print(f"csv {csv_path}")
    print(f"svg {svg_path}  viewBox {W} x {H}")


if __name__ == "__main__":
    main()
