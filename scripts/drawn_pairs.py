"""Two drawn curves: Lissajous, and the yin-yang boundary.

    .venv/bin/python scripts/drawn_pairs.py

Neither is a new species of curve — the Lissajous figure is transcendental and
the yin-yang boundary is an exact pair of semicircles. They are here because a
catalogue of curves should include the shapes people actually draw, and because
the yin-yang boundary is the cleanest example of an exact arc composition that
is not a single named curve.
"""

from __future__ import annotations

import math


def lissajous(a=3, b=2, phase=math.pi / 2, n=1600):
    """x = sin(a t + phase), y = sin(b t), t ∈ [0, 2π]."""
    return [(math.sin(a * (2 * math.pi * i / n) + phase),
             math.sin(b * (2 * math.pi * i / n))) for i in range(n + 1)]


def yin_yang(n=240):
    """The S-boundary: semicircle (0,1)→(0,0) about (0,½), then (0,0)→(0,−1) about (0,−½)."""
    out = []
    for i in range(n + 1):                       # right semicircle, (0,1) → (0,0)
        th = math.pi / 2 - math.pi * i / n
        out.append((0.5 * math.cos(th), 0.5 + 0.5 * math.sin(th)))
    for i in range(n + 1):                       # left semicircle, (0,0) → (0,−1)
        th = math.pi / 2 + math.pi * i / n
        out.append((0.5 * math.cos(th), -0.5 + 0.5 * math.sin(th)))
    return out


def cases():
    return [
        ("Lissajous · 3:2", lissajous(),
         "x = sin(3t + π/2), y = sin(2t) · transcendental, drawn not claimed exact",
         "scripts/drawn_pairs.py"),
        ("yin-yang · the S-boundary", yin_yang(),
         "two semicircles, radius ½, centres (0,±½) · exact arcs; with the unit circle it is the symbol",
         "scripts/drawn_pairs.py"),
    ]


if __name__ == "__main__":
    for title, pts, note, source in cases():
        print(f"{title}: {len(pts)} points · {note}")
