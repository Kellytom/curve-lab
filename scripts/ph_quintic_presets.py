"""Save the gallery's named recipes as data, with a sheet of SVGs.

    .venv/bin/python scripts/ph_quintic_presets.py

Writes:

    workbench/ph-quintic-presets.json    one record per named recipe
    workbench/ph-quintic-presets.svg     every recipe drawn and labelled

A preset is the pair of speed recipes (u, v).  The curve is
r(t) = integral of (u + i v)^2 dt, the pitch is the lcm of the integrated
coefficients' denominators, and the bend is the arc length divided by the
straight-line distance between the ends.  Recipes are stored as exact
fraction strings, so a consumer never has to guess what 0.2 means.
"""

from __future__ import annotations

import json
import math
from fractions import Fraction as F
from pathlib import Path

import ph_quintic_lattice as Q

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "workbench" / "ph-quintic-presets.json"
SVG_PATH = ROOT / "workbench" / "ph-quintic-presets.svg"

# id, label, u, v, source, note
CASES = [
    ("the-target", "the target", (F(1, 5), -2, 2), (F(2, 5), F(-3, 2), F(8, 5)),
     "Q8", "the two-lobe S that Q7 morphs toward"),
    ("u0-025", "speedXAtEnds = 0.25", (F(1, 4), -2, 2), (F(2, 5), F(-3, 2), F(8, 5)),
     "Q8", "raising speedXAtEnds straightens the middle"),
    ("v0-05", "speedYAtEnds = 0.5", (F(1, 5), -2, 2), (F(1, 2), F(-3, 2), F(8, 5)),
     "Q8", "raising speedYAtEnds moves the speed path off the origin"),
    ("u0-025-v0-05", "speedXAtEnds = 0.25, speedYAtEnds = 0.5", (F(1, 4), -2, 2), (F(1, 2), F(-3, 2), F(8, 5)),
     "Q8", "both offsets at once: the bend collapses to 1.85"),
    ("v1-14", "speedYLinear = -1.4", (F(1, 5), -2, 2), (F(2, 5), F(-7, 5), F(8, 5)),
     "Q8", "a smaller tilt: bend 2.69"),
    ("v1-16", "speedYLinear = -1.6", (F(1, 5), -2, 2), (F(2, 5), F(-8, 5), F(8, 5)),
     "Q8", "the tilt vanishes and the curve doubles back: bend 9.00"),
    ("target-x10", "the target x10", (2, -20, 20), (4, -15, 16),
     "Q8", "same shape as the target, pitch 15 instead of 1500"),
    ("bend-2-pick", "bend 2.00 | v = 4u - 6", (2, -3, 3), (2, -12, 12),
     "Q9", "the recommended curve: integers, pitch 10, endpoint (15, 4)"),
    ("bend-2-pitch-5", "bend 2.00 | pitch 5", (3, -9, 9), (1, -15, 15),
     "Q8", "the cheapest bend-2 grid"),
    ("round-269", "yours | bend 2.69", (F(1, 2), F(-1, 2), F(1, 2)), (F(7, 10), -4, 4),
     "Q8", "the round decimal S; at x10 its pitch is 2"),
    ("round-269-x10", "yours x10", (5, -5, 5), (7, -40, 40),
     "Q8", "the same shape as yours, pitch 2"),
    ("round-224", "yours | speedYAtEnds = 0.5 | bend 2.24", (F(1, 2), F(-1, 2), F(1, 2)),
     (F(1, 2), -4, 4), "Q8", "the speedYAtEnds = 0.5 variant: same turn, cheaper pitch than 0.7"),
    ("round-224-x2", "speedYAtEnds = 0.5 x2 | bend 2.24", (1, -1, 1), (1, -8, 8),
     "Q8", "the integer form: bend 2.24, pitch 30, endpoint (7, -14)"),
    ("find-318", "the interesting curve", (F(-19, 20), F(-63, 5), 16),
     (F(59, 20), F(-141, 10), 16),
     "Q8", "bend 3.18 at pitch 600; u and v share the leading 16, so x(t) is quartic"),
    ("find-204", "the earlier 2.04 find", (F(74, 125), F(-53, 100), F(53, 100)),
     (F(347, 500), F(-506, 125), F(4099, 1000)),
     "Q7", "b = 6.7, a = -1, morphLambda = 0.51; decimals make the pitch 15 million"),
]


def bend_ratio(u, v, samples=800):
    """Arc length divided by the straight-line distance between the ends."""
    points = Q.uv_samples(u, v, samples)
    arc = sum(math.hypot(b[1] - a[1], b[2] - a[2]) for a, b in zip(points, points[1:]))
    chord = math.hypot(points[-1][1] - points[0][1], points[-1][2] - points[0][2])
    return arc / chord if chord > 1e-9 else float("inf")


def closest_approach(u, v, samples=800):
    """How close the speed path (u, v) comes to the origin."""
    best = float("inf")
    for i in range(samples + 1):
        t = i / samples
        a = u[0] + u[1] * t + u[2] * t * t
        b = v[0] + v[1] * t + v[2] * t * t
        best = min(best, math.hypot(a, b))
    return best


