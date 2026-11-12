"""Figure: the curve's whole-number hits, with the twelve-triangle chain.

Curve t in [-3, 3]; step width 1/4, so the pitch is 256 cells per unit.
y is up in the model. SVG y is down, so the flip happens once, in fy().

Run:  .venv/bin/python tph_tri_chain/glyph.py
"""

import csv
import os
from fractions import Fraction as F

from chain import chain, grid, integral

T_MAX = F(3)        # the first lattice stop
N_HALF = 12         # twelve triangles per branch, as asked
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


def build():
    pos, dt = chain(F(0), T_MAX, N_HALF)
    g = grid(pos)
    left = []
    x = y = F(0)
    for r in pos:                       # mirror, travelling out from the nose
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
        w.writerow(["step", "t_mid", "dx_cells", "dy_cells", "ds_cells",
                    "X_cells", "Y_cells", "dx", "dy", "ds", "x", "y"])
        for nd in nodes[1:]:
            w.writerow([nd["i"], f"{float(nd['t']):+.2f}", int(nd["dx"] * g),
                        int(nd["dy"] * g), int(nd["ds"] * g),
                        int(nd["x"] * g), int(nd["y"] * g),
                        f"{float(nd['dx']):.6f}", f"{float(nd['dy']):.6f}",
                        f"{float(nd['ds']):.6f}", f"{float(nd['x']):.6f}",
                        f"{float(nd['y']):.6f}"])
    return path


def smooth(n=360):
    return [(float(t - t**3 / 3), float(t**2))
            for t in (-T_MAX + 2 * T_MAX * F(k, n) for k in range(n + 1))]


