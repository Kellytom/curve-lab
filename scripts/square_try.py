"""Try square and frame assemblies of the generated curves.

    .venv/bin/python scripts/square_try.py [outdir]

Writes a page of panels to `outdir` (default: $TMPDIR/curve-lab-square) and
screenshots it. The rule under test is `curve_lab/square_assembly.py`: the leg
bisects the corner. A square's corner is 90°, so a 45° leg gives a smooth join
for an arch and a 90° miter for an S.

The frame is the same rule with three chords on each side; the central cross
and the frame are built separately and only meet in the overlay panel.
"""

from __future__ import annotations

import math
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab import square_assembly as S  # noqa: E402
from curve_lab.pyth_cubic import case, case_c  # noqa: E402

INK, BLUE, RED, GOLD, MUTED = "#2e2413", "#1f5fa8", "#a23b2a", "#b58312", "#7b6c4e"
EDGE_COLOURS = [INK, BLUE, RED, GOLD]
SIDE = 300.0


def _arch():
    row = case_c(3, 4, 5)
    return [row["p0"], row["p1"], row["p2"], row["p3"]]


def _s():
    row = case(3, 4, 5)
    return [row["p0"], row["p1"], row["p2"], row["p3"]]


def _sample(points, n=220):
    return [S.cubic_at(points, i / n) for i in range(n + 1)]


def _layer(curves, side, colours=None, width=2.0, dash=None):
    return {"curves": curves, "side": side,
            "colours": colours or EDGE_COLOURS, "width": width, "dash": dash}


def _panel(layers, title, w=380, h=400):
    drawn = [[_sample(c["points"]) for c in layer["curves"]] for layer in layers]
    corners = []
    for layer in layers:
        side = layer["side"]
        corners.append([(0, 0), (side, 0), (side, side), (0, side)])
    all_points = [p for layer in drawn for curve in layer for p in curve]
    all_points += [p for square in corners for p in square]
    x0 = min(p[0] for p in all_points)
    x1 = max(p[0] for p in all_points)
    y0 = min(p[1] for p in all_points)
    y1 = max(p[1] for p in all_points)
    pad = 24
    k = min((w - 2 * pad) / (x1 - x0), (h - 90 - 2 * pad) / (y1 - y0))

    def put(p):
        return (pad + (p[0] - x0) * k, 70 + (h - 90) - pad - (p[1] - y0) * k)

    body = [f'<rect width="{w}" height="{h}" fill="#fffdf7" stroke="#d8ccae"/>']
    body.append(f'<text x="14" y="24" font-size="14" fill="{INK}">{title}</text>')
    for square in corners:
        points = " ".join(f"{put(p)[0]:.1f},{put(p)[1]:.1f}"
                          for p in square + [square[0]])
        body.append(f'<polygon points="{points}" fill="none" stroke="#c9bda0" '
                    f'stroke-width="1" stroke-dasharray="5 4"/>')
    for layer, curves in zip(layers, drawn):
        for index, points in enumerate(curves):
            colour = layer["colours"][index % len(layer["colours"])]
            text = " ".join(f"{put(p)[0]:.1f},{put(p)[1]:.1f}" for p in points)
            dash = f' stroke-dasharray="{layer["dash"]}"' if layer["dash"] else ""
            body.append(f'<polyline points="{text}" fill="none" stroke="{colour}" '
                        f'stroke-width="{layer["width"]}" stroke-linecap="round" '
                        f'stroke-linejoin="round"{dash}/>')
    return (f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">'
            + "".join(body) + "</svg>")


def _kink_summary(kinks):
    values = sorted({round(angle) for _name, angle in kinks})
    return " / ".join(f"{value}°" for value in values)


