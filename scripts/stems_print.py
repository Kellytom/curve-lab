"""Three generator stems as geometry for the 8.5 x 11 print sheet.

    .venv/bin/python scripts/stems_print.py
    open workbench/stems-abc.svg

The stems are the generator presets, sampled from their exact rational Bézier
control data:

    a  sextic   n=6  h=(1,2)  u=(-1,1,0)  v=(2,-1,0)  step 1/2
    b  quintic  n=5  h=(1)    u=(-2,-1,1) v=(-1,-1,2) step 1/2
    c  cubic    n=3  h=(1)    u=(2,-2)    v=(1,-2)    step 1/4

a is rotated clockwise until its first tangent is vertical; b and c are rotated
30 and 35 degrees counter-clockwise.  Each is fitted to its own tight square
(side = the larger extent), and the three squares sit side by side with their
bottoms aligned.  Model coordinates are +y up; the page is +y down, so the flip
happens once in the stem mapping: page_y = cell_bottom - (model_y - y0).

This script now writes only workbench/stems-abc.json.  The SVG and the print
wrapper are rendered from that JSON by scripts/stems_print.mjs, so the Python
side is geometry only: inputs, rotated boxes, page placement and 2,001 page-
coordinate samples (667 per stem).
"""

from __future__ import annotations

import json
import math
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generators as G  # noqa: E402

INK, MUTED, GUIDE = "#2e2413", "#7b6c4e", "#ece4cf"
DOT = "#b23a2b"
PAGE_W, PAGE_H = 850.0, 1100.0      # 100 units per inch
MARGIN = 50.0
DRAW_W, DRAW_H = PAGE_W - 2 * MARGIN, PAGE_H - 2 * MARGIN
CELL, PAD, GAP = 50.0, 2.0, 10.0
CELL_TOP = 1000.0
CELL_BOTTOM = CELL_TOP + CELL
X0 = MARGIN + (DRAW_W - (3 * CELL + 2 * GAP)) / 2
N = 666                              # 667 points per stem, 2,001 total

STEMS = [
    dict(label="a", key="sextic",
         spec=dict(key="sextic", n=6, h=(1, 2), u=(-1, 1, 0),
                   v=(2, -1, 0), m=2),
         rotation="start-vertical"),
    dict(label="b", key="quintic",
         spec=dict(key="quintic", n=5, h=(1,), u=(-2, -1, 1),
                   v=(-1, -1, 2), m=2),
         rotation=30.0),
    dict(label="c", key="cubic",
         spec=dict(key="cubic", n=3, h=(1,), u=(2, -2),
                   v=(1, -2), m=4),
         rotation=35.0, mirror=True),
]


def rotate(points, angle):
    c, s = math.cos(angle), math.sin(angle)
    return [(x * c - y * s, x * s + y * c) for x, y in points]


def extent(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)


def stem_points(spec, n=N):
    item = G.build_preset(spec)
    scale = item["scale"]
    pts = [item["curve"].bezier(F(i, n)) for i in range(n + 1)]
    return [(float(x) * scale, float(y) * scale) for x, y in pts], item


def main():
    cells = []
    for i, stem in enumerate(STEMS):
        pts, item = stem_points(stem["spec"])
        p0, p2 = pts[0], pts[2]
        page_start = math.degrees(math.atan2(-(p2[1] - p0[1]),
                                             p2[0] - p0[0]))
        if stem["rotation"] == "start-vertical":
            # a clockwise turn that puts the first tangent on the page
            # vertical; pick the candidate nearest the requested 120 degrees
            cands = [(90 - page_start) % 360, (270 - page_start) % 360]
            cw = min(cands, key=lambda d: abs(d - 120))
            model_rot = -cw
            direction = "cw"
            rotate_deg = cw
        else:
            model_rot = stem["rotation"]
            direction = "ccw"
            rotate_deg = stem["rotation"]
        rot = rotate(pts, math.radians(model_rot))
        x0, y0, x1, y1 = extent(rot)
        dx, dy = x1 - x0, y1 - y0
        side = max(dx, dy)
        scale = (CELL - 2 * PAD) / side
        cell_x = X0 + i * (CELL + GAP)
        cx = (x0 + x1) / 2
        page = []
        sign = -1 if stem.get("mirror") else 1
        for x, y in rot:
            px = cell_x + CELL / 2 + sign * (x - cx) * scale
            py = CELL_BOTTOM - PAD - (y - y0) * scale
            page.append((px, py))
        start_page = page[0]
        end_page = page[-1]
        lean = "right" if start_page[0] > end_page[0] else "left"
        cells.append(dict(stem=stem, pts=rot, page=page, item=item,
                          x0=x0, y0=y0, x1=x1, y1=y1, dx=dx, dy=dy,
                          side=side, scale=scale, cell_x=cell_x,
                          rotate_deg=rotate_deg, direction=direction,
                          lean=lean, mirror=bool(stem.get("mirror")),
                          start_page=start_page, end_page=end_page))


    data = {
        "page": {"width_in": 8.5, "height_in": 11.0, "margin_in": 0.5,
                 "drawing_in": [7.5, 10.0], "units_per_in": 100},
        "stems": [],
        "note": ("Three generator presets, not clothoid chains: the PH "
                 "generator data is the constant set.  Page samples are in "
                 "inches, +y down, at 667 per stem."),
    }
    for c in cells:
        st = c["stem"]
        data["stems"].append({
            "label": st["label"],
            "preset": st["key"],
            "inputs": {"n": st["spec"]["n"],
                       "h": list(st["spec"]["h"]),
                       "u": list(st["spec"]["u"]),
                       "v": list(st["spec"]["v"]),
                       "step": f"1/{st['spec']['m']}",
                       "control_scale": c["item"]["scale"]},
            "rotation": {"direction": c["direction"],
                         "deg": round(c["rotate_deg"], 4)},
            "mirror": c["mirror"],
            "lean": c["lean"],
            "natural_box": [round(v, 3) for v in
                            (c["x0"], c["y0"], c["x1"], c["y1"])],
            "cell": {"x_in": round(c["cell_x"] / 100, 4),
                     "bottom_in": round(CELL_BOTTOM / 100, 4),
                     "side_in": round(CELL / 100, 4)},
            "scale_page_per_model": round(c["scale"], 6),
            "start_page_in": [round(v / 100, 5) for v in c["start_page"]],
            "end_page_in": [round(v / 100, 5) for v in c["end_page"]],
            "points_page_in": [[round(x / 100, 5), round(y / 100, 5)]
                               for x, y in c["page"]],
        })
    json_path = ROOT / "workbench" / "stems-abc.json"
    json_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(json_path)
    for c in cells:
        print(f"  {c['stem']['label']}  {c['direction']} "
              f"{c['rotate_deg']:.2f} deg  box {c['dx']:.1f} x {c['dy']:.1f}"
              f"  cell scale {c['scale']:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