def record(preset):
    """One JSON record, with exact fractions kept as strings."""
    preset_id, label, u, v, source, note = preset
    inflection, pitch, end, _swing = Q.s_info(u, v)
    return {
        "id": preset_id,
        "label": label,
        "source": source,
        "note": note,
        "u": [str(c) for c in u],
        "v": [str(c) for c in v],
        "bend": round(bend_ratio(u, v), 2),
        "pitch": pitch,
        "inflection": round(inflection, 2),
        "closest_approach": round(closest_approach(u, v), 2),
        "endpoint": [str(end[0]), str(end[1])],
        "endpoint_at_pitch": [str(end[0] * pitch), str(end[1] * pitch)],
    }


def build_records():
    return [record(preset) for preset in CASES]


def build_document(records):
    return {
        "title": "PH quintic preset recipes",
        "generator": "scripts/ph_quintic_presets.py",
        "convention": (
            "u and v are exact fractions as strings; the curve is "
            "r(t) = integral of (u + i v)^2 dt; pitch is the lcm of the "
            "integrated coefficients' denominators; bend is arc / chord"
        ),
        "how_to_find": [
            "never let v be a multiple of u: arg(w) is then constant and the curve is straight",
            "choose the heading turn first: 167 deg gives bend 2.00, 215 deg gives 5.58, past 230 deg it loops",
            "use the even pair u0 - u2 t + u2 t^2, v0 - v2 t + v2 t^2 for an inflection at t = 1/2",
            "move the speed path nearer the origin to add bend; keep the closest approach above zero",
            "clear the denominators last: the pitch is the lcm, and scaling the recipe by n divides it by n^2",
        ],
        "presets": records,
    }


def panel_svg(u, v, label, bend, pitch, width=290, height=250):
    points = Q.uv_samples(u, v, 400)
    xs = [p[1] for p in points]
    ys = [p[2] for p in points]
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    top, side, bottom = 44, 18, 26
    scale = min((width - 2 * side) / max(1e-9, x1 - x0),
                (height - top - bottom) / max(1e-9, y1 - y0))
    offset_x = (width - (x1 - x0) * scale) / 2
    offset_y = top + (height - top - bottom - (y1 - y0) * scale) / 2
    fx = lambda value: offset_x + (value - x0) * scale
    fy = lambda value: offset_y + (y1 - value) * scale
    path = "M" + " L".join(f"{fx(p[1]):.1f},{fy(p[2]):.1f}" for p in points)
    return (
        f'<g><rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" '
        f'fill="#fbf7ec" stroke="#d8ccae"/>'
        f'<text x="{side}" y="20" font-size="12" font-weight="600" fill="#2e2413">{label}</text>'
        f'<text x="{side}" y="34" font-size="10" fill="#7b6c4e">bend {bend:.2f} | pitch {pitch:,}</text>'
        f'<path d="{path}" fill="none" stroke="#2e2413" stroke-width="2"/>'
        f"</g>"
    )


def build_svg(records):
    columns, panel_width, panel_height, gap = 4, 290, 250, 14
    header, footer = 74, 40
    rows = (len(records) + columns - 1) // columns
    width = columns * panel_width + (columns + 1) * gap
    height = header + rows * (panel_height + gap) + footer
    panels = []
    for index, item in enumerate(records):
        row, column = divmod(index, columns)
        x = gap + column * (panel_width + gap)
        y = header + row * (panel_height + gap)
        u = tuple(F(c) for c in item["u"])
        v = tuple(F(c) for c in item["v"])
        panels.append(
            f'<g transform="translate({x},{y})">'
            + panel_svg(u, v, item["label"], item["bend"], item["pitch"])
            + "</g>"
        )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img" '
        f'aria-label="PH quintic preset recipes, one panel each">'
        f'<rect width="{width}" height="{height}" fill="#f3eddf"/>'
        f'<text x="{gap}" y="30" font-size="18" font-weight="600" fill="#2e2413">'
        f"PH quintic preset recipes</text>"
        f'<text x="{gap}" y="50" font-size="12" fill="#7b6c4e">'
        f"curve: r(t) = integral of (u + i v)^2 dt | bend: arc / chord | pitch: lcm of the "
        f"integrated coefficients' denominators</text>"
        f'<text x="{gap}" y="64" font-size="11" fill="#8a7a58">'
        f"exact recipes and their metrics: workbench/ph-quintic-presets.json | "
        f"generated by scripts/ph_quintic_presets.py</text>"
        + "".join(panels)
        + f'<text x="{gap}" y="{height - 14}" font-size="11" fill="#8a7a58">'
        f"{len(records)} presets | integer recipes are written without a denominator; "
        f"decimals cost pitch</text>"
        f"</svg>"
    )


def main():
    records = build_records()
    JSON_PATH.write_text(json.dumps(build_document(records), indent=2) + "\n")
    SVG_PATH.write_text(build_svg(records))
    print(f"{JSON_PATH.relative_to(ROOT)}  {len(records)} presets")
    print(f"{SVG_PATH.relative_to(ROOT)}  {SVG_PATH.stat().st_size} bytes")


if __name__ == "__main__":
    main()
