"""Generate the fish glyph chain: CSV of exact integer steps + labelled SVG.

y is up in the model (the T-PH curve has y = t^2 >= 0). SVG y is down, so the
flip happens once, in `fy()`, at output. Nowhere else.

Run:  .venv/bin/python tph_tri_chain/glyph.py
"""

import csv
import os
from fractions import Fraction as F

from chain import chain, grid, integral

T_MAX = F(12, 5)   # stop parameter; 2.4 = 12/5
N_HALF = 120       # triangles per half; dt = 1/50
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


def build():
    """Left tail -> nose -> right tail, as one list of nodes."""
    pos, dt = chain(F(0), T_MAX, N_HALF)
    g = grid(pos)
    half = [dict(i=r["i"], t=r["t"], dx=r["dx"], dy=r["dy"], ds=r["ds"],
                 x=r["x"], y=r["y"]) for r in pos]
    # mirror: x(-t) = -x(t), y(-t) = y(t), same triples reflected
    left = []
    x = y = F(0)
    for r in half:                       # travel leftwards from the nose
        x -= r["dx"]
        y += r["dy"]
        left.append(dict(i=r["i"], t=-r["t"], dx=-r["dx"], dy=r["dy"],
                         ds=r["ds"], x=x, y=y))
    nodes = [dict(i=0, t=F(0), dx=F(0), dy=F(0), ds=F(0), x=F(0), y=F(0))]
    nodes += list(reversed(left))
    chain_x, chain_y = F(0), F(0)
    for r in half:
        chain_x += r["dx"]
        chain_y += r["dy"]
        nodes.append(dict(i=0, t=r["t"], dx=r["dx"], dy=r["dy"], ds=r["ds"],
                          x=chain_x, y=chain_y))
    for k, nd in enumerate(nodes):
        nd["i"] = k
    return nodes, g, dt


def write_csv(nodes, g):
    path = os.path.join(OUT, "fish-t24.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["step", "t_mid", "dx_grid", "dy_grid", "ds_grid",
                    "X_grid", "Y_grid", "t_mid_float",
                    "dx_float", "dy_float", "ds_float", "x_float", "y_float"])
        for nd in nodes[1:]:
            w.writerow([nd["i"], f"{float(nd['t']):+.2f}", int(nd["dx"] * g), int(nd["dy"] * g),
                        int(nd["ds"] * g), int(nd["x"] * g), int(nd["y"] * g),
                        f"{float(nd['t']):.4f}", f"{float(nd['dx']):.6f}",
                        f"{float(nd['dy']):.6f}", f"{float(nd['ds']):.6f}",
                        f"{float(nd['x']):.6f}", f"{float(nd['y']):.6f}"])
    return path


def smooth(n=480):
    pts = []
    for k in range(n + 1):
        t = -T_MAX + (2 * T_MAX) * F(k, n)
        pts.append((float(t - t**3 / 3), float(t**2)))
    return pts


