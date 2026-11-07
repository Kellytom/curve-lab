"""The Maclaurin trisectrix: a rational curve with an irrational node.

    .venv/bin/python scripts/maclaurin.py

y²(1 + x) = x²(3 − x). Lines through the node give the parametrisation

    x = (3 − t²)/(1 + t²),   y = t x.

The loop is t ∈ [−√3, √3], and the node is exactly at t = ±√3 — so the loop
closes on an irrational parameter, exactly like the Reuleaux's 60°. The exact
loop is drawn with √3 and declared; the Pell copy uses 71/41 for √3 and leaves
a gap that is measured.
"""

from __future__ import annotations

import math


def point(t):
    x = (3.0 - t * t) / (1.0 + t * t)
    return (x, t * x)


def loop(k, n=500):
    return [point(-k + 2 * k * i / n) for i in range(n + 1)]


def equation(x, y):
    """The residual of y²(1+x) − x²(3−x); zero on the curve."""
    return y * y * (1.0 + x) - x * x * (3.0 - x)


ROOT3 = math.sqrt(3.0)
PELL3 = 71.0 / 41.0            # below √3, so the loop leaves a gap at the node


def cases():
    exact = loop(ROOT3)
    pell = loop(PELL3)
    return [
        ("Maclaurin trisectrix · exact loop", exact,
         "t ∈ [−√3, √3] · node at t = ±√3 · irrational, declared outside NAMED",
         "scripts/maclaurin.py"),
        ("Maclaurin trisectrix · Pell 71/41", pell,
         f"the same loop at 71/41 for √3 · node gap {math.dist(pell[0], pell[-1]):.2e}",
         "scripts/maclaurin.py · Pell 71/41"),
    ]


if __name__ == "__main__":
    for title, pts, note, source in cases():
        worst = max(abs(equation(x, y)) for x, y in pts[::10])
        print(f"{title}: residual {worst:.1e}, gap {math.dist(pts[0], pts[-1]):.2e}")
