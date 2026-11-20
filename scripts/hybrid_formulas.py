#!/usr/bin/env python3
"""The hybrid polynomials of a rational circle, graphed.

    .venv/bin/python scripts/hybrid_formulas.py --write

No cos, no sin. The parameter is a rational number

    t = tan(θ/2)
    C(t) = (1 − t²)/(1 + t²)      the rational cosine
    S(t) = 2t/(1 + t²)            the rational sine
    C(t)² + S(t)² = 1             exactly, for every rational t

and the curve is

    x(t) = C(t)⁵,  y(t) = S(t)³

Every station is an exact rational pair. The drawing between stations is a line, and
the figure says so. The point (−1, 0) is not reached by any finite t; it is the one
point the parametrisation misses, and the caption says that too.

Spec: none yet; this is the probe for the sandbox-algo page.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "workbench" / "hybrid-formulas.json"
OUT_SVG = ROOT / "workbench" / "hybrid-formulas.svg"

SPAN = 12          # t from −SPAN to +SPAN
PER_UNIT = 60      # stations per unit of t
COLOURS = ["#2f6fa8", "#a8341f", "#6f4a2a", "#c9761f", "#4a7a4a", "#7a6a55"]


def station(t):
    c = (1 - t * t) / (1 + t * t)
    s = (2 * t) / (1 + t * t)
    x = c ** 5
    y = s ** 3
    x2, y2 = x * x, y * y
    x3 = x2 * x
    base = x2 + y2
    mid_quad = 2 * x * y
    mid_cubic = 3 * (x2 * y + x * y2)
    mid_quint = 10 * (x3 * y2 + x2 * y * y)
    mid_quint_all = 5 * (x2 * x2 * y + x * y2 * y2) + mid_quint
    return c, s, x, y, {
        "quadratic": base + mid_quad,
        "cubic": base + mid_cubic,
        "quintic": base + mid_quint,
        "quintic, all four terms": base + mid_quint_all,
        "cubic + quintic": base + mid_cubic + mid_quint,
        "all five": base + mid_quad + mid_cubic + mid_quint,
    }


def svg_panel(x, y, width, height, title, subtitle, series, *, axes=True,
              xlabel="", ylabel="", legend=(), marks=()):
    pad = {"left": 56, "right": 18, "top": 66, "bottom": 156}
    plot = (x + pad["left"], y + pad["top"], x + width - pad["right"], y + height - pad["bottom"])
    xs = [p[0] for s in series for p in s["points"]] + [0]
    ys = [p[1] for s in series for p in s["points"]] + [0]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    span = max(x1 - x0, y1 - y0) * 0.06 or 1
    x0, x1, y0, y1 = x0 - span, x1 + span, y0 - span, y1 + span
    k = min((plot[2] - plot[0]) / (x1 - x0), (plot[3] - plot[1]) / (y1 - y0))
    ox = plot[0] + ((plot[2] - plot[0]) - (x1 - x0) * k) / 2 - x0 * k
    oy = plot[1] + ((plot[3] - plot[1]) - (y1 - y0) * k) / 2 + y1 * k

    def px(p):
        return ox + p[0] * k, oy - p[1] * k

    parts = [f'<text x="{x}" y="{y + 28}" font-size="16" font-weight="600" fill="#3b2d1c">{title}</text>',
             f'<text x="{x}" y="{y + 48}" font-size="15" fill="#5a4a36">{subtitle}</text>',
             f'<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="#fffef9" stroke="#d9cdb8"/>']
    if axes:
        a, b = px((x0, 0)), px((x1, 0))
        c, d = px((0, y0)), px((0, y1))
        parts.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#b9a98a"/>')
        parts.append(f'<line x1="{c[0]:.1f}" y1="{c[1]:.1f}" x2="{d[0]:.1f}" y2="{d[1]:.1f}" stroke="#b9a98a"/>')
        parts.append(f'<text x="{b[0] - 8:.1f}" y="{a[1] + 18:.1f}" font-size="15" fill="#3b2d1c">{xlabel}</text>')
        parts.append(f'<text x="{c[0] + 8:.1f}" y="{d[1] + 16:.1f}" font-size="15" fill="#3b2d1c">{ylabel}</text>')
    for item in series:
        d = "M" + " L".join(f"{px(p)[0]:.2f},{px(p)[1]:.2f}" for p in item["points"])
        dash = f' stroke-dasharray="{item["dash"]}"' if item.get("dash") else ""
        parts.append(f'<path d="{d}" fill="none" stroke="{item["colour"]}" '
                     f'stroke-width="{item.get("width", 1.6)}"{dash}/>')
    for p, colour in marks:
        q = px(p)
        parts.append(f'<circle cx="{q[0]:.1f}" cy="{q[1]:.1f}" r="3.4" fill="{colour}"/>')
    for index, (label, colour) in enumerate(legend):
        ly = y + height - 30 - (len(legend) - 1 - index) * 20
        parts.append(f'<line x1="{x + 18}" y1="{ly}" x2="{x + 44}" y2="{ly}" stroke="{colour}" stroke-width="2.4"/>')
        parts.append(f'<text x="{x + 52}" y="{ly + 5}" font-size="15" fill="#3b2d1c">{label}</text>')
    return "".join(parts)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    steps = SPAN * PER_UNIT
    curve, series_points, ranges = [], {}, {}
    for j in range(-steps, steps + 1):
        t = Fraction(j, PER_UNIT)
        _, _, x, y, values = station(t)
        curve.append((float(x), float(y)))
        u = float(t) / (1 + abs(float(t)))     # the station's place round the circle, rational, no trig
        for name, value in values.items():
            series_points.setdefault(name, []).append((u, float(value)))
            lo, hi = ranges.get(name, (float(value), float(value)))
            ranges[name] = (min(lo, float(value)), max(hi, float(value)))
    labels = list(ranges)

    # one exact station, printed so the claim is checkable
    c, s, x1, y1, _ = station(Fraction(1, 2))
    print(f"t = 1/2:  C = {c},  S = {s}   x = {x1},  y = {y1}")

    panel_curve = svg_panel(
        20, 20, 470, 540,
        "Fig. H1 · x = C(t)⁵, y = S(t)³",
        "C = (1 − t²)/(1 + t²), S = 2t/(1 + t²); t from −12 to 12 in steps of 1/60.",
        [{"points": curve, "colour": "#2f6fa8", "width": 2.0}],
        xlabel="x", ylabel="y", marks=[(curve[steps], "#c9761f")],
        legend=[("x = C⁵, y = S³ — exact at every station", "#2f6fa8"),
                ("t = 0 → (1, 0)", "#c9761f")],
    )
    panel_values = svg_panel(
        510, 20, 470, 540,
        "Fig. H2 · the five middle-term combinations",
        "P against u = t/(1+|t|), the station's place round the circle; no trig in the axis.",
        [{"points": series_points[name], "colour": COLOURS[i],
          **({"dash": "7 5", "width": 1.3} if name == "quintic, all four terms" else {})}
         for i, name in enumerate(labels)],
        xlabel="u", ylabel="P",
        legend=[(f"{name}  ({ranges[name][0]:.2f} … {ranges[name][1]:.2f})", COLOURS[i])
                for i, name in enumerate(labels)],
    )
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 580" width="1000" height="580" '
           f'role="img" aria-label="Fig. H1 and H2">'
           f'<rect width="1000" height="580" fill="#fffdf7"/>{panel_curve}{panel_values}'
           f'<text x="20" y="572" font-size="15" fill="#5a4a36">'
           f'the join between stations is a straight line; (−1, 0) is the one point no finite t reaches.</text></svg>')

    print("P ranges over t in [−12, 12]:")
    for name in labels:
        print(f"  {name:26} {ranges[name][0]:+.4f} … {ranges[name][1]:+.4f}")
    if args.write:
        OUT_SVG.write_text(svg)
        OUT_JSON.write_text(json.dumps({
            "format": "curve-lab.hybrid-formulas/1",
            "parameter": "t = tan(theta/2)",
            "x": "C(t)^5", "y": "S(t)^3",
            "C": "(1-t^2)/(1+t^2)", "S": "2t/(1+t^2)",
            "span": SPAN, "perUnit": PER_UNIT,
            "exactStation": {"t": "1/2", "C": "3/5", "S": "4/5",
                             "x": str(x1), "y": str(y1)},
            "ranges": {name: list(span) for name, span in ranges.items()},
            "missingPoint": [-1, 0],
        }, indent=1) + "\n")
        print(f"wrote {OUT_SVG.relative_to(ROOT)} and {OUT_JSON.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