def svg(nodes, g, path):
    xs = [float(nd["x"]) for nd in nodes]
    ys = [float(nd["y"]) for nd in nodes]
    xmin, xmax = min(xs) - 0.14, max(xs) + 0.14
    ymin, ymax = -0.30, max(ys) + 0.22

    ml, mr, mt, mb = 96, 56, 132, 86
    avail_w, avail_h = 700, 860
    sc = min(avail_w / (xmax - xmin), avail_h / (ymax - ymin))
    W = ml + sc * (xmax - xmin) + mr
    H = mt + sc * (ymax - ymin) + mb

    def fx(x):
        return ml + (x - xmin) * sc

    def fy(y):                      # the one y flip: model y up -> SVG y down
        return mt + (ymax - y) * sc

    o = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" '
             f'height="{H:.0f}" viewBox="0 0 {W:.0f} {H:.0f}" '
             f'font-family="Helvetica, Arial, sans-serif">')
    o.append(f'<rect width="{W:.0f}" height="{H:.0f}" fill="#fff"/>')

    # gridlines + ticks
    for k in range(-2, 3):
        o.append(f'<line x1="{fx(k):.1f}" y1="{fy(ymin):.1f}" x2="{fx(k):.1f}" '
                 f'y2="{fy(ymax):.1f}" stroke="#ececec" stroke-width="1"/>')
        o.append(f'<text x="{fx(k):.1f}" y="{fy(0)+18:.1f}" font-size="13" '
                 f'text-anchor="middle" fill="#555">{k}</text>')
    for k in range(0, 7):
        o.append(f'<line x1="{fx(xmin):.1f}" y1="{fy(k):.1f}" x2="{fx(xmax):.1f}" '
                 f'y2="{fy(k):.1f}" stroke="#ececec" stroke-width="1"/>')
        o.append(f'<text x="{fx(0)-10:.1f}" y="{fy(k)+5:.1f}" font-size="13" '
                 f'text-anchor="end" fill="#555">{k}</text>')

    # axes
    o.append(f'<line x1="{fx(xmin):.1f}" y1="{fy(0):.1f}" x2="{fx(xmax):.1f}" '
             f'y2="{fy(0):.1f}" stroke="#444" stroke-width="1.6"/>')
    o.append(f'<line x1="{fx(0):.1f}" y1="{fy(ymin):.1f}" x2="{fx(0):.1f}" '
             f'y2="{fy(ymax):.1f}" stroke="#444" stroke-width="1.6"/>')
    o.append(f'<text x="{fx(xmax)+10:.1f}" y="{fy(0)+5:.1f}" font-size="16" '
             f'fill="#222">x</text>')
    o.append(f'<text x="{fx(0)+10:.1f}" y="{fy(ymax)-6:.1f}" font-size="16" '
             f'fill="#222">y (up)</text>')

    # self-intersection line
    o.append(f'<line x1="{fx(xmin):.1f}" y1="{fy(3):.1f}" x2="{fx(xmax):.1f}" '
             f'y2="{fy(3):.1f}" stroke="#b06" stroke-width="1.4" '
             f'stroke-dasharray="7 5"/>')
    o.append(f'<text x="{fx(xmin)+10:.1f}" y="{fy(3)-8:.1f}" font-size="15" '
             f'fill="#b06">self-intersection (0, 3), t = &#177;&#8730;3</text>')

    # right-triangle legs, axis-aligned, one L per step
    for nd in nodes[1:]:
        x0, y0 = float(nd["x"]) - float(nd["dx"]), float(nd["y"]) - float(nd["dy"])
        x1, y1 = float(nd["x"]), float(nd["y"])
        o.append(f'<polyline points="{fx(x0):.1f},{fy(y0):.1f} {fx(x1):.1f},{fy(y0):.1f} '
                 f'{fx(x1):.1f},{fy(y1):.1f}" fill="none" stroke="#9bb7d4" '
                 f'stroke-width="0.8" opacity="0.85"/>')

    # smooth curve
    pts = " ".join(f"{fx(x):.1f},{fy(y):.1f}" for x, y in smooth())
    o.append(f'<polyline points="{pts}" fill="none" stroke="#7a7a7a" '
             f'stroke-width="2.2"/>')

    # chain: the hypotenuses, tip to tail
    pts = " ".join(f"{fx(float(nd['x'])):.1f},{fy(float(nd['y'])):.1f}" for nd in nodes)
    o.append(f'<polyline points="{pts}" fill="none" stroke="#111" stroke-width="2.6"/>')

    # nodes every 12th, plus the named ones
    for nd in nodes[::12]:
        o.append(f'<circle cx="{fx(float(nd["x"])):.1f}" cy="{fy(float(nd["y"])):.1f}" '
                 f'r="2.2" fill="#111"/>')

    # named points
    marks = [(0.0, 0.0, "nose (0, 0)", 14, 18, "start"),
             (0.0, 3.0, "crossing (0, 3)", 12, -14, "middle"),
             (-2.20792, 5.76, "tip (&#8722;2.208, 5.76)", 13, -12, "start"),
             (2.20792, 5.76, "tip (2.208, 5.76)", -13, -12, "end")]
    for mx, my, lab, dx, dy, anchor in marks:
        o.append(f'<circle cx="{fx(mx):.1f}" cy="{fy(my):.1f}" r="4.6" fill="#c00"/>')
        o.append(f'<text x="{fx(mx)+dx:.1f}" y="{fy(my)+dy:.1f}" font-size="15" '
                 f'fill="#c00" text-anchor="{anchor}">{lab}</text>')

    # title block
    o.append(f'<text x="{ml-30:.1f}" y="34" font-size="21" font-weight="600" '
             f'fill="#111">Fig. T1 &#8212; T-PH fish glyph as a Pythagorean triangle chain</text>')
    o.append(f'<text x="{ml-30:.1f}" y="62" font-size="15" fill="#444">'
             f'midpoint rule, u = 1, v = t; t &#8712; [&#8722;12/5, 12/5], '
             f'N = 240 triangles, &#916;t = 1/50</text>')
    o.append(f'<text x="{ml-30:.1f}" y="84" font-size="15" fill="#444">'
             f'every leg and hypotenuse an exact integer on the 500000 grid '
             f'(= 160 &#215; 3125)</text>')
    o.append(f'<text x="{ml-30:.1f}" y="106" font-size="15" fill="#444">'
             f'chain length 14.015840 against exact 1752/125 = 14.016000</text>')

    # legend
    lx, ly = fx(xmin) + 16, fy(ymin) - 118
    rows = [("#7a7a7a", 2.2, None, "smooth T-PH curve"),
            ("#111", 2.6, None, "chain: hypotenuses, tip to tail"),
            ("#9bb7d4", 0.8, None, "triangle legs &#916;x, &#916;y (one L per step)")]
    o.append(f'<rect x="{lx-10:.1f}" y="{ly-24:.1f}" width="392" height="112" '
             f'fill="#fff" fill-opacity="0.92" stroke="#bbb"/>')
    for k, (col, wdt, _, lab) in enumerate(rows):
        yy = ly + k * 26
        o.append(f'<line x1="{lx:.1f}" y1="{yy:.1f}" x2="{lx+34:.1f}" y2="{yy:.1f}" '
                 f'stroke="{col}" stroke-width="{wdt}"/>')
        o.append(f'<text x="{lx+44:.1f}" y="{yy+5:.1f}" font-size="15" '
                 f'fill="#222">{lab}</text>')
    yy = ly + 3 * 26
    o.append(f'<circle cx="{lx+17:.1f}" cy="{yy:.1f}" r="4.4" fill="#c00"/>')
    o.append(f'<text x="{lx+44:.1f}" y="{yy+5:.1f}" font-size="15" fill="#222">'
             f'named point (nose, crossing, tail tip)</text>')

    o.append('</svg>')
    with open(path, "w") as fh:
        fh.write("\n".join(o) + "\n")
    return path, W, H


