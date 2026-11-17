"""Exact metrics for a polynomial PH curve, at any degree.

    from ph_quintic_metrics import metrics
    metrics((2, -3, 3), (2, -12, 12))

The curve is `r(t) = integral of w(t)^2 dt` with `w = u + i v`, and `u`, `v`
are polynomials of any degree.  In the centred frame `h = t - 1/2`,

    w(h) = sum_k c_k h^k

and both integrals are finite sums, because

    integral of h^m over [-1/2, 1/2] = 0                  m odd
                                     = 1 / (2^m (m+1))    m even

so

    arc   = sum_{k,l} (cx_k cx_l + cy_k cy_l) * W(k+l)
    chord = sum_{k,l} (cx_k cx_l - cy_k cy_l) * W(k+l)
          + i sum_{k,l} (cx_k cy_l + cy_k cx_l) * W(k+l)
    bend  = arc / |chord|

Nothing is sampled.  Degree 2 gives the weights 1, 1/12, 1/80 used by the
gallery; degree 3 gives the next row, and so on.  The grid, the inflection
and the closest approach are computed the same way at every degree.

**This file is now a facade.** The arithmetic moved to `curve_lab/measure.py`
on 2026-11-16 so the engine holds one reference instead of two: the page's
JavaScript squared a row of 10^8 and reported grid 5,148 where this arithmetic
gives 36, and a copy in a script could drift the same way. The names below are
kept because a dozen scripts and tests import them; new code should import
`curve_lab.measure` directly.
"""

from __future__ import annotations

import math
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from curve_lab.measure import (  # noqa: E402
    arc_and_chord,
    bend,
    centred,
    closest,
    curve_polynomials,
    grid,
    inflection,
    inflections,
    metrics,
    speeds_from_terms,
    to_fraction,
    weight,
)

__all__ = [
    "to_fraction",
    "curve_polynomials",
    "diagnostics",
    "centred",
    "weight",
    "exact_bend",
    "pitch",
    "grid",
    "inflection",
    "inflections",
    "closest",
    "metrics",
    "speeds_from_terms",
]


def exact_bend(speed_x, speed_y):
    """(arc, chord, bend), exactly. The old name for `arc_and_chord`."""
    return arc_and_chord(speed_x, speed_y)


def pitch(speed_x, speed_y) -> int:
    """The grid, under the name the pages and older scripts use."""
    return grid(speed_x, speed_y)


def _trim(polynomial):
    out = list(polynomial)
    while out and not out[-1]:
        out.pop()
    return out


def diagnostics(speed_x, speed_y):
    """The degeneracy checks, in one place, with a level and a message."""
    x, y = curve_polynomials(speed_x, speed_y)

    def degree(polynomial):
        for k in range(len(polynomial) - 1, -1, -1):
            if polynomial[k]:
                return k
        return 0

    def is_zero(polynomial):
        return all(not coefficient for coefficient in polynomial) or not polynomial

    degree_x, degree_y = degree(x), degree(y)
    m = metrics(speed_x, speed_y)
    report = [
        {
            "code": "degree",
            "level": "info",
            "message": f"degree {max(degree_x, degree_y)} (x {degree_x}, y {degree_y})",
        }
    ]
    if degree_x == 0 and degree_y == 0:
        report.append({"code": "point", "level": "error", "message": "the curve is a single point"})
    if is_zero(x) or is_zero(y):
        report.append(
            {
                "code": "axis-line",
                "level": "error",
                "message": "one coordinate is identically zero: an axis-aligned straight line",
            }
        )
    if m["bend"] <= 1 + 1e-9:
        report.append(
            {"code": "straight", "level": "warning", "message": "the curve is a straight line (bend 1.00)"}
        )
    if m["closest"] <= 1e-9:
        report.append({"code": "cusp", "level": "error", "message": "the speed vanishes: a cusp"})
    if m["inflection"] is None:
        report.append({"code": "no-inflection", "level": "warning", "message": "no inflection: a C, not an S"})
    return report


if __name__ == "__main__":
    for label, u, v in [
        ("the pick", (2, -3, 3), (2, -12, 12)),
        ("the target", (Fraction(1, 5), -2, 2), (Fraction(2, 5), Fraction(-3, 2), Fraction(8, 5))),
        ("degree 7", (1, 0, 0, 0), (0, 1, 0, 0)),
    ]:
        m = metrics(u, v)
        print(
            f"{label:10s} bend {m['bend']:6.3f}  pitch {m['pitch']:>6}  "
            f"inflection {m['inflection']}  closest {m['closest']:.2f}"
        )