def main() -> int:
    outdir = Path(sys.argv[1]) if len(sys.argv) > 1 else \
        Path(os.environ.get("TMPDIR", "/tmp")) / "curve-lab-square"
    outdir.mkdir(parents=True, exist_ok=True)
    panels = []

    s45 = S.assemble(_s(), SIDE, 45.0)
    c45 = S.assemble(_arch(), SIDE, 45.0)
    c_raw = S.assemble(_arch(), SIDE)
    s_raw = S.assemble(_s(), SIDE)

    frame = S.frame(_arch(), 3, 45.0, alternate=False, side=3 * SIDE)
    frame_alt = S.frame(_arch(), 3, 45.0, alternate=True, side=3 * SIDE)

    # the cross, centred in the frame, drawn separately and then overlaid
    shift = (frame["side"] - SIDE) / 2.0
    cross = [{"name": c["name"], "points": [(x + shift, y + shift)
                                            for x, y in c["points"]],
              "start_leg": c["start_leg"], "end_leg": c["end_leg"]}
             for c in c45]

    panels.append((_panel([_layer(s_raw, SIDE)], "S 3-4-5, as drawn"),
                   f"S as drawn · leg {s_raw[0]['start_leg']:.1f}° · "
                   f"corners {_kink_summary(S.corner_kinks(s_raw))}"))
    panels.append((_panel([_layer(s45, SIDE)], "S 3-4-5, leg 45°"),
                   f"S leg 45° · corners {_kink_summary(S.corner_kinks(s45))} "
                   f"(right angles)"))
    panels.append((_panel([_layer(c45, SIDE)], "C 3-4-5, leg 45°"),
                   f"arch leg 45° · corners {_kink_summary(S.corner_kinks(c45))} "
                   f"(continuous)"))
    panels.append((_panel([_layer(c_raw, SIDE)], "C 3-4-5, as drawn"),
                   f"arch as drawn · leg {c_raw[0]['start_leg']:.1f}° · "
                   f"corners {_kink_summary(S.corner_kinks(c_raw))}"))
    panels.append((_panel([_layer(frame["curves"], frame["side"])],
                          "Frame · 3 chords a side"),
                   f"side {frame['side']:.0f} = 3 × {SIDE:.0f} · joins "
                   f"{_kink_summary(frame['kinks'])}"))
    panels.append((_panel([_layer(frame_alt["curves"], frame_alt["side"])],
                          "Frame · every other copy flipped"),
                   f"joins {_kink_summary(frame_alt['kinks'])}"))
    panels.append((_panel([_layer(frame["curves"], frame["side"],
                                  colours=["#b9ab8c"], width=2.0),
                           _layer(cross, SIDE, colours=[INK], width=2.0)],
                          "Frame and cross, overlaid"),
                   "frame grey · cross ink · built separately"))

    for _svg, caption in panels:
        print(caption)
    page = ('<!doctype html><html><head><meta charset="utf-8"><title>square try</title>'
            '<style>body{margin:0;background:#f6f1e4;font:14px Georgia,serif;color:#2e2413}'
            'main{max-width:1200px;margin:0 auto;padding:26px}'
            '.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}'
            'figure{margin:0;background:#fffdf7;border:1px solid #d8ccae}'
            'figcaption{padding:6px 10px;font:11px ui-monospace,Menlo,monospace;color:#555}'
            'svg{display:block;width:100%;height:auto}</style></head><body><main>'
            '<h1>Square and frame from one curve</h1>'
            '<p>the leg bisects the corner · south ink, east blue, north red, west gold</p>'
            '<div class="grid">'
            + "".join(f'<figure>{svg}<figcaption>{caption}</figcaption></figure>'
                      for svg, caption in panels)
            + '</div></main></body></html>')
    index = outdir / "index.html"
    index.write_text(page, encoding="utf-8")
    png = outdir / "squares.png"
    result = subprocess.run(["node", str(ROOT / "scripts" / "shot.mjs"),
                             f"file://{index}", str(png), "1200", "900", "full"],
                            cwd=ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout[-800:])
        print(result.stderr[-800:])
    print(index)
    print(png)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
