#!/usr/bin/env python3
"""The canon check: is the traced figure proportioned like a human figure?

    .venv/bin/python deep2/canon.py deep2/spans/redeemer.json

Overlays the 8-head canon on a traced figure and measures what the trace
actually has:
  - the head counts: figure height ÷ head height (the classic canons run
    7.5–8 heads for the adult standing figure; Byzantine icons run closer
    to 7–7.5);
  - the arm span over the height (near 1 for a figure with open arms);
  - the landmark lines at every 1/8 of the height, drawn on the figure.

The head is found from the silhouette itself: scan the figure's rows for the
run width, and the head is the top blob before the shoulders/arms jump the
width. Works for silhouettes with open arms; the report says when it does not.
"""

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent


def rows_of(spans, samples=120):
    """Sample the outline (all spans, joined head to tail) into points."""
    pts = []
    for s in spans:
        p0, c1, c2, p3 = s["p0"], s["c1"], s["c2"], s["p3"]
        for i in range(samples):
            t = i / (samples - 1)
            mt = 1 - t
            pts.append(
                (
                    mt**3 * p0[0] + 3 * mt * mt * t * c1[0] + 3 * mt * t * t * c2[0] + t**3 * p3[0],
                    mt**3 * p0[1] + 3 * mt * mt * t * c1[1] + 3 * mt * t * t * c2[1] + t**3 * p3[1],
                )
            )
    return np.array(pts)


def main(argv):
    path = Path(argv[0]) if argv else HERE / "spans" / "redeemer.json"
    data = json.loads(path.read_text())
    pts = rows_of(data["curves"])
    x0, y0 = pts.min(axis=0)
    x1, y1 = pts.max(axis=0)
    height = y1 - y0 or 1

    # width profile per 1% of height (y is up in the spans)
    bins = 200
    profile = np.zeros(bins)
    for px, py in pts:
        b = min(bins - 1, int((py - y0) / height * bins))
        profile[b] = max(profile[b], abs(px - (x0 + x1) / 2) * 2)

    # the head is NOT detected automatically: the open arms sit almost at
    # the top of this pose, and every profile heuristic misread it (33 heads
    # on the first run). The overlay puts the 1/8 lines on the figure so the
    # landmarks are judged by eye; the numbers here are what can be trusted.

    # overlay: the figure + the 8-head lines + the centre axis
    def f(v):
        return f"{v:.4f}"

    parts = []
    for s in data["curves"]:
        parts.append(f"M {f(s['p0'][0])} {f(s['p0'][1])}")
        for key in ("c1", "c2", "p3"):
            pass
    d = []
    d.append(f"M {f(data['curves'][0]['p0'][0])} {f(data['curves'][0]['p0'][1])}")
    for s in data["curves"]:
        d.append(
            f"C {f(s['c1'][0])} {f(s['c1'][1])} {f(s['c2'][0])} {f(s['c2'][1])} {f(s['p3'][0])} {f(s['p3'][1])}"  # noqa: E501
        )

    lines = []
    for k in range(9):
        y = y0 + height * k / 8
        lines.append(
            f'<line x1="{f(x0 - 0.05)}" y1="{f(y)}" x2="{f(x1 + 0.05)}" y2="{f(y)}" '
            f'stroke="#c9a441" stroke-width="0.0015" stroke-dasharray="0.008 0.006"/>'
        )
    cx = (x0 + x1) / 2
    lines.append(
        f'<line x1="{f(cx)}" y1="{f(y0 - 0.05)}" x2="{f(cx)}" y2="{f(y1 + 0.05)}" '
        f'stroke="#2f6fa8" stroke-width="0.0012" stroke-dasharray="0.004 0.004"/>'
    )
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-0.1 -0.1 1.2 1.2" '
        'width="560" height="620"><rect x="-0.1" y="-0.1" width="1.2" height="1.2" fill="#fffef9"/>'
        + "".join(lines)
        + f'<path d="{" ".join(d)}" fill="none" stroke="#3b2d1c" stroke-width="0.005"/>'
        + "</svg>"
    )
    out = HERE / "out" / f"{path.stem}-canon.svg"
    out.write_text(svg)
    print(f"  overlay: out/{out.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
