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


def yin_yang_g2(a=0.7, spans=4, n=90):
    """A G2 S-boundary: quintic Hermite spans spliced at matched p, p', p''.

    The underlying curve is (a·sin 2πt, 1 − 2t); each span interpolates the
    position, first and second derivatives at its ends, so the joins are G2.
    """
    from missing_families import quintic_hermite

    def P(t):
        return (a * math.sin(2 * math.pi * t), 1.0 - 2.0 * t)

    def dP(t):
        return (2 * math.pi * a * math.cos(2 * math.pi * t), -2.0)

    def d2P(t):
        return (-4 * math.pi ** 2 * a * math.sin(2 * math.pi * t), 0.0)

    pts, knots = [], [0.0]
    for s in range(spans):
        t0, t1 = s / spans, (s + 1) / spans
        h = t1 - t0
        span = quintic_hermite(
            P(t0), P(t1),
            (h * dP(t0)[0], h * dP(t0)[1]), (h * dP(t1)[0], h * dP(t1)[1]),
            (h * h * d2P(t0)[0], h * h * d2P(t0)[1]),
            (h * h * d2P(t1)[0], h * h * d2P(t1)[1]), n=n)
        pts.extend(span if not pts else span[1:])
        knots.append(t1)
    return pts, [P(t) for t in knots]


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
    g2, _knots = yin_yang_g2()
    return [
        ("Lissajous · 3:2", lissajous(),
         "x = sin(3t + π/2), y = sin(2t) · transcendental, drawn not claimed exact",
         "scripts/drawn_pairs.py"),
        ("yin-yang · G2 splice", g2,
         "four quintic Hermite spans · p, p′, p″ matched at the three interior knots",
         "scripts/drawn_pairs.py"),
    ]


if __name__ == "__main__":
    for title, pts, note, source in cases():
        print(f"{title}: {len(pts)} points · {note}")