def main():
    os.makedirs(OUT, exist_ok=True)
    nodes, g, dt = build()
    csv_path = write_csv(nodes, g)
    svg_path, W, H = svg(nodes, g, os.path.join(OUT, "fish-t24.svg"))

    exact = integral(T_MAX)
    total = sum(nd["ds"] for nd in nodes[1:])
    print(f"grid            {g}  = {F(g, 3125)} x 3125")
    print(f"triangles       {len(nodes)-1}  (dt = {dt})")
    print(f"nodes           all integer on the grid")
    print(f"  left tip      ({int(nodes[-1]['x']*g)}, {int(nodes[-1]['y']*g)})")
    print(f"  right tip     ({int(nodes[1]['x']*g)}, {int(nodes[1]['y']*g)})")
    print(f"  nose          ({int(nodes[0]['x']*g)}, {int(nodes[0]['y']*g)})")
    print(f"chain length    {total} = {float(total):.6f}")
    print(f"exact length    {2*exact[2]} = {float(2*exact[2]):.6f}")
    print(f"error           {float(total - 2*exact[2]):+.3e}")
    near = min(nodes, key=lambda n: float(n["x"]) ** 2 + (float(n["y"]) - 3) ** 2)
    print(f"crossing        nearest node to (0,3) is "
          f"({float(near['x']):+.5f}, {float(near['y']):.5f}), "
          f"off by {abs(float(near['y'])-3):.5f} in y")
    print(f"tip y exact?    {nodes[1]['y'] == F(144, 25)}  (y = 144/25 for any N)")
    print(f"csv             {csv_path}")
    print(f"svg             {svg_path}  ({W:.0f} x {H:.0f})")


if __name__ == "__main__":
    main()
