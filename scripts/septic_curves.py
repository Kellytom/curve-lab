"""The named curves found in the septic sandbox, with their exact metrics.

    .venv/bin/python scripts/septic_curves.py

Writes workbench/septic-curves.json, which the sandbox injects as the seed
for its saved-curves row.  A curve is the eight speed numbers; everything
else - bend, pitch, inflection, closest, degree - is computed here.
"""

from __future__ import annotations

import json
from pathlib import Path

import ph_quintic_metrics as M

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "workbench" / "septic-curves.json"

# name, speed x (four), speed y (four)
#
# The first four were shaped by hand in panel B.  The rest are promoted from
# gallery D (`workbench/septic-samples.json`), one per measured signature, so
# the gallery has a stable name to click instead of eight numbers to retype:
#
#   small-loop     the smallest speeds in the gallery that close a loop
#   tight-loop     the tightest self-approach in the gallery (closest 0.197)
#   shallow-turn   the smallest bend in the gallery (1.498), a 180 degree turn
#   narrow-arch    heading +90 to -90 with x returning to its start: an arch
#   vertical-s     heading -90 to +90: the S read as a vertical stroke
#   tight-hook     the largest bend in the gallery (2.575)
#   straight-start x'(t) = (1, 0, 0, 0), so x is exactly t, then y dives
#   long-sweep     the widest reach in the gallery (4.35 by 5.00)
#
# Every promoted curve keeps its gallery speed numbers unchanged; the test
# `test_the_promoted_curves_keep_their_gallery_numbers` holds that.
CURVES = [
    ("half-heart", (1.95, 4.85, 6.45, -16), (2.0, -4.95, 5.05, 5.25)),
    ("flourish-a", (1.95, 4.4, 6.45, -16), (2.0, -8.0, 4.95, 5.2)),
    ("flourish-b", (2.05, 4.4, 5.75, -16), (1.75, -7.85, 5.15, 8.5)),
    ("lazy-s-2", (2, -3, 3, 0.5), (2, -12, 12, -0.5)),
    ("small-loop", (1, -1, 0, 0), (0, -1, 1, 1)),
    ("tight-loop", (1, -1, -1, 1), (0, -1, 1, 1)),
    ("shallow-turn", (1, 0, -1, 0), (0, -1, 1, 1)),
    ("narrow-arch", (1, -2, 2, 0), (1, -1, 2, -3)),
    ("vertical-s", (1, 0, 2, 0), (-1, -1, 3, 2)),
    ("tight-hook", (1, -2, 2, 1), (1, 0, -2, 0)),
    ("straight-start", (1, 0, 0, 0), (0, 1, -2, -2)),
    ("long-sweep", (3, -1, 1, -1), (2, 0, -3, -3)),
    # the classic: all eight speeds integers, and the position controls are
    # integers at 105 (170.333 -> 17885, 0.571 -> 60). bend 3.011, pitch 105.
    ("integer-105", (2, -5, 6, 0), (4, -20, 20, -2)),
    # its sibling: integer speeds, integer controls at 70, bend 1.290 (the
    # shallowest S in the set). 1.143 -> 80 at 70.
    ("integer-70", (2, -3, 3, 3), (2, -12, 12, 1)),
    # the double loop: two self-crossings, measured by segment test at 1200
    # samples, at (-0.07, 0.21) and (-2.71, -1.68). bend 3.446, pitch 210.
    ("double-loop", (2, -5, 6, 1), (3, -26, 23, 5)),
]


def record(name, speed_x, speed_y):
    metrics = M.metrics(speed_x, speed_y)
    x, y = M.curve_polynomials(speed_x, speed_y)
    degree_x = max((k for k, c in enumerate(x) if c), default=0)
    degree_y = max((k for k, c in enumerate(y) if c), default=0)
    return {
        "name": name,
        "speedX": list(speed_x),
        "speedY": list(speed_y),
        "bend": round(metrics["bend"], 3),
        "pitch": metrics["pitch"],
        "inflection": None if metrics["inflection"] is None else round(metrics["inflection"], 3),
        "closest": round(metrics["closest"], 3),
        "degree": [degree_x, degree_y],
    }


def build():
    return {"title": "named curves from the septic sandbox",
            "curves": [record(*curve) for curve in CURVES]}


def main():
    document = build()
    OUT.write_text(json.dumps(document, indent=2) + "\n")
    for curve in document["curves"]:
        print(f"{curve['name']:12s} bend {curve['bend']:.3f}  pitch {curve['pitch']:,}  "
              f"degree {curve['degree']}")


if __name__ == "__main__":
    main()
