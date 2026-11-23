#!/usr/bin/env python3
"""What the traced spans are, in numbers — and the snap toward the grid.

    .venv/bin/python deep2/measure_spans.py deep2/spans/redeemer.json

For a spans file from trace.py, prints and writes:
  - the span count;
  - the join continuity: at each join the angle between the incoming and
    outgoing tangents — a real corner in the reference shows as a deliberate
    kink, a smooth stretch as ~0°;
  - the snap cost: the largest move when every point is quantised to a 1/1000
    grid — how far the traced drawing is from an exact grid;
  - a snapped SVG, drawn from the quantised spans.
"""

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def angle_between(a, b):
    ax, ay = a
    bx, by = b
    na, nb = math.hypot(ax, ay), math.hypot(bx, by)
    if na == 0 or nb == 0:
        return 90.0
    c = max(-1.0, min(1.0, (ax * bx + ay * by) / (na * nb)))
    return math.degrees(math.acos(c))


def main(argv):
    path = Path(argv[0]) if argv else HERE / "spans" / "redeemer.json"
    data = json.loads(path.read_text())
    spans = data["curves"]
    curves = spans  # each span is one curve here
    kinks = []
    for i in range(len(spans) - 1):
        end = spans[i]["p3"]
        nxt = spans[i + 1]
        if abs(end[0] - nxt["p0"][0]) > 1e-6 or abs(end[1] - nxt["p0"][1]) > 1e-6:
            kinks.append((i, None))  # a break between subpaths
            continue
        incoming = (end[0] - spans[i]["c2"][0], end[1] - spans[i]["c2"][1])
        outgoing = (nxt["c1"][0] - end[0], nxt["c1"][1] - end[1])
        kinks.append((i, angle_between(incoming, outgoing)))
    smooth = [k for _, k in kinks if k is not None]
    corners = [k for k in smooth if k > 35]
    steps = [k for k in smooth if 5 < k <= 35]
    print(f"{path.name}: {len(spans)} spans")
    if smooth:
        print(f"  joins: {len(smooth)} seamless; smooth kinks ≤5°: {sum(1 for k in smooth if k <= 5)}; "
              f"small kinks 5–35°: {len(steps)}; corners >35°: {len(corners)}")
        print(f"  worst smooth kink: {max(smooth):.2f}°")

    # snap every coordinate to a 1/1000 grid and measure the largest move
    def snap(v):
        return round(v * 1000) / 1000

    biggest = 0.0
    snapped = []
    for s in spans:
        out = {}
        for key in ("p0", "c1", "c2", "p3"):
            q = [snap(s[key][0]), snap(s[key][1])]
            biggest = max(biggest, abs(q[0] - s[key][0]), abs(q[1] - s[key][1]))
            out[key] = q
        snapped.append(out)
    print(f"  snap to 1/1000: largest move {biggest:.5f} of the figure's height")

    def f(v):
        return f"{v:.3f}".rstrip("0").rstrip(".")

    parts = [f"M {f(snapped[0]['p0'][0])} {f(snapped[0]['p0'][1])}"]
    for s in snapped:
        parts.append(f"C {f(s['c1'][0])} {f(s['c1'][1])} {f(s['c2'][0])} {f(s['c2'][1])} "
                     f"{f(s['p3'][0])} {f(s['p3'][1])}")
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -0.05 1 1.1" '
           'width="600" height="660"><rect x="0" y="-0.05" width="1" height="1.1" fill="#fffef9"/>'
           f'<path d="{" ".join(parts)}" fill="none" stroke="#3b2d1c" stroke-width="0.004"/></svg>')
    out_svg = HERE / "out" / f"{path.stem}-snapped.svg"
    out_svg.write_text(svg)
    print(f"  snapped drawing: out/{out_svg.name}")


if __name__ == "__main__":
    main(sys.argv[1:])