def svg(nodes, g, path):
    xs = [float(n["x"]) for n in nodes]
    ys = [float(n["y"]) for n in nodes]
    xmin, xmax = min(xs + [-6.0]) - 0.30, max(xs + [6.0]) + 0.30
    ymin, ymax = -0.55, max(ys + [9.0]) + 0.55

    ml, mr, mt, mb = 92, 54, 128, 200
    avail_w, avail_h = 680, 780
    sc = min(avail_w / (xmax - xmin), avail_h / (ymax - ymin))
    W = ml + sc * (xmax - xmin) + mr
    H = mt + sc * (ymax - ymin) + mb

    def fx(x):
        return ml + (x - xmin) * sc

    def fy(y):                      # the one y flip: model y up -> SVG y down
        return mt + (ymax - y) * sc

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" '
         f'viewBox="0 0 {W:.0f} {H:.0f}" font-family="Helvetica, Arial, sans-serif">',
         f'<rect width="{W:.0f}" height="{H:.0f}" fill="#fff"/>']

    for k in range(-28, 29):
        o.append(f'<line x1="{fx(k/4):.1f}" y1="{fy(ymin):.1f}" x2="{fx(k/4):.1f}" '
                 f'y2="{fy(ymax):.1f}" stroke="#f4efe2" stroke-width="1"/>')
    for k in range(0, 41):
        o.append(f'<line x1="{fx(xmin):.1f}" y1="{fy(k/4):.1f}" x2="{fx(xmax):.1f}" '
                 f'y2="{fy(k/4):.1f}" stroke="#f4efe2" stroke-width="1"/>')
    for k in range(-6, 7):
        o.append(f'<line x1="{fx(k):.1f}" y1="{fy(ymin):.1f}" x2="{fx(k):.1f}" '
                 f'y2="{fy(ymax):.1f}" stroke="#ddd3b8" stroke-width="1.2"/>')
        o.append(f'<text x="{fx(k):.1f}" y="{fy(0)+17:.1f}" font-size="12" '
                 f'text-anchor="middle" fill="#666">{k}</text>')
    for k in range(0, 10):
        o.append(f'<line x1="{fx(xmin):.1f}" y1="{fy(k):.1f}" x2="{fx(xmax):.1f}" '
                 f'y2="{fy(k):.1f}" stroke="#ddd3b8" stroke-width="1.2"/>')
        o.append(f'<text x="{fx(0)-9:.1f}" y="{fy(k)+4:.1f}" font-size="12" '
                 f'text-anchor="end" fill="#666">{k}</text>')

    o.append(f'<line x1="{fx(xmin):.1f}" y1="{fy(0):.1f}" x2="{fx(xmax):.1f}" '
             f'y2="{fy(0):.1f}" stroke="#3a3a3a" stroke-width="2.4"/>')
    o.append(f'<line x1="{fx(0):.1f}" y1="{fy(ymin):.1f}" x2="{fx(0):.1f}" '
             f'y2="{fy(ymax):.1f}" stroke="#3a3a3a" stroke-width="2.4"/>')
    o.append(f'<text x="{fx(xmax)+8:.1f}" y="{fy(0)+5:.1f}" font-size="15" fill="#222">x</text>')
    o.append(f'<text x="{fx(0)+9:.1f}" y="{fy(ymax)-6:.1f}" font-size="15" fill="#222">y</text>')

    # chain legs
    for nd in nodes[1:]:
        x0, y0 = float(nd["x"]) - float(nd["dx"]), float(nd["y"]) - float(nd["dy"])
        x1, y1 = float(nd["x"]), float(nd["y"])
        o.append(f'<polyline points="{fx(x0):.1f},{fy(y0):.1f} {fx(x1):.1f},{fy(y0):.1f} '
                 f'{fx(x1):.1f},{fy(y1):.1f}" fill="none" stroke="#9bb7d4" stroke-width="1"/>')

    pts = " ".join(f"{fx(x):.1f},{fy(y):.1f}" for x, y in smooth())
    o.append(f'<polyline points="{pts}" fill="none" stroke="#7a7a7a" stroke-width="2.2"/>')

    pts = " ".join(f"{fx(float(n['x'])):.1f},{fy(float(n['y'])):.1f}" for n in nodes)
    o.append(f'<polyline points="{pts}" fill="none" stroke="#111" stroke-width="2.5"/>')

    for nd in nodes:
        o.append(f'<circle cx="{fx(float(nd["x"])):.1f}" cy="{fy(float(nd["y"])):.1f}" '
                 f'r="3" fill="#111"/>')

    # the whole-number hits
    hits = [(0.0, 0.0, "nose (0, 0)", 12, 20, "start"),
            (0.0, 3.0, "waist (0, 3) at t = &#177;&#8730;3", 12, -12, "start"),
            (6.0, 9.0, "hit (6, 9)", -11, -12, "end"),
            (-6.0, 9.0, "hit (&#8722;6, 9)", -10, -12, "end")]
    for hx, hy, lab, dx, dy, anchor in hits:
        o.append(f'<circle cx="{fx(hx):.1f}" cy="{fy(hy):.1f}" r="6.5" fill="none" '
                 f'stroke="#c00" stroke-width="2"/>')
        o.append(f'<text x="{fx(hx)+dx:.1f}" y="{fy(hy)+dy:.1f}" font-size="15" '
                 f'fill="#c00" text-anchor="{anchor}">{lab}</text>')

    tip = nodes[-1]
    o.append(f'<text x="{fx(float(tip["x"]))+12:.1f}" y="{fy(float(tip["y"]))+26:.1f}" '
             f'font-size="14" fill="#111" text-anchor="start">chain tip '
             f'{float(tip["x"]):.5f}</text>')

    o.append(f'<text x="{ml-24:.1f}" y="34" font-size="20" font-weight="600" fill="#111">'
             f'Fig. T1 &#8212; whole-number hits, 12 triangles per side</text>')
    for k, line in enumerate([
            "curve x = t &#8722; t&#179;/3, y = t&#178;; whole-number hits at t = 0, 3, 6&#8230; and the waist",
            "midpoint chain: step 1/4, pitch 256 cells per unit, y exact, x 1/64 short"]):
        o.append(f'<text x="{ml-24:.1f}" y="{62 + k*22}" font-size="14" fill="#444">{line}</text>')

    lx, ly = fx(xmin) + 14, fy(ymin) + 34
    o.append(f'<rect x="{lx-9:.1f}" y="{ly-22:.1f}" width="452" height="122" fill="#fff" '
             f'fill-opacity="0.97" stroke="#d8ccae"/>')
    rows = [("#7a7a7a", 2.2, "smooth curve"), ("#111", 2.5, "chain, 24 hypotenuses"),
            ("#9bb7d4", 1.0, "step legs"), ("#c00", 2.0, "whole-number hit"),
            ("#ddd3b8", 1.2, "grid: unit lines; pale every 1/4; pitch 256")]
    for k, (col, wdt, lab) in enumerate(rows):
        yy = ly + k * 22
        o.append(f'<line x1="{lx:.1f}" y1="{yy:.1f}" x2="{lx+30:.1f}" y2="{yy:.1f}" '
                 f'stroke="{col}" stroke-width="{wdt}"/>')
        o.append(f'<text x="{lx+40:.1f}" y="{yy+5:.1f}" font-size="15" fill="#222">{lab}</text>')

    o.append("</svg>")
    with open(path, "w") as fh:
        fh.write("\n".join(o) + "\n")
    return path, W, H


def main():
    os.makedirs(OUT, exist_ok=True)
    nodes, g, dt = build()
    csv_path = write_csv(nodes, g)
    svg_path, W, H = svg(nodes, g, os.path.join(OUT, "lattice-t3.svg"))
    xt, yt, st = integral(T_MAX)
    total = sum(n["ds"] for n in nodes[1:])
    print(f"t_max {T_MAX}  N {N_HALF}/branch  step width {dt}  pitch {g}")
    print(f"triangles {len(nodes)-1}")
    print(f"chain tip ({nodes[-1]['x']}, {nodes[-1]['y']})  exact ({xt}, {yt})")
    print(f"gap {nodes[-1]['x'] - xt} = {float(nodes[-1]['x'] - xt):.6f}")
    print(f"chain length {total} = {float(total):.6f}   exact {2*st}")
    print(f"csv {csv_path}")
    print(f"svg {svg_path}  {W:.0f} x {H:.0f}")


if __name__ == "__main__":
    main()
